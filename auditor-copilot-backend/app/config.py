"""Application settings for Gemini, Neon PostgreSQL, and Qdrant."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    TESTING: bool = False

    # Neon PostgreSQL Database & pgvector
    DATABASE_URL: str = ""
    VECTOR_STORE_BACKEND: str = "neon_pgvector"
    VECTOR_STORE_PROVIDER: str = "qdrant"
    NEON_DB_COLLECTION: str = "audit_docs"

    # Qdrant Cloud Free Vector Database
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "audit_evidence"

    # Google Cloud Vertex AI / Gemini (The only authorized LLM provider)
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "global"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_PROVIDER: str = "gemini"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_EMBEDDING_DIMENSIONS: int = 768

    # Authentication & Security
    JWT_SECRET_KEY: str = "auditready_copilot_jwt_secret_signing_key_32bytes_min"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Frontend CORS configuration
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )

    # File uploads & Evidence Storage
    UPLOAD_DIR: str = "storage/evidence_uploads"
    MAX_FILE_SIZE_MB: int = 50

    model_config = SettingsConfigDict(
        env_file=(".env", "auditor-copilot-backend/.env"),
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()