"""
Base Store Interface for Stain Database
Abstract base class defining the interface for all database backends
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class StoreBackend(Enum):
    """Supported database backends"""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MSSQL = "mssql"
    ORACLE = "oracle"
    DB2 = "db2"
    SNOWFLAKE = "snowflake"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"


class BaseStore(ABC):
    """
    Abstract base class for all database store implementations

    This class defines the interface that all database backends must implement
    to provide consistent storage and retrieval of stain data.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the store with configuration

        Args:
            config: Dictionary containing database configuration
                   (host, port, database, user, password, etc.)
        """
        self.config = config
        self.backend_type: StoreBackend | None = None
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the database

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Close connection to the database

        Returns:
            True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    def initialize_schema(self) -> bool:
        """
        Initialize database schema (tables, indexes, etc.)

        Returns:
            True if schema initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def save_stain(self, stain: dict[str, Any]) -> bool:
        """
        Save a stain to the database

        Args:
            stain: Dictionary containing stain data

        Returns:
            True if save successful, False otherwise
        """
        pass

    @abstractmethod
    def get_stain(self, tag_id: str) -> dict[str, Any] | None:
        """
        Retrieve a stain by tag ID

        Args:
            tag_id: Unique tag identifier

        Returns:
            Stain dictionary if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_stains(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        """
        Retrieve all stains with optional pagination

        Args:
            limit: Maximum number of stains to return (None = all)
            offset: Number of stains to skip

        Returns:
            List of stain dictionaries
        """
        pass

    @abstractmethod
    def get_stains_by_type(self, marker_type: str, limit: int | None = None) -> list[dict[str, Any]]:
        """
        Retrieve stains filtered by marker type

        Args:
            marker_type: Type of marker (MALWARE, EVIL_AI, etc.)
            limit: Maximum number of stains to return

        Returns:
            List of stain dictionaries
        """
        pass

    @abstractmethod
    def get_stains_by_color(self, color: str, limit: int | None = None) -> list[dict[str, Any]]:
        """
        Retrieve stains filtered by color

        Args:
            color: Color of tracer (RED, PURPLE, etc.)
            limit: Maximum number of stains to return

        Returns:
            List of stain dictionaries
        """
        pass

    @abstractmethod
    def get_stains_by_ip(self, ip: str) -> list[dict[str, Any]]:
        """
        Retrieve stains associated with an IP address

        Args:
            ip: IP address to search for

        Returns:
            List of stain dictionaries
        """
        pass

    @abstractmethod
    def get_stains_by_threat_score(self, min_score: float, max_score: float = 10.0) -> list[dict[str, Any]]:
        """
        Retrieve stains within a threat score range

        Args:
            min_score: Minimum threat score
            max_score: Maximum threat score

        Returns:
            List of stain dictionaries
        """
        pass

    @abstractmethod
    def update_stain(self, tag_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing stain

        Args:
            tag_id: Unique tag identifier
            updates: Dictionary of fields to update

        Returns:
            True if update successful, False otherwise
        """
        pass

    @abstractmethod
    def delete_stain(self, tag_id: str) -> bool:
        """
        Delete a stain from the database

        Args:
            tag_id: Unique tag identifier

        Returns:
            True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    def search_stains(self, query: str, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Search for stains matching a query

        Args:
            query: Search query string
            fields: List of fields to search in (None = all fields)

        Returns:
            List of matching stain dictionaries
        """
        pass

    @abstractmethod
    def count_stains(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count stains with optional filters

        Args:
            filters: Dictionary of filter conditions

        Returns:
            Number of stains matching filters
        """
        pass

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary containing statistics (total stains, by type, etc.)
        """
        pass

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected

    def get_backend_type(self) -> StoreBackend | None:
        """Get the backend type"""
        return self.backend_type

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
