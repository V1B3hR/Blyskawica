"""
Asset Widgets

Widgets for displaying asset data including maps and lists.
"""

from typing import Any

from .base import BaseWidget


class AssetMapWidget(BaseWidget):
    """
    Asset map widget.

    Displays assets on a network topology or geographic map.
    """

    async def get_data(self) -> dict[str, Any]:
        """Fetch asset map data."""
        # In real implementation, fetch from database
        return {
            "map_type": self.config.get("map_type", "network"),
            "assets": [
                {
                    "id": "asset-1",
                    "name": "web-server-01",
                    "type": "server",
                    "status": "online",
                    "risk_score": 75,
                    "position": {"x": 100, "y": 100},
                },
                {
                    "id": "asset-2",
                    "name": "database-01",
                    "type": "database",
                    "status": "online",
                    "risk_score": 45,
                    "position": {"x": 200, "y": 150},
                },
            ],
            "connections": [
                {"source": "asset-1", "target": "asset-2", "type": "network"},
            ],
        }

    def get_schema(self) -> dict[str, Any]:
        """Get widget schema."""
        return {
            "type": "object",
            "properties": {
                "map_type": {
                    "type": "string",
                    "enum": ["network", "geographic", "logical"],
                    "default": "network",
                },
                "show_connections": {"type": "boolean", "default": True},
                "filter_by_risk": {"type": "string", "enum": ["all", "high", "critical"]},
            },
        }


class AssetListWidget(BaseWidget):
    """
    Asset list widget.

    Displays assets in a filterable list format.
    """

    async def get_data(self) -> dict[str, Any]:
        """Fetch asset list data."""
        return {
            "assets": [
                {
                    "id": "asset-1",
                    "name": "web-server-01",
                    "type": "server",
                    "ip": "192.168.1.10",
                    "risk_score": 75,
                    "vulnerabilities": 5,
                },
                {
                    "id": "asset-2",
                    "name": "database-01",
                    "type": "database",
                    "ip": "192.168.1.20",
                    "risk_score": 45,
                    "vulnerabilities": 2,
                },
            ],
            "total_count": 25,
            "page": self.config.get("page", 1),
        }

    def get_schema(self) -> dict[str, Any]:
        """Get widget schema."""
        return {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "minimum": 1, "default": 1},
                "per_page": {"type": "integer", "minimum": 5, "maximum": 100, "default": 20},
                "filter_type": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["name", "risk_score", "vulnerabilities"],
                    "default": "risk_score",
                },
            },
        }
