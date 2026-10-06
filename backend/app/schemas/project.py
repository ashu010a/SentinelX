"""Pydantic schemas for projects."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    target: str
    description: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    target: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectWithStats(ProjectResponse):
    asset_count: int = 0
    vulnerability_count: int = 0
