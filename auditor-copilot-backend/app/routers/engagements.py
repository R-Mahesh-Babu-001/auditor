"""
Engagements router for managing audit engagement lifecycles, objectives, and scope.
"""

import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditEngagement, EngagementMembership, Organization
from app.schemas import EngagementCreate, EngagementResponse
from app.routers.auth import get_default_context

router = APIRouter(prefix="/engagements", tags=["Engagements"])


@router.get("")
def list_engagements(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all audit engagements for the current organization."""
    org, _ = get_default_context(db)
    query = db.query(AuditEngagement).filter(AuditEngagement.organization_id == org.id)
    if status:
        query = query.filter(AuditEngagement.status == status)
    engagements = query.order_by(AuditEngagement.created_at.desc()).all()

    return [
        {
            "id": str(e.id),
            "organization_id": str(e.organization_id),
            "engagement_code": e.engagement_code,
            "name": e.name,
            "audit_type": e.audit_type,
            "business_unit": e.business_unit,
            "objective": e.objective,
            "scope_description": e.scope_description,
            "period_start": str(e.period_start) if e.period_start else None,
            "period_end": str(e.period_end) if e.period_end else None,
            "status": e.status,
            "overall_risk": e.overall_risk,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in engagements
    ]


@router.post("")
def create_engagement(
    req: EngagementCreate,
    db: Session = Depends(get_db),
):
    """Create a new audit engagement with scope and objectives."""
    org, user = get_default_context(db)

    engagement = AuditEngagement(
        organization_id=org.id,
        engagement_code=req.engagement_code,
        name=req.name,
        audit_type=req.audit_type,
        business_unit=req.business_unit,
        objective=req.objective,
        scope_description=req.scope_description,
        period_start=req.period_start,
        period_end=req.period_end,
        status="planning",
        overall_risk=req.overall_risk or "medium",
        lead_user_id=user.id,
        created_by=user.id,
    )
    db.add(engagement)
    db.flush()

    # Add creator as lead auditor
    membership = EngagementMembership(
        organization_id=org.id,
        engagement_id=engagement.id,
        user_id=user.id,
        engagement_role="lead_auditor",
    )
    db.add(membership)
    db.commit()

    return {
        "status": "success",
        "id": str(engagement.id),
        "engagement_code": engagement.engagement_code,
        "name": engagement.name,
    }


@router.get("/{engagement_id}")
def get_engagement_details(
    engagement_id: str,
    db: Session = Depends(get_db),
):
    """Get full details of a specific audit engagement."""
    org, _ = get_default_context(db)
    try:
        e_uuid = uuid.UUID(engagement_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID.")

    engagement = db.query(AuditEngagement).filter(
        AuditEngagement.id == e_uuid,
        AuditEngagement.organization_id == org.id,
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found.")

    return {
        "id": str(engagement.id),
        "organization_id": str(engagement.organization_id),
        "engagement_code": engagement.engagement_code,
        "name": engagement.name,
        "audit_type": engagement.audit_type,
        "business_unit": engagement.business_unit,
        "objective": engagement.objective,
        "scope_description": engagement.scope_description,
        "period_start": str(engagement.period_start) if engagement.period_start else None,
        "period_end": str(engagement.period_end) if engagement.period_end else None,
        "status": engagement.status,
        "overall_risk": engagement.overall_risk,
        "created_at": engagement.created_at.isoformat() if engagement.created_at else None,
    }

