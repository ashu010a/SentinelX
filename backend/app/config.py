import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelX"
    VERSION: str = "1.0.0-rc1"
    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sentinelx.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "")
    
    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def async_database_url(self) -> str:
        url = self.sync_database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("sqlite://"):
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url

def get_settings():
    return Settings()
