# FILE: services/llm-proxy/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    SERVICE_NAME: str = "llm-proxy"
    PORT: int = 8002
    ENV: str = "development"

    # LLM Provider API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Default LLM Configuration
    DEFAULT_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-4-turbo-preview"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    DEFAULT_MAX_TOKENS: int = 4096
    DEFAULT_TEMPERATURE: float = 0.7

    # Redis (for caching)
    REDIS_URL: str
    CACHE_TTL_SECONDS: int = 3600

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
