"""
forest/trees/forest_map.py
ForestMap class - maps and manages the entire infrastructure.

The forest map provides:
- Complete infrastructure topology
- Tree relationships and dependencies
- Network-wide threat visualization
- Infrastructure health dashboard
"""

from datetime import datetime
from typing import Any


class ForestMap:
    """
    Maps and manages the entire infrastructure forest.

    Analogia: 🗺️ Mapa Lasu - Complete view of the entire infrastructure
    """

    def __init__(self, map_name: str = "Infrastructure Map"):
        """
        Initialize the forest map.

        Args:
            map_name: Name of this forest map
        """
        self.map_name = map_name
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

        # Trees indexed by various keys for fast lookup
        self.trees = {}  # tree_id -> Tree
        self.trees_by_hostname = {}  # hostname -> Tree
        self.trees_by_ip = {}  # ip_address -> Tree

        # Network topology
        self.network_segments = {}  # segment_name -> list of tree_ids
        self.tree_relationships = {}  # tree_id -> list of connected tree_ids

        # Statistics
        self.total_trees = 0
        self.total_branches = 0
        self.total_leaves = 0
        self.total_threats = 0

    def add_tree(self, tree):
        """
        Add a tree to the forest map.

        Args:
            tree: Tree object to add
        """
        self.trees[tree.component_id] = tree
        self.trees_by_hostname[tree.hostname] = tree
        self.trees_by_ip[tree.ip_address] = tree
        self.total_trees += 1
        self.last_updated = datetime.now()

    def remove_tree(self, tree_id: str):
        """Remove a tree from the forest map"""
        if tree_id in self.trees:
            tree = self.trees[tree_id]
            del self.trees[tree_id]
            del self.trees_by_hostname[tree.hostname]
            del self.trees_by_ip[tree.ip_address]
            self.total_trees -= 1
            self.last_updated = datetime.now()

    def get_tree(self, tree_id: str):
        """Get a tree by ID"""
        return self.trees.get(tree_id)

    def get_tree_by_hostname(self, hostname: str):
        """Get a tree by hostname"""
        return self.trees_by_hostname.get(hostname)

    def get_tree_by_ip(self, ip_address: str):
        """Get a tree by IP address"""
        return self.trees_by_ip.get(ip_address)

    def get_all_trees(self) -> list:
        """Get all trees in the forest"""
        return list(self.trees.values())

    def get_threatened_trees(self) -> list:
        """Get all trees with threats"""
        return [tree for tree in self.trees.values() if tree.has_threats()]

    def add_network_segment(self, segment_name: str, tree_ids: list[str]):
        """
        Add a network segment grouping.

        Args:
            segment_name: Name of the network segment (e.g., "DMZ", "Internal")
            tree_ids: List of tree IDs in this segment
        """
        self.network_segments[segment_name] = tree_ids
        self.last_updated = datetime.now()

    def get_network_segment(self, segment_name: str) -> list:
        """Get all trees in a network segment"""
        tree_ids = self.network_segments.get(segment_name, [])
        return [self.trees[tid] for tid in tree_ids if tid in self.trees]

    def add_tree_relationship(self, tree_id_1: str, tree_id_2: str):
        """
        Add a relationship/connection between two trees.

        Args:
            tree_id_1: First tree ID
            tree_id_2: Second tree ID
        """
        if tree_id_1 not in self.tree_relationships:
            self.tree_relationships[tree_id_1] = []
        if tree_id_2 not in self.tree_relationships:
            self.tree_relationships[tree_id_2] = []

        if tree_id_2 not in self.tree_relationships[tree_id_1]:
            self.tree_relationships[tree_id_1].append(tree_id_2)
        if tree_id_1 not in self.tree_relationships[tree_id_2]:
            self.tree_relationships[tree_id_2].append(tree_id_1)

        self.last_updated = datetime.now()

    def get_connected_trees(self, tree_id: str) -> list:
        """Get all trees connected to a specific tree"""
        connected_ids = self.tree_relationships.get(tree_id, [])
        return [self.trees[tid] for tid in connected_ids if tid in self.trees]

    def update_statistics(self):
        """Update forest-wide statistics"""
        self.total_trees = len(self.trees)
        self.total_branches = sum(len(tree.branches) for tree in self.trees.values())
        self.total_leaves = sum(
            sum(len(branch.leaves) for branch in tree.branches.values()) for tree in self.trees.values()
        )
        self.total_threats = sum(tree.get_threat_count() for tree in self.trees.values())
        self.last_updated = datetime.now()

    def get_forest_health(self) -> float:
        """Get overall forest health score"""
        if not self.trees:
            return 100.0

        total_health = sum(tree.health_score for tree in self.trees.values())
        return total_health / len(self.trees)

    def get_forest_summary(self) -> dict[str, Any]:
        """Get a summary of the entire forest"""
        self.update_statistics()

        return {
            "map_name": self.map_name,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "total_trees": self.total_trees,
            "total_branches": self.total_branches,
            "total_leaves": self.total_leaves,
            "total_threats": self.total_threats,
            "threatened_trees": len(self.get_threatened_trees()),
            "average_health": self.get_forest_health(),
            "network_segments": len(self.network_segments),
        }

    def get_threat_map(self) -> dict[str, Any]:
        """Get a map of all threats in the forest"""
        threat_map = {}

        for tree in self.trees.values():
            if tree.has_threats():
                tree_threats = {
                    "hostname": tree.hostname,
                    "ip_address": tree.ip_address,
                    "direct_threats": tree.get_threat_count(),
                    "threatened_branches": len(tree.get_branches_with_threats()),
                    "health_score": tree.health_score,
                }
                threat_map[tree.component_id] = tree_threats

        return threat_map

    def get_visual_map(self) -> str:
        """Get ASCII art visualization of the forest"""
        lines = [
            "═══════════════════════════════════════════════════════",
            f"  🗺️  {self.map_name}",
            "═══════════════════════════════════════════════════════",
            "",
            f"🌳 Total Trees: {self.total_trees}",
            f"🌿 Total Branches: {self.total_branches}",
            f"🍃 Total Leaves: {self.total_leaves}",
            f"⚠️  Total Threats: {self.total_threats}",
            f"💚 Average Health: {self.get_forest_health():.1f}%",
            "",
            "─────────────────────────────────────────────────────",
            "Trees in Forest:",
            "",
        ]

        for tree in sorted(self.trees.values(), key=lambda t: t.hostname):
            threat_marker = f"⚠️{tree.get_threat_count()}" if tree.has_threats() else "✓"
            lines.append(
                f"  [{threat_marker}] 🌳 {tree.hostname} ({tree.ip_address}) - Health: {tree.health_score:.1f}%"
            )

        lines.append("")
        lines.append("═══════════════════════════════════════════════════════")

        return "\n".join(lines)

    def __str__(self):
        return f"🗺️ ForestMap '{self.map_name}': {self.total_trees} trees, {self.total_threats} threats"
