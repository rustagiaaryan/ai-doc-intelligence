# FILE: services/document-service/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    SERVICE_NAME: str = "document-service"
    PORT: int = 8001
    ENV: str = "development"

    # Database
    DATABASE_URL: str

    # S3/MinIO Configuration
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str = "documents"
    S3_REGION: str = "us-east-1"
    USE_SSL: bool = False

    # Auth Service
    AUTH_SERVICE_URL: str

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "doc", "docx", "md"]

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
