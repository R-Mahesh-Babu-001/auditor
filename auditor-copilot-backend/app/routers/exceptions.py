"""
Exceptions router for triage, evidence investigation, and human review decisions.
Provides full source row traceability and enforces multi-tenant isolation.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    AuditException,
    AuditEventLog,
    ExceptionRowLink,
    DatasetRow,
    ExceptionEvidenceLink,
)
from app.schemas import ExceptionDispositionRequest
from app.routers.auth import (
    OrganizationContext,
    get_current_context,
    require_reviewer_role,
)

router = APIRouter(prefix="/exceptions", tags=["Exceptions & Triage"])


@router.get("")
def list_exceptions(
    engagement_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """List exceptions filterable by engagement, status, and severity."""
    query = db.query(AuditException).filter(AuditException.organization_id == ctx.organization_id)
    eff_eng_id = engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    if eff_eng_id:
        try:
            query = query.filter(AuditException.engagement_id == uuid.UUID(eff_eng_id))
        except ValueError:
            pass
    if status:
        query = query.filter(AuditException.status == status)
    if severity:
        query = query.filter(AuditException.severity == severity)

    exceptions = query.order_by(AuditException.created_at.desc()).limit(limit).all()
    return [
        {
            "id": str(e.id),
            "exception_key": e.exception_key,
            "exception_type": e.exception_type,
            "title": e.title,
            "description": e.description,
            "severity": e.severity,
            "status": e.status,
            "expected_values": e.expected_values,
            "observed_values": e.observed_values,
            "resolution_code": e.resolution_code,
            "resolution_notes": e.resolution_notes,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in exceptions
    ]


@router.get("/{exception_id}")
def get_exception_details(
    exception_id: str,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Retrieve full details, observed/expected records, and evidence links for an exception."""
    try:
        exc_uuid = uuid.UUID(exception_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exception UUID.")

    exc = db.query(AuditException).filter(
        AuditException.id == exc_uuid,
        AuditException.organization_id == ctx.organization_id,
    ).first()

    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found.")

    # Retrieve associated source rows
    row_links = db.query(ExceptionRowLink).filter(
        ExceptionRowLink.exception_id == exc.id,
        ExceptionRowLink.organization_id == ctx.organization_id,
    ).all()

    linked_rows = []
    for rl in row_links:
        row = db.query(DatasetRow).filter(
            DatasetRow.id == rl.dataset_row_id,
            DatasetRow.organization_id == ctx.organization_id,
        ).first()
        linked_rows.append({
            "dataset_id": str(rl.dataset_id),
            "dataset_row_id": str(rl.dataset_row_id),
            "link_role": rl.link_role,
            "row_number": row.row_number if row else None,
            "data": (row.normalized_data or row.raw_data) if row else {},
        })

    return {
        "id": str(exc.id),
        "exception_key": exc.exception_key,
        "exception_type": exc.exception_type,
        "title": exc.title,
        "description": exc.description,
        "severity": exc.severity,
        "status": exc.status,
        "expected_values": exc.expected_values,
        "observed_values": exc.observed_values,
        "rationale": exc.rationale,
        "resolution_code": exc.resolution_code,
        "resolution_notes": exc.resolution_notes,
        "source_rows": linked_rows,
        "created_at": exc.created_at.isoformat() if exc.created_at else None,
    }


@router.post("/{exception_id}/disposition")
def submit_exception_disposition(
    exception_id: str,
    req: ExceptionDispositionRequest,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Record human auditor disposition review decision (confirmed finding, false positive, accepted, etc.)."""
    try:
        exc_uuid = uuid.UUID(exception_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exception UUID.")

    exc = db.query(AuditException).filter(
        AuditException.id == exc_uuid,
        AuditException.organization_id == ctx.organization_id,
    ).first()

    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found.")

    # If closing or accepting exception, verify reviewer role
    if req.status in ("closed", "accepted_exception"):
        allowed_roles = {"audit_manager", "reviewer", "admin", "org_admin", "lead_auditor"}
        if ctx.role.lower() not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Closing or accepting exceptions requires Reviewer or Manager role. Current role is '{ctx.role}'."
            )

    before_status = exc.status
    exc.status = req.status
    exc.resolution_code = req.resolution_code or req.status
    exc.resolution_notes = req.resolution_notes
    exc.reviewed_by = ctx.user_id
    exc.reviewed_at = datetime.utcnow()
    if req.status in ("closed", "false_positive", "accepted_exception"):
        exc.closed_at = datetime.utcnow()

    # Log audit event
    event = AuditEventLog(
        organization_id=ctx.organization_id,
        engagement_id=exc.engagement_id,
        actor_user_id=ctx.user_id,
        event_type="exception_disposition",
        entity_type="audit_exceptions",
        entity_id=exc.id,
        event_metadata={"action": f"Changed status from {before_status} to {req.status}", "reason": req.resolution_notes},
    )
    db.add(event)
    db.commit()

    return {
        "status": "success",
        "exception_id": str(exc.id),
        "new_status": exc.status,
        "reviewed_at": exc.reviewed_at.isoformat(),
    }
