
"""
Main entry point for the FastAPI backend service.
Initializes the FastAPI app, configures CORS, and includes all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers for different API endpoints
from app.routers import chat, analysis, documents, sop_flow, health
from app.routers import compliance
from app.routers import corporate
from app.routers import memory
from app.config import settings

# Create FastAPI app instance
app = FastAPI(
    title="Auditor Copilot Backend",
    version="0.1.0"
)

# -----------------------------
# CORS Middleware
# -----------------------------
# Allow cross-origin requests from frontend origins
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
# Routers
# -----------------------------
# Register API routers for different functionalities
app.include_router(health.router)
app.include_router(chat.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(sop_flow.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(corporate.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
