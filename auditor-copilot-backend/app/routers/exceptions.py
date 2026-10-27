"""
Exceptions router for triage, evidence investigation, and human review decisions.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditException, AuditEventLog
from app.schemas import ExceptionDispositionRequest
from app.routers.auth import get_default_context

router = APIRouter(prefix="/exceptions", tags=["Exceptions & Triage"])


@router.get("")
def list_exceptions(
    engagement_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List exceptions filterable by engagement, status, and severity."""
    org, _ = get_default_context(db)
    query = db.query(AuditException).filter(AuditException.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditException.engagement_id == uuid.UUID(engagement_id))
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
    db: Session = Depends(get_db),
):
    """Retrieve full details, observed/expected records, and evidence links for an exception."""
    org, _ = get_default_context(db)
    try:
        exc_uuid = uuid.UUID(exception_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exception UUID.")

    exc = db.query(AuditException).filter(
        AuditException.id == exc_uuid,
        AuditException.organization_id == org.id,
    ).first()

    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found.")

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
        "created_at": exc.created_at.isoformat() if exc.created_at else None,
    }


@router.post("/{exception_id}/disposition")
def submit_exception_disposition(
    exception_id: str,
    req: ExceptionDispositionRequest,
    db: Session = Depends(get_db),
):
    """Record human auditor disposition review decision (confirmed finding, false positive, accepted, etc.)."""
    org, user = get_default_context(db)
    try:
        exc_uuid = uuid.UUID(exception_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exception UUID.")

    exc = db.query(AuditException).filter(
        AuditException.id == exc_uuid,
        AuditException.organization_id == org.id,
    ).first()

    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found.")

    before_status = exc.status
    exc.status = req.status
    exc.resolution_code = req.resolution_code or req.status
    exc.resolution_notes = req.resolution_notes
    exc.reviewed_by = user.id
    exc.reviewed_at = datetime.utcnow()
    if req.status in ("closed", "false_positive", "accepted_exception"):
        exc.closed_at = datetime.utcnow()

    # Log audit event
    event = AuditEventLog(
        organization_id=org.id,
        engagement_id=exc.engagement_id,
        actor_user_id=user.id,
        event_type="exception_disposition",
        entity_type="audit_exceptions",
        entity_id=exc.id,
        action=f"Changed status from {before_status} to {req.status}",
        event_metadata={"reason": req.resolution_notes},
    )
    db.add(event)
    db.commit()

    return {
        "status": "success",
        "exception_id": str(exc.id),
        "new_status": exc.status,
        "reviewed_at": exc.reviewed_at.isoformat(),
    }

