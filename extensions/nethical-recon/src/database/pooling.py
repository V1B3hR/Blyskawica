"""
Connection Pooling Optimization for Database
"""

import logging
from typing import Any
from collections import deque


class ConnectionPool:
    """Optimized connection pool"""

    def __init__(self, min_size: int = 5, max_size: int = 20):
        self.logger = logging.getLogger("nethical.connection_pool")
        self._initialize_logger()
        self.min_size = min_size
        self.max_size = max_size
        self.pool: deque = deque()
        self.active_connections = 0

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [ConnectionPool] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_connection(self):
        """Get connection from pool"""
        if self.pool:
            conn = self.pool.popleft()
            self.active_connections += 1
            return conn
        elif self.active_connections < self.max_size:
            self.active_connections += 1
            self.logger.info("Creating new connection")
            return object()  # Mock connection
        return None

    def release_connection(self, conn):
        """Return connection to pool"""
        if len(self.pool) < self.max_size:
            self.pool.append(conn)
        self.active_connections -= 1

    def get_statistics(self) -> dict[str, Any]:
        """Get pool statistics"""
        return {
            "pool_size": len(self.pool),
            "active_connections": self.active_connections,
            "min_size": self.min_size,
            "max_size": self.max_size,
        }
