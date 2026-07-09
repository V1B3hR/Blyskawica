"""
Store Factory
Factory pattern for unified database access across all backends
"""

from typing import Any

from .base_store import BaseStore, StoreBackend
from .db2_store import Db2Store
from .elasticsearch_store import ElasticsearchStore
from .mongodb_store import MongoDBStore
from .mssql_store import MSSQLStore
from .mysql_store import MySQLStore
from .oracle_store import OracleStore
from .postgres_store import PostgreSQLStore
from .redis_cache import RedisCache
from .snowflake_store import SnowflakeStore
from .sqlite_store import SQLiteStore


class StoreFactory:
    """
    Factory class for creating database store instances

    Provides unified interface for creating and managing database connections
    across all supported backends.
    """

    # Registry of available store implementations
    _STORE_REGISTRY = {
        StoreBackend.SQLITE: SQLiteStore,
        StoreBackend.POSTGRESQL: PostgreSQLStore,
        StoreBackend.MYSQL: MySQLStore,
        StoreBackend.MSSQL: MSSQLStore,
        StoreBackend.ORACLE: OracleStore,
        StoreBackend.DB2: Db2Store,
        StoreBackend.SNOWFLAKE: SnowflakeStore,
        StoreBackend.MONGODB: MongoDBStore,
        StoreBackend.REDIS: RedisCache,
        StoreBackend.ELASTICSEARCH: ElasticsearchStore,
    }

    @classmethod
    def create_store(cls, backend: str, config: dict[str, Any]) -> BaseStore:
        """
        Create a database store instance

        Args:
            backend: Backend type (sqlite, postgresql, mysql, etc.)
            config: Configuration dictionary for the backend

        Returns:
            Store instance implementing BaseStore interface

        Raises:
            ValueError: If backend is not supported
            NotImplementedError: If backend requires additional packages

        Example:
            >>> store = StoreFactory.create_store('sqlite', {'database': 'stains.db'})
            >>> store.connect()
            >>> store.initialize_schema()
        """
        try:
            backend_enum = StoreBackend(backend.lower())
        except ValueError:
            raise ValueError(
                f"Unsupported backend: {backend}. " f"Supported backends: {', '.join([b.value for b in StoreBackend])}"
            )

        store_class = cls._STORE_REGISTRY.get(backend_enum)
        if not store_class:
            raise ValueError(f"No implementation found for backend: {backend}")

        return store_class(config)

    @classmethod
    def create_default_store(cls) -> BaseStore:
        """
        Create default SQLite store for quick start

        Returns:
            SQLite store with default configuration
        """
        return cls.create_store("sqlite", {"database": "stains.db"})

    @classmethod
    def list_available_backends(cls) -> list:
        """
        List all available backend types

        Returns:
            List of backend type strings
        """
        return [backend.value for backend in StoreBackend]

    @classmethod
    def get_backend_info(cls, backend: str) -> dict[str, str]:
        """
        Get information about a specific backend

        Args:
            backend: Backend type string

        Returns:
            Dictionary with backend information
        """
        backend_info = {
            "sqlite": {
                "name": "SQLite",
                "description": "Local file-based database for single-user development and testing",
                "use_case": "Local dev/testing, small deployments",
                "requires": "Built-in (no extra packages)",
                "connection_example": "{'database': 'stains.db'}",
            },
            "postgresql": {
                "name": "PostgreSQL",
                "description": "Advanced open-source relational database with JSONB support",
                "use_case": "Team deployments, advanced SQL features",
                "requires": "pip install psycopg2-binary",
                "connection_example": "{'host': 'localhost', 'port': 5432, 'database': 'stains', 'user': 'user', 'password': 'pass'}",
            },
            "mysql": {
                "name": "MySQL",
                "description": "Widely-adopted relational database for web-scale applications",
                "use_case": "Web-scale applications, wide hosting support",
                "requires": "pip install mysql-connector-python",
                "connection_example": "{'host': 'localhost', 'port': 3306, 'database': 'stains', 'user': 'user', 'password': 'pass'}",
            },
            "mssql": {
                "name": "Microsoft SQL Server",
                "description": "Enterprise database for Windows/.NET environments",
                "use_case": "Windows enterprise, .NET integration",
                "requires": "pip install pyodbc",
                "connection_example": "{'connection_string': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;...'}",
            },
            "oracle": {
                "name": "Oracle Database",
                "description": "Enterprise-grade database for mission-critical systems",
                "use_case": "Large enterprise, financial systems",
                "requires": "pip install cx_Oracle",
                "connection_example": "{'user': 'user', 'password': 'pass', 'dsn': 'host:port/service'}",
            },
            "db2": {
                "name": "IBM Db2",
                "description": "Mainframe integration and legacy enterprise systems",
                "use_case": "Mainframe integration, IBM ecosystem",
                "requires": "pip install ibm_db",
                "connection_example": "{'database': 'db', 'hostname': 'host', 'port': 50000, 'protocol': 'TCPIP', 'uid': 'user', 'pwd': 'pass'}",
            },
            "snowflake": {
                "name": "Snowflake",
                "description": "Cloud data warehouse for large-scale analytics",
                "use_case": "Big data analytics, reporting",
                "requires": "pip install snowflake-connector-python",
                "connection_example": "{'user': 'user', 'password': 'pass', 'account': 'account', 'warehouse': 'wh', 'database': 'db'}",
            },
            "mongodb": {
                "name": "MongoDB",
                "description": "Flexible document storage for unstructured data",
                "use_case": "Schema-less storage, rapid iteration",
                "requires": "pip install pymongo",
                "connection_example": "{'host': 'localhost', 'port': 27017, 'database': 'stains'}",
            },
            "redis": {
                "name": "Redis",
                "description": "High-speed caching layer for frequently accessed data",
                "use_case": "Caching, session management",
                "requires": "pip install redis",
                "connection_example": "{'host': 'localhost', 'port': 6379, 'db': 0}",
            },
            "elasticsearch": {
                "name": "Elasticsearch",
                "description": "Fast full-text search and log aggregation",
                "use_case": "Full-text search, threat hunting",
                "requires": "pip install elasticsearch",
                "connection_example": "{'hosts': ['http://localhost:9200'], 'index': 'stains'}",
            },
        }

        return backend_info.get(
            backend.lower(),
            {
                "name": "Unknown",
                "description": "Backend information not available",
                "use_case": "N/A",
                "requires": "N/A",
                "connection_example": "N/A",
            },
        )


# Convenience function for quick store creation
def create_store(backend: str = "sqlite", config: dict[str, Any] | None = None) -> BaseStore:
    """
    Convenience function to create a database store

    Args:
        backend: Backend type (default: 'sqlite')
        config: Configuration dictionary (default: None, uses defaults)

    Returns:
        Store instance

    Example:
        >>> store = create_store()  # Creates SQLite store with defaults
        >>> store = create_store('postgresql', {'host': 'localhost', ...})
    """
    if config is None:
        if backend == "sqlite":
            config = {"database": "stains.db"}
        else:
            raise ValueError(f"Configuration required for backend: {backend}")

    return StoreFactory.create_store(backend, config)
