"""Centralized secrets manager for Nethical Recon."""

import os
from typing import Any

from .backends import DotEnvBackend, EnvBackend
from .base import SecretsBackend


class SecretsManager:
    """
    Centralized secrets manager with support for multiple backends.

    Supports:
    - Environment variables (default)
    - .env files
    - HashiCorp Vault (future)
    - Kubernetes Secrets (future)
    """

    def __init__(self, backend: SecretsBackend | None = None):
        """
        Initialize secrets manager.

        Args:
            backend: Secrets backend to use. If None, uses environment variables.
        """
        if backend is None:
            # Try to use .env file if it exists, otherwise fall back to env vars
            env_file = os.getenv("SECRETS_ENV_FILE", ".env")
            if os.path.exists(env_file):
                backend = DotEnvBackend(env_file)
            else:
                backend = EnvBackend()

        self._backend = backend

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a secret value.

        Args:
            key: Secret key to retrieve
            default: Default value if key not found

        Returns:
            Secret value or default
        """
        return self._backend.get(key, default)

    def get_required(self, key: str) -> Any:
        """
        Get a required secret value.

        Args:
            key: Secret key to retrieve

        Returns:
            Secret value

        Raises:
            ValueError: If secret key is not found
        """
        value = self._backend.get(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found")
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a secret value.

        Args:
            key: Secret key to set
            value: Secret value
        """
        self._backend.set(key, value)

    def list_keys(self) -> list[str]:
        """
        List all available secret keys.

        Returns:
            List of secret keys
        """
        return self._backend.list_keys()

    def exists(self, key: str) -> bool:
        """
        Check if a secret key exists.

        Args:
            key: Secret key to check

        Returns:
            True if key exists, False otherwise
        """
        return self._backend.exists(key)

    def get_api_config(self) -> dict[str, Any]:
        """
        Get API-related secrets.

        Returns:
            Dict with API secrets
        """
        return {
            "secret_key": self.get("API_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION"),
            "database_url": self.get("DATABASE_URL", "sqlite:///./nethical_recon.db"),
            "broker_url": self.get("BROKER_URL", "redis://localhost:6379/0"),
            "result_backend": self.get("RESULT_BACKEND", "redis://localhost:6379/1"),
        }

    def get_external_api_keys(self) -> dict[str, str | None]:
        """
        Get external API keys (Shodan, Censys, etc.).

        Returns:
            Dict with external API keys
        """
        return {
            "shodan_api_key": self.get("SHODAN_API_KEY"),
            "censys_api_id": self.get("CENSYS_API_ID"),
            "censys_api_secret": self.get("CENSYS_API_SECRET"),
            "openai_api_key": self.get("OPENAI_API_KEY"),
        }

    def get_database_config(self) -> dict[str, Any]:
        """
        Get database-related secrets.

        Returns:
            Dict with database secrets
        """
        return {
            "database_url": self.get("DATABASE_URL", "sqlite:///./nethical_recon.db"),
            "db_user": self.get("DB_USER"),
            "db_password": self.get("DB_PASSWORD"),
            "db_host": self.get("DB_HOST", "localhost"),
            "db_port": self.get("DB_PORT", "5432"),
            "db_name": self.get("DB_NAME", "nethical_recon"),
        }


# Global secrets manager instance
_secrets_manager: SecretsManager | None = None


def get_secrets_manager() -> SecretsManager:
    """
    Get the global secrets manager instance.

    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def init_secrets_manager(backend: SecretsBackend | None = None) -> SecretsManager:
    """
    Initialize the global secrets manager with a custom backend.

    Args:
        backend: Secrets backend to use

    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    _secrets_manager = SecretsManager(backend)
    return _secrets_manager
