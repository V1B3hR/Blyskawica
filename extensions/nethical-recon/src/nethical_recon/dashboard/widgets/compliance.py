"""
Compliance Widgets

Widgets for displaying compliance and CISA-specific data.
"""

from typing import Any

from .base import BaseWidget


class ComplianceScoreWidget(BaseWidget):
    """
    Compliance score widget.

    Displays overall compliance score and breakdown by framework.
    """

    async def get_data(self) -> dict[str, Any]:
        """Fetch compliance score data."""
        return {
            "overall_score": 85.5,
            "by_framework": {
                "CISA KEV": 92.0,
                "OWASP Top 10": 88.0,
                "NIST CSF": 82.0,
                "PCI DSS": 78.0,
            },
            "trend": "improving",
            "last_updated": "2025-01-14T22:00:00Z",
        }

    def get_schema(self) -> dict[str, Any]:
        """Get widget schema."""
        return {
            "type": "object",
            "properties": {
                "frameworks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["CISA KEV", "OWASP Top 10", "NIST CSF"],
                },
                "show_trend": {"type": "boolean", "default": True},
            },
        }


class KEVWidget(BaseWidget):
    """
    CISA KEV widget.

    Displays CISA Known Exploited Vulnerabilities status.
    """

    async def get_data(self) -> dict[str, Any]:
        """Fetch KEV data."""
        return {
            "total_kev": 3,
            "open_kev": 2,
            "overdue_kev": 1,
            "vulnerabilities": [
                {
                    "cve_id": "CVE-2021-44228",
                    "name": "Log4Shell",
                    "due_date": "2022-01-15",
                    "status": "overdue",
                    "days_overdue": 730,
                },
                {
                    "cve_id": "CVE-2021-45046",
                    "name": "Log4j RCE",
                    "due_date": "2022-01-20",
                    "status": "open",
                    "days_remaining": 5,
                },
            ],
            "compliance_percentage": 33.3,
        }

    def get_schema(self) -> dict[str, Any]:
        """Get widget schema."""
        return {
            "type": "object",
            "properties": {
                "show_details": {"type": "boolean", "default": True},
                "max_items": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
        }
