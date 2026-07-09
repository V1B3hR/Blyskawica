"""Authentication and authorization."""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import APIConfig
from .models import TokenData, User, UserInDB

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# HTTP Bearer scheme for API key authentication
bearer_scheme = HTTPBearer(auto_error=False)

# In-memory user database (in production, use proper database)
# Default admin user:  admin/admin123
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@nethical.local",
        "full_name": "Admin User",
        "hashed_password": "$2b$12$M5oZwts4WYJpL. KIXtYG2udleiwNnDY6GHXwPfr5.tezBKSBZTpRe",  # admin123
        "disabled": False,
        "scopes": ["read", "write", "admin"],
    },
    "operator": {
        "username": "operator",
        "email": "operator@nethical.local",
        "full_name": "Operator User",
        "hashed_password": "$2b$12$M5oZwts4WYJpL.KIXtYG2udleiwNnDY6GHXwPfr5.tezBKSBZTpRe",  # admin123
        "disabled": False,
        "scopes": ["read", "write"],
    },
    "viewer": {
        "username": "viewer",
        "email": "viewer@nethical.local",
        "full_name": "Viewer User",
        "hashed_password": "$2b$12$M5oZwts4WYJpL.KIXtYG2udleiwNnDY6GHXwPfr5.tezBKSBZTpRe",  # admin123
        "disabled": False,
        "scopes": ["read"],
    },
}

# In-memory API keys (in production, use proper database)
# Format: {api_key:  {name, scopes, created_at, expires_at, last_used_at}}
fake_api_keys = {
    "nethical_test_key_12345": {
        "name": "Test API Key",
        "scopes": ["read", "write"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": None,
        "last_used_at": None,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB | None:
    """Get a user from the database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> UserInDB | None:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    config = APIConfig.from_env()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
    return encoded_jwt


def verify_token(token: str) -> TokenData | None:
    """Verify a JWT token."""
    config = APIConfig.from_env()
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            return None
        scopes = payload.get("scopes", [])
        return TokenData(username=username, scopes=scopes)
    except JWTError:
        return None


def verify_api_key(api_key: str) -> dict | None:
    """Verify an API key."""
    if api_key in fake_api_keys:
        key_data = fake_api_keys[api_key]
        # Check if expired
        if key_data["expires_at"] and key_data["expires_at"] < datetime.now(timezone.utc):
            return None
        # Update last used
        key_data["last_used_at"] = datetime.now(timezone.utc)
        return key_data
    return None


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"nethical_{secrets.token_urlsafe(32)}"


async def get_current_user_from_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User | None:
    """Get the current user from a JWT token."""
    if not token:
        return None

    token_data = verify_token(token)
    if not token_data or not token_data.username:
        return None

    user = get_user(token_data.username)
    if user is None:
        return None

    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        scopes=user.scopes,
    )


async def get_current_user_from_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User | None:
    """Get the current user from an API key."""
    if not credentials:
        return None

    api_key = credentials.credentials
    key_data = verify_api_key(api_key)
    if not key_data:
        return None

    # Create a synthetic user for API key authentication
    return User(
        username=key_data["name"],
        email=None,
        full_name=key_data["name"],
        disabled=False,
        scopes=key_data["scopes"],
    )


async def get_current_user(
    token_user: Annotated[User | None, Depends(get_current_user_from_token)],
    api_key_user: Annotated[User | None, Depends(get_current_user_from_api_key)],
) -> User:
    """Get the current user from either token or API key."""
    user = token_user or api_key_user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current active user."""
    return current_user


def require_scope(required_scope: str):
    """Dependency to require a specific scope."""

    async def scope_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if required_scope not in current_user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions.  Required scope: {required_scope}",
            )
        return current_user

    return scope_checker


# Convenience dependencies for common scopes
require_read = require_scope("read")
require_write = require_scope("write")
require_admin = require_scope("admin")
