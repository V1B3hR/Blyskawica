"""Evidence model - represents artifacts with provenance."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """Type of evidence artifact."""

    RAW_OUTPUT = "raw_output"
    JSON = "json"
    XML = "xml"
    SCREENSHOT = "screenshot"
    LOG = "log"
    REPORT = "report"


class Evidence(BaseModel):
    """
    Represents evidence collected during a tool run.

    Evidence includes the raw output, file paths, checksums for integrity,
    and full provenance information for auditability.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique evidence identifier")
    run_id: UUID = Field(..., description="Tool run that generated this evidence")
    type: EvidenceType = Field(..., description="Type of evidence")
    file_path: str | None = Field(None, description="Path to evidence file")
    content: str | None = Field(None, description="Evidence content (for small artifacts)")
    size_bytes: int | None = Field(None, description="File size in bytes")
    checksum_sha256: str | None = Field(None, description="SHA-256 hash of the content")
    checksum_md5: str | None = Field(None, description="MD5 hash of the content (legacy)")
    mime_type: str | None = Field(None, description="MIME type of the evidence")
    description: str | None = Field(None, description="Human-readable description")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Evidence collection timestamp (UTC)")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "run_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "xml",
                "file_path": "/var/evidence/nmap_scan_20231215_143022.xml",
                "size_bytes": 45678,
                "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "mime_type": "application/xml",
                "description": "Nmap XML output",
            }
        }
