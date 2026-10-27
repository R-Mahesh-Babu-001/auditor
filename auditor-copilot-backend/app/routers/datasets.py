"""
Datasets router for tabular data profiling, canonical field mapping, and normalization.
"""

import io
import csv
import uuid
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
)
from app.routers.auth import get_default_context
from app.audit.profiling import (
    profile_dataset_rows,
    suggest_canonical_mappings,
    normalize_row_to_canonical,
)

router = APIRouter(prefix="/datasets", tags=["Datasets & Profiling"])


@router.get("")
def list_datasets(
    engagement_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all audit datasets with row counts and profiling status."""
    org, _ = get_default_context(db)
    query = db.query(AuditDataset).filter(AuditDataset.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditDataset.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass

    datasets = query.order_by(AuditDataset.created_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "dataset_code": d.dataset_code,
            "dataset_name": d.dataset_name,
            "dataset_type": d.dataset_type,
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
    dataset_type: str = Form("p2p_transactions"),
    db: Session = Depends(get_db),
):
    """Upload a CSV/XLSX file, profile fields, suggest canonical mappings, and store rows."""
    org, user = get_default_context(db)
    try:
        eng_uuid = uuid.UUID(engagement_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID.")

    content = await file.read()
    filename = file.filename.lower()

    rows: List[Dict[str, Any]] = []
    if filename.endswith(".csv"):
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = [dict(r) for r in reader]
    elif filename.endswith((".xlsx", ".xls")):
        import pandas as pd
        df = pd.read_excel(io.BytesIO(content))
        # Fill NaN with empty string
        df = df.where(pd.notnull(df), None)
        rows = df.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="Only CSV or XLSX files are supported for tabular datasets.")

    if not rows:
        raise HTTPException(status_code=400, detail="Uploaded dataset file contains zero data rows.")

    # Profile rows
    profile = profile_dataset_rows(rows)
    suggested_mappings = suggest_canonical_mappings(list(rows[0].keys()))

    # Build mapping dict
    mapping_dict = {m["source_column"]: m["canonical_field"] for m in suggested_mappings if m["canonical_field"]}

    # Create dataset record in Neon DB
    code = f"DS-{uuid.uuid4().hex[:6].upper()}"
    dataset = AuditDataset(
        organization_id=org.id,
        engagement_id=eng_uuid,
        dataset_code=code,
        dataset_name=dataset_name,
        dataset_type=dataset_type,
        version_number=1,
        schema_definition=profile,
        row_count=len(rows),
        valid_row_count=len(rows),
        invalid_row_count=0,
        status="profiled",
        created_by=user.id,
    )
    db.add(dataset)
    db.flush()

    # Store column mappings
    for col in suggested_mappings:
        c_model = DatasetColumn(
            organization_id=org.id,
            dataset_id=dataset.id,
            source_column_name=col["source_column"],
            canonical_field=col["canonical_field"],
            mapping_status=col["mapping_status"],
            mapping_confidence=col["confidence"],
            transformation={},
        )
        db.add(c_model)

    # Store first 1,000 rows (respecting Neon 1GB storage limits)
    valid_count = 0
    invalid_count = 0
    for idx, raw_row in enumerate(rows[:1000], start=1):
        norm_row, errors = normalize_row_to_canonical(raw_row, mapping_dict)
        val_status = "invalid" if errors else "valid"
        if errors:
            invalid_count += 1
        else:
            valid_count += 1

        db_row = DatasetRow(
            organization_id=org.id,
            engagement_id=eng_uuid,
            dataset_id=dataset.id,
            row_number=idx,
            raw_data=raw_row,
            normalized_data=norm_row,
            validation_status=val_status,
            validation_errors=errors,
        )
        db.add(db_row)

    dataset.valid_row_count = valid_count
    dataset.invalid_row_count = invalid_count
    db.commit()

    return {
        "status": "success",
        "dataset_id": str(dataset.id),
        "dataset_code": dataset.dataset_code,
        "row_count": len(rows),
        "profile": profile,
        "suggested_mappings": suggested_mappings,
    }


@router.get("/{dataset_id}/preview")
def get_dataset_preview(
    dataset_id: str,
    limit: int = 25,
    db: Session = Depends(get_db),
):
    """Retrieve raw and canonical normalized preview rows for a dataset."""
    org, _ = get_default_context(db)
    try:
        ds_uuid = uuid.UUID(dataset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid dataset UUID.")

    rows = db.query(DatasetRow).filter(
        DatasetRow.dataset_id == ds_uuid,
        DatasetRow.organization_id == org.id,
    ).order_by(DatasetRow.row_number).limit(limit).all()

    return [
        {
            "id": str(r.id),
            "row_number": r.row_number,
            "raw_data": r.raw_data,
            "normalized_data": r.normalized_data,
            "validation_status": r.validation_status,
            "validation_errors": r.validation_errors,
        }
        for r in rows
    ]

