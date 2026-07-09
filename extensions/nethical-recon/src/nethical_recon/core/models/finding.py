"""Finding model - represents normalized security findings."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity level of a finding."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(str, Enum):
    """Confidence level in the finding."""

    CONFIRMED = "confirmed"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TENTATIVE = "tentative"


class Finding(BaseModel):
    """
    Represents a normalized security finding.

    Findings are normalized outputs from various security tools,
    providing a consistent format for analysis and reporting.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique finding identifier")
    run_id: UUID = Field(..., description="Tool run that discovered this finding")
    title: str = Field(..., description="Short title of the finding")
    description: str = Field(..., description="Detailed description")
    severity: Severity = Field(..., description="Severity level")
    confidence: Confidence = Field(..., description="Confidence in the finding")
    category: str = Field(..., description="Finding category (e.g., 'open_port', 'vulnerability')")
    affected_asset: str | None = Field(None, description="Affected host, service, or URL")
    port: int | None = Field(None, ge=1, le=65535, description="Port number if applicable")
    protocol: str | None = Field(None, description="Protocol (tcp, udp, http, etc.)")
    service: str | None = Field(None, description="Service name")
    service_version: str | None = Field(None, description="Service version")
    cve_ids: list[str] = Field(default_factory=list, description="CVE identifiers")
    cwe_ids: list[str] = Field(default_factory=list, description="CWE identifiers")
    references: list[str] = Field(default_factory=list, description="External references")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    evidence_ids: list[UUID] = Field(default_factory=list, description="Related evidence IDs")
    raw_data: dict = Field(default_factory=dict, description="Raw tool output data")
    discovered_at: datetime = Field(default_factory=datetime.utcnow, description="Discovery timestamp (UTC)")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Open SSH Port",
                "description": "SSH service is publicly accessible",
                "severity": "medium",
                "confidence": "high",
                "category": "open_port",
                "affected_asset": "example.com",
                "port": 22,
                "protocol": "tcp",
                "service": "ssh",
                "service_version": "OpenSSH 8.2p1",
                "tags": ["network", "ssh"],
            }
        }
