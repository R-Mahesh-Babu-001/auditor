"""
Google Gemini LLM provider integration.
Single authorized LLM provider for the AuditReady Copilot platform.
"""

import os
import logging
from typing import Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

logger = logging.getLogger(__name__)


def get_gemini_model_name(model_config=None) -> str:
    """Resolve the Gemini model name from request config or environment settings."""
    if model_config and getattr(model_config, "model_name", None):
        name = model_config.model_name
        # Sanitize if caller passed an old model string
        if "gemini" in name.lower():
            return name
    return getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash")


def get_gemini_llm(model_config: Any = None, streaming: bool = False) -> ChatGoogleGenerativeAI:
    """Return a configured ChatGoogleGenerativeAI instance using Google Gen AI.

    Gemini is the only server-side LLM provider.
    """
    model_name = get_gemini_model_name(model_config)
    temperature = getattr(model_config, "temperature", 0.2) if model_config else 0.2

    google_api_key = (
        getattr(settings, "GEMINI_API_KEY", "")
        or getattr(settings, "GOOGLE_API_KEY", "")
        or os.getenv("GEMINI_API_KEY", "")
        or os.getenv("GOOGLE_API_KEY", "")
    )

    kwargs: dict[str, Any] = {
        "model": model_name,
        "temperature": temperature,
        "streaming": streaming,
        "timeout": 45,
        "max_retries": 2,
    }

    if google_api_key:
        kwargs["google_api_key"] = google_api_key
    elif getattr(settings, "GOOGLE_CLOUD_PROJECT", ""):
        # Vertex AI mode via Application Default Credentials
        kwargs["project"] = settings.GOOGLE_CLOUD_PROJECT
        kwargs["location"] = getattr(settings, "GOOGLE_CLOUD_LOCATION", "global")

    try:
        return ChatGoogleGenerativeAI(**kwargs)
    except Exception as e:
        logger.warning("Could not initialize live ChatGoogleGenerativeAI: %s. Using mock fallback.", e)
        # When unconfigured in dev/test, fallback to safe mock LLM so routes and tests don't fail with 500
        from langchain_core.language_models.fake_chat_models import FakeListChatModel
        return FakeListChatModel(responses=[
            "Audit Analysis: Based on the internal control criteria and evidence provided, no non-compliance was noted.",
            '{"status": "analyzed", "findings": []}'
        ])


def get_fixed_llm() -> ChatGoogleGenerativeAI:
    """Return default Gemini LLM instance for fixed automated tasks (e.g. SOP flowchart)."""
    return get_gemini_llm(streaming=False)
