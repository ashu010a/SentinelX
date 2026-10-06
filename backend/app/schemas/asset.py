"""Pydantic schemas for assets."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_id: UUID
    port: int
    protocol: str | None = None
    service: str | None = None
    version: str | None = None
    banner: str | None = None
    created_at: datetime


class EndpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_id: UUID
    url: str
    status_code: int | None = None
    title: str | None = None
    content_type: str | None = None
    content_length: int | None = None
    technologies: dict | None = None
    created_at: datetime


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    hostname: str | None = None
    ip: str | None = None
    type: str
    status: str
    risk_score: float | None = None
    first_seen: datetime
    last_seen: datetime


class AssetWithDetails(AssetResponse):
    services: list[ServiceResponse] = []
    endpoints: list[EndpointResponse] = []
    vulnerabilities: list = []  # Will use VulnerabilityResponse from vulnerability schema
