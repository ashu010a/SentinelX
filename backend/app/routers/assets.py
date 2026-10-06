"""Asset endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetResponse, AssetWithDetails

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


@router.get("/", response_model=list[AssetResponse])
async def list_assets(
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all assets, optionally filtered by project."""
    query = select(Asset).order_by(Asset.last_seen.desc())
    if project_id:
        query = query.where(Asset.project_id == project_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{asset_id}", response_model=AssetWithDetails)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single asset with its services, endpoints, and vulnerabilities."""
    result = await db.execute(
        select(Asset)
        .where(Asset.id == asset_id)
        .options(
            selectinload(Asset.services),
            selectinload(Asset.endpoints),
            selectinload(Asset.vulnerabilities),
        )
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset
