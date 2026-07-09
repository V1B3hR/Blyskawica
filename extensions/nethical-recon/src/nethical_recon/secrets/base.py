"""Base classes for secrets management."""

from abc import ABC, abstractmethod
from typing import Any


class SecretsBackend(ABC):
    """Abstract base class for secrets backends."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a secret value by key.

        Args:
            key: Secret key to retrieve
            default: Default value if key not found

        Returns:
            Secret value or default
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set a secret value.

        Args:
            key: Secret key to set
            value: Secret value
        """
        pass

    @abstractmethod
    def list_keys(self) -> list[str]:
        """
        List all available secret keys.

        Returns:
            List of secret keys
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a secret key exists.

        Args:
            key: Secret key to check

        Returns:
            True if key exists, False otherwise
        """
        pass
