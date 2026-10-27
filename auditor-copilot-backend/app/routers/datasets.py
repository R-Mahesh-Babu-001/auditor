"""
Datasets router for tabular data profiling, canonical field mapping, row normalization, and validation.
Enforces canonical dataset types, SHA-256 deduplication, real row-level validation metrics, and multi-tenant isolation.
"""

import io
import csv
import uuid
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    AuditDataset,
    DatasetColumn,
    DatasetRow,
    AuditEngagement,
    EvidenceFile,
)
from app.schemas import DatasetMappingRequest
from app.routers.auth import OrganizationContext, get_current_context
from app.audit.profiling import (
    CANONICAL_DATASET_TYPES,
    profile_dataset_rows,
    suggest_canonical_mappings,
    normalize_row_to_canonical,
)

router = APIRouter(prefix="/datasets", tags=["Datasets & Profiling"])


@router.get("")
def list_datasets(
    engagement_id: Optional[str] = None,
    dataset_type: Optional[str] = None,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """List all audit datasets with real row counts, validation metrics, and profiling status."""
    query = db.query(AuditDataset).filter(AuditDataset.organization_id == ctx.organization_id)
    eff_eng_id = engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    if eff_eng_id:
        try:
            query = query.filter(AuditDataset.engagement_id == uuid.UUID(eff_eng_id))
        except ValueError:
            pass

    if dataset_type:
        query = query.filter(AuditDataset.dataset_type == dataset_type)

    datasets = query.order_by(AuditDataset.created_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "dataset_code": d.dataset_code,
            "dataset_name": d.dataset_name,
            "dataset_type": d.dataset_type,
            "version_number": d.version_number,
            "row_count": d.row_count,
            "valid_row_count": d.valid_row_count,
            "invalid_row_count": d.invalid_row_count,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in datasets
    ]


@router.post("/upload")
async def upload_and_profile_dataset(
    file: UploadFile = File(...),
    engagement_id: str = Form(...),
    dataset_name: str = Form(...),
    dataset_type: str = Form("invoices"),
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Upload a CSV/XLSX file, profile fields, suggest canonical mappings, validate rows, and persist dataset."""
    try:
        eng_uuid = uuid.UUID(engagement_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID format.")

    # Validate engagement belongs to caller's organization
    engagement = db.query(AuditEngagement).filter(
        AuditEngagement.id == eng_uuid,
        AuditEngagement.organization_id == ctx.organization_id,
    ).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found in active organization.")

    # Validate canonical dataset type
    clean_type = dataset_type.lower().strip()
    # Normalize aliases
    alias_map = {
        "p2p_transactions": "invoices",
        "purchase_order": "purchase_orders",
        "po": "purchase_orders",
        "goods_receipt": "goods_receipts",
        "gr": "goods_receipts",
        "invoice": "invoices",
        "payment": "payments",
        "approval": "approvals",
        "supplier": "suppliers",
        "vendor": "suppliers",
        "user": "user_access",
        "employee": "employee_directory",
        "ai": "ai_system_inventory",
    }
    clean_type = alias_map.get(clean_type, clean_type)

    if clean_type not in CANONICAL_DATASET_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dataset_type '{dataset_type}'. Must be one of: {', '.join(CANONICAL_DATASET_TYPES)}",
        )

    content = await file.read()
    file_sha256 = hashlib.sha256(content).hexdigest()
    filename = file.filename.lower()

    # Check for duplicate file upload in this engagement
    existing_duplicate = db.query(AuditDataset).filter(
        AuditDataset.organization_id == ctx.organization_id,
        AuditDataset.engagement_id == eng_uuid,
        AuditDataset.schema_definition["file_sha256"].astext == file_sha256,
    ).first()

    if existing_duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"Identical file already ingested in this engagement as dataset '{existing_duplicate.dataset_name}' ({existing_duplicate.dataset_code}).",
        )

    rows: List[Dict[str, Any]] = []
    if filename.endswith(".csv"):
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = [dict(r) for r in reader]
    elif filename.endswith((".xlsx", ".xls")):
        import pandas as pd
        df = pd.read_excel(io.BytesIO(content))
        df = df.where(pd.notnull(df), None)
        rows = df.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="Only CSV or XLSX files are supported for tabular datasets.")

    if not rows:
        raise HTTPException(status_code=400, detail="Uploaded dataset file contains zero data rows.")

    # Profile rows
    profile = profile_dataset_rows(rows)
    profile["file_sha256"] = file_sha256
    profile["original_filename"] = file.filename

    # Suggest canonical mappings
    suggested_mappings = suggest_canonical_mappings(list(rows[0].keys()))
    mapping_dict = {
        m["source_column"]: m["canonical_field"]
        for m in suggested_mappings
        if m["canonical_field"]
    }

    # Create dataset record in Neon DB
    code = f"DS-{uuid.uuid4().hex[:6].upper()}"
    dataset = AuditDataset(
        organization_id=ctx.organization_id,
        engagement_id=eng_uuid,
        dataset_code=code,
        dataset_name=dataset_name,
        dataset_type=clean_type,
        version_number=1,
        schema_definition=profile,
        row_count=len(rows),
        valid_row_count=0,
        invalid_row_count=0,
        status="profiling",
        created_by=ctx.user_id,
    )
    db.add(dataset)
    db.flush()

    # Store column mappings
    for col in suggested_mappings:
        c_model = DatasetColumn(
            organization_id=ctx.organization_id,
            dataset_id=dataset.id,
            source_column_name=col["source_column"],
            canonical_field=col["canonical_field"],
            mapping_status=col["mapping_status"],
            mapping_confidence=col["confidence"],
            transformation={},
        )
        db.add(c_model)

    # Store rows with truthful row-level validation
    valid_count = 0
    invalid_count = 0
    for idx, raw_row in enumerate(rows, start=1):
        norm_row, errors = normalize_row_to_canonical(raw_row, mapping_dict, dataset_type=clean_type)
        row_status = "invalid" if errors else "valid"
        if errors:
            invalid_count += 1
        else:
            valid_count += 1

        row_sha = hashlib.sha256(str(sorted(raw_row.items())).encode("utf-8")).hexdigest()
        db_row = DatasetRow(
            organization_id=ctx.organization_id,
            engagement_id=eng_uuid,
            dataset_id=dataset.id,
            row_number=idx,
            raw_data=raw_row,
            normalized_data=norm_row,
            row_sha256=row_sha,
            validation_status=row_status,
            validation_errors=errors,
        )
        db.add(db_row)

    dataset.valid_row_count = valid_count
    dataset.invalid_row_count = invalid_count
    dataset.status = "validated" if valid_count > 0 and invalid_count == 0 else ("validation_failed" if valid_count == 0 else "profiled")
    db.commit()

    return {
        "status": "success",
        "dataset_id": str(dataset.id),
        "dataset_code": dataset.dataset_code,
        "dataset_name": dataset.dataset_name,
        "dataset_type": dataset.dataset_type,
        "row_count": len(rows),
        "valid_row_count": valid_count,
        "invalid_row_count": invalid_count,
        "dataset_status": dataset.status,
        "profile": profile,
        "suggested_mappings": suggested_mappings,
    }


@router.get("/{dataset_id}/preview")
def get_dataset_preview(
    dataset_id: str,
    limit: int = 50,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Retrieve raw and canonical normalized preview rows with row validation details."""
    try:
        ds_uuid = uuid.UUID(dataset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid dataset UUID format.")

    dataset = db.query(AuditDataset).filter(
        AuditDataset.id == ds_uuid,
        AuditDataset.organization_id == ctx.organization_id,
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    rows = db.query(DatasetRow).filter(
        DatasetRow.dataset_id == ds_uuid,
        DatasetRow.organization_id == ctx.organization_id,
    ).order_by(DatasetRow.row_number).limit(limit).all()

    return {
        "dataset_id": str(dataset.id),
        "dataset_code": dataset.dataset_code,
        "dataset_name": dataset.dataset_name,
        "dataset_type": dataset.dataset_type,
        "row_count": dataset.row_count,
        "valid_row_count": dataset.valid_row_count,
        "invalid_row_count": dataset.invalid_row_count,
        "status": dataset.status,
        "rows": [
            {
                "id": str(r.id),
                "row_number": r.row_number,
                "raw_data": r.raw_data,
                "normalized_data": r.normalized_data,
                "validation_status": r.validation_status,
                "validation_errors": r.validation_errors,
            }
            for r in rows
        ],
    }


@router.post("/{dataset_id}/mapping")
def update_dataset_mapping(
    dataset_id: str,
    req: DatasetMappingRequest,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Update column mappings and re-normalize rows."""
    try:
        ds_uuid = uuid.UUID(dataset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid dataset UUID format.")

    dataset = db.query(AuditDataset).filter(
        AuditDataset.id == ds_uuid,
        AuditDataset.organization_id == ctx.organization_id,
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    mapping_dict = {}
    for m in req.mappings:
        mapping_dict[m.source_column] = m.canonical_field
        col = db.query(DatasetColumn).filter(
            DatasetColumn.dataset_id == ds_uuid,
            DatasetColumn.source_column_name == m.source_column,
        ).first()
        if col:
            col.canonical_field = m.canonical_field
            col.mapping_status = "confirmed" if m.is_confirmed else "proposed"
            col.updated_at = datetime.utcnow()

    # Re-normalize rows
    rows = db.query(DatasetRow).filter(DatasetRow.dataset_id == ds_uuid).all()
    valid_count = 0
    invalid_count = 0
    for r in rows:
        norm, errors = normalize_row_to_canonical(r.raw_data, mapping_dict, dataset_type=dataset.dataset_type)
        r.normalized_data = norm
        r.validation_status = "invalid" if errors else "valid"
        r.validation_errors = errors
        if errors:
            invalid_count += 1
        else:
            valid_count += 1

    dataset.valid_row_count = valid_count
    dataset.invalid_row_count = invalid_count
    dataset.status = "validated" if valid_count > 0 and invalid_count == 0 else "profiled"
    dataset.updated_at = datetime.utcnow()
    db.commit()

    return {
        "status": "success",
        "dataset_id": str(dataset.id),
        "valid_row_count": valid_count,
        "invalid_row_count": invalid_count,
        "dataset_status": dataset.status,
    }
