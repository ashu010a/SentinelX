"""Vulnerability endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.schemas.vulnerability import VulnerabilityResponse, VulnStatsSummary

router = APIRouter(prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])


@router.get("/stats/summary", response_model=VulnStatsSummary)
async def vulnerability_stats(
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get vulnerability count breakdown by severity."""
    query = select(
        func.count(case((Vulnerability.severity == "critical", 1))).label("critical"),
        func.count(case((Vulnerability.severity == "high", 1))).label("high"),
        func.count(case((Vulnerability.severity == "medium", 1))).label("medium"),
        func.count(case((Vulnerability.severity == "low", 1))).label("low"),
        func.count(case((Vulnerability.severity == "info", 1))).label("info"),
        func.count(Vulnerability.id).label("total"),
    )

    if project_id:
        query = query.join(Asset, Vulnerability.asset_id == Asset.id).where(
            Asset.project_id == project_id
        )

    result = await db.execute(query)
    row = result.one()

    return VulnStatsSummary(
        critical=row.critical,
        high=row.high,
        medium=row.medium,
        low=row.low,
        info=row.info,
        total=row.total,
    )


@router.get("/", response_model=list[VulnerabilityResponse])
async def list_vulnerabilities(
    project_id: UUID | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List vulnerabilities with optional project and severity filters."""
    query = select(Vulnerability).order_by(Vulnerability.first_seen.desc())

    if project_id:
        query = query.join(Asset, Vulnerability.asset_id == Asset.id).where(
            Asset.project_id == project_id
        )

    if severity:
        query = query.where(Vulnerability.severity == severity.lower())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vuln_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single vulnerability by ID."""
    result = await db.execute(
        select(Vulnerability).where(Vulnerability.id == vuln_id)
    )
    vuln = result.scalar_one_or_none()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln
