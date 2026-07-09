"""Target model - represents scan targets."""

from __future__ import annotations

import ipaddress
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class TargetType(str, Enum):
    """Type of target."""

    DOMAIN = "domain"
    IP = "ip"
    CIDR = "cidr"
    URL = "url"


class TargetScope(str, Enum):
    """Scope of the target for engagement."""

    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    UNKNOWN = "unknown"


class Target(BaseModel):
    """
    Represents a target for reconnaissance.

    A target can be a domain, IP address, CIDR range, or URL.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique target identifier")
    value: str = Field(..., description="Target value (domain, IP, CIDR, or URL)")
    type: TargetType = Field(..., description="Type of target")
    scope: TargetScope = Field(default=TargetScope.UNKNOWN, description="Engagement scope")
    description: str | None = Field(None, description="Target description")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp (UTC)")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp (UTC)")

    @model_validator(mode="after")
    def validate_target_value(self) -> Target:
        """Validate target value based on type."""
        if self.type == TargetType.IP:
            try:
                ipaddress.ip_address(self.value)
            except ValueError as e:
                raise ValueError(f"Invalid IP address: {self.value}") from e

        elif self.type == TargetType.CIDR:
            try:
                ipaddress.ip_network(self.value, strict=False)
            except ValueError as e:
                raise ValueError(f"Invalid CIDR notation: {self.value}") from e

        elif self.type == TargetType.URL:
            if not self.value.startswith(("http://", "https://")):
                raise ValueError(f"URL must start with http:// or https://: {self.value}")

        return self

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "value": "example.com",
                "type": "domain",
                "scope": "in_scope",
                "description": "Primary target domain",
                "tags": ["web", "production"],
            }
        }
