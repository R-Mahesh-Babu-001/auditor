"""
Evidence files and document intake router for Audit Copilot.
Handles validation, SHA-256 hashing, private file storage, text extraction, and metadata indexing.
"""

import os
import uuid
import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.config import settings
from app.models import EvidenceFile, EvidenceProcessingJob, EvidenceFragment
from app.routers.auth import get_default_context
from app.utils.validators import validate_file
from app.utils.pdf_loader import load_document
from app.utils.vector_store import add_documents_to_store

router = APIRouter(prefix="/evidence", tags=["Evidence & Documents"])


def ensure_upload_dir() -> str:
    path = getattr(settings, "UPLOAD_DIR", "storage/evidence_uploads")
    os.makedirs(path, exist_ok=True)
    return path


@router.get("")
def list_evidence(
    engagement_id: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all uploaded evidence files with hashing and processing statuses."""
    org, _ = get_default_context(db)
    query = db.query(EvidenceFile).filter(EvidenceFile.organization_id == org.id)
    if engagement_id:
        try:
            query = query.filter(EvidenceFile.engagement_id == uuid.UUID(engagement_id))
        except ValueError:
            pass
    if category:
        query = query.filter(EvidenceFile.evidence_category == category)

    files = query.order_by(EvidenceFile.uploaded_at.desc()).all()

    return [
        {
            "id": str(f.id),
            "original_filename": f.original_filename,
            "evidence_category": f.evidence_category,
            "mime_type": f.mime_type,
            "file_size_bytes": f.file_size_bytes,
            "sha256_hex": f.sha256_hex,
            "processing_status": f.processing_status,
            "processing_error": f.processing_error,
            "uploaded_at": f.uploaded_at.isoformat() if f.uploaded_at else None,
        }
        for f in files
    ]


@router.post("/upload")
async def upload_evidence(
    files: List[UploadFile] = File(...),
    engagement_id: Optional[str] = Form(None),
    category: str = Form("policy"),
    db: Session = Depends(get_db),
):
    """Upload, hash, securely store, and extract text/fragments for evidence files."""
    org, user = get_default_context(db)
    upload_dir = ensure_upload_dir()
    results = []

    eng_uuid = None
    if engagement_id:
        try:
            eng_uuid = uuid.UUID(engagement_id)
        except ValueError:
            pass

    for file in files:
        validate_file(file.filename)
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)

        # Check for duplicate
        existing = db.query(EvidenceFile).filter(
            EvidenceFile.organization_id == org.id,
            EvidenceFile.sha256_hex == file_hash,
        ).first()

        if existing:
            results.append({
                "id": str(existing.id),
                "filename": file.filename,
                "status": "duplicate_detected",
                "message": f"Exact duplicate of previously uploaded evidence '{existing.original_filename}'.",
            })
            continue

        # Save private copy
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
        storage_key = f"{org.id}_{uuid.uuid4().hex[:12]}.{ext}"
        storage_path = os.path.join(upload_dir, storage_key)
        with open(storage_path, "wb") as f_out:
            f_out.write(content)

        # Record in Neon DB
        ev_file = EvidenceFile(
            organization_id=org.id,
            engagement_id=eng_uuid,
            uploaded_by=user.id,
            original_filename=file.filename,
            storage_object_key=storage_key,
            mime_type=file.content_type,
            file_extension=ext,
            file_size_bytes=file_size,
            sha256_hex=file_hash,
            evidence_category=category,
            confidentiality="confidential",
            processing_status="processing",
            uploaded_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(ev_file)
        db.flush()

        # Extract text chunks and store fragments + vector memory
        try:
            docs = load_document(content, file.filename)
            for idx, doc in enumerate(docs):
                frag = EvidenceFragment(
                    organization_id=org.id,
                    evidence_file_id=ev_file.id,
                    fragment_type="paragraph",
                    fragment_index=idx,
                    text_content=doc.page_content,
                    page_number=doc.metadata.get("page", 1) if doc.metadata else 1,
                    source_locator={"filename": file.filename, "page": doc.metadata.get("page", 1)},
                    meta=doc.metadata or {},
                )
                db.add(frag)

            # Also index into Neon pgvector for engagement RAG
            coll_name = f"ENGAGEMENT_{eng_uuid}" if eng_uuid else "DOCUMENT_ANALYSIS"
            add_documents_to_store(docs, collection_name=coll_name)

            ev_file.processing_status = "completed"
        except Exception as e:
            ev_file.processing_status = "failed"
            ev_file.processing_error = str(e)[:300]

        db.commit()
        results.append({
            "id": str(ev_file.id),
            "filename": file.filename,
            "status": ev_file.processing_status,
            "sha256": file_hash,
            "size_bytes": file_size,
        })

    return {"uploaded": results}

