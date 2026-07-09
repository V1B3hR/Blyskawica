"""Delta monitoring for attack surface changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from nethical_recon.passive_recon.alerting import Alert, AlertManager, AlertSeverity


class ChangeType(Enum):
    """Types of attack surface changes."""

    NEW_ASSET = "new_asset"
    REMOVED_ASSET = "removed_asset"
    MODIFIED_ASSET = "modified_asset"
    NEW_SERVICE = "new_service"
    REMOVED_SERVICE = "removed_service"
    NEW_TECHNOLOGY = "new_technology"
    NEW_VULNERABILITY = "new_vulnerability"
    CONFIGURATION_CHANGE = "configuration_change"


@dataclass
class SurfaceChange:
    """Represents a change in the attack surface."""

    change_type: ChangeType
    timestamp: datetime
    asset_id: str
    description: str
    severity: AlertSeverity = AlertSeverity.INFO
    details: dict[str, Any] = field(default_factory=dict)
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None


class DeltaMonitor:
    """Monitor attack surface changes and generate alerts."""

    def __init__(self, alert_manager: Optional[AlertManager] = None):
        """Initialize delta monitor.

        Args:
            alert_manager: AlertManager for sending alerts
        """
        self.alert_manager = alert_manager or AlertManager()
        self.changes: list[SurfaceChange] = []

    def compare_snapshots(self, baseline: Any, current: Any) -> list[SurfaceChange]:
        """Compare two snapshots and detect changes.

        Args:
            baseline: Baseline snapshot
            current: Current snapshot

        Returns:
            List of detected changes
        """
        changes = []
        timestamp = datetime.now()

        # Create asset dictionaries for comparison
        baseline_assets = {asset.asset_id: asset for asset in baseline.assets}
        current_assets = {asset.asset_id: asset for asset in current.assets}

        # Detect new assets
        for asset_id in current_assets.keys() - baseline_assets.keys():
            asset = current_assets[asset_id]
            change = SurfaceChange(
                change_type=ChangeType.NEW_ASSET,
                timestamp=timestamp,
                asset_id=asset_id,
                description=f"New asset discovered: {asset.host}",
                severity=AlertSeverity.MEDIUM,
                details={
                    "asset_type": asset.asset_type,
                    "host": asset.host,
                    "port": asset.port,
                    "service": asset.service,
                },
                new_value=asset,
            )
            changes.append(change)

        # Detect removed assets
        for asset_id in baseline_assets.keys() - current_assets.keys():
            asset = baseline_assets[asset_id]
            change = SurfaceChange(
                change_type=ChangeType.REMOVED_ASSET,
                timestamp=timestamp,
                asset_id=asset_id,
                description=f"Asset removed: {asset.host}",
                severity=AlertSeverity.LOW,
                details={
                    "asset_type": asset.asset_type,
                    "host": asset.host,
                },
                old_value=asset,
            )
            changes.append(change)

        # Detect modified assets
        for asset_id in baseline_assets.keys() & current_assets.keys():
            baseline_asset = baseline_assets[asset_id]
            current_asset = current_assets[asset_id]

            asset_changes = self._compare_assets(baseline_asset, current_asset, timestamp)
            changes.extend(asset_changes)

        self.changes.extend(changes)
        return changes

    def _compare_assets(self, baseline: Any, current: Any, timestamp: datetime) -> list[SurfaceChange]:
        """Compare two assets and detect changes.

        Args:
            baseline: Baseline asset
            current: Current asset
            timestamp: Change timestamp

        Returns:
            List of detected changes
        """
        changes = []

        # Compare services
        if baseline.service != current.service:
            change = SurfaceChange(
                change_type=ChangeType.MODIFIED_ASSET,
                timestamp=timestamp,
                asset_id=current.asset_id,
                description=f"Service changed on {current.host}",
                severity=AlertSeverity.MEDIUM,
                details={
                    "old_service": baseline.service,
                    "new_service": current.service,
                },
                old_value=baseline.service,
                new_value=current.service,
            )
            changes.append(change)

        # Compare service versions
        if baseline.service_version != current.service_version:
            change = SurfaceChange(
                change_type=ChangeType.CONFIGURATION_CHANGE,
                timestamp=timestamp,
                asset_id=current.asset_id,
                description=f"Service version changed on {current.host}",
                severity=AlertSeverity.INFO,
                details={
                    "service": current.service,
                    "old_version": baseline.service_version,
                    "new_version": current.service_version,
                },
                old_value=baseline.service_version,
                new_value=current.service_version,
            )
            changes.append(change)

        # Compare technologies
        baseline_techs = {t["name"]: t for t in baseline.technologies}
        current_techs = {t["name"]: t for t in current.technologies}

        # New technologies
        for tech_name in current_techs.keys() - baseline_techs.keys():
            tech = current_techs[tech_name]
            change = SurfaceChange(
                change_type=ChangeType.NEW_TECHNOLOGY,
                timestamp=timestamp,
                asset_id=current.asset_id,
                description=f"New technology detected on {current.host}: {tech_name}",
                severity=AlertSeverity.MEDIUM,
                details={"technology": tech},
                new_value=tech,
            )
            changes.append(change)

        return changes

    def generate_alerts(self, changes: list[SurfaceChange], channel: Optional[str] = None) -> None:
        """Generate alerts for detected changes.

        Args:
            changes: List of changes
            channel: Specific alert channel or None for all
        """
        for change in changes:
            # Only alert on medium or higher severity
            if change.severity in [AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                alert = Alert(
                    title=f"Attack Surface Change: {change.change_type.value}",
                    message=change.description,
                    severity=change.severity,
                    metadata={
                        "asset_id": change.asset_id,
                        "timestamp": change.timestamp.isoformat(),
                        "details": change.details,
                    },
                )
                self.alert_manager.send_alert(alert, channel)

    def get_trending_changes(self, hours: int = 24) -> dict[ChangeType, int]:
        """Get trending changes over a time period.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary of change types and counts
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)
        recent_changes = [c for c in self.changes if c.timestamp >= cutoff]

        trending = {}
        for change in recent_changes:
            trending[change.change_type] = trending.get(change.change_type, 0) + 1

        return trending

    def get_high_risk_changes(self) -> list[SurfaceChange]:
        """Get high-risk changes.

        Returns:
            List of high/critical severity changes
        """
        return [c for c in self.changes if c.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]]
