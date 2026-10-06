"""Project endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.asset import Asset
from app.models.project import Project
from app.models.vulnerability import Vulnerability
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectWithStats

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project with a target domain."""
    project = Project(
        name=data.name,
        target=data.target,
        description=data.description,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


@router.get("/", response_model=list[ProjectWithStats])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects with asset and vulnerability counts."""
    # Subquery for asset counts
    asset_count_sq = (
        select(
            Asset.project_id,
            func.count(Asset.id).label("asset_count"),
        )
        .group_by(Asset.project_id)
        .subquery()
    )

    # Subquery for vulnerability counts (via assets)
    vuln_count_sq = (
        select(
            Asset.project_id,
            func.count(Vulnerability.id).label("vulnerability_count"),
        )
        .join(Vulnerability, Vulnerability.asset_id == Asset.id)
        .group_by(Asset.project_id)
        .subquery()
    )

    query = (
        select(
            Project,
            func.coalesce(asset_count_sq.c.asset_count, 0).label("asset_count"),
            func.coalesce(vuln_count_sq.c.vulnerability_count, 0).label(
                "vulnerability_count"
            ),
        )
        .outerjoin(asset_count_sq, Project.id == asset_count_sq.c.project_id)
        .outerjoin(vuln_count_sq, Project.id == vuln_count_sq.c.project_id)
        .order_by(Project.created_at.desc())
    )

    result = await db.execute(query)
    rows = result.all()

    projects = []
    for row in rows:
        project = row[0]
        project_data = ProjectWithStats.model_validate(project)
        project_data.asset_count = row[1]
        project_data.vulnerability_count = row[2]
        projects.append(project_data)

    return projects


@router.get("/{project_id}", response_model=ProjectWithStats)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single project by ID with stats."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Count assets
    asset_result = await db.execute(
        select(func.count(Asset.id)).where(Asset.project_id == project_id)
    )
    asset_count = asset_result.scalar() or 0

    # Count vulnerabilities
    vuln_result = await db.execute(
        select(func.count(Vulnerability.id))
        .join(Asset, Vulnerability.asset_id == Asset.id)
        .where(Asset.project_id == project_id)
    )
    vuln_count = vuln_result.scalar() or 0

    project_data = ProjectWithStats.model_validate(project)
    project_data.asset_count = asset_count
    project_data.vulnerability_count = vuln_count
    return project_data


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a project and all associated data."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
