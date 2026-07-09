"""IOC model - represents indicators of compromise."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class IOCType(str, Enum):
    """Type of indicator of compromise."""

    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    FILE_HASH_MD5 = "file_hash_md5"
    FILE_HASH_SHA1 = "file_hash_sha1"
    FILE_HASH_SHA256 = "file_hash_sha256"
    FILE_PATH = "file_path"
    MUTEX = "mutex"
    REGISTRY_KEY = "registry_key"
    USER_AGENT = "user_agent"


class IOC(BaseModel):
    """
    Represents an Indicator of Compromise (IOC).

    IOCs are artifacts that suggest malicious or suspicious activity.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique IOC identifier")
    finding_id: UUID | None = Field(None, description="Related finding ID")
    type: IOCType = Field(..., description="Type of IOC")
    value: str = Field(..., description="IOC value")
    description: str | None = Field(None, description="IOC description")
    threat_level: str | None = Field(None, description="Threat level (low, medium, high, critical)")
    confidence: str | None = Field(None, description="Confidence in the IOC")
    source: str | None = Field(None, description="Source of the IOC (tool name, feed, etc.)")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    first_seen: datetime = Field(default_factory=datetime.utcnow, description="First seen timestamp (UTC)")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen timestamp (UTC)")
    is_active: bool = Field(default=True, description="Whether the IOC is still active")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "type": "ip",
                "value": "192.0.2.100",
                "description": "Suspicious IP address from malware C2",
                "threat_level": "high",
                "confidence": "high",
                "source": "threat_feed",
                "tags": ["malware", "c2"],
                "is_active": True,
            }
        }
