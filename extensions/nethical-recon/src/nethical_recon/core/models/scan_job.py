"""ScanJob model - represents a scan orchestration job."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status of a scan job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanJob(BaseModel):
    """
    Represents a scan job that orchestrates multiple tool runs.

    A scan job can run multiple tools against a target and aggregate results.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique job identifier")
    target_id: UUID = Field(..., description="Target being scanned")
    name: str = Field(..., description="Job name")
    description: str | None = Field(None, description="Job description")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current job status")
    tools: list[str] = Field(default_factory=list, description="Tools to run in this job")
    config: dict = Field(default_factory=dict, description="Job configuration")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp (UTC)")
    started_at: datetime | None = Field(None, description="Job start timestamp (UTC)")
    completed_at: datetime | None = Field(None, description="Job completion timestamp (UTC)")
    error_message: str | None = Field(None, description="Error message if job failed")
    created_by: str = Field(default="system", description="User who created the job")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "target_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Full recon scan",
                "description": "Complete reconnaissance of target",
                "tools": ["nmap", "nikto", "dirb"],
                "created_by": "admin",
            }
        }
