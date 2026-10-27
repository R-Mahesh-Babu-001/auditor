"""
Router for managing remediation actions, tracking corrective controls,
and verifying remediation evidence in Neon PostgreSQL.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import uuid

from app.db.session import get_db
from app.routers.auth import get_current_context, OrganizationContext
from app.models.workpaper import RemediationAction, RemediationEvidenceLink, AuditFinding
from app.models.evidence import EvidenceFile

router = APIRouter(prefix="/remediation", tags=["Remediation"])


class CreateRemediationRequest(BaseModel):
    engagement_id: Optional[uuid.UUID] = None
    finding_id: uuid.UUID
    action_title: str
    action_description: str
    due_date: Optional[date] = None
    owner_user_id: Optional[uuid.UUID] = None
    management_comment: Optional[str] = None


class UpdateRemediationRequest(BaseModel):
    action_title: Optional[str] = None
    action_description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    owner_user_id: Optional[uuid.UUID] = None
    management_comment: Optional[str] = None


class VerifyRemediationRequest(BaseModel):
    verification_note: Optional[str] = None
    status: str = "verified_closed"


class LinkEvidenceRequest(BaseModel):
    evidence_file_id: uuid.UUID
    evidence_note: Optional[str] = None


@router.get("")
def list_remediations(
    engagement_id: Optional[uuid.UUID] = Query(None),
    finding_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """List all remediation actions for the current organization."""
    query = db.query(RemediationAction).filter(
        RemediationAction.organization_id == ctx.organization_id
    )

    eff_eng = engagement_id or ctx.engagement_id
    if eff_eng:
        query = query.filter(RemediationAction.engagement_id == eff_eng)
    if finding_id:
        query = query.filter(RemediationAction.finding_id == finding_id)
    if status:
        query = query.filter(RemediationAction.status == status)

    actions = query.order_by(RemediationAction.created_at.desc()).all()

    today = date.today()
    results = []
    for a in actions:
        # Check overdue dynamically if still open
        current_status = a.status
        if a.due_date and a.due_date < today and current_status in ["open", "in_progress"]:
            current_status = "overdue"

        results.append({
            "id": str(a.id),
            "organization_id": str(a.organization_id),
            "engagement_id": str(a.engagement_id),
            "finding_id": str(a.finding_id),
            "action_title": a.action_title,
            "action_description": a.action_description,
            "due_date": a.due_date.isoformat() if a.due_date else None,
            "status": current_status,
            "management_comment": a.management_comment,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
            "verified_by": str(a.verified_by) if a.verified_by else None,
            "verified_at": a.verified_at.isoformat() if a.verified_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        })

    return {"actions": results, "count": len(results)}


@router.post("")
def create_remediation(
    req: CreateRemediationRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Create a new remediation action linked to a finding."""
    eff_eng = req.engagement_id or ctx.engagement_id
    if not eff_eng:
        raise HTTPException(status_code=400, detail="engagement_id is required")

    # Verify finding exists
    finding = db.query(AuditFinding).filter(
        AuditFinding.id == req.finding_id,
        AuditFinding.organization_id == ctx.organization_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    action = RemediationAction(
        organization_id=ctx.organization_id,
        engagement_id=eff_eng,
        finding_id=req.finding_id,
        action_title=req.action_title,
        action_description=req.action_description,
        due_date=req.due_date,
        owner_user_id=req.owner_user_id or ctx.user_id,
        status="open",
        management_comment=req.management_comment,
        created_by=ctx.user_id,
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    return {
        "message": "Remediation action created successfully",
        "action": {
            "id": str(action.id),
            "finding_id": str(action.finding_id),
            "action_title": action.action_title,
            "status": action.status,
            "due_date": action.due_date.isoformat() if action.due_date else None,
        }
    }


@router.get("/{action_id}")
def get_remediation_detail(
    action_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Get single remediation action details along with linked evidence and finding info."""
    action = db.query(RemediationAction).filter(
        RemediationAction.id == action_id,
        RemediationAction.organization_id == ctx.organization_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Remediation action not found")

    finding = db.query(AuditFinding).filter(AuditFinding.id == action.finding_id).first()

    links = db.query(RemediationEvidenceLink).filter(
        RemediationEvidenceLink.remediation_action_id == action.id
    ).all()

    evidence_items = []
    for link in links:
        ev = db.query(EvidenceFile).filter(EvidenceFile.id == link.evidence_file_id).first()
        evidence_items.append({
            "link_id": str(link.id),
            "evidence_file_id": str(link.evidence_file_id),
            "filename": ev.filename if ev else "Unknown",
            "evidence_note": link.evidence_note,
            "submitted_at": link.submitted_at.isoformat() if link.submitted_at else None,
        })

    return {
        "id": str(action.id),
        "organization_id": str(action.organization_id),
        "engagement_id": str(action.engagement_id),
        "finding_id": str(action.finding_id),
        "finding_title": finding.title if finding else None,
        "finding_severity": finding.severity if finding else None,
        "action_title": action.action_title,
        "action_description": action.action_description,
        "due_date": action.due_date.isoformat() if action.due_date else None,
        "status": action.status,
        "management_comment": action.management_comment,
        "submitted_at": action.submitted_at.isoformat() if action.submitted_at else None,
        "verified_by": str(action.verified_by) if action.verified_by else None,
        "verified_at": action.verified_at.isoformat() if action.verified_at else None,
        "created_at": action.created_at.isoformat() if action.created_at else None,
        "linked_evidence": evidence_items,
    }


@router.patch("/{action_id}")
def update_remediation(
    action_id: uuid.UUID,
    req: UpdateRemediationRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Update remediation action details or progress."""
    action = db.query(RemediationAction).filter(
        RemediationAction.id == action_id,
        RemediationAction.organization_id == ctx.organization_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Remediation action not found")

    if req.action_title is not None:
        action.action_title = req.action_title
    if req.action_description is not None:
        action.action_description = req.action_description
    if req.status is not None:
        action.status = req.status
        if req.status in ["in_progress", "under_review"] and not action.submitted_at:
            action.submitted_at = datetime.utcnow()
    if req.due_date is not None:
        action.due_date = req.due_date
    if req.owner_user_id is not None:
        action.owner_user_id = req.owner_user_id
    if req.management_comment is not None:
        action.management_comment = req.management_comment

    action.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(action)

    return {"message": "Remediation action updated", "id": str(action.id), "status": action.status}


@router.post("/{action_id}/verify")
def verify_remediation(
    action_id: uuid.UUID,
    req: VerifyRemediationRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Auditor verification and formal closure of remediation action."""
    action = db.query(RemediationAction).filter(
        RemediationAction.id == action_id,
        RemediationAction.organization_id == ctx.organization_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Remediation action not found")

    action.status = req.status
    action.verified_by = ctx.user_id
    action.verified_at = datetime.utcnow()
    if req.verification_note:
        existing_comment = action.management_comment or ""
        action.management_comment = (
            f"{existing_comment}\n[Verification Note ({datetime.utcnow().strftime('%Y-%m-%d')})]: {req.verification_note}"
        ).strip()

    action.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": f"Remediation action marked as {action.status}",
        "id": str(action.id),
        "status": action.status,
        "verified_at": action.verified_at.isoformat(),
    }


@router.post("/{action_id}/evidence")
def link_remediation_evidence(
    action_id: uuid.UUID,
    req: LinkEvidenceRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Attach supporting evidence file proving remediation closure."""
    action = db.query(RemediationAction).filter(
        RemediationAction.id == action_id,
        RemediationAction.organization_id == ctx.organization_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Remediation action not found")

    ev = db.query(EvidenceFile).filter(
        EvidenceFile.id == req.evidence_file_id,
        EvidenceFile.organization_id == ctx.organization_id,
    ).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence file not found")

    link = RemediationEvidenceLink(
        organization_id=ctx.organization_id,
        engagement_id=action.engagement_id,
        remediation_action_id=action.id,
        evidence_file_id=req.evidence_file_id,
        evidence_note=req.evidence_note,
        submitted_by=ctx.user_id,
    )
    db.add(link)
    db.commit()

    return {"message": "Evidence linked to remediation action", "link_id": str(link.id)}

