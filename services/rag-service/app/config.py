# FILE: services/rag-service/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    SERVICE_NAME: str = "rag-service"
    PORT: int = 8004
    ENV: str = "development"

    # Database
    DATABASE_URL: str

    # Redis (for caching)
    REDIS_URL: str

    # LLM Proxy Service
    LLM_PROXY_URL: str

    # Auth Service
    AUTH_SERVICE_URL: str

    # RAG Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_CONTEXT_LENGTH: int = 4000

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
