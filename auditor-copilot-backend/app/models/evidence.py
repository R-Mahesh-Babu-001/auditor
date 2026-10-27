"""
Evidence and Dataset models for audit_copilot.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Numeric, DateTime, Date, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

SCHEMA = "audit_copilot"


class EvidenceFile(Base):
    __tablename__ = "evidence_files"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    original_filename = Column(Text, nullable=False)
    storage_object_key = Column(Text, nullable=False)
    mime_type = Column(String, nullable=True)
    file_extension = Column(String, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    sha256_hex = Column(String(64), nullable=True)
    evidence_category = Column(String, nullable=False, default="policy")  # policy, dataset, soc_report, questionnaire, log, general
    source_system = Column(String, nullable=True)
    source_period_start = Column(Date, nullable=True)
    source_period_end = Column(Date, nullable=True)
    confidentiality = Column(String, nullable=False, default="confidential")
    processing_status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    retention_until = Column(Date, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class EvidenceProcessingJob(Base):
    __tablename__ = "evidence_processing_jobs"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    evidence_file_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=False)
    job_type = Column(String, nullable=False, default="extract_text")
    status = Column(String, nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(String, nullable=True)
    error_summary = Column(Text, nullable=True)
    metrics = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class EvidenceFragment(Base):
    __tablename__ = "evidence_fragments"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    evidence_file_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=False)
    fragment_type = Column(String, nullable=False, default="paragraph")
    fragment_index = Column(Integer, nullable=False, default=0)
    text_content = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)
    section_heading = Column(Text, nullable=True)
    sheet_name = Column(Text, nullable=True)
    row_start = Column(BigInteger, nullable=True)
    row_end = Column(BigInteger, nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    content_sha256 = Column(String(64), nullable=True)
    vector_store = Column(String, nullable=True, default="neon_pgvector")
    vector_ref = Column(Text, nullable=True)
    meta = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditDataset(Base):
    __tablename__ = "audit_datasets"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    dataset_code = Column(String, nullable=False)
    dataset_name = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False, default="p2p_transactions")
    version_number = Column(Integer, nullable=False, default=1)
    schema_definition = Column(JSONB, nullable=False, default=dict)
    row_count = Column(BigInteger, nullable=False, default=0)
    valid_row_count = Column(BigInteger, nullable=False, default=0)
    invalid_row_count = Column(BigInteger, nullable=False, default=0)
    status = Column(String, nullable=False, default="draft")  # draft, profiled, mapped, validated, approved
    approved_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    source_column_name = Column(Text, nullable=False)
    canonical_field = Column(String, nullable=True)
    source_data_type = Column(String, nullable=True)
    target_data_type = Column(String, nullable=True)
    mapping_status = Column(String, nullable=False, default="proposed")  # proposed, confirmed, ignored
    mapping_confidence = Column(Numeric, nullable=True, default=0.0)
    transformation = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class DatasetRow(Base):
    __tablename__ = "dataset_rows"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    row_number = Column(BigInteger, nullable=False)
    raw_data = Column(JSONB, nullable=False, default=dict)
    normalized_data = Column(JSONB, nullable=False, default=dict)
    row_sha256 = Column(String(64), nullable=True)
    validation_status = Column(String, nullable=False, default="valid")  # valid, invalid, warning
    validation_errors = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
