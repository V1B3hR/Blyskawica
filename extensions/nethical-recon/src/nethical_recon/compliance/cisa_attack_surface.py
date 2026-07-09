"""
CISA Attack Surface Monitoring

Monitors attack surface areas recommended by CISA including internet-facing assets,
remote access services, email, web applications, cloud services, and supply chain.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CISAAttackSurfaceArea(Enum):
    """CISA-recommended attack surface monitoring areas."""

    INTERNET_FACING_ASSETS = "internet_facing_assets"
    REMOTE_ACCESS_SERVICES = "remote_access_services"
    EMAIL_INFRASTRUCTURE = "email_infrastructure"
    WEB_APPLICATIONS = "web_applications"
    CLOUD_SERVICES = "cloud_services"
    SUPPLY_CHAIN = "supply_chain"


@dataclass
class AttackSurfaceMetrics:
    """Metrics for an attack surface area."""

    area: CISAAttackSurfaceArea
    total_assets: int = 0
    exposed_assets: int = 0
    vulnerable_assets: int = 0
    monitored: bool = False
    last_scan: str = ""
    exposure_level: str = "unknown"
    recommendations: list[str] = field(default_factory=list)


class CISAAttackSurfaceMonitor:
    """
    CISA Attack Surface Monitor.

    Monitors and categorizes assets according to CISA-recommended attack surface areas.

    Features:
    - Asset categorization by CISA areas
    - Exposure tracking
    - Coverage monitoring
    - Gap identification
    - Alert on new exposures
    """

    def __init__(self):
        """Initialize CISA attack surface monitor."""
        self._metrics: dict[CISAAttackSurfaceArea, AttackSurfaceMetrics] = {}
        self._asset_categories: dict[str, CISAAttackSurfaceArea] = {}
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize metrics for all attack surface areas."""
        for area in CISAAttackSurfaceArea:
            self._metrics[area] = AttackSurfaceMetrics(area=area)

    def categorize_asset(self, asset_id: str, asset_type: str, asset_metadata: dict[str, Any]) -> CISAAttackSurfaceArea:
        """
        Categorize asset into CISA attack surface area.

        Args:
            asset_id: Asset identifier
            asset_type: Type of asset
            asset_metadata: Asset metadata

        Returns:
            CISA attack surface area
        """
        area = self._determine_area(asset_type, asset_metadata)
        self._asset_categories[asset_id] = area
        return area

    def _determine_area(self, asset_type: str, metadata: dict[str, Any]) -> CISAAttackSurfaceArea:
        """Determine attack surface area for asset."""
        asset_type_lower = asset_type.lower()

        # Check for internet-facing assets
        if metadata.get("internet_facing", False) or metadata.get("public", False):
            return CISAAttackSurfaceArea.INTERNET_FACING_ASSETS

        # Check for remote access services
        if any(service in asset_type_lower for service in ["vpn", "rdp", "ssh", "remote desktop", "remote access"]):
            return CISAAttackSurfaceArea.REMOTE_ACCESS_SERVICES

        # Check for email infrastructure
        if any(service in asset_type_lower for service in ["smtp", "email", "mail server", "exchange"]):
            return CISAAttackSurfaceArea.EMAIL_INFRASTRUCTURE

        # Check for web applications
        if any(service in asset_type_lower for service in ["web", "http", "https", "api", "webapp"]):
            return CISAAttackSurfaceArea.WEB_APPLICATIONS

        # Check for cloud services
        if any(
            service in asset_type_lower for service in ["aws", "azure", "gcp", "cloud", "s3", "lambda", "container"]
        ):
            return CISAAttackSurfaceArea.CLOUD_SERVICES

        # Check for supply chain
        if any(service in asset_type_lower for service in ["vendor", "supplier", "third-party", "partner"]):
            return CISAAttackSurfaceArea.SUPPLY_CHAIN

        # Default to internet-facing if uncertain
        return CISAAttackSurfaceArea.INTERNET_FACING_ASSETS

    def update_metrics(
        self, area: CISAAttackSurfaceArea, total: int, exposed: int, vulnerable: int, monitored: bool = True
    ):
        """
        Update metrics for attack surface area.

        Args:
            area: Attack surface area
            total: Total assets in area
            exposed: Number of exposed assets
            vulnerable: Number of vulnerable assets
            monitored: Whether area is being monitored
        """
        metrics = self._metrics[area]
        metrics.total_assets = total
        metrics.exposed_assets = exposed
        metrics.vulnerable_assets = vulnerable
        metrics.monitored = monitored

        # Calculate exposure level
        if total == 0:
            metrics.exposure_level = "none"
        else:
            exposure_ratio = exposed / total
            if exposure_ratio >= 0.7:
                metrics.exposure_level = "high"
            elif exposure_ratio >= 0.4:
                metrics.exposure_level = "medium"
            else:
                metrics.exposure_level = "low"

        # Generate recommendations
        metrics.recommendations = self._generate_recommendations(area, metrics)

        logger.debug(f"Updated metrics for {area.value}: {total} total, {exposed} exposed, {vulnerable} vulnerable")

    def _generate_recommendations(self, area: CISAAttackSurfaceArea, metrics: AttackSurfaceMetrics) -> list[str]:
        """Generate recommendations for attack surface area."""
        recommendations = []

        if metrics.exposure_level == "high":
            recommendations.append(f"High exposure detected in {area.value}. Review and reduce attack surface.")

        if metrics.vulnerable_assets > 0:
            recommendations.append(
                f"{metrics.vulnerable_assets} vulnerable assets found. Prioritize patching and remediation."
            )

        if not metrics.monitored:
            recommendations.append(f"Enable monitoring for {area.value} per CISA recommendations.")

        # Area-specific recommendations
        area_recommendations = {
            CISAAttackSurfaceArea.INTERNET_FACING_ASSETS: [
                "Minimize internet-facing assets",
                "Implement web application firewall",
                "Regular vulnerability scanning",
            ],
            CISAAttackSurfaceArea.REMOTE_ACCESS_SERVICES: [
                "Implement multi-factor authentication",
                "Use VPN with strong encryption",
                "Monitor and log all remote access",
            ],
            CISAAttackSurfaceArea.EMAIL_INFRASTRUCTURE: [
                "Implement DMARC, SPF, and DKIM",
                "Deploy email security gateway",
                "Enable advanced threat protection",
            ],
            CISAAttackSurfaceArea.WEB_APPLICATIONS: [
                "Follow OWASP security guidelines",
                "Implement HTTPS with HSTS",
                "Regular security testing",
            ],
            CISAAttackSurfaceArea.CLOUD_SERVICES: [
                "Enable cloud security posture management",
                "Review and minimize permissions",
                "Monitor for misconfigurations",
            ],
            CISAAttackSurfaceArea.SUPPLY_CHAIN: [
                "Assess third-party security practices",
                "Monitor vendor security posture",
                "Implement vendor risk management",
            ],
        }

        if area in area_recommendations and metrics.monitored:
            recommendations.extend(area_recommendations[area][:2])

        return recommendations

    def get_coverage_report(self) -> dict[str, Any]:
        """
        Get attack surface coverage report.

        Returns:
            Coverage report showing monitoring status for each area
        """
        monitored_areas = [area for area, metrics in self._metrics.items() if metrics.monitored]
        total_areas = len(CISAAttackSurfaceArea)

        coverage_percentage = (len(monitored_areas) / total_areas) * 100 if total_areas else 0

        return {
            "total_areas": total_areas,
            "monitored_areas": len(monitored_areas),
            "coverage_percentage": round(coverage_percentage, 2),
            "areas": {area.value: self._get_area_summary(metrics) for area, metrics in self._metrics.items()},
            "high_exposure_areas": [
                area.value for area, metrics in self._metrics.items() if metrics.exposure_level == "high"
            ],
            "gaps": [area.value for area in CISAAttackSurfaceArea if not self._metrics[area].monitored],
        }

    def _get_area_summary(self, metrics: AttackSurfaceMetrics) -> dict[str, Any]:
        """Get summary for an attack surface area."""
        return {
            "total_assets": metrics.total_assets,
            "exposed_assets": metrics.exposed_assets,
            "vulnerable_assets": metrics.vulnerable_assets,
            "monitored": metrics.monitored,
            "exposure_level": metrics.exposure_level,
            "recommendations": metrics.recommendations,
        }

    def get_exposed_assets_summary(self) -> dict[str, Any]:
        """
        Get summary of exposed assets across all areas.

        Returns:
            Summary of exposed assets
        """
        total_assets = sum(metrics.total_assets for metrics in self._metrics.values())
        total_exposed = sum(metrics.exposed_assets for metrics in self._metrics.values())
        total_vulnerable = sum(metrics.vulnerable_assets for metrics in self._metrics.values())

        return {
            "total_assets": total_assets,
            "total_exposed": total_exposed,
            "total_vulnerable": total_vulnerable,
            "exposure_percentage": round((total_exposed / total_assets) * 100, 2) if total_assets > 0 else 0,
            "by_area": {
                area.value: {
                    "exposed": metrics.exposed_assets,
                    "vulnerable": metrics.vulnerable_assets,
                }
                for area, metrics in self._metrics.items()
            },
        }
