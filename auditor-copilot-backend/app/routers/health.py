"""
Health router for service, database, and Gemini provider status checks.
"""

from fastapi import APIRouter
from app.config import settings
from app.db.session import check_db_health

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers and system monitoring."""
    db_info = check_db_health()
    gemini_configured = bool(
        getattr(settings, "GEMINI_API_KEY", "")
        or getattr(settings, "GOOGLE_API_KEY", "")
        or getattr(settings, "GOOGLE_CLOUD_PROJECT", "")
    )

    return {
        "status": "ok",
        "service": "auditor-copilot-backend",
        "database": {
            "backend": getattr(settings, "VECTOR_STORE_BACKEND", "neon_pgvector"),
            "status": db_info.get("status", "unknown"),
            "schema": db_info.get("schema", "audit_copilot"),
            "table_count": db_info.get("table_count", 0),
            "neon_configured": bool(getattr(settings, "DATABASE_URL", "")),
        },
        "llm": {
            "provider": "gemini",
            "model": getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash"),
            "configured": gemini_configured,
        },
    }


@router.get("/ready")
async def readiness_check():
    """Readiness endpoint verifying database connection without exposing secrets."""
    db_info = check_db_health()
    ready = db_info.get("status") == "connected"
    return {
        "ready": ready,
        "database_status": db_info.get("status"),
        "schema": db_info.get("schema"),
    }
