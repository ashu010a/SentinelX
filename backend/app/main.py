"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import assets, projects, scans, vulnerabilities

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown logic."""
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Attack Surface Management & Vulnerability Intelligence Platform",
    lifespan=lifespan,
)

# CORS — allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(scans.router)
app.include_router(assets.router)
app.include_router(vulnerabilities.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
