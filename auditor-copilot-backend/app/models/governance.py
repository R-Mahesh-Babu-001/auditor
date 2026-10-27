"""
Chat, Agent Runs, SOP Process Maps, and Audit Event Log models.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Numeric, DateTime, ForeignKey, PrimaryKeyConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from app.db.session import Base

SCHEMA = "audit_copilot"


class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=False)
    agent_type = Column(String, nullable=False, default="copilot")
    title = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.chat_conversations.id"), nullable=False)
    sequence_number = Column(BigInteger, nullable=False, default=1)
    role = Column(String, nullable=False)  # user, assistant, system
    content_text = Column(Text, nullable=False)
    meta = Column("metadata", JSONB, nullable=False, default=dict)
    token_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.chat_conversations.id"), nullable=True)
    requested_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    agent_type = Column(String, nullable=False, default="p2p_testing")
    status = Column(String, nullable=False, default="completed")
    model_provider = Column(String, nullable=True, default="gemini")
    model_name = Column(String, nullable=True, default="gemini-3.5-flash")
    prompt_version = Column(String, nullable=True, default="1.0.0")
    input_sha256 = Column(String(64), nullable=True)
    output_sha256 = Column(String(64), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    latency_ms = Column(BigInteger, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    error_code = Column(String, nullable=True)
    error_summary = Column(Text, nullable=True)
    meta = Column("metadata", JSONB, nullable=False, default=dict)


class AgentRunSource(Base):
    __tablename__ = "agent_run_sources"
    __table_args__ = (
        PrimaryKeyConstraint("organization_id", "agent_run_id", "evidence_file_id"),
        {"schema": SCHEMA}
    )

    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.agent_runs.id"), nullable=False)
    evidence_file_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=False)
    fragment_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_fragments.id"), nullable=True)
    source_purpose = Column(String, nullable=False, default="context")
    rank_position = Column(Integer, nullable=True)
    relevance_score = Column(Numeric, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class SOPProcessMap(Base):
    __tablename__ = "sop_process_maps"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=True)
    source_evidence_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.evidence_files.id"), nullable=True)
    title = Column(String, nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    diagram_json = Column(JSONB, nullable=False, default=dict)
    status = Column(String, nullable=False, default="draft")  # draft, reviewed, approved
    created_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AuditEventLog(Base):
    __tablename__ = "audit_event_log"
    __table_args__ = {"schema": SCHEMA}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.organizations.id"), nullable=False)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.audit_engagements.id"), nullable=True)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey(f"{SCHEMA}.app_users.id"), nullable=True)
    event_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    request_id = Column(String, nullable=True)
    source_ip = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    before_state = Column(JSONB, nullable=True)
    after_state = Column(JSONB, nullable=True)
    event_metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
