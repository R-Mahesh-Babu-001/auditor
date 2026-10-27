"""
Risk and Control Matrix (RCM) router for criteria, risks, controls, and mapping verification.
"""

import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    AuditCriterion,
    AuditRisk,
    AuditControl,
    CriteriaControlMapping,
    RiskControlMapping,
)
from app.routers.auth import get_default_context

router = APIRouter(prefix="/rcm", tags=["Risk & Control Matrix"])


@router.get("/criteria")
def list_criteria(
    engagement_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    org, _ = get_default_context(db)
    query = db.query(AuditCriterion).filter(AuditCriterion.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditCriterion.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass
    items = query.order_by(AuditCriterion.criterion_code).all()
    return [
        {
            "id": str(c.id),
            "criterion_code": c.criterion_code,
            "title": c.title,
            "requirement_type": c.requirement_type,
            "requirement_text": c.requirement_text,
            "status": c.status,
            "version_number": c.version_number,
        }
        for c in items
    ]


@router.get("/risks")
def list_risks(
    engagement_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    org, _ = get_default_context(db)
    query = db.query(AuditRisk).filter(AuditRisk.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditRisk.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass
    items = query.order_by(AuditRisk.risk_code).all()
    return [
        {
            "id": str(r.id),
            "risk_code": r.risk_code,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "status": r.status,
        }
        for r in items
    ]


@router.get("/controls")
def list_controls(
    engagement_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    org, _ = get_default_context(db)
    query = db.query(AuditControl).filter(AuditControl.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(AuditControl.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass
    items = query.order_by(AuditControl.control_code).all()
    return [
        {
            "id": str(c.id),
            "control_code": c.control_code,
            "title": c.title,
            "description": c.description,
            "control_type": c.control_type,
            "execution_type": c.execution_type,
            "status": c.status,
        }
        for c in items
    ]


@router.get("/coverage")
def get_rcm_coverage(
    engagement_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Return coverage metrics and gap analysis for Risk & Control Matrix."""
    org, _ = get_default_context(db)
    eng_uuid = uuid.UUID(engagement_id) if engagement_id else None

    crit_query = db.query(AuditCriterion).filter(AuditCriterion.organization_id == org.id)
    ctrl_query = db.query(AuditControl).filter(AuditControl.organization_id == org.id)
    risk_query = db.query(AuditRisk).filter(AuditRisk.organization_id == org.id)
    map_query = db.query(CriteriaControlMapping).filter(CriteriaControlMapping.organization_id == org.id)

    if eng_uuid:
        crit_query = crit_query.filter(AuditCriterion.engagement_id == eng_uuid)
        ctrl_query = ctrl_query.filter(AuditControl.engagement_id == eng_uuid)
        risk_query = risk_query.filter(AuditRisk.engagement_id == eng_uuid)
        map_query = map_query.filter(CriteriaControlMapping.engagement_id == eng_uuid)

    criteria = crit_query.all()
    controls = ctrl_query.all()
    risks = risk_query.all()
    mappings = map_query.all()

    mapped_crit_ids = {m.criterion_id for m in mappings}
    unmapped_criteria = [c.criterion_code for c in criteria if c.id not in mapped_crit_ids]

    mapped_ctrl_ids = {m.control_id for m in mappings}
    unmapped_controls = [c.control_code for c in controls if c.id not in mapped_ctrl_ids]

    coverage_pct = round((len(mapped_crit_ids) / len(criteria) * 100.0), 1) if criteria else 100.0

    return {
        "total_criteria": len(criteria),
        "total_controls": len(controls),
        "total_risks": len(risks),
        "total_mappings": len(mappings),
        "coverage_percentage": coverage_pct,
        "unmapped_criteria": unmapped_criteria,
        "unmapped_controls": unmapped_controls,
    }

