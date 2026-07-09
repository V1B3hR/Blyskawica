"""
Attack Surface Mapper

Core module for mapping and analyzing the attack surface of targets,
integrating fingerprinting, service detection, and asset tracking.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .fingerprinting import TechnologyFingerprinter, ServiceDetector, CMSDetector


@dataclass
class Asset:
    """Represents a discovered asset."""

    asset_id: str
    asset_type: str  # host, service, application, etc.
    host: str
    port: int | None = None
    protocol: str | None = None
    technologies: list[dict[str, Any]] = field(default_factory=list)
    services: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AttackSurfaceSnapshot:
    """Represents a point-in-time snapshot of the attack surface."""

    snapshot_id: str
    target: str
    assets: list[Asset]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


class AttackSurfaceMapper:
    """
    Attack Surface Mapper

    Maps the attack surface of targets by discovering and cataloging
    hosts, services, technologies, and their relationships.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tech_fingerprinter = TechnologyFingerprinter()
        self.service_detector = ServiceDetector()
        self.cms_detector = CMSDetector()

    def map_surface(self, target: str, ports: list[int] | None = None) -> AttackSurfaceSnapshot:
        """
        Map the attack surface of a target.

        Args:
            target: Target host or URL
            ports: Optional list of ports to scan

        Returns:
            Attack surface snapshot
        """
        self.logger.info(f"Mapping attack surface for {target}")

        assets = []
        snapshot_id = f"snapshot_{target}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Detect technologies if target is a URL
        if target.startswith("http://") or target.startswith("https://"):
            tech_results = self.tech_fingerprinter.fingerprint(target)
            cms_result = self.cms_detector.detect_cms(target)

            # Create asset for web application
            asset = Asset(
                asset_id=f"web_{target}",
                asset_type="web_application",
                host=target,
                technologies=[
                    {
                        "name": r.technology,
                        "category": r.category,
                        "version": r.version,
                        "confidence": r.confidence,
                    }
                    for r in tech_results
                ],
                metadata={"cms": cms_result},
            )
            assets.append(asset)

        # Detect services on ports
        if ports:
            host = target.replace("http://", "").replace("https://", "").split("/")[0]
            service_results = self.service_detector.analyze_ports(host, ports)

            for svc in service_results:
                asset = Asset(
                    asset_id=f"service_{host}_{svc['port']}",
                    asset_type="service",
                    host=host,
                    port=svc["port"],
                    protocol=svc["protocol"],
                    services=[svc],
                )
                assets.append(asset)

        snapshot = AttackSurfaceSnapshot(
            snapshot_id=snapshot_id,
            target=target,
            assets=assets,
        )

        self.logger.info(f"Mapped {len(assets)} assets for {target}")
        return snapshot

    def compare_snapshots(self, baseline: AttackSurfaceSnapshot, current: AttackSurfaceSnapshot) -> dict[str, Any]:
        """
        Compare two attack surface snapshots to detect changes.

        Args:
            baseline: Baseline snapshot
            current: Current snapshot

        Returns:
            Comparison result with added/removed/changed assets
        """
        self.logger.info(f"Comparing snapshots: {baseline.snapshot_id} vs {current.snapshot_id}")

        baseline_assets = {a.asset_id: a for a in baseline.assets}
        current_assets = {a.asset_id: a for a in current.assets}

        added = [a for aid, a in current_assets.items() if aid not in baseline_assets]
        removed = [a for aid, a in baseline_assets.items() if aid not in current_assets]

        # Find changed assets
        changed = []
        for aid in set(baseline_assets.keys()) & set(current_assets.keys()):
            baseline_asset = baseline_assets[aid]
            current_asset = current_assets[aid]

            if self._asset_changed(baseline_asset, current_asset):
                changed.append(
                    {
                        "asset_id": aid,
                        "baseline": baseline_asset,
                        "current": current_asset,
                    }
                )

        return {
            "added": added,
            "removed": removed,
            "changed": changed,
            "total_baseline": len(baseline_assets),
            "total_current": len(current_assets),
        }

    def _asset_changed(self, baseline: Asset, current: Asset) -> bool:
        """Check if an asset has changed between snapshots."""
        # Compare technologies
        baseline_techs = {t["name"] for t in baseline.technologies}
        current_techs = {t["name"] for t in current.technologies}

        if baseline_techs != current_techs:
            return True

        # Compare services
        baseline_svcs = {s.get("service") for s in baseline.services}
        current_svcs = {s.get("service") for s in current.services}

        if baseline_svcs != current_svcs:
            return True

        return False

    def generate_report(self, snapshot: AttackSurfaceSnapshot) -> dict[str, Any]:
        """
        Generate a summary report of the attack surface.

        Args:
            snapshot: Attack surface snapshot

        Returns:
            Summary report
        """
        self.logger.info(f"Generating report for snapshot {snapshot.snapshot_id}")

        # Count assets by type
        asset_types = {}
        for asset in snapshot.assets:
            asset_types[asset.asset_type] = asset_types.get(asset.asset_type, 0) + 1

        # Count technologies by category
        tech_categories = {}
        for asset in snapshot.assets:
            for tech in asset.technologies:
                category = tech.get("category", "unknown")
                tech_categories[category] = tech_categories.get(category, 0) + 1

        # Identify exposed services
        exposed_services = []
        for asset in snapshot.assets:
            if asset.asset_type == "service" and asset.port:
                exposed_services.append(
                    {
                        "host": asset.host,
                        "port": asset.port,
                        "protocol": asset.protocol,
                        "service": asset.services[0].get("service") if asset.services else "unknown",
                    }
                )

        return {
            "snapshot_id": snapshot.snapshot_id,
            "target": snapshot.target,
            "timestamp": snapshot.timestamp.isoformat(),
            "total_assets": len(snapshot.assets),
            "assets_by_type": asset_types,
            "technologies_by_category": tech_categories,
            "exposed_services": exposed_services,
        }
