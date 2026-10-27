"""
Database session and connection management for Neon PostgreSQL.
Configured for the 'audit_copilot' schema with connection pooling.
"""

import logging
from typing import Generator
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import settings

logger = logging.getLogger(__name__)

# Base class for all audit_copilot ORM models
Base = declarative_base()

_engine: sqlalchemy.Engine | None = None
_SessionFactory: sessionmaker | None = None


def get_db_url() -> str:
    raw_url = getattr(settings, "DATABASE_URL", "")
    if not raw_url:
        raise ValueError("DATABASE_URL is not set in environment or configuration.")
    # Convert postgresql:// to postgresql+psycopg:// for psycopg 3
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


def get_engine() -> sqlalchemy.Engine:
    global _engine
    if _engine is not None:
        return _engine

    db_url = get_db_url()
    _engine = sqlalchemy.create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
    )
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionFactory
    if _SessionFactory is not None:
        return _SessionFactory
    engine = get_engine()
    _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions."""
    SessionFactory = get_session_factory()
    db: Session = SessionFactory()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> dict:
    """Safely ping the Neon database and return status without leaking credentials."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1;"))
            # Check schema
            res = conn.execute(sqlalchemy.text(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'audit_copilot';"
            )).scalar()
        return {
            "status": "connected",
            "schema": "audit_copilot",
            "table_count": int(res or 0),
        }
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        return {
            "status": "error",
            "detail": str(e)[:120],
        }
