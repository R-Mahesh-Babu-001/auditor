"""
Audit Findings, Workpapers, Versions, and Remediation models.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Integer, Date, DateTime, ForeignKey, PrimaryKeyConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

SCHEMA = "audit_copilot"


class AuditFinding(Base):
    __tablename__ = "audit_findings"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    finding_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    finding_type = Column(String, nullable=True, default="control_deficiency")
    severity = Column(String, nullable=False, default="medium")  # low, medium, high, critical
    status = Column(String, nullable=False, default="draft")  # draft, under_review, confirmed, remediated, closed
    criterion_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_criteria.id"), nullable=True)
    risk_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_risks.id"), nullable=True)
    control_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_controls.id"), nullable=True)
    condition_text = Column(Text, nullable=False)
    criteria_text = Column(Text, nullable=True)
    cause_text = Column(Text, nullable=True)
    consequence_text = Column(Text, nullable=True)
    recommendation_text = Column(Text, nullable=True)
    management_response = Column(Text, nullable=True)
    finding_owner_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    validated_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FindingException(Base):
    __tablename__ = "finding_exceptions"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "engagement_id", "finding_id", "exception_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    finding_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_findings.id"), nullable=False)
    exception_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_exceptions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Workpaper(Base):
    __tablename__ = "workpapers"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    workpaper_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    workpaper_type = Column(String, nullable=False, default="testing_summary")
    objective = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    population_description = Column(Text, nullable=True)
    sampling_method = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")  # draft, in_review, approved, rejected
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkpaperVersion(Base):
    __tablename__ = "workpaper_versions"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    workpaper_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.workpapers.id"), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    content_markdown = Column(Text, nullable=False)
    structured_content = Column(JSONB, nullable=False, default=dict)
    conclusion_status = Column(String, nullable=False, default="satisfactory_with_exceptions")
    generation_method = Column(String, nullable=False, default="automated_gemini")
    model_provider = Column(String, nullable=True, default="gemini")
    model_name = Column(String, nullable=True, default="gemini-3.5-flash")
    prompt_version = Column(String, nullable=True, default="1.0.0")
    input_snapshot_hash = Column(String(64), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    review_status = Column(String, nullable=False, default="pending_review")
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_comment = Column(Text, nullable=True)


class WorkpaperExceptionLink(Base):
    __tablename__ = "workpaper_exception_links"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "engagement_id", "workpaper_version_id", "exception_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    workpaper_version_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.workpaper_versions.id"), nullable=False)
    exception_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_exceptions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkpaperEvidenceLink(Base):
    __tablename__ = "workpaper_evidence_links"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    workpaper_version_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.workpaper_versions.id"), nullable=False)
    evidence_file_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=False)
    fragment_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_fragments.id"), nullable=True)
    claim_or_section = Column(Text, nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RemediationAction(Base):
    __tablename__ = "remediation_actions"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    finding_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_findings.id"), nullable=False)
    action_title = Column(String, nullable=False)
    action_description = Column(Text, nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="open")  # open, in_progress, under_review, verified_closed, overdue
    management_comment = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RemediationEvidenceLink(Base):
    __tablename__ = "remediation_evidence_links"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    remediation_action_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.remediation_actions.id"), nullable=False)
    evidence_file_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=False)
    evidence_note = Column(Text, nullable=True)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

