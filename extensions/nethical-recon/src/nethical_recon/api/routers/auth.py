"""Authentication endpoints."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import (
    User,
    authenticate_user,
    create_access_token,
    fake_api_keys,
    generate_api_key,
    get_current_active_user,
    require_admin,
)
from ..config import APIConfig
from ..models import APIKeyCreate, APIKeyResponse, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login with username and password to get a JWT token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    config = APIConfig.from_env()
    access_token_expires = timedelta(minutes=config.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token)


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: Annotated[User, Depends(require_admin)],
):
    """Create a new API key (admin only)."""
    from datetime import datetime, timezone
    from uuid import uuid4

    # Generate new API key
    api_key = generate_api_key()

    # Store in fake database
    key_id = uuid4()
    fake_api_keys[api_key] = {
        "name": key_data.name,
        "scopes": key_data.scopes,
        "created_at": datetime.now(timezone.utc),
        "expires_at": key_data.expires_at,
        "last_used_at": None,
    }

    return APIKeyResponse(
        id=key_id,
        name=key_data.name,
        key=api_key,
        scopes=key_data.scopes,
        created_at=fake_api_keys[api_key]["created_at"],
        expires_at=key_data.expires_at,
        last_used_at=None,
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get information about the currently authenticated user."""
    return current_user
