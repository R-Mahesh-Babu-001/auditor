"""
Main entry point for the FastAPI backend service.
Initializes the FastAPI app, configures CORS, and includes all API routers.
Enterprise-grade AuditReady Copilot powered by Google Gemini and Neon PostgreSQL.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Existing legacy routers (kept compatible)
from app.routers import chat, analysis, documents, sop_flow, health
from app.routers import compliance, corporate, memory

# Enterprise Audit Copilot routers
from app.routers import auth
from app.routers import engagements
from app.routers import evidence
from app.routers import datasets
from app.routers import rcm
from app.routers import tests
from app.routers import exceptions
from app.routers import findings
from app.routers import workpapers
from app.routers import remediation
from app.routers import dashboard
from app.routers import continuous
from app.routers import governance

from app.config import settings

# Create FastAPI app instance
app = FastAPI(
    title="AuditReady Copilot Backend",
    description="Evidence-first AI Audit Platform powered by Google Gemini and Neon PostgreSQL",
    version="2.0.0",
)

# -----------------------------
# CORS Middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",")
    if hasattr(settings, "CORS_ORIGINS") else [
        "http://localhost:3000",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# System & Diagnostic Routers
# -----------------------------
app.include_router(health.router)

# -----------------------------
# Core Audit Copilot API Routers
# -----------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(engagements.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
app.include_router(rcm.router, prefix="/api")
app.include_router(tests.router, prefix="/api")
app.include_router(exceptions.router, prefix="/api")
app.include_router(findings.router, prefix="/api")
app.include_router(workpapers.router, prefix="/api")
app.include_router(remediation.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(continuous.router, prefix="/api")
app.include_router(governance.router, prefix="/api")

# -----------------------------
# Conversational & Legacy Endpoints
# -----------------------------
app.include_router(chat.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(sop_flow.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(corporate.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
