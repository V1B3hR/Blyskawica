"""API configuration."""

import logging
import secrets as python_secrets
from dataclasses import dataclass

from nethical_recon.secrets import get_secrets_manager

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuration for the REST API."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 4

    # Security
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"  # Used for JWT signing
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API
    api_prefix: str = "/api/v1"
    title: str = "Nethical Recon API"
    description: str = "Professional-grade REST API for cybersecurity reconnaissance and threat hunting"
    version: str = "1.0.0"

    # CORS
    cors_origins: list[str] | None = None
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] | None = None
    cors_allow_headers: list[str] | None = None

    # Pagination
    default_page_size: int = 50
    max_page_size: int = 1000

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load configuration from environment variables using secrets manager."""
        secrets_mgr = get_secrets_manager()

        # Auto-generate API secret if not set or using default
        api_secret = secrets_mgr.get("API_SECRET_KEY")

        if not api_secret or api_secret == "CHANGE_THIS_IN_PRODUCTION":
            # Generate a strong 256-bit secret key
            api_secret = python_secrets.token_urlsafe(32)
            secrets_mgr.set("API_SECRET_KEY", api_secret)
            logger.warning(
                f"Generated new API secret key: {api_secret[:10]}... "
                "(Store this securely - it will be used for JWT signing)"
            )

        return cls(
            host=secrets_mgr.get("API_HOST", "0.0.0.0"),
            port=int(secrets_mgr.get("API_PORT", "8000")),
            reload=secrets_mgr.get("API_RELOAD", "false").lower() == "true",
            workers=int(secrets_mgr.get("API_WORKERS", "4")),
            secret_key=api_secret,
            algorithm=secrets_mgr.get("API_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(secrets_mgr.get("API_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            api_prefix=secrets_mgr.get("API_PREFIX", "/api/v1"),
            title=secrets_mgr.get("API_TITLE", "Nethical Recon API"),
            version=secrets_mgr.get("API_VERSION", "1.0.0"),
            cors_origins=(
                secrets_mgr.get("API_CORS_ORIGINS", "").split(",") if secrets_mgr.get("API_CORS_ORIGINS") else None
            ),
            default_page_size=int(secrets_mgr.get("API_DEFAULT_PAGE_SIZE", "50")),
            max_page_size=int(secrets_mgr.get("API_MAX_PAGE_SIZE", "1000")),
        )
