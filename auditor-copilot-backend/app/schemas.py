"""
Pydantic schemas for request/response models used across all Audit Copilot API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import uuid


class ModelConfig(BaseModel):
    """Configuration for LLM provider and model selection. Gemini is the only provider."""
    provider: str = "gemini"
    model_name: Optional[str] = "gemini-3.5-flash"
    temperature: float = 0.2


class EngagementCreate(BaseModel):
    engagement_code: str
    name: str
    audit_type: str = "procure_to_pay"
    business_unit: Optional[str] = None
    objective: str
    scope_description: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    overall_risk: Optional[str] = "medium"


class EngagementResponse(BaseModel):
    id: str
    organization_id: str
    engagement_code: str
    name: str
    audit_type: str
    business_unit: Optional[str] = None
    objective: str
    scope_description: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    status: str
    overall_risk: Optional[str] = None
    created_at: datetime


class DatasetColumnMapping(BaseModel):
    source_column: str
    canonical_field: Optional[str] = None
    is_confirmed: bool = True


class DatasetMappingRequest(BaseModel):
    mappings: List[DatasetColumnMapping]


class TestRunRequest(BaseModel):
    rule_code: Optional[str] = None
    template_code: Optional[str] = None
    engagement_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    selected_dataset_ids: Optional[Dict[str, str]] = None  # maps dataset_type -> dataset_id
    dataset_ids: Optional[List[str]] = None  # optional list of dataset IDs


class TokenRequest(BaseModel):
    email: str
    password: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    role: str
    organization_id: str


class WorkpaperApproveRequest(BaseModel):
    notes: Optional[str] = None


class ExceptionDispositionRequest(BaseModel):
    status: str  # under_review, confirmed_finding, false_positive, accepted_exception, closed
    resolution_code: Optional[str] = None
    resolution_notes: str
    rationale: Optional[str] = None


class FindingCreateRequest(BaseModel):
    title: str
    severity: str = "medium"  # low, medium, high, critical
    condition_text: str
    criteria_text: Optional[str] = None
    cause_text: Optional[str] = None
    consequence_text: Optional[str] = None
    recommendation_text: Optional[str] = None
    management_response: Optional[str] = None
    exception_ids: Optional[List[str]] = None


class WorkpaperGenerateRequest(BaseModel):
    title: str
    workpaper_type: str = "p2p_testing_summary"
    objective: Optional[str] = None
    methodology: Optional[str] = None


class RemediationActionCreate(BaseModel):
    finding_id: str
    action_title: str
    action_description: str
    due_date: Optional[date] = None
    owner_name: Optional[str] = None


class RemediationVerifyRequest(BaseModel):
    status: str  # verified_closed, in_progress, overdue
    verification_notes: str


# Legacy & Copilot endpoint request models
class ChatRequest(BaseModel):
    query: str
    llm_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    user_id: Optional[str] = None
    engagement_id: Optional[str] = None


class AnalysisRequest(BaseModel):
    scenario: str
    llm_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    user_id: Optional[str] = None
    engagement_id: Optional[str] = None


class DocumentQueryRequest(BaseModel):
    question: str
    llm_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    user_id: Optional[str] = None
    engagement_id: Optional[str] = None


class ComplianceRequest(BaseModel):
    query: str
    llm_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    user_id: Optional[str] = None
    engagement_id: Optional[str] = None
    mode: Optional[str] = "IT"


class CorporateRequest(BaseModel):
    query: str
    llm_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    user_id: Optional[str] = None
    engagement_id: Optional[str] = None


class SOPFlowRequest(BaseModel):
    sop_text: str
