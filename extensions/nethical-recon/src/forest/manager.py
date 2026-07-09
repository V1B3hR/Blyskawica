"""
forest/manager.py
Forest Manager - orchestrates the entire forest infrastructure.

The Forest Manager:
- Manages trees (hosts/servers)
- Coordinates threat detection
- Maintains forest health
- Provides central control
"""

from datetime import datetime
from typing import Any

from .base import ForestBase
from .threats import BaseThreat, ThreatDetector
from .trees import ForestMap, Tree


class ForestManager(ForestBase):
    """
    Central manager for the forest infrastructure.

    Analogia: 🌲 Leśniczy - Zarządza całym lasem
    """

    def __init__(self, forest_name: str = "Infrastructure"):
        """
        Initialize the forest manager.

        Args:
            forest_name: Name of the forest
        """
        super().__init__(forest_name)

        # Core components
        self.forest_map = ForestMap(f"{forest_name} Map")
        self.threat_detector = ThreatDetector()

        # Trees managed by this forest
        self.trees = {}  # tree_id -> Tree

        # Statistics
        self.total_scans = 0
        self.last_scan_time = None

    def add_tree(self, tree: Tree):
        """
        Add a tree to the forest.

        Args:
            tree: Tree object to add
        """
        self.trees[tree.component_id] = tree
        self.forest_map.add_tree(tree)
        self.add_component(tree)

    def remove_tree(self, tree_id: str):
        """Remove a tree from the forest"""
        if tree_id in self.trees:
            del self.trees[tree_id]
            self.forest_map.remove_tree(tree_id)
            self.remove_component(tree_id)

    def get_tree(self, tree_id: str) -> Tree | None:
        """Get a tree by ID"""
        return self.trees.get(tree_id)

    def get_tree_by_hostname(self, hostname: str) -> Tree | None:
        """Get a tree by hostname"""
        return self.forest_map.get_tree_by_hostname(hostname)

    def get_tree_by_ip(self, ip_address: str) -> Tree | None:
        """Get a tree by IP address"""
        return self.forest_map.get_tree_by_ip(ip_address)

    def get_all_trees(self) -> list[Tree]:
        """Get all trees in the forest"""
        return list(self.trees.values())

    def detect_threat(self, threat: BaseThreat, tree_id: str, branch_id: str | None = None, leaf_id: str | None = None):
        """
        Detect and register a threat in the forest.

        Args:
            threat: Threat object
            tree_id: Tree where threat was detected
            branch_id: Optional branch where threat was detected
            leaf_id: Optional leaf where threat was detected
        """
        # Set threat location
        threat.set_location(tree_id, branch_id, leaf_id)

        # Add threat to appropriate component
        tree = self.get_tree(tree_id)
        if tree:
            tree.add_threat(threat)

            if branch_id:
                branch = tree.get_branch(branch_id)
                if branch:
                    branch.add_threat(threat)

                    if leaf_id:
                        leaf = branch.get_leaf(leaf_id)
                        if leaf:
                            leaf.add_threat(threat)

    def scan_forest(self) -> dict[str, Any]:
        """
        Perform a complete forest scan.

        Returns:
            Scan results dictionary
        """
        scan_start = datetime.now()

        # Update forest statistics
        self.forest_map.update_statistics()

        # Scan each tree
        scan_results = {
            "scan_time": scan_start.isoformat(),
            "trees_scanned": len(self.trees),
            "threats_found": self.threat_detector.get_threat_summary(),
            "forest_health": self.get_total_health_score(),
            "tree_details": [],
        }

        for tree in self.trees.values():
            tree_info = {
                "tree_id": tree.component_id,
                "hostname": tree.hostname,
                "ip_address": tree.ip_address,
                "health_score": tree.health_score,
                "status": tree.status.name,
                "threat_count": tree.get_threat_count(),
                "branch_count": len(tree.branches),
            }
            scan_results["tree_details"].append(tree_info)

        self.total_scans += 1
        self.last_scan_time = scan_start

        return scan_results

    def get_forest_status(self) -> dict[str, Any]:
        """Get complete forest status"""
        return {
            "forest_name": self.forest_name,
            "total_trees": len(self.trees),
            "forest_health": self.get_total_health_score(),
            "total_threats": self.get_total_threat_count(),
            "threat_summary": self.threat_detector.get_threat_summary(),
            "map_summary": self.forest_map.get_forest_summary(),
            "total_scans": self.total_scans,
            "last_scan": self.last_scan_time.isoformat() if self.last_scan_time else None,
        }

    def get_visual_overview(self) -> str:
        """Get ASCII art overview of the forest"""
        lines = [
            "╔═══════════════════════════════════════════════════════════════╗",
            f"║  🌲 FOREST MANAGER: {self.forest_name}",
            "╠═══════════════════════════════════════════════════════════════╣",
            f"║  🌳 Trees: {len(self.trees)}",
            f"║  💚 Health: {self.get_total_health_score():.1f}%",
            f"║  ⚠️  Threats: {self.get_total_threat_count()}",
            f"║  🔍 Scans: {self.total_scans}",
            "╠═══════════════════════════════════════════════════════════════╣",
            "║  Trees:",
        ]

        for tree in sorted(self.trees.values(), key=lambda t: t.hostname):
            threat_marker = f"⚠️{tree.get_threat_count()}" if tree.has_threats() else "✓"
            lines.append(f"║    [{threat_marker}] 🌳 {tree.hostname} - {tree.health_score:.1f}%")

        lines.append("╚═══════════════════════════════════════════════════════════════╝")

        return "\n".join(lines)

    def __str__(self):
        return (
            f"🌲 ForestManager '{self.forest_name}': {len(self.trees)} trees, {self.get_total_threat_count()} threats"
        )
