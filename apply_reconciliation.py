import os
import shutil
import re

def write_file(path, content):
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print("Starting backend reconciliation...")

# 1. Config Handling (Sync + Async DB URLs)
write_file("backend/app/config.py", """
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
""")

# 2. Database Handling
write_file("backend/app/database.py", """
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import get_settings

settings = get_settings()

# Async Engine (For modern API routes)
async_engine = create_async_engine(settings.async_database_url, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync Engine (For Legacy Engines & Celery)
sync_engine = create_engine(settings.sync_database_url, echo=settings.DEBUG)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_sync_db():
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
""")

# 3. Consolidate Models
legacy_models = open("backend/models.py", "r").read()
# Replace `from database import Base` with `from app.database import Base`
legacy_models = legacy_models.replace("from database import Base", "from app.database import Base")
write_file("backend/app/models/schema.py", legacy_models)
write_file("backend/app/models/__init__.py", "from app.models.schema import *")

# 4. Migrate Logic to canonical Router
legacy_main = open("backend/main.py", "r").read()
# Strip the app init from legacy
legacy_endpoints = legacy_main.split('app = FastAPI(title="SentinelX MVP API")')[1]
legacy_endpoints = legacy_endpoints.replace('@app.', '@router.')
legacy_endpoints = legacy_endpoints.replace('from database import Base, engine, get_db', 'from app.database import get_sync_db as get_db')
legacy_endpoints = legacy_endpoints.replace('from database import SessionLocal', 'from app.database import SyncSessionLocal as SessionLocal')
legacy_endpoints = legacy_endpoints.replace('import models', 'from app.models import schema as models')
# Map routes to /api/v1/ and remove duplicates
legacy_endpoints = legacy_endpoints.replace('"/api/', '"/api/v1/')
# Specifically remove `create_project` to avoid collision with modern router
legacy_endpoints = re.sub(r'@router\.post\("/api/v1/projects"\).*?return p', '', legacy_endpoints, flags=re.DOTALL)
legacy_endpoints = re.sub(r'@router\.get\("/api/v1/health"\).*?return {"status": "ok"}', '', legacy_endpoints, flags=re.DOTALL)

write_file("backend/app/routers/legacy.py", f"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_sync_db as get_db
from app.database import SyncSessionLocal as SessionLocal
from app.models import schema as models
import os
import shutil

router = APIRouter(tags=["advanced"])
{legacy_endpoints}
""")

# 5. Build Canonical Main
write_file("backend/app/main.py", """
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import async_engine, Base
from app.routers import legacy

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(legacy.router)

@app.get("/health")
def health(): return {"status": "alive"}

@app.get("/ready")
def ready(): return {"status": "ready"}
""")

# 6. Celery Worker Canonicalization
write_file("backend/app/workers/celery_app.py", """
from celery import Celery
from app.config import get_settings

settings = get_settings()
celery_app = Celery("sentinelx", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
""")

legacy_worker = open("backend/worker.py", "r").read()
legacy_worker = legacy_worker.replace("from database import SessionLocal", "from app.database import SyncSessionLocal as SessionLocal")
legacy_worker = legacy_worker.replace("import models", "from app.models import schema as models")
write_file("backend/app/workers/tasks.py", f"""
from app.workers.celery_app import celery_app
{legacy_worker}

@celery_app.task(name="execute_scan")
def execute_scan(scan_job_id: str):
    execute_scan_sync(scan_job_id)
""")

# 7. Remove Legacy Files
os.remove("backend/main.py")
os.remove("backend/models.py")
os.remove("backend/database.py")
os.remove("backend/worker.py")

# 8. Fix Frontend API
write_file("frontend/lib/api.ts", """
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`API Error ${res.status}: ${err}`);
    }
    return res.json();
}
""")

# 9. Dockerfiles Update
with open("backend/Dockerfile.prod", "r") as f: df = f.read()
df = df.replace('CMD ["uvicorn", "main:app"', 'CMD ["uvicorn", "app.main:app"')
with open("backend/Dockerfile.prod", "w") as f: f.write(df)

with open("backend/Dockerfile.worker", "r") as f: dfw = f.read()
dfw = dfw.replace('CMD ["celery", "-A", "app.workers.celery_app"', 'CMD ["celery", "-A", "app.workers.tasks"')
with open("backend/Dockerfile.worker", "w") as f: f.write(dfw)

print("Reconciliation complete.")
