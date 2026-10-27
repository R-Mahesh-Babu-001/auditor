"""
Factory module for LLM creation.
Enforces Google Gemini as the single, exclusive LLM provider.
"""

from app.llm.gemini import get_gemini_llm, get_fixed_llm


def get_llm(llm_config=None, streaming: bool = False):
    """Return the configured Gemini LLM instance.

    Google Gemini is the only LLM provider. Any legacy provider name is safely mapped to Gemini.
    """
    return get_gemini_llm(model_config=llm_config, streaming=streaming)


__all__ = ["get_llm", "get_fixed_llm"]
