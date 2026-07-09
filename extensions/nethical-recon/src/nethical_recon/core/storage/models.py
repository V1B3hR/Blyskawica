"""SQLAlchemy ORM models for Nethical Recon."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from ..models import (
    AssetType,
    Confidence,
    EvidenceType,
    IOCType,
    JobStatus,
    Severity,
    TargetScope,
    TargetType,
    ToolStatus,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class TargetModel(Base):
    """SQLAlchemy model for Target."""

    __tablename__ = "targets"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[TargetType] = mapped_column(Enum(TargetType), nullable=False)
    scope: Mapped[TargetScope] = mapped_column(Enum(TargetScope), default=TargetScope.UNKNOWN)
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    jobs: Mapped[list["ScanJobModel"]] = relationship("ScanJobModel", back_populates="target")


class ScanJobModel(Base):
    """SQLAlchemy model for ScanJob."""

    __tablename__ = "scan_jobs"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    target_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("targets.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    tools: Mapped[list] = mapped_column(JSON, default=list)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(100), default="system")

    # Relationships
    target: Mapped["TargetModel"] = relationship("TargetModel", back_populates="jobs")
    tool_runs: Mapped[list["ToolRunModel"]] = relationship("ToolRunModel", back_populates="job")
    assets: Mapped[list["AssetModel"]] = relationship("AssetModel", back_populates="job")


class ToolRunModel(Base):
    """SQLAlchemy model for ToolRun."""

    __tablename__ = "tool_runs"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    job_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("scan_jobs.id"), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_version: Mapped[str] = mapped_column(String(50), nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ToolStatus] = mapped_column(Enum(ToolStatus), default=ToolStatus.PENDING)
    exit_code: Mapped[int | None] = mapped_column(Integer)
    stdout: Mapped[str | None] = mapped_column(Text)
    stderr: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    job: Mapped["ScanJobModel"] = relationship("ScanJobModel", back_populates="tool_runs")
    evidence: Mapped[list["EvidenceModel"]] = relationship("EvidenceModel", back_populates="tool_run")
    findings: Mapped[list["FindingModel"]] = relationship("FindingModel", back_populates="tool_run")


class EvidenceModel(Base):
    """SQLAlchemy model for Evidence."""

    __tablename__ = "evidence"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    run_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("tool_runs.id"), nullable=False)
    type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(1000))
    content: Mapped[str | None] = mapped_column(Text)
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    checksum_md5: Mapped[str | None] = mapped_column(String(32))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    tool_run: Mapped["ToolRunModel"] = relationship("ToolRunModel", back_populates="evidence")


class FindingModel(Base):
    """SQLAlchemy model for Finding."""

    __tablename__ = "findings"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    run_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("tool_runs.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    confidence: Mapped[Confidence] = mapped_column(Enum(Confidence), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    affected_asset: Mapped[str | None] = mapped_column(String(500))
    port: Mapped[int | None] = mapped_column(Integer)
    protocol: Mapped[str | None] = mapped_column(String(50))
    service: Mapped[str | None] = mapped_column(String(100))
    service_version: Mapped[str | None] = mapped_column(String(100))
    cve_ids: Mapped[list] = mapped_column(JSON, default=list)
    cwe_ids: Mapped[list] = mapped_column(JSON, default=list)
    references: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    evidence_ids: Mapped[list] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    tool_run: Mapped["ToolRunModel"] = relationship("ToolRunModel", back_populates="findings")


class AssetModel(Base):
    """SQLAlchemy model for Asset."""

    __tablename__ = "assets"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    job_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("scan_jobs.id"), nullable=False)
    type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Asset-specific fields
    ip_address: Mapped[str | None] = mapped_column(String(45))
    hostname: Mapped[str | None] = mapped_column(String(255))
    port: Mapped[int | None] = mapped_column(Integer)
    protocol: Mapped[str | None] = mapped_column(String(50))
    service_name: Mapped[str | None] = mapped_column(String(100))
    service_version: Mapped[str | None] = mapped_column(String(100))
    os_name: Mapped[str | None] = mapped_column(String(100))
    os_version: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    job: Mapped["ScanJobModel"] = relationship("ScanJobModel", back_populates="assets")


class IOCModel(Base):
    """SQLAlchemy model for IOC."""

    __tablename__ = "iocs"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    finding_id: Mapped[Uuid | None] = mapped_column(Uuid, ForeignKey("findings.id"))
    type: Mapped[IOCType] = mapped_column(Enum(IOCType), nullable=False)
    value: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    threat_level: Mapped[str | None] = mapped_column(String(50))
    confidence: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(200))
    tags: Mapped[list] = mapped_column(JSON, default=list)
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserModel(Base):
    """SQLAlchemy model for User authentication."""

    __tablename__ = "users"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    mfa_secret: Mapped[str | None] = mapped_column(String(255))
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)


class APIKeyModel(Base):
    """SQLAlchemy model for API Keys."""

    __tablename__ = "api_keys"

    id: Mapped[Uuid] = mapped_column(Uuid, primary_key=True, default=uuid4)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Uuid] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
