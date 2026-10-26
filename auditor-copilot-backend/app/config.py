
"""
Configuration module for environment variables and settings.
Uses Pydantic BaseSettings for type-safe config management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    # Azure OpenAI API configuration
    AZURE_OPENAI_4o_MINI_API_KEY: str
    AZURE_OPENAI_4o_MINI_ENDPOINT: str
    AZURE_OPENAI_4o_MINI_DEPLOYMENT: str
    AZURE_OPENAI_4o_MINI_API_VERSION: str

    AZURE_OPENAI_EMBEDDING_ENDPOINT: str
    AZURE_OPENAI_EMBEDDING_API_KEY: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str
    AZURE_OPENAI_EMBEDDING_API_VERSION: str

    # AWS Bedrock configuration
    AWS_REGION: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # ChromaDB vector store configuration
    CHROMA_DB_COLLECTION: str = "audit_docs"
    CHROMA_DB_DIR: str = "chroma_db"
    # Toggle usage of Chroma backend. Set to True only if chromadb native bindings are
    # correctly installed and compatible with the host environment. Default: False (use FAISS/Dummy fallback).
    CHROMA_ENABLED: bool = False

    # Pydantic settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# Singleton settings instance
settings = Settings()
