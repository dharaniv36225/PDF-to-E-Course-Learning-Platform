"""Application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    All values are read from environment variables (or a local ``.env`` file).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- General ---
    PROJECT_NAME: str = "PDF to E-Course Learning Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # --- Security / JWT ---
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30

    # --- Database ---
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ecourse"

    # --- CORS ---
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_STORAGE_BUCKET: str = "pdfs"

    # --- AI providers ---
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-70b-instruct"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 4096

    # --- Embeddings / Vector store ---
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./chroma_store"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    RETRIEVER_TOP_K: int = 5

    # --- Storage ---
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 25
    USE_SUPABASE_STORAGE: bool = False

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = 120

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        """Ensure the SQLAlchemy URL uses the psycopg (v3) driver.

        Managed providers such as Render and Supabase expose connection strings
        using the bare ``postgresql://`` (or legacy ``postgres://``) scheme.
        """
        if isinstance(value, str):
            if value.startswith("postgres://"):
                return "postgresql+psycopg://" + value[len("postgres://") :]
            if value.startswith("postgresql://"):
                return "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


settings = get_settings()
