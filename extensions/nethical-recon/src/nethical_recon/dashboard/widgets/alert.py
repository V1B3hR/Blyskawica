"""
Alert and Risk Widgets

Widgets for displaying alerts and risk metrics.
"""

from typing import Any

from .base import BaseWidget


class AlertFeedWidget(BaseWidget):
    """
    Alert feed widget.

    Displays recent security alerts and notifications.
    """

    async def get_data(self) -> dict[str, Any]:
        """Fetch alert feed data."""
        return {
            "alerts": [
                {
                    "id": "alert-1",
                    "title": "CISA KEV Detected: CVE-2021-44228",
                    "severity": "critical",
                    "timestamp": "2025-01-14T21:45:00Z",
                    "type": "kev",
                    "status": "new",
                },
                {
                    "id": "alert-2",
                    "title": "High-risk port exposed: 3389",
                    "severity": "high",
                    "timestamp": "2025-01-14T21:30:00Z",
                    "type": "exposure",
                    "status": "acknowledged",
                },
                {
                    "id": "alert-3",
                    "title": "New vulnerable asset discovered",
                    "severity": "medium",
                    "timestamp": "2025-01-14T21:15:00Z",
                    "type": "vulnerability",
                    "status": "new",
                },
            ],
            "total_count": 25,
            "unread_count": 5,
        }

    def get_schema(self) -> dict[str, Any]:
        """Get widget schema."""
        return {
            "type": "object",
            "properties": {
                "max_items": {"type": "integer", "minimum": 5, "maximum": 50, "default": 10},
                "filter_severity": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
                },
                "filter_type": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["kev", "vulnerability", "exposure", "threat_intel"]},
                },
                "show_unread_only": {"type": "boolean", "default": False},
            },
        }


class RiskScoreWidget(BaseWidget):
    """
    Risk score widget.

    Displays overall risk score and key metrics.
    """

    async def get_data(self) -> dict[str, Any]:
        """Fetch risk score data."""
        return {
            "overall_score": 68.5,
            "risk_level": "high",
            "metrics": {
                "critical_assets": 5,
                "high_risk_assets": 12,
                "total_vulnerabilities": 70,
                "kev_vulnerabilities": 3,
            },
            "trend": {
                "direction": "increasing",
                "change_percentage": 5.2,
            },
            "top_risks": [
                {"name": "KEV Vulnerabilities", "score": 95},
                {"name": "Exposed High-Risk Ports", "score": 78},
                {"name": "Outdated Software", "score": 65},
            ],
        }

    def get_schema(self) -> dict[str, Any]:
        """Get widget schema."""
        return {
            "type": "object",
            "properties": {
                "show_trend": {"type": "boolean", "default": True},
                "show_top_risks": {"type": "boolean", "default": True},
                "top_risks_count": {"type": "integer", "minimum": 3, "maximum": 10, "default": 5},
            },
        }
