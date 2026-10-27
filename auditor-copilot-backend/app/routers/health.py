"""
Health router for service, database, Qdrant vector store, and Gemini provider status checks.
"""

from fastapi import APIRouter
from app.config import settings
from app.db.session import check_db_health
from app.utils.qdrant_store import get_qdrant_vector_store

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

    try:
        qdrant_health = get_qdrant_vector_store().healthcheck()
    except Exception as e:
        qdrant_health = {"status": "error", "error": str(e), "ready": False}

    return {
        "status": "ok",
        "service": "auditor-copilot-backend",
        "database": {
            "provider": "neon_postgresql",
            "backend": "neon_pgvector",
            "status": db_info.get("status", "unknown"),
            "schema": db_info.get("schema", "audit_copilot"),
            "table_count": db_info.get("table_count", 0),
            "neon_configured": bool(getattr(settings, "DATABASE_URL", "")),
        },
        "vector_store": qdrant_health,
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
