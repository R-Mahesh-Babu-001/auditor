"""
Audit Findings and Formal Reports router.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    AuditFinding,
    FindingException,
    AuditException,
    AuditEventLog,
)
from app.schemas import FindingCreateRequest
from app.routers.auth import get_default_context

router = APIRouter(prefix="/findings", tags=["Findings & Reports"])


@router.get("")
def list_findings(
    engagement_id: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all confirmed audit findings with severity and remediation status."""
    org, _ = get_default_context(db)
    query = db.query(AuditFinding).filter(AuditFinding.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditFinding.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass
    if severity:
        query = query.filter(AuditFinding.severity == severity)

    findings = query.order_by(AuditFinding.created_at.desc()).all()
    return [
        {
            "id": str(f.id),
            "finding_code": f.finding_code,
            "title": f.title,
            "severity": f.severity,
            "status": f.status,
            "condition_text": f.condition_text,
            "criteria_text": f.criteria_text,
            "cause_text": f.cause_text,
            "consequence_text": f.consequence_text,
            "recommendation_text": f.recommendation_text,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in findings
    ]


@router.post("")
def create_finding(
    engagement_id: str,
    req: FindingCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a formal audit finding and link supporting exceptions."""
    org, user = get_default_context(db)
    try:
        eng_uuid = uuid.UUID(engagement_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID.")

    code = f"FND-{uuid.uuid4().hex[:6].upper()}"
    finding = AuditFinding(
        organization_id=org.id,
        engagement_id=eng_uuid,
        finding_code=code,
        title=req.title,
        severity=req.severity,
        status="confirmed",
        condition_text=req.condition_text,
        criteria_text=req.criteria_text,
        cause_text=req.cause_text,
        consequence_text=req.consequence_text,
        recommendation_text=req.recommendation_text,
        management_response=req.management_response,
        validated_by=user.id,
        validated_at=datetime.utcnow(),
        created_by=user.id,
    )
    db.add(finding)
    db.flush()

    # Link exceptions
    if req.exception_ids:
        for exc_id in req.exception_ids:
            try:
                db.add(FindingException(
                    organization_id=org.id,
                    engagement_id=eng_uuid,
                    finding_id=finding.id,
                    exception_id=uuid.UUID(exc_id),
                ))
            except Exception:
                pass

    event = AuditEventLog(
        organization_id=org.id,
        engagement_id=eng_uuid,
        actor_user_id=user.id,
        event_type="finding_created",
        entity_type="audit_findings",
        entity_id=finding.id,
        action=f"Created finding {code}: {req.title}",
        event_metadata={"severity": req.severity},
    )
    db.add(event)
    db.commit()

    return {
        "status": "success",
        "finding_id": str(finding.id),
        "finding_code": finding.finding_code,
        "title": finding.title,
    }

