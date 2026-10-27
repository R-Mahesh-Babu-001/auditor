"""
Router for ITGC (Segregation of Duties & Access Controls), Vendor Assurance,
AI Governance reviews, and SOP Process Map persistence.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.db.session import get_db
from app.routers.auth import get_current_context, OrganizationContext
from app.models.governance import SOPProcessMap, AuditEventLog
from app.models.tests import AuditException
from app.models.p2p import P2PSupplier
from app.audit.rules.itgc_and_governance import (
    run_itgc_sod_analysis,
    run_vendor_assurance_review,
    run_ai_governance_review,
    SOD_CONFLICT_PAIRS,
)

router = APIRouter(prefix="/governance", tags=["ITGC & Governance"])


class SoDAnalysisRequest(BaseModel):
    engagement_id: Optional[uuid.UUID] = None
    user_roles: List[Dict[str, Any]]
    leavers: Optional[List[Dict[str, Any]]] = None
    inactive_days_threshold: int = 90
    persist_exceptions: bool = False


class VendorAssuranceRequest(BaseModel):
    engagement_id: Optional[uuid.UUID] = None
    vendors: Optional[List[Dict[str, Any]]] = None
    use_db_suppliers: bool = True


class AIGovernanceRequest(BaseModel):
    engagement_id: Optional[uuid.UUID] = None
    ai_systems: List[Dict[str, Any]]


class SaveSOPMapRequest(BaseModel):
    engagement_id: Optional[uuid.UUID] = None
    source_evidence_id: Optional[uuid.UUID] = None
    title: str
    diagram_json: Dict[str, Any]
    status: str = "draft"


@router.get("/sod-matrix")
def get_sod_matrix():
    """Returns the standard Segregation of Duties conflicting role matrix."""
    return {
        "conflict_pairs": [
            {"role_a": r_a, "role_b": r_b, "rationale": rat}
            for r_a, r_b, rat in SOD_CONFLICT_PAIRS
        ]
    }


@router.post("/itgc/sod")
def execute_itgc_sod(
    req: SoDAnalysisRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Run IT General Controls (SoD conflicts, retained leaver access, dormant accounts)."""
    eff_eng = req.engagement_id or ctx.engagement_id
    res = run_itgc_sod_analysis(
        user_roles=req.user_roles,
        leavers=req.leavers,
        inactive_days_threshold=req.inactive_days_threshold,
    )

    if req.persist_exceptions and eff_eng:
        for exc in res.get("exceptions", []):
            db_exc = AuditException(
                organization_id=ctx.organization_id,
                engagement_id=eff_eng,
                test_run_id=None,
                exception_key=exc["exception_key"],
                exception_type=exc["exception_type"],
                severity=exc["severity"],
                title=exc["title"],
                description=exc["description"],
                observed_values=exc.get("observed_values", {}),
                expected_values=exc.get("expected_values", {}),
                disposition="open",
            )
            db.add(db_exc)
        db.commit()

    return res


@router.post("/vendor-assurance")
def execute_vendor_assurance(
    req: VendorAssuranceRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Run Vendor Assurance verification on active suppliers."""
    vendor_list = req.vendors or []

    if req.use_db_suppliers and not vendor_list:
        suppliers = db.query(P2PSupplier).filter(
            P2PSupplier.organization_id == ctx.organization_id
        ).all()
        for s in suppliers:
            vendor_list.append({
                "vendor_name": s.supplier_name,
                "risk_tier": s.risk_tier or "medium",
                "has_soc_report": s.is_critical_vendor,
                "is_active": s.is_active,
            })

    return run_vendor_assurance_review(vendor_list)


@router.post("/ai-governance")
def execute_ai_governance(
    req: AIGovernanceRequest,
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Run AI Inventory & Governance readiness evaluation against NIST / EU AI Act standards."""
    return run_ai_governance_review(req.ai_systems)


@router.get("/sop-maps")
def list_sop_maps(
    engagement_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """List SOP Process Maps stored in Neon PostgreSQL."""
    query = db.query(SOPProcessMap).filter(
        SOPProcessMap.organization_id == ctx.organization_id
    )
    eff_eng = engagement_id or ctx.engagement_id
    if eff_eng:
        query = query.filter(SOPProcessMap.engagement_id == eff_eng)

    maps = query.order_by(SOPProcessMap.created_at.desc()).all()
    results = [
        {
            "id": str(m.id),
            "engagement_id": str(m.engagement_id),
            "title": m.title,
            "version_number": m.version_number,
            "diagram_json": m.diagram_json,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in maps
    ]
    return {"sop_maps": results, "count": len(results)}


@router.post("/sop-maps")
def save_sop_map(
    req: SaveSOPMapRequest,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Save or update an SOP Process Map diagram in Neon PostgreSQL."""
    eff_eng = req.engagement_id or ctx.engagement_id
    if not eff_eng:
        raise HTTPException(status_code=400, detail="engagement_id is required")

    sop = SOPProcessMap(
        organization_id=ctx.organization_id,
        engagement_id=eff_eng,
        source_evidence_id=req.source_evidence_id,
        title=req.title,
        version_number=1,
        diagram_json=req.diagram_json,
        status=req.status,
        created_by=ctx.user_id,
    )
    db.add(sop)
    db.commit()
    db.refresh(sop)

    return {"message": "SOP map saved successfully", "id": str(sop.id), "title": sop.title}


@router.get("/audit-logs")
def get_audit_event_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    ctx: OrganizationContext = Depends(get_current_context),
):
    """Retrieve immutable audit event logs for compliance verification."""
    logs = db.query(AuditEventLog).filter(
        AuditEventLog.organization_id == ctx.organization_id
    ).order_by(AuditEventLog.created_at.desc()).limit(limit).all()

    results = [
        {
            "id": str(l.id),
            "event_type": l.event_type,
            "entity_type": l.entity_type,
            "entity_id": str(l.entity_id) if l.entity_id else None,
            "actor_user_id": str(l.actor_user_id) if l.actor_user_id else None,
            "created_at": l.created_at.isoformat() if l.created_at else None,
            "event_metadata": l.event_metadata,
        }
        for l in logs
    ]
    return {"audit_logs": results, "count": len(results)}

