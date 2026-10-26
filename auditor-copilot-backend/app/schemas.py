
"""
Pydantic schemas for request/response models used in API endpoints.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any

class ModelConfig(BaseModel):
    """
    Configuration for LLM provider and model selection.
    """
    provider: str  # e.g., 'azure_openai', 'aws_bedrock'
    model_name: str
    temperature: float = 0.2

class ChatRequest(BaseModel):
    """
    Request body for chat endpoint.
    """
    query: str
    llm_config: ModelConfig
    user_id: Optional[str] = None

class AnalysisRequest(BaseModel):
    """
    Request body for analysis endpoint.
    """
    scenario: str
    llm_config: ModelConfig
    user_id: Optional[str] = None

class DocumentQueryRequest(BaseModel):
    """
    Request body for document query endpoint.
    """
    question: str
    llm_config: ModelConfig
    user_id: Optional[str] = None

class ComplianceRequest(BaseModel):
    """Request for compliance agent endpoints."""
    query: str
    llm_config: ModelConfig
    user_id: Optional[str] = None
    mode: Optional[str] = "IT"

class CorporateRequest(BaseModel):
    """Request for corporate agent endpoints."""
    query: str
    llm_config: ModelConfig
    user_id: Optional[str] = None

class SOPFlowRequest(BaseModel):
    """
    Request body for SOP flowchart generation endpoint.
    """
    sop_text: str
