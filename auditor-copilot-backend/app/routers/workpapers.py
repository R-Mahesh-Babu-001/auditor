"""
Workpapers router for drafting, versioning, evidence verification, and review sign-offs.
"""

import uuid
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
from app.schemas import WorkpaperGenerateRequest
from app.routers.auth import get_default_context
from app.audit.workpapers import generate_structured_workpaper

router = APIRouter(prefix="/workpapers", tags=["Workpapers"])


@router.get("")
def list_workpapers(
    engagement_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all audit workpapers for the engagement."""
    org, _ = get_default_context(db)
    query = db.query(Workpaper).filter(Workpaper.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(Workpaper.engagement_id == uuid.UUID(engagement_id))
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
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in wps
    ]


@router.post("/generate")
def generate_workpaper(
    engagement_id: str,
    req: WorkpaperGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate structured audit workpaper with factual evidence verification."""
    org, user = get_default_context(db)
    try:
        eng_uuid = uuid.UUID(engagement_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid engagement UUID.")

    return generate_structured_workpaper(
        db=db,
        organization_id=org.id,
        engagement_id=eng_uuid,
        title=req.title,
        workpaper_type=req.workpaper_type,
        objective_override=req.objective,
        user_id=user.id,
    )


@router.get("/{workpaper_id}/versions")
def get_workpaper_versions(
    workpaper_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve full version history and markdown content for a workpaper."""
    org, _ = get_default_context(db)
    try:
        wp_uuid = uuid.UUID(workpaper_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workpaper UUID.")

    versions = db.query(WorkpaperVersion).filter(
        WorkpaperVersion.workpaper_id == wp_uuid,
        WorkpaperVersion.organization_id == org.id,
    ).order_by(WorkpaperVersion.version_number.desc()).all()

    return [
        {
            "id": str(v.id),
            "version_number": v.version_number,
            "content_markdown": v.content_markdown,
            "structured_content": v.structured_content,
            "conclusion_status": v.conclusion_status,
            "review_status": v.review_status,
            "review_comment": v.review_comment,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]

