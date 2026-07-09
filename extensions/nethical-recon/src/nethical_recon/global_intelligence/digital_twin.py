"""
Organization Digital Twin

Creates a virtual replica of the organization's digital infrastructure,
assets, and attack surface for simulation and analysis.

Part of ROADMAP 5.0 Section V.15: Global Attack Surface Intelligence
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class TwinAsset:
    """Represents an asset in the digital twin"""

    asset_id: UUID = field(default_factory=uuid4)
    real_asset_id: str = ""  # Reference to real asset
    asset_type: str = ""
    name: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    connections: list[str] = field(default_factory=list)  # Connected asset IDs
    state: dict[str, Any] = field(default_factory=dict)
    last_sync: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TwinRelationship:
    """Represents a relationship between assets in the twin"""

    relationship_id: UUID = field(default_factory=uuid4)
    source_asset: str = ""
    target_asset: str = ""
    relationship_type: str = ""  # connects_to, depends_on, manages, etc.
    properties: dict[str, Any] = field(default_factory=dict)


class DigitalTwin:
    """
    Organization Digital Twin

    Creates and maintains a virtual replica of the organization's:
    - Infrastructure assets
    - Network topology
    - Service dependencies
    - Security posture
    - Attack surface

    Features:
    - Real-time synchronization with live environment
    - What-if analysis and simulation
    - Attack path modeling
    - Change impact analysis
    - Disaster recovery planning
    - Security testing sandbox

    Use Cases:
    - Test security changes before deployment
    - Simulate attack scenarios
    - Model network changes
    - Plan disaster recovery
    - Visualize dependencies
    - Risk assessment
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize digital twin

        Args:
            config: Configuration options
                - organization_name: Name of the organization
                - sync_interval_minutes: Minutes between syncs (default: 60)
                - enable_simulation: Enable what-if simulation (default: True)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.organization_name = self.config.get("organization_name", "Unknown")
        self.sync_interval_minutes = self.config.get("sync_interval_minutes", 60)
        self.enable_simulation = self.config.get("enable_simulation", True)

        # Twin state
        self._assets: dict[str, TwinAsset] = {}
        self._relationships: list[TwinRelationship] = []
        self._last_sync: datetime | None = None
        self._twin_id: UUID = uuid4()

        self.logger.info(f"Digital Twin initialized for {self.organization_name}")

    def create_twin(
        self,
        assets: list[dict[str, Any]],
        relationships: list[dict[str, Any]] | None = None,
    ) -> UUID:
        """
        Create digital twin from real infrastructure

        Args:
            assets: List of real assets to replicate
            relationships: Optional relationships between assets

        Returns:
            Twin ID
        """
        self.logger.info(f"Creating digital twin with {len(assets)} assets")

        # Clear existing twin
        self._assets.clear()
        self._relationships.clear()

        # Create twin assets
        for asset in assets:
            twin_asset = self._create_twin_asset(asset)
            self._assets[str(twin_asset.asset_id)] = twin_asset

        # Create relationships
        if relationships:
            for rel in relationships:
                twin_rel = self._create_twin_relationship(rel)
                self._relationships.append(twin_rel)
        else:
            # Infer relationships from asset data
            self._infer_relationships()

        self._last_sync = datetime.utcnow()

        self.logger.info(
            f"Digital twin created: {len(self._assets)} assets, " f"{len(self._relationships)} relationships"
        )

        return self._twin_id

    def sync_with_real_infrastructure(self, updated_assets: list[dict[str, Any]]) -> int:
        """
        Sync digital twin with real infrastructure

        Args:
            updated_assets: Current state of real assets

        Returns:
            Number of assets updated
        """
        self.logger.info("Syncing digital twin with real infrastructure")

        updates_count = 0

        for real_asset in updated_assets:
            real_id = real_asset.get("id", "")

            # Find corresponding twin asset
            twin_asset = self._find_twin_by_real_id(real_id)

            if twin_asset:
                # Update existing twin asset
                if self._update_twin_asset(twin_asset, real_asset):
                    updates_count += 1
            else:
                # Create new twin asset for newly discovered asset
                new_twin = self._create_twin_asset(real_asset)
                self._assets[str(new_twin.asset_id)] = new_twin
                updates_count += 1

        self._last_sync = datetime.utcnow()

        self.logger.info(f"Sync completed: {updates_count} assets updated")

        return updates_count

    def simulate_attack_path(self, entry_point: str, target: str) -> dict[str, Any]:
        """
        Simulate attack path from entry point to target

        Args:
            entry_point: Starting asset for attack
            target: Target asset

        Returns:
            Attack path simulation results
        """
        self.logger.info(f"Simulating attack path from {entry_point} to {target}")

        if not self.enable_simulation:
            self.logger.warning("Simulation is disabled")
            return {}

        # Find entry and target assets
        entry_asset = self._find_twin_by_name(entry_point)
        target_asset = self._find_twin_by_name(target)

        if not entry_asset or not target_asset:
            self.logger.warning("Entry point or target not found in twin")
            return {}

        # Find attack paths using graph traversal
        paths = self._find_paths(str(entry_asset.asset_id), str(target_asset.asset_id))

        # Analyze each path
        analyzed_paths = []
        for path in paths:
            path_analysis = self._analyze_attack_path(path)
            analyzed_paths.append(path_analysis)

        # Sort by feasibility
        analyzed_paths.sort(key=lambda p: p["feasibility_score"], reverse=True)

        result = {
            "entry_point": entry_point,
            "target": target,
            "paths_found": len(analyzed_paths),
            "paths": analyzed_paths[:5],  # Top 5 most feasible paths
            "recommendations": self._generate_path_mitigations(analyzed_paths),
        }

        self.logger.info(f"Found {len(analyzed_paths)} potential attack paths")

        return result

    def simulate_change_impact(self, change_description: dict[str, Any]) -> dict[str, Any]:
        """
        Simulate impact of infrastructure change

        Args:
            change_description: Description of proposed change
                - asset_id: Asset to change
                - change_type: Type of change (add, remove, modify)
                - properties: New properties

        Returns:
            Impact analysis
        """
        self.logger.info("Simulating infrastructure change impact")

        asset_id = change_description.get("asset_id", "")
        change_type = change_description.get("change_type", "")

        # Find affected asset
        twin_asset = self._find_twin_by_real_id(asset_id)

        if not twin_asset:
            return {"error": "Asset not found in twin"}

        # Analyze dependencies
        dependencies = self._find_dependencies(str(twin_asset.asset_id))

        # Simulate change
        impact = {
            "changed_asset": twin_asset.name,
            "change_type": change_type,
            "directly_affected": len(dependencies),
            "affected_assets": [self._assets[dep].name for dep in dependencies if dep in self._assets],
            "risk_assessment": self._assess_change_risk(twin_asset, change_type, dependencies),
            "recommendations": self._generate_change_recommendations(change_type, len(dependencies)),
        }

        return impact

    def get_twin_state(self) -> dict[str, Any]:
        """Get current state of digital twin"""
        return {
            "twin_id": str(self._twin_id),
            "organization": self.organization_name,
            "asset_count": len(self._assets),
            "relationship_count": len(self._relationships),
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
        }

    def _create_twin_asset(self, real_asset: dict[str, Any]) -> TwinAsset:
        """Create twin asset from real asset"""
        twin = TwinAsset(
            real_asset_id=real_asset.get("id", ""),
            asset_type=real_asset.get("asset_type", ""),
            name=real_asset.get("name", ""),
            properties=real_asset.copy(),
            state={"status": "active"},
        )

        return twin

    def _create_twin_relationship(self, real_relationship: dict[str, Any]) -> TwinRelationship:
        """Create twin relationship"""
        return TwinRelationship(
            source_asset=real_relationship.get("source", ""),
            target_asset=real_relationship.get("target", ""),
            relationship_type=real_relationship.get("type", ""),
            properties=real_relationship.get("properties", {}),
        )

    def _infer_relationships(self) -> None:
        """Infer relationships between assets based on properties"""
        # Simplified relationship inference
        for asset_id, asset in self._assets.items():
            connections = asset.properties.get("connections", [])

            for connection in connections:
                # Find target asset
                target = self._find_twin_by_name(connection)

                if target:
                    rel = TwinRelationship(
                        source_asset=asset_id,
                        target_asset=str(target.asset_id),
                        relationship_type="connects_to",
                    )
                    self._relationships.append(rel)

    def _update_twin_asset(self, twin_asset: TwinAsset, real_asset: dict[str, Any]) -> bool:
        """Update twin asset with real asset data"""
        # Check if there are changes
        if twin_asset.properties == real_asset:
            return False

        # Update properties
        twin_asset.properties = real_asset.copy()
        twin_asset.last_sync = datetime.utcnow()

        return True

    def _find_twin_by_real_id(self, real_id: str) -> TwinAsset | None:
        """Find twin asset by real asset ID"""
        for asset in self._assets.values():
            if asset.real_asset_id == real_id:
                return asset

        return None

    def _find_twin_by_name(self, name: str) -> TwinAsset | None:
        """Find twin asset by name"""
        for asset in self._assets.values():
            if asset.name == name:
                return asset

        return None

    def _find_paths(self, start: str, target: str, max_depth: int = 5) -> list[list[str]]:
        """Find paths between two assets using BFS"""
        if start == target:
            return [[start]]

        visited = set()
        queue = [[start]]
        paths = []

        while queue and len(paths) < 10:  # Limit to 10 paths
            path = queue.pop(0)
            node = path[-1]

            if len(path) > max_depth:
                continue

            if node == target:
                paths.append(path)
                continue

            if node in visited:
                continue

            visited.add(node)

            # Find neighbors
            neighbors = self._get_neighbors(node)

            for neighbor in neighbors:
                if neighbor not in path:
                    queue.append(path + [neighbor])

        return paths

    def _get_neighbors(self, asset_id: str) -> list[str]:
        """Get neighboring assets"""
        neighbors = []

        for rel in self._relationships:
            if rel.source_asset == asset_id:
                neighbors.append(rel.target_asset)
            elif rel.target_asset == asset_id:
                neighbors.append(rel.source_asset)

        return neighbors

    def _analyze_attack_path(self, path: list[str]) -> dict[str, Any]:
        """Analyze an attack path"""
        # Calculate feasibility
        feasibility = 100.0 - (len(path) * 10)  # Shorter paths are more feasible

        # Check for security controls
        for asset_id in path:
            asset = self._assets.get(asset_id)
            if asset and not asset.properties.get("public_access", False):
                feasibility -= 10  # Internal assets are harder to access

        path_names = [self._assets[aid].name for aid in path if aid in self._assets]

        return {
            "path": path_names,
            "length": len(path),
            "feasibility_score": max(0, feasibility),
            "difficulty": "easy" if feasibility > 70 else "medium" if feasibility > 40 else "hard",
        }

    def _find_dependencies(self, asset_id: str) -> list[str]:
        """Find assets that depend on the given asset"""
        dependencies = []

        for rel in self._relationships:
            if rel.source_asset == asset_id:
                dependencies.append(rel.target_asset)

        return dependencies

    def _assess_change_risk(self, asset: TwinAsset, change_type: str, dependencies: list[str]) -> str:
        """Assess risk of a change"""
        if change_type == "remove" and len(dependencies) > 5:
            return "HIGH - Many dependent assets will be affected"
        elif change_type == "remove" and len(dependencies) > 0:
            return "MEDIUM - Some assets depend on this"
        elif change_type == "modify":
            return "LOW - Modification with limited impact"
        else:
            return "LOW - Safe change"

    def _generate_path_mitigations(self, paths: list[dict[str, Any]]) -> list[str]:
        """Generate mitigation recommendations for attack paths"""
        if not paths:
            return []

        recommendations = [
            "Implement network segmentation to increase attack path complexity",
            "Add monitoring for lateral movement detection",
        ]

        # Check if many paths exist
        if len(paths) > 5:
            recommendations.append("Reduce attack surface by limiting connectivity between zones")

        return recommendations

    def _generate_change_recommendations(self, change_type: str, dependency_count: int) -> list[str]:
        """Generate recommendations for infrastructure change"""
        recommendations = []

        if change_type == "remove":
            recommendations.append("Ensure dependent services have alternatives")
            recommendations.append("Plan gradual decommissioning")

        if dependency_count > 0:
            recommendations.append(f"Coordinate with {dependency_count} dependent asset owners")
            recommendations.append("Implement change in maintenance window")

        return recommendations
