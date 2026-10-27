"""
Workpapers router for drafting, versioning, evidence verification, and reviewer sign-offs.
Enforces multi-tenant isolation, structured facts generation, and explicit reviewer approval gates.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Workpaper,
    WorkpaperVersion,
    WorkpaperEvidenceLink,
    WorkpaperExceptionLink,
)
from app.schemas import WorkpaperGenerateRequest, WorkpaperApproveRequest
from app.routers.auth import (
    OrganizationContext,
    get_current_context,
    require_reviewer_role,
)
from app.audit.workpapers import generate_structured_workpaper

router = APIRouter(prefix="/workpapers", tags=["Workpapers"])


@router.get("")
def list_workpapers(
    engagement_id: Optional[str] = None,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """List all audit workpapers for the engagement and organization."""
    query = db.query(Workpaper).filter(Workpaper.organization_id == ctx.organization_id)
    eff_eng_id = engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    if eff_eng_id:
        try:
            query = query.filter(Workpaper.engagement_id == uuid.UUID(eff_eng_id))
        except ValueError:
            pass

    wps = query.order_by(Workpaper.created_at.desc()).all()
    return [
        {
            "id": str(w.id),
            "workpaper_code": w.workpaper_code,
            "title": w.title,
            "workpaper_type": w.workpaper_type,
            "status": w.status,
            "approved_by": str(w.approved_by) if w.approved_by else None,
            "approved_at": w.approved_at.isoformat() if w.approved_at else None,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in wps
    ]


@router.post("/generate")
def generate_workpaper(
    req: WorkpaperGenerateRequest,
    engagement_id: Optional[str] = None,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Generate structured audit workpaper with factual evidence verification and facts hashing."""
    eff_eng_id = engagement_id or (str(ctx.engagement_id) if ctx.engagement_id else None)
    if not eff_eng_id:
        raise HTTPException(status_code=400, detail="Missing engagement ID for workpaper generation.")

    try:
        eng_uuid = uuid.UUID(eff_eng_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID format.")

    try:
        return generate_structured_workpaper(
            db=db,
            organization_id=ctx.organization_id,
            engagement_id=eng_uuid,
            title=req.title,
            workpaper_type=req.workpaper_type,
            objective_override=req.objective,
            user_id=ctx.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate workpaper: {str(e)}")


@router.get("/{workpaper_id}/versions")
def get_workpaper_versions(
    workpaper_id: str,
    ctx: OrganizationContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Retrieve full version history and markdown content for a workpaper."""
    try:
        wp_uuid = uuid.UUID(workpaper_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workpaper UUID format.")

    wp = db.query(Workpaper).filter(
        Workpaper.id == wp_uuid,
        Workpaper.organization_id == ctx.organization_id,
    ).first()
    if not wp:
        raise HTTPException(status_code=404, detail="Workpaper not found.")

    versions = db.query(WorkpaperVersion).filter(
        WorkpaperVersion.workpaper_id == wp_uuid,
        WorkpaperVersion.organization_id == ctx.organization_id,
    ).order_by(WorkpaperVersion.version_number.desc()).all()

    return [
        {
            "id": str(v.id),
            "version_number": v.version_number,
            "content_markdown": v.content_markdown,
            "structured_content": v.structured_content,
            "conclusion_status": v.conclusion_status,
            "review_status": v.review_status,
            "input_snapshot_hash": v.input_snapshot_hash,
            "generation_method": v.generation_method,
            "reviewed_by": str(v.reviewed_by) if v.reviewed_by else None,
            "reviewed_at": v.reviewed_at.isoformat() if v.reviewed_at else None,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]


@router.post("/{workpaper_id}/approve")
def approve_workpaper(
    workpaper_id: str,
    req: Optional[WorkpaperApproveRequest] = None,
    ctx: OrganizationContext = Depends(require_reviewer_role),
    db: Session = Depends(get_db),
):
    """Reviewer approval gate: approves a draft workpaper.

    Requires reviewer or manager role. Never automatically approves.
    """
    try:
        wp_uuid = uuid.UUID(workpaper_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workpaper UUID format.")

    wp = db.query(Workpaper).filter(
        Workpaper.id == wp_uuid,
        Workpaper.organization_id == ctx.organization_id,
    ).first()
    if not wp:
        raise HTTPException(status_code=404, detail="Workpaper not found.")

    now = datetime.utcnow()
    wp.status = "approved"
    wp.approved_by = ctx.user_id
    wp.approved_at = now
    wp.updated_at = now

    latest_version = db.query(WorkpaperVersion).filter(
        WorkpaperVersion.workpaper_id == wp.id,
        WorkpaperVersion.organization_id == ctx.organization_id,
    ).order_by(WorkpaperVersion.version_number.desc()).first()

    if latest_version:
        latest_version.review_status = "approved"
        latest_version.reviewed_by = ctx.user_id
        latest_version.reviewed_at = now
        if req and req.notes:
            latest_version.review_comment = req.notes

    db.commit()

    return {
        "status": "approved",
        "workpaper_id": str(wp.id),
        "workpaper_code": wp.workpaper_code,
        "approved_by": str(ctx.user_id),
        "approved_at": now.isoformat(),
        "notes": req.notes if req else None,
    }
