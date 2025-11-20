# FILE: services/api-gateway/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    SERVICE_NAME: str = "api-gateway"
    PORT: int = 8080
    ENV: str = "development"

    # Backend Services
    AUTH_SERVICE_URL: str
    DOCUMENT_SERVICE_URL: str
    LLM_PROXY_URL: str
    INGESTION_WORKER_URL: str
    RAG_SERVICE_URL: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:30000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
