"""
Baseline Management

Manages baseline snapshots of attack surfaces for change detection
and tracking over time.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .mapper import AttackSurfaceSnapshot, Asset


@dataclass
class AssetBaseline:
    """Represents a baseline for an asset."""

    asset_id: str
    baseline_snapshot_id: str
    baseline_timestamp: datetime
    expected_technologies: list[str] = field(default_factory=list)
    expected_services: list[str] = field(default_factory=list)
    expected_ports: list[int] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaselineManager:
    """
    Baseline Manager

    Manages baseline snapshots and tracks changes to the attack surface over time.
    Provides alerting for new assets, removed assets, and configuration changes.
    """

    def __init__(self, storage_path: str | None = None):
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path) if storage_path else Path.cwd() / "baselines"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.baselines: dict[str, AttackSurfaceSnapshot] = {}

    def create_baseline(self, snapshot: AttackSurfaceSnapshot, name: str | None = None) -> str:
        """
        Create a baseline from an attack surface snapshot.

        Args:
            snapshot: Attack surface snapshot
            name: Optional baseline name (defaults to target name)

        Returns:
            Baseline identifier
        """
        baseline_name = name or f"baseline_{snapshot.target}"
        self.logger.info(f"Creating baseline: {baseline_name}")

        self.baselines[baseline_name] = snapshot
        self._save_baseline(baseline_name, snapshot)

        return baseline_name

    def load_baseline(self, name: str) -> AttackSurfaceSnapshot | None:
        """
        Load a baseline from storage.

        Args:
            name: Baseline name

        Returns:
            Attack surface snapshot or None if not found
        """
        if name in self.baselines:
            return self.baselines[name]

        baseline_file = self.storage_path / f"{name}.json"
        if not baseline_file.exists():
            self.logger.warning(f"Baseline {name} not found")
            return None

        try:
            with open(baseline_file, "r") as f:
                data = json.load(f)
                snapshot = self._deserialize_snapshot(data)
                self.baselines[name] = snapshot
                return snapshot
        except Exception as e:
            self.logger.error(f"Failed to load baseline {name}: {e}")
            return None

    def update_baseline(self, name: str, snapshot: AttackSurfaceSnapshot) -> bool:
        """
        Update an existing baseline.

        Args:
            name: Baseline name
            snapshot: New snapshot

        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Updating baseline: {name}")
        self.baselines[name] = snapshot
        self._save_baseline(name, snapshot)
        return True

    def get_asset_baseline(self, snapshot: AttackSurfaceSnapshot, asset_id: str) -> AssetBaseline | None:
        """
        Get baseline for a specific asset.

        Args:
            snapshot: Baseline snapshot
            asset_id: Asset identifier

        Returns:
            Asset baseline or None if not found
        """
        for asset in snapshot.assets:
            if asset.asset_id == asset_id:
                return AssetBaseline(
                    asset_id=asset.asset_id,
                    baseline_snapshot_id=snapshot.snapshot_id,
                    baseline_timestamp=snapshot.timestamp,
                    expected_technologies=[t["name"] for t in asset.technologies],
                    expected_services=[s.get("service", "") for s in asset.services],
                    expected_ports=[asset.port] if asset.port else [],
                )
        return None

    def detect_changes(self, baseline_name: str, current_snapshot: AttackSurfaceSnapshot) -> dict[str, Any]:
        """
        Detect changes between baseline and current snapshot.

        Args:
            baseline_name: Name of baseline to compare against
            current_snapshot: Current snapshot

        Returns:
            Change detection result
        """
        baseline = self.load_baseline(baseline_name)
        if not baseline:
            return {"error": f"Baseline {baseline_name} not found"}

        self.logger.info(f"Detecting changes from baseline {baseline_name}")

        baseline_assets = {a.asset_id: a for a in baseline.assets}
        current_assets = {a.asset_id: a for a in current_snapshot.assets}

        # New assets (potential security concern)
        new_assets = [a for aid, a in current_assets.items() if aid not in baseline_assets]

        # Removed assets (potential availability concern)
        removed_assets = [a for aid, a in baseline_assets.items() if aid not in current_assets]

        # Changed assets
        changed_assets = []
        for aid in set(baseline_assets.keys()) & set(current_assets.keys()):
            baseline_asset = baseline_assets[aid]
            current_asset = current_assets[aid]
            changes = self._compare_assets(baseline_asset, current_asset)
            if changes:
                changed_assets.append(
                    {
                        "asset_id": aid,
                        "changes": changes,
                    }
                )

        # Calculate risk score
        risk_score = self._calculate_risk_score(new_assets, removed_assets, changed_assets)

        return {
            "baseline_name": baseline_name,
            "baseline_timestamp": baseline.timestamp.isoformat(),
            "current_timestamp": current_snapshot.timestamp.isoformat(),
            "new_assets": [self._asset_to_dict(a) for a in new_assets],
            "removed_assets": [self._asset_to_dict(a) for a in removed_assets],
            "changed_assets": changed_assets,
            "risk_score": risk_score,
            "summary": {
                "total_new": len(new_assets),
                "total_removed": len(removed_assets),
                "total_changed": len(changed_assets),
            },
        }

    def _compare_assets(self, baseline: Asset, current: Asset) -> dict[str, Any]:
        """Compare two assets and return differences."""
        changes = {}

        # Compare technologies
        baseline_techs = {t["name"] for t in baseline.technologies}
        current_techs = {t["name"] for t in current.technologies}

        added_techs = current_techs - baseline_techs
        removed_techs = baseline_techs - current_techs

        if added_techs or removed_techs:
            changes["technologies"] = {
                "added": list(added_techs),
                "removed": list(removed_techs),
            }

        # Compare services
        baseline_svcs = {s.get("service") for s in baseline.services}
        current_svcs = {s.get("service") for s in current.services}

        added_svcs = current_svcs - baseline_svcs
        removed_svcs = baseline_svcs - current_svcs

        if added_svcs or removed_svcs:
            changes["services"] = {
                "added": list(added_svcs),
                "removed": list(removed_svcs),
            }

        return changes

    def _calculate_risk_score(
        self, new_assets: list[Asset], removed_assets: list[Asset], changed_assets: list[dict[str, Any]]
    ) -> float:
        """Calculate risk score based on changes."""
        score = 0.0

        # New assets increase risk (potential shadow IT, misconfigurations)
        score += len(new_assets) * 10

        # Removed assets may indicate issues
        score += len(removed_assets) * 5

        # Changed assets indicate configuration drift
        score += len(changed_assets) * 3

        # Normalize to 0-100 scale
        return min(100.0, score)

    def _save_baseline(self, name: str, snapshot: AttackSurfaceSnapshot) -> None:
        """Save baseline to storage."""
        baseline_file = self.storage_path / f"{name}.json"
        try:
            data = self._serialize_snapshot(snapshot)
            with open(baseline_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
            self.logger.info(f"Baseline saved to {baseline_file}")
        except Exception as e:
            self.logger.error(f"Failed to save baseline {name}: {e}")

    def _serialize_snapshot(self, snapshot: AttackSurfaceSnapshot) -> dict[str, Any]:
        """Serialize snapshot to dict."""
        return {
            "snapshot_id": snapshot.snapshot_id,
            "target": snapshot.target,
            "timestamp": snapshot.timestamp.isoformat(),
            "assets": [self._asset_to_dict(a) for a in snapshot.assets],
            "metadata": snapshot.metadata,
        }

    def _deserialize_snapshot(self, data: dict[str, Any]) -> AttackSurfaceSnapshot:
        """Deserialize snapshot from dict."""
        assets = [self._dict_to_asset(a) for a in data["assets"]]
        return AttackSurfaceSnapshot(
            snapshot_id=data["snapshot_id"],
            target=data["target"],
            assets=assets,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )

    def _asset_to_dict(self, asset: Asset) -> dict[str, Any]:
        """Convert asset to dict."""
        return {
            "asset_id": asset.asset_id,
            "asset_type": asset.asset_type,
            "host": asset.host,
            "port": asset.port,
            "protocol": asset.protocol,
            "technologies": asset.technologies,
            "services": asset.services,
            "metadata": asset.metadata,
            "discovered_at": asset.discovered_at.isoformat(),
            "last_seen": asset.last_seen.isoformat(),
        }

    def _dict_to_asset(self, data: dict[str, Any]) -> Asset:
        """Convert dict to asset."""
        return Asset(
            asset_id=data["asset_id"],
            asset_type=data["asset_type"],
            host=data["host"],
            port=data.get("port"),
            protocol=data.get("protocol"),
            technologies=data.get("technologies", []),
            services=data.get("services", []),
            metadata=data.get("metadata", {}),
            discovered_at=datetime.fromisoformat(data["discovered_at"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
        )
