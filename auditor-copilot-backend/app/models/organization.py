"""
Organization, User, Membership, and Engagement models for audit_copilot.
"""

import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, Date, ForeignKey, Table
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base

SCHEMA = "audit_copilot"


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="active")
    settings = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    password_hash = Column(Text, nullable=True)
    auth_provider = Column(String, nullable=False, default="local")
    external_subject = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=False)
    role = Column(String, nullable=False, default="auditor")  # admin, audit_manager, auditor, reviewer, read_only
    status = Column(String, nullable=False, default="active")
    invited_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditEngagement(Base):
    __tablename__ = "audit_engagements"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    audit_type = Column(String, nullable=False, default="procure_to_pay")
    business_unit = Column(String, nullable=True)
    objective = Column(Text, nullable=False)
    scope_description = Column(Text, nullable=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="planning")  # planning, fieldwork, review, completed, archived
    overall_risk = Column(String, nullable=True, default="medium")
    lead_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class EngagementMembership(Base):
    __tablename__ = "engagement_memberships"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=False)
    engagement_role = Column(String, nullable=False, default="staff_auditor")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

