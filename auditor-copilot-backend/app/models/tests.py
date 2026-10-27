"""
Audit Test Rules, Test Runs, Exceptions, and Exception Links models.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Boolean, DateTime, ForeignKey, PrimaryKeyConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

SCHEMA = "audit_copilot"


class AuditTestRuleTemplate(Base):
    __tablename__ = "audit_test_rule_templates"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # procure_to_pay, itgc, vendor, ai_governance
    implementation_key = Column(String, nullable=False)
    default_parameters = Column(JSONB, nullable=False, default=dict)
    required_dataset_types = Column(JSONB, nullable=False, default=list)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditTestRule(Base):
    __tablename__ = "audit_test_rules"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_test_rule_templates.id"), nullable=True)
    rule_code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    parameters = Column(JSONB, nullable=False, default=dict)
    status = Column(String, nullable=False, default="draft")  # draft, approved, deprecated
    approved_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditTestRun(Base):
    __tablename__ = "audit_test_runs"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_test_rules.id"), nullable=False)
    rule_version = Column(Integer, nullable=False, default=1)
    execution_status = Column(String, nullable=False, default="pending")  # pending, running, completed, failed
    requested_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    population_count = Column(BigInteger, nullable=False, default=0)
    passed_count = Column(BigInteger, nullable=False, default=0)
    exception_count = Column(BigInteger, nullable=False, default=0)
    skipped_count = Column(BigInteger, nullable=False, default=0)
    parameters_snapshot = Column(JSONB, nullable=False, default=dict)
    input_snapshot = Column(JSONB, nullable=False, default=dict)
    result_summary = Column(JSONB, nullable=False, default=dict)
    code_version = Column(String, nullable=True, default="1.0.0")
    error_code = Column(String, nullable=True)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class TestRunDataset(Base):
    __tablename__ = "test_run_datasets"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "engagement_id", "test_run_id", "dataset_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_test_runs.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    dataset_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditException(Base):
    __tablename__ = "audit_exceptions"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_test_runs.id"), nullable=False)
    exception_key = Column(String, nullable=False)
    exception_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False, default="medium")  # low, medium, high, critical
    status = Column(String, nullable=False, default="flagged")  # flagged, needs_evidence, under_review, confirmed_finding, false_positive, accepted_exception, closed
    expected_values = Column(JSONB, nullable=False, default=dict)
    observed_values = Column(JSONB, nullable=False, default=dict)
    rationale = Column(Text, nullable=True)
    resolution_code = Column(String, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class ExceptionRowLink(Base):
    __tablename__ = "exception_row_links"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "engagement_id", "exception_id", "dataset_id", "dataset_row_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    exception_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_exceptions.id"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_datasets.id"), nullable=False)
    dataset_row_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.dataset_rows.id"), nullable=False)
    link_role = Column(String, nullable=False, default="source_row")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class ExceptionEvidenceLink(Base):
    __tablename__ = "exception_evidence_links"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    exception_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_exceptions.id"), nullable=False)
    evidence_file_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=False)
    fragment_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_fragments.id"), nullable=True)
    link_role = Column(String, nullable=False, default="supporting_evidence")
    source_locator = Column(JSONB, nullable=False, default=dict)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

