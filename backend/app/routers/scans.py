"""Scan job endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project
from app.models.scan_job import ScanJob
from app.schemas.scan import ScanCreate, ScanResponse

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])


@router.post("/", response_model=ScanResponse, status_code=201)
async def create_scan(
    data: ScanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create and start a new scan job for a project."""
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == data.project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create scan job
    scan_job = ScanJob(
        project_id=data.project_id,
        scan_type=data.scan_type,
        status="pending",
    )
    db.add(scan_job)
    await db.flush()
    await db.refresh(scan_job)

    # Dispatch Celery task
    from app.workers.tasks import run_scan_pipeline

    run_scan_pipeline.delay(str(scan_job.id))

    return scan_job


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List scan jobs, optionally filtered by project."""
    query = select(ScanJob).order_by(ScanJob.created_at.desc())
    if project_id:
        query = query.where(ScanJob.project_id == project_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get scan job status and results."""
    result = await db.execute(select(ScanJob).where(ScanJob.id == scan_id))
    scan_job = result.scalar_one_or_none()
    if not scan_job:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan_job
