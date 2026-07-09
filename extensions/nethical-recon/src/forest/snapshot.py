"""
Forest Snapshot and Diff
Captures forest state snapshots and compares them to detect changes
"""

import logging
import json
from datetime import datetime
from typing import Any
import hashlib


class ForestSnapshot:
    """Represents a snapshot of forest state at a point in time"""

    def __init__(self, forest_name: str, timestamp: datetime | None = None):
        """
        Initialize forest snapshot

        Args:
            forest_name: Name of the forest
            timestamp: Optional timestamp (defaults to now)
        """
        self.forest_name = forest_name
        self.timestamp = timestamp or datetime.now()
        self.snapshot_id = self._generate_id()

        # Snapshot data
        self.trees: dict[str, dict[str, Any]] = {}
        self.overall_health: float = 0.0
        self.total_threats: int = 0
        self.metadata: dict[str, Any] = {}

    def _generate_id(self) -> str:
        """Generate unique snapshot ID"""
        data = f"{self.forest_name}_{self.timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def add_tree(self, tree_id: str, tree_data: dict[str, Any]):
        """
        Add a tree to the snapshot

        Args:
            tree_id: Tree identifier
            tree_data: Tree data dictionary
        """
        self.trees[tree_id] = tree_data

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary"""
        return {
            "snapshot_id": self.snapshot_id,
            "forest_name": self.forest_name,
            "timestamp": self.timestamp.isoformat(),
            "overall_health": self.overall_health,
            "total_threats": self.total_threats,
            "total_trees": len(self.trees),
            "trees": self.trees,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int | None = None) -> str:
        """Convert snapshot to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ForestSnapshot":
        """Create snapshot from dictionary"""
        snapshot = cls(data["forest_name"], datetime.fromisoformat(data["timestamp"]))
        snapshot.snapshot_id = data["snapshot_id"]
        snapshot.overall_health = data["overall_health"]
        snapshot.total_threats = data["total_threats"]
        snapshot.trees = data["trees"]
        snapshot.metadata = data.get("metadata", {})
        return snapshot

    @classmethod
    def from_json(cls, json_str: str) -> "ForestSnapshot":
        """Create snapshot from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class ForestDiff:
    """Represents differences between two forest snapshots"""

    def __init__(self, old_snapshot: ForestSnapshot, new_snapshot: ForestSnapshot):
        """
        Initialize forest diff

        Args:
            old_snapshot: Older snapshot
            new_snapshot: Newer snapshot
        """
        self.old_snapshot = old_snapshot
        self.new_snapshot = new_snapshot
        self.timestamp = datetime.now()

        # Compute differences
        self.trees_added: list[str] = []
        self.trees_removed: list[str] = []
        self.trees_modified: dict[str, dict[str, Any]] = {}

        self.health_change: float = 0.0
        self.threat_change: int = 0

        self._compute_diff()

    def _compute_diff(self):
        """Compute differences between snapshots"""
        old_trees = set(self.old_snapshot.trees.keys())
        new_trees = set(self.new_snapshot.trees.keys())

        # Find added and removed trees
        self.trees_added = list(new_trees - old_trees)
        self.trees_removed = list(old_trees - new_trees)

        # Find modified trees
        common_trees = old_trees & new_trees
        for tree_id in common_trees:
            old_tree = self.old_snapshot.trees[tree_id]
            new_tree = self.new_snapshot.trees[tree_id]

            changes = self._compare_trees(old_tree, new_tree)
            if changes:
                self.trees_modified[tree_id] = changes

        # Compute overall changes
        self.health_change = self.new_snapshot.overall_health - self.old_snapshot.overall_health
        self.threat_change = self.new_snapshot.total_threats - self.old_snapshot.total_threats

    def _compare_trees(self, old_tree: dict[str, Any], new_tree: dict[str, Any]) -> dict[str, Any]:
        """Compare two tree states"""
        changes = {}

        # Check health score
        if old_tree.get("health_score") != new_tree.get("health_score"):
            changes["health_score"] = {"old": old_tree.get("health_score"), "new": new_tree.get("health_score")}

        # Check status
        if old_tree.get("status") != new_tree.get("status"):
            changes["status"] = {"old": old_tree.get("status"), "new": new_tree.get("status")}

        # Check threat count
        if old_tree.get("threat_count") != new_tree.get("threat_count"):
            changes["threat_count"] = {"old": old_tree.get("threat_count"), "new": new_tree.get("threat_count")}

        # Check branches
        old_branches = set(old_tree.get("branches", {}).keys())
        new_branches = set(new_tree.get("branches", {}).keys())

        if old_branches != new_branches:
            changes["branches"] = {
                "added": list(new_branches - old_branches),
                "removed": list(old_branches - new_branches),
            }

        return changes

    def has_changes(self) -> bool:
        """Check if there are any changes"""
        return bool(self.trees_added or self.trees_removed or self.trees_modified)

    def to_dict(self) -> dict[str, Any]:
        """Convert diff to dictionary"""
        return {
            "old_snapshot_id": self.old_snapshot.snapshot_id,
            "new_snapshot_id": self.new_snapshot.snapshot_id,
            "old_timestamp": self.old_snapshot.timestamp.isoformat(),
            "new_timestamp": self.new_snapshot.timestamp.isoformat(),
            "diff_timestamp": self.timestamp.isoformat(),
            "trees_added": self.trees_added,
            "trees_removed": self.trees_removed,
            "trees_modified": self.trees_modified,
            "health_change": self.health_change,
            "threat_change": self.threat_change,
            "has_changes": self.has_changes(),
        }

    def to_json(self, indent: int | None = None) -> str:
        """Convert diff to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    def get_summary(self) -> str:
        """Get human-readable summary of changes"""
        lines = [
            f"Forest Diff Summary",
            f"===================",
            f"From: {self.old_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"To:   {self.new_snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"Trees Added:    {len(self.trees_added)}",
            f"Trees Removed:  {len(self.trees_removed)}",
            f"Trees Modified: {len(self.trees_modified)}",
            f"",
            f"Health Change:  {self.health_change:+.1f}",
            f"Threat Change:  {self.threat_change:+d}",
        ]

        if self.trees_added:
            lines.append("\nAdded Trees:")
            for tree_id in self.trees_added:
                tree = self.new_snapshot.trees[tree_id]
                lines.append(f"  + {tree.get('hostname', tree_id)}")

        if self.trees_removed:
            lines.append("\nRemoved Trees:")
            for tree_id in self.trees_removed:
                tree = self.old_snapshot.trees[tree_id]
                lines.append(f"  - {tree.get('hostname', tree_id)}")

        if self.trees_modified:
            lines.append("\nModified Trees:")
            for tree_id, changes in self.trees_modified.items():
                tree = self.new_snapshot.trees[tree_id]
                lines.append(f"  ~ {tree.get('hostname', tree_id)}:")
                for key, value in changes.items():
                    if isinstance(value, dict) and "old" in value and "new" in value:
                        lines.append(f"    {key}: {value['old']} → {value['new']}")
                    else:
                        lines.append(f"    {key}: {value}")

        return "\n".join(lines)


class ForestSnapshotManager:
    """
    Manages forest snapshots and provides diff functionality
    """

    def __init__(self, max_snapshots: int = 100):
        """
        Initialize snapshot manager

        Args:
            max_snapshots: Maximum number of snapshots to keep
        """
        self.logger = logging.getLogger("nethical.snapshot_manager")
        self._initialize_logger()

        self.max_snapshots = max_snapshots
        self.snapshots: dict[str, ForestSnapshot] = {}
        self.snapshot_history: list[str] = []  # Ordered list of snapshot IDs

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [SnapshotManager] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def capture_snapshot(self, forest) -> ForestSnapshot:
        """
        Capture a snapshot of the current forest state

        Args:
            forest: Forest instance to snapshot

        Returns:
            ForestSnapshot instance
        """
        snapshot = ForestSnapshot(forest.forest_name)

        # Capture overall metrics
        snapshot.overall_health = forest.get_total_health_score()
        snapshot.total_threats = forest.get_total_threat_count()

        # Capture each tree
        for tree in getattr(forest, "trees", {}).values():
            tree_data = {
                "hostname": tree.hostname,
                "ip_address": tree.ip_address,
                "health_score": tree.health_score,
                "status": tree.status.name,
                "threat_count": tree.get_threat_count(),
                "branches": {
                    branch.component_id: {
                        "service_name": branch.service_name,
                        "port": branch.port,
                        "protocol": branch.protocol,
                    }
                    for branch in tree.branches.values()
                },
            }
            snapshot.add_tree(tree.component_id, tree_data)

        # Store snapshot
        self.snapshots[snapshot.snapshot_id] = snapshot
        self.snapshot_history.append(snapshot.snapshot_id)

        # Cleanup old snapshots
        if len(self.snapshot_history) > self.max_snapshots:
            old_id = self.snapshot_history.pop(0)
            del self.snapshots[old_id]

        self.logger.info(f"Captured snapshot {snapshot.snapshot_id} " f"({len(snapshot.trees)} trees)")

        return snapshot

    def get_snapshot(self, snapshot_id: str) -> ForestSnapshot | None:
        """Get a snapshot by ID"""
        return self.snapshots.get(snapshot_id)

    def get_latest_snapshot(self) -> ForestSnapshot | None:
        """Get the most recent snapshot"""
        if not self.snapshot_history:
            return None
        return self.snapshots[self.snapshot_history[-1]]

    def compare_snapshots(self, old_snapshot_id: str, new_snapshot_id: str) -> ForestDiff | None:
        """
        Compare two snapshots

        Args:
            old_snapshot_id: ID of older snapshot
            new_snapshot_id: ID of newer snapshot

        Returns:
            ForestDiff instance or None if snapshots not found
        """
        old_snapshot = self.get_snapshot(old_snapshot_id)
        new_snapshot = self.get_snapshot(new_snapshot_id)

        if not old_snapshot or not new_snapshot:
            self.logger.error("One or both snapshots not found")
            return None

        diff = ForestDiff(old_snapshot, new_snapshot)
        self.logger.info(
            f"Compared snapshots {old_snapshot_id} vs {new_snapshot_id}: "
            f"{len(diff.trees_added)} added, {len(diff.trees_removed)} removed, "
            f"{len(diff.trees_modified)} modified"
        )

        return diff

    def compare_with_latest(self, snapshot_id: str) -> ForestDiff | None:
        """Compare a snapshot with the latest snapshot"""
        latest = self.get_latest_snapshot()
        if not latest:
            return None
        return self.compare_snapshots(snapshot_id, latest.snapshot_id)

    def save_snapshot(self, snapshot_id: str, filename: str) -> bool:
        """
        Save a snapshot to file

        Args:
            snapshot_id: ID of snapshot to save
            filename: File path to save to

        Returns:
            bool: True if saved successfully
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            self.logger.error(f"Snapshot {snapshot_id} not found")
            return False

        try:
            with open(filename, "w") as f:
                f.write(snapshot.to_json(indent=2))
            self.logger.info(f"Saved snapshot {snapshot_id} to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save snapshot: {e}")
            return False

    def load_snapshot(self, filename: str) -> ForestSnapshot | None:
        """
        Load a snapshot from file

        Args:
            filename: File path to load from

        Returns:
            ForestSnapshot instance or None if failed
        """
        try:
            with open(filename, "r") as f:
                snapshot = ForestSnapshot.from_json(f.read())

            # Store the loaded snapshot
            self.snapshots[snapshot.snapshot_id] = snapshot
            if snapshot.snapshot_id not in self.snapshot_history:
                self.snapshot_history.append(snapshot.snapshot_id)

            self.logger.info(f"Loaded snapshot {snapshot.snapshot_id} from {filename}")
            return snapshot
        except Exception as e:
            self.logger.error(f"Failed to load snapshot: {e}")
            return None

    def get_statistics(self) -> dict[str, Any]:
        """Get snapshot statistics"""
        if not self.snapshots:
            return {"total_snapshots": 0, "oldest_snapshot": None, "newest_snapshot": None}

        oldest = self.snapshots[self.snapshot_history[0]]
        newest = self.snapshots[self.snapshot_history[-1]]

        return {
            "total_snapshots": len(self.snapshots),
            "max_snapshots": self.max_snapshots,
            "oldest_snapshot": {"id": oldest.snapshot_id, "timestamp": oldest.timestamp.isoformat()},
            "newest_snapshot": {"id": newest.snapshot_id, "timestamp": newest.timestamp.isoformat()},
        }
