"""
WebSocket Live Updates for Dashboard
"""

import logging
from typing import Any
from datetime import datetime


class DashboardWebSocketManager:
    """Manages dashboard WebSocket connections"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.dashboard_ws")
        self._initialize_logger()
        self.connections: list[Any] = []
        self.update_count = 0

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [DashboardWS] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def add_connection(self, conn):
        """Add WebSocket connection"""
        self.connections.append(conn)
        self.logger.info(f"Connection added (total: {len(self.connections)})")

    def broadcast_update(self, update_type: str, data: dict[str, Any]):
        """Broadcast update to all connections"""
        message = {"type": update_type, "data": data, "timestamp": datetime.now().isoformat()}
        self.update_count += 1
        self.logger.debug(f"Broadcasting {update_type} to {len(self.connections)} connections")
