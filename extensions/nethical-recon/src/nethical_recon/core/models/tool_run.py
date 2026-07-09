"""ToolRun model - represents execution of a specific tool."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ToolStatus(str, Enum):
    """Status of a tool run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ToolRun(BaseModel):
    """
    Represents a single tool execution within a scan job.

    Tracks the execution details, timing, and results of a security tool.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique run identifier")
    job_id: UUID = Field(..., description="Parent job identifier")
    tool_name: str = Field(..., description="Name of the tool (e.g., 'nmap', 'nikto')")
    tool_version: str = Field(..., description="Version of the tool")
    command: str = Field(..., description="Full command line executed")
    status: ToolStatus = Field(default=ToolStatus.PENDING, description="Current run status")
    exit_code: int | None = Field(None, description="Exit code of the tool")
    stdout: str | None = Field(None, description="Standard output")
    stderr: str | None = Field(None, description="Standard error output")
    started_at: datetime | None = Field(None, description="Run start timestamp (UTC)")
    completed_at: datetime | None = Field(None, description="Run completion timestamp (UTC)")
    duration_seconds: float | None = Field(None, description="Execution duration in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp (UTC)")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "tool_name": "nmap",
                "tool_version": "7.94",
                "command": "nmap -sV -p- example.com",
                "status": "completed",
                "exit_code": 0,
            }
        }
