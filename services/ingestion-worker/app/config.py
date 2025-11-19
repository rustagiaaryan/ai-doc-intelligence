# FILE: services/ingestion-worker/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    SERVICE_NAME: str = "ingestion-worker"
    PORT: int = 8003
    ENV: str = "development"

    # Database
    DATABASE_URL: str

    # Redis (for task queue)
    REDIS_URL: str

    # S3/MinIO Configuration
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str = "documents"
    S3_REGION: str = "us-east-1"
    USE_SSL: bool = False

    # LLM Proxy Service
    LLM_PROXY_URL: str

    # Text Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CHUNKS_PER_DOCUMENT: int = 500

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
