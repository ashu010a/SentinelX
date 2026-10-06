"""Asset model — discovered hosts, subdomains, IPs."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    type: Mapped[str] = mapped_column(
        String(50), default="subdomain"
    )  # subdomain, ip, url
    status: Mapped[str] = mapped_column(String(50), default="active")
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    project = relationship("Project", back_populates="assets")
    services = relationship(
        "Service", back_populates="asset", cascade="all, delete-orphan"
    )
    endpoints = relationship(
        "Endpoint", back_populates="asset", cascade="all, delete-orphan"
    )
    vulnerabilities = relationship(
        "Vulnerability", back_populates="asset", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Asset {self.hostname or self.ip}>"
