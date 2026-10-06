"""SentinelX configuration module."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://sentinelx:sentinelx@db:5432/sentinelx"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://sentinelx:sentinelx@db:5432/sentinelx"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # API
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    PROJECT_NAME: str = "SentinelX"
    VERSION: str = "0.1.0"

    # Scanner timeouts (seconds)
    SCANNER_TIMEOUT: int = 600

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
