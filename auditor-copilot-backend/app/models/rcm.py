"""
Risk and Control Matrix (RCM) models: Criteria, Risks, Controls, and Mappings.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Integer, SmallInteger, Date, DateTime, ForeignKey, PrimaryKeyConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base

SCHEMA = "audit_copilot"


class AuditCriterion(Base):
    __tablename__ = "audit_criteria"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    criterion_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    requirement_type = Column(String, nullable=False)  # law, regulation, policy, contract, standard, guidance
    requirement_text = Column(Text, nullable=False)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    source_locator = Column(JSONB, nullable=False, default=dict)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    version_number = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="draft")  # draft, reviewed, approved
    approved_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditRisk(Base):
    __tablename__ = "audit_risks"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    risk_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    inherent_likelihood = Column(SmallInteger, nullable=True)
    inherent_impact = Column(SmallInteger, nullable=True)
    residual_likelihood = Column(SmallInteger, nullable=True)
    residual_impact = Column(SmallInteger, nullable=True)
    risk_owner_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    status = Column(String, nullable=False, default="draft")
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditControl(Base):
    __tablename__ = "audit_controls"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    control_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    control_type = Column(String, nullable=False, default="preventive")  # preventive, detective, corrective
    execution_type = Column(String, nullable=False, default="automated")  # manual, automated, semi-automated
    frequency = Column(String, nullable=True, default="per_transaction")
    control_owner_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    design_assessment = Column(String, nullable=False, default="unassessed")
    operating_assessment = Column(String, nullable=False, default="unassessed")
    evidence_requirements = Column(JSONB, nullable=False, default=list)
    status = Column(String, nullable=False, default="draft")
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class CriteriaControlMapping(Base):
    __tablename__ = "criteria_control_mappings"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "engagement_id", "criterion_id", "control_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    criterion_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_criteria.id"), nullable=False)
    control_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_controls.id"), nullable=False)
    mapping_status = Column(String, nullable=False, default="draft")  # draft, reviewed, approved
    mapping_rationale = Column(Text, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class RiskControlMapping(Base):
    __tablename__ = "risk_control_mappings"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "engagement_id", "risk_id", "control_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    risk_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_risks.id"), nullable=False)
    control_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_controls.id"), nullable=False)
    mapping_rationale = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

