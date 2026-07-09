"""
Dashboard Widgets

Widget library for composable dashboards.
"""

from .base import BaseWidget
from .vulnerability import VulnerabilityChartWidget, VulnerabilityTableWidget
from .asset import AssetMapWidget, AssetListWidget
from .compliance import ComplianceScoreWidget, KEVWidget
from .alert import AlertFeedWidget, RiskScoreWidget

__all__ = [
    "BaseWidget",
    "VulnerabilityChartWidget",
    "VulnerabilityTableWidget",
    "AssetMapWidget",
    "AssetListWidget",
    "ComplianceScoreWidget",
    "KEVWidget",
    "AlertFeedWidget",
    "RiskScoreWidget",
]
