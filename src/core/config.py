from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "savdhaan-ai"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-to-a-random-64-char-string"  # noqa: S105

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://savdhaan:savdhaan@localhost:5432/savdhaan"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AI — Anthropic Claude
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL_FAST: str = "claude-sonnet-4-6"
    CLAUDE_MODEL_COMPLEX: str = "claude-opus-4-6"

    # OCR
    GOOGLE_VISION_API_KEY: str = ""
    OCR_PROVIDER: str = "tesseract"

    # Threat Intelligence
    GOOGLE_SAFE_BROWSING_KEY: str = ""
    PHISHTANK_API_KEY: str = ""
    SPAMHAUS_DQS_KEY: str = ""
    URLHAUS_ENABLED: bool = True

    # Rate Limiting
    RATE_LIMIT_FREE: int = 10
    RATE_LIMIT_PREMIUM: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 3600

    # Content Retention
    RAW_CONTENT_RETENTION_HOURS: int = 1

    # S3 / MinIO
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"  # noqa: S105
    S3_BUCKET_NAME: str = "savdhaan-cards"
    S3_REGION: str = "us-east-1"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


settings = Settings()
