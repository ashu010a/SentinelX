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
