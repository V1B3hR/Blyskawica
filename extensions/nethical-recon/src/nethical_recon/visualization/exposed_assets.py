"""Exposed asset detection module."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ExposureLevel(Enum):
    """Asset exposure levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExposedAsset:
    """Represents an exposed asset."""

    asset_id: str
    host: str
    port: int
    service: Optional[str]
    exposure_level: ExposureLevel
    reasons: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ExposedAssetDetector:
    """Detector for exposed and potentially vulnerable assets."""

    # High-risk ports that should not be exposed to internet
    HIGH_RISK_PORTS = {
        21: "FTP - Unencrypted file transfer",
        23: "Telnet - Unencrypted remote access",
        445: "SMB - File sharing, often targeted",
        3389: "RDP - Remote Desktop Protocol",
        5432: "PostgreSQL - Database",
        3306: "MySQL - Database",
        1433: "MS SQL - Database",
        27017: "MongoDB - Database",
        6379: "Redis - Database",
        9200: "Elasticsearch - Search engine",
        5984: "CouchDB - Database",
        2375: "Docker - Container management (unencrypted)",
        2376: "Docker - Container management (TLS)",
        8080: "Common alt HTTP port",
        8888: "Common alt HTTP port",
    }

    # Medium-risk ports
    MEDIUM_RISK_PORTS = {
        22: "SSH - Remote access",
        25: "SMTP - Mail server",
        110: "POP3 - Mail retrieval",
        143: "IMAP - Mail retrieval",
        3000: "Common development port",
        5000: "Common development port",
        8000: "Common development port",
    }

    def __init__(self):
        """Initialize exposed asset detector."""
        pass

    def analyze_asset(self, asset: Any) -> Optional[ExposedAsset]:
        """Analyze an asset for exposure.

        Args:
            asset: Asset object

        Returns:
            ExposedAsset if asset is exposed, None otherwise
        """
        if not asset.port:
            return None

        exposure_level = ExposureLevel.LOW
        reasons = []
        recommendations = []

        # Check port risk level
        if asset.port in self.HIGH_RISK_PORTS:
            exposure_level = ExposureLevel.HIGH
            reasons.append(f"High-risk port {asset.port}: {self.HIGH_RISK_PORTS[asset.port]}")
            recommendations.append(f"Consider restricting access to port {asset.port}")
        elif asset.port in self.MEDIUM_RISK_PORTS:
            exposure_level = ExposureLevel.MEDIUM
            reasons.append(f"Medium-risk port {asset.port}: {self.MEDIUM_RISK_PORTS[asset.port]}")
            recommendations.append(f"Ensure proper authentication on port {asset.port}")

        # Check for unencrypted services
        if asset.service:
            service_lower = asset.service.lower()
            if any(unencrypted in service_lower for unencrypted in ["ftp", "telnet", "http"]) and asset.port not in [
                443,
                8443,
            ]:
                if exposure_level == ExposureLevel.LOW:
                    exposure_level = ExposureLevel.MEDIUM
                reasons.append(f"Unencrypted service: {asset.service}")
                recommendations.append("Use encrypted alternatives (SFTP, SSH, HTTPS)")

        # Check for database services exposed
        if asset.service and any(
            db in asset.service.lower() for db in ["mysql", "postgres", "mongodb", "redis", "elastic"]
        ):
            if exposure_level.value in ["low", "medium"]:
                exposure_level = ExposureLevel.HIGH
            reasons.append("Database service exposed to network")
            recommendations.append("Restrict database access to application servers only")

        # Check for admin interfaces
        if asset.port in [8080, 8443, 9090, 9000]:
            if "admin" in asset.service.lower() if asset.service else False:
                exposure_level = ExposureLevel.HIGH
                reasons.append("Administrative interface exposed")
                recommendations.append("Restrict admin interface to internal network")

        # Only return if there's actual exposure detected
        if reasons:
            return ExposedAsset(
                asset_id=asset.asset_id,
                host=asset.host,
                port=asset.port,
                service=asset.service,
                exposure_level=exposure_level,
                reasons=reasons,
                recommendations=recommendations,
                metadata={
                    "asset_type": asset.asset_type,
                    "protocol": asset.protocol,
                },
            )

        return None

    def analyze_snapshot(self, snapshot: Any) -> list[ExposedAsset]:
        """Analyze all assets in a snapshot for exposure.

        Args:
            snapshot: AttackSurfaceSnapshot object

        Returns:
            List of exposed assets
        """
        exposed_assets = []

        for asset in snapshot.assets:
            exposed = self.analyze_asset(asset)
            if exposed:
                exposed_assets.append(exposed)

        return exposed_assets

    def get_critical_exposures(self, exposed_assets: list[ExposedAsset]) -> list[ExposedAsset]:
        """Get critically exposed assets.

        Args:
            exposed_assets: List of exposed assets

        Returns:
            List of critically exposed assets
        """
        return [a for a in exposed_assets if a.exposure_level == ExposureLevel.CRITICAL]

    def generate_exposure_report(self, exposed_assets: list[ExposedAsset]) -> dict[str, Any]:
        """Generate exposure summary report.

        Args:
            exposed_assets: List of exposed assets

        Returns:
            Report dictionary
        """
        # Count by exposure level
        level_counts = {
            ExposureLevel.LOW: 0,
            ExposureLevel.MEDIUM: 0,
            ExposureLevel.HIGH: 0,
            ExposureLevel.CRITICAL: 0,
        }

        for asset in exposed_assets:
            level_counts[asset.exposure_level] += 1

        # Identify most common exposure reasons
        reason_counts = {}
        for asset in exposed_assets:
            for reason in asset.reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1

        top_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_exposed": len(exposed_assets),
            "exposure_levels": {
                "low": level_counts[ExposureLevel.LOW],
                "medium": level_counts[ExposureLevel.MEDIUM],
                "high": level_counts[ExposureLevel.HIGH],
                "critical": level_counts[ExposureLevel.CRITICAL],
            },
            "top_exposure_reasons": [{"reason": r, "count": c} for r, c in top_reasons],
            "critical_assets": [
                {"asset_id": a.asset_id, "host": a.host, "port": a.port, "reasons": a.reasons}
                for a in exposed_assets
                if a.exposure_level in [ExposureLevel.HIGH, ExposureLevel.CRITICAL]
            ],
        }
