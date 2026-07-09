"""
Connection Pool Manager
Manages database connection pooling for improved performance
"""

import logging
import threading
import time
from queue import Empty, Queue
from typing import Any

from .base_store import BaseStore
from .store_factory import StoreFactory

logger = logging.getLogger(__name__)


class ConnectionPoolExhausted(Exception):
    """Exception raised when connection pool is exhausted."""

    pass


class ConnectionPool:
    """
    Connection pool manager for database stores

    Manages a pool of database connections to improve performance
    and resource utilization in multi-threaded environments.
    """

    def __init__(self, backend: str, config: dict[str, Any], pool_size: int = 5, max_overflow: int = 10):
        """
        Initialize connection pool

        Args:
            backend: Database backend type
            config: Database configuration
            pool_size: Initial pool size (default: 5)
            max_overflow: Maximum number of connections beyond pool_size (default: 10)
        """
        self.backend = backend
        self.config = config
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.max_connections = pool_size + max_overflow

        self._pool: Queue = Queue(maxsize=self.max_connections)
        self._current_size = 0
        self._lock = threading.Lock()

        # Initialize pool with connections
        for _ in range(pool_size):
            connection = self._create_connection()
            if connection:
                self._pool.put(connection)

    def _create_connection(self) -> BaseStore | None:
        """Create a new database connection"""
        try:
            store = StoreFactory.create_store(self.backend, self.config)
            if store.connect():
                with self._lock:
                    self._current_size += 1
                return store
            return None
        except Exception as e:
            logger.error(f"Error creating connection: {e}")
            return None

    def get_connection(self, timeout: float = 5.0, retries: int = 3, retry_delay: float = 1.0) -> BaseStore:
        """
        Get a connection from the pool with retry logic.

        Args:
            timeout: Maximum time to wait for a connection (seconds)
            retries: Number of retry attempts (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1.0)

        Returns:
            Database store connection

        Raises:
            ConnectionPoolExhausted: If no connection available after retries
        """
        for attempt in range(retries):
            try:
                # Try to get existing connection
                return self._pool.get(timeout=timeout)
            except Empty:
                # Pool is empty, try to create new connection if under max
                with self._lock:
                    if self._current_size < self.max_connections:
                        connection = self._create_connection()
                        if connection:
                            return connection

                # Still no connection available, retry with exponential backoff
                if attempt < retries - 1:
                    wait_time = retry_delay * (2**attempt)
                    logger.warning(
                        f"Pool exhausted, retry {attempt + 1}/{retries} after {wait_time:.1f}s "
                        f"(pool size: {self._current_size}/{self.max_connections})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Pool exhausted after {retries} retries "
                        f"(pool size: {self._current_size}/{self.max_connections})"
                    )
                    raise ConnectionPoolExhausted(
                        f"No connections available after {retries} retries. "
                        f"Pool size: {self._current_size}/{self.max_connections}"
                    )

        # Should not reach here, but just in case
        raise ConnectionPoolExhausted("Failed to acquire connection")

    def return_connection(self, connection: BaseStore):
        """
        Return a connection to the pool

        Args:
            connection: Database store connection to return
        """
        if connection and connection.is_connected():
            try:
                self._pool.put_nowait(connection)
            except Exception:
                # Pool is full, close the connection
                connection.disconnect()
                with self._lock:
                    self._current_size -= 1
        else:
            # Connection is dead, close it and decrement counter
            if connection:
                try:
                    connection.disconnect()
                except Exception:
                    pass
            with self._lock:
                self._current_size -= 1

    def close_all(self):
        """Close all connections in the pool"""
        while not self._pool.empty():
            try:
                connection = self._pool.get_nowait()
                connection.disconnect()
            except Empty:
                break

        with self._lock:
            self._current_size = 0

    def get_stats(self) -> dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "backend": self.backend,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "max_connections": self.max_connections,
            "current_size": self._current_size,
            "available": self._pool.qsize(),
            "in_use": self._current_size - self._pool.qsize(),
        }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()
        return False


class PooledStore:
    """
    Pooled store wrapper that automatically manages connection lifecycle
    """

    def __init__(self, pool: ConnectionPool):
        """
        Initialize pooled store

        Args:
            pool: Connection pool to use
        """
        self.pool = pool
        self._connection: BaseStore | None = None

    def __enter__(self) -> BaseStore:
        """Get connection from pool"""
        self._connection = self.pool.get_connection()
        if not self._connection:
            raise RuntimeError("Failed to acquire connection from pool")
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Return connection to pool"""
        if self._connection:
            self.pool.return_connection(self._connection)
            self._connection = None
        return False
