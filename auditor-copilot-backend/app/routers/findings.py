"""
Audit Findings and Formal Reports router.
Enforces multi-tenant isolation and reviewer role requirement for finding closure.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
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
from app.routers.auth import (
    OrganizationContext,
    get_current_context,
    require_reviewer_role,
)

router = APIRouter(prefix="/findings", tags=["Findings & Reports"])


class FindingCloseRequest(BaseModel):
    closure_notes: Optional[str] = None


@router.get("")
def list_findings(
    engagement_id: Optional[str] = None,
    severity: Optional[str] = None,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """List all confirmed audit findings with severity and remediation status."""
    query = db.query(AuditFinding).filter(AuditFinding.organization_id == ctx.organization_id)
    eff_eng_id = engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    if eff_eng_id:
        try:
            query = query.filter(AuditFinding.engagement_id == uuid.UUID(eff_eng_id))
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
    req: FindingCreateRequest,
    engagement_id: Optional[str] = None,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Create a formal audit finding and link supporting exceptions."""
    eff_eng_id = engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    if not eff_eng_id:
        raise HTTPException(status_code=400, detail="Missing engagement ID for finding creation.")

    try:
        eng_uuid = uuid.UUID(eff_eng_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID.")

    code = f"FND-{uuid.uuid4().hex[:6].upper()}"
    finding = AuditFinding(
        organization_id=ctx.organization_id,
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
        validated_by=ctx.user_id,
        validated_at=datetime.utcnow(),
        created_by=ctx.user_id,
    )
    db.add(finding)
    db.flush()

    # Link exceptions
    if req.exception_ids:
        for exc_id in req.exception_ids:
            try:
                db.add(FindingException(
                    organization_id=ctx.organization_id,
                    engagement_id=eng_uuid,
                    finding_id=finding.id,
                    exception_id=uuid.UUID(exc_id),
                ))
            except Exception:
                pass

    event = AuditEventLog(
        organization_id=ctx.organization_id,
        engagement_id=eng_uuid,
        actor_user_id=ctx.user_id,
        event_type="finding_created",
        entity_type="audit_findings",
        entity_id=finding.id,
        event_metadata={"action": f"Created finding {code}: {req.title}", "severity": req.severity},
    )
    db.add(event)
    db.commit()

    return {
        "status": "success",
        "finding_id": str(finding.id),
        "finding_code": finding.finding_code,
        "title": finding.title,
    }


@router.post("/{finding_id}/close")
def close_finding(
    finding_id: str,
    req: Optional[FindingCloseRequest] = None,
    ctx: OrganizationContext = Depends(require_reviewer_role),
    db: Session = Depends(get_db),
):
    """Reviewer gate: close an audit finding. Requires Reviewer or Manager role."""
    try:
        fnd_uuid = uuid.UUID(finding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid finding UUID format.")

    finding = db.query(AuditFinding).filter(
        AuditFinding.id == fnd_uuid,
        AuditFinding.organization_id == ctx.organization_id,
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found.")

    finding.status = "closed"
    finding.updated_at = datetime.utcnow()
    db.commit()

    return {
        "status": "closed",
        "finding_id": str(finding.id),
        "finding_code": finding.finding_code,
        "closed_by": str(ctx.user_id),
        "closed_at": datetime.utcnow().isoformat(),
    }
