"""API request and response models."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from nethical_recon.core.models import (
    Severity,
    JobStatus,
    TargetScope,
    TargetType,
    ToolStatus,
)


# Base response models
class BaseResponse(BaseModel):
    """Base response model."""

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Target models
class TargetCreate(BaseModel):
    """Request model for creating a target."""

    value: str = Field(..., description="Target value (domain, IP, or CIDR)")
    type: TargetType = Field(..., description="Target type")
    scope: TargetScope = Field(default=TargetScope.IN_SCOPE, description="Target scope")
    description: str | None = Field(None, description="Optional description")
    tags: list[str] = Field(default_factory=list, description="Optional tags")


class TargetResponse(BaseResponse):
    """Response model for a target."""

    id: UUID
    value: str
    type: TargetType
    scope: TargetScope
    description: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class TargetUpdate(BaseModel):
    """Request model for updating a target."""

    scope: TargetScope | None = None
    description: str | None = None
    tags: list[str] | None = None


# Job models
class JobCreate(BaseModel):
    """Request model for creating a scan job."""

    target_id: UUID = Field(..., description="Target ID to scan")
    name: str = Field(..., description="Job name", min_length=1, max_length=255)
    description: str | None = Field(None, description="Optional job description")
    tools: list[str] = Field(..., description="List of tools to run", min_length=1)
    config: dict[str, Any] = Field(default_factory=dict, description="Optional configuration")


class JobResponse(BaseResponse):
    """Response model for a scan job."""

    id: UUID
    target_id: UUID
    name: str
    description: str | None
    tools: list[str]
    status: JobStatus
    config: dict[str, Any]
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


class JobStatusResponse(BaseResponse):
    """Extended job status with statistics."""

    id: UUID
    target_id: UUID
    name: str
    status: JobStatus
    tools: list[str]
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    tool_runs_count: int
    findings_count: int
    findings_by_severity: dict[str, int]


# Tool run models
class ToolRunResponse(BaseResponse):
    """Response model for a tool run."""

    id: UUID
    job_id: UUID
    tool_name: str
    tool_version: str | None
    command: str
    status: ToolStatus
    exit_code: int | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None
    stdout: str | None
    stderr: str | None


# Finding models
class FindingResponse(BaseResponse):
    """Response model for a finding."""

    id: UUID
    run_id: UUID
    title: str
    description: str
    severity: Severity
    confidence: str  # Actually Confidence enum
    category: str
    affected_asset: str | None = None
    port: int | None = None
    protocol: str | None = None
    service: str | None = None
    service_version: str | None = None
    cve_ids: list[str]
    cwe_ids: list[str]
    references: list[str]
    tags: list[str]
    discovered_at: datetime


# Report models
class ReportCreate(BaseModel):
    """Request model for generating a report."""

    job_id: UUID = Field(..., description="Job ID to generate report for")
    format: str = Field(default="json", description="Report format (json, markdown, html, pdf)")


class ReportResponse(BaseResponse):
    """Response model for a report."""

    job_id: UUID
    job_name: str
    target: str
    generated_at: datetime
    tools: list[str]
    findings_count: int
    findings_by_severity: dict[str, int]
    findings: list[FindingResponse]
    tool_runs: list[ToolRunResponse]


# Auth models
class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    username: str | None = None
    scopes: list[str] = []


class User(BaseModel):
    """User model."""

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = False
    scopes: list[str] = []


class UserInDB(User):
    """User model with hashed password."""

    hashed_password: str


class APIKeyCreate(BaseModel):
    """Request model for creating an API key."""

    name: str = Field(..., description="API key name", min_length=1, max_length=255)
    scopes: list[str] = Field(default=["read"], description="API key scopes")
    expires_at: datetime | None = Field(None, description="Optional expiration date")


class APIKeyResponse(BaseModel):
    """Response model for an API key."""

    id: UUID
    name: str
    key: str  # Only returned on creation
    scopes: list[str]
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None


# Health check
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    database: str
    worker: str
