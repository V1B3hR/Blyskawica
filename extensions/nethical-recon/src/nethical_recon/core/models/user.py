"""User domain model for authentication and authorization."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User domain model."""

    id: UUID
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    hashed_password: str
    full_name: str | None = None
    disabled: bool = False
    scopes: list[str] = Field(default_factory=list)
    mfa_secret: str | None = None
    mfa_enabled: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class APIKey(BaseModel):
    """API Key domain model."""

    id: UUID
    key_hash: str
    name: str = Field(..., min_length=1, max_length=255)
    user_id: UUID
    scopes: list[str] = Field(default_factory=list)
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    is_active: bool = True

    class Config:
        """Pydantic config."""

        from_attributes = True
