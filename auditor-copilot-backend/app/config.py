"""Application settings for Gemini and Neon PostgreSQL."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Neon PostgreSQL Database & pgvector
    DATABASE_URL: str = ""
    VECTOR_STORE_BACKEND: str = "neon_pgvector"
    NEON_DB_COLLECTION: str = "audit_docs"

    # Google Cloud Vertex AI / Gemini (The only authorized LLM provider)
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "global"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_EMBEDDING_DIMENSIONS: int = 768

    # Frontend CORS configuration
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )

    # File uploads
    UPLOAD_DIR: str = "storage/evidence_uploads"
    MAX_FILE_SIZE_MB: int = 50

    model_config = SettingsConfigDict(
        env_file=(".env", "auditor-copilot-backend/.env"),
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()