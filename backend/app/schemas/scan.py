"""Pydantic schemas for scan jobs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScanCreate(BaseModel):
    project_id: UUID
    scan_type: str = "full"


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    status: str
    scan_type: str
    current_step: str | None = None
    progress: int
    results: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
