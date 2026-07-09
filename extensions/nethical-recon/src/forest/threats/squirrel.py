"""
forest/threats/squirrel.py
Squirrel threat - represents lateral movement.

The squirrel:
- Jumps between branches (host hopping)
- Seeks hiding spots (vulnerable services)
- Leaves supplies (persistence mechanisms)
"""

from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType


class Squirrel(BaseThreat):
    """
    Squirrel threat - Lateral movement.

    Analogia: 🐿️ Wiewiórka - Skacze między gałęziami
    """

    def __init__(
        self,
        threat_id: str,
        name: str,
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a Squirrel threat.

        Args:
            threat_id: Unique identifier
            name: Lateral movement technique name
            severity: Severity level (default: MEDIUM)
            metadata: Additional metadata
        """
        super().__init__(threat_id, name, ThreatType.SQUIRREL, severity, metadata)

        # Squirrel-specific attributes
        self.movement_technique = metadata.get("technique", "Unknown") if metadata else "Unknown"
        self.credential_type = metadata.get("credential_type") if metadata else None

        # Track the squirrel's path through the forest
        self.visited_trees = []  # List of tree_ids the squirrel has visited
        self.current_tree = None
        self.movement_path = []  # Ordered list of (tree_id, timestamp)

        # Persistence locations
        self.hiding_spots = []  # Where the squirrel has left "supplies"

    def get_description(self) -> str:
        """Get description of the Squirrel threat"""
        return (
            f"Lateral movement detected: {self.name}. "
            f"This squirrel is hopping between branches using: {self.movement_technique}. "
            f"Visited {len(self.visited_trees)} trees so far. "
            f"{'Using ' + self.credential_type + ' credentials.' if self.credential_type else ''}"
        )

    def get_behavior_pattern(self) -> str:
        """Get characteristic behavior pattern"""
        behaviors = [f"Technique: {self.movement_technique}", f"Trees visited: {len(self.visited_trees)}"]

        if self.credential_type:
            behaviors.append(f"Credentials: {self.credential_type}")
        if self.hiding_spots:
            behaviors.append(f"Hiding spots: {len(self.hiding_spots)}")
        if len(self.visited_trees) > 3:
            behaviors.append("⚠️ Advanced lateral movement!")

        return " | ".join(behaviors)

    def add_movement(self, from_tree_id: str, to_tree_id: str):
        """
        Record a movement from one tree to another.

        Args:
            from_tree_id: Source tree ID
            to_tree_id: Destination tree ID
        """
        from datetime import datetime

        if to_tree_id not in self.visited_trees:
            self.visited_trees.append(to_tree_id)

        self.movement_path.append({"from": from_tree_id, "to": to_tree_id, "timestamp": datetime.now().isoformat()})

        self.current_tree = to_tree_id
        self.add_indicator(f"{from_tree_id} -> {to_tree_id}", "movement_path")

        # Escalate severity if extensive movement detected
        if len(self.visited_trees) > 3 and self.severity == ThreatSeverity.MEDIUM:
            self.severity = ThreatSeverity.HIGH

    def add_hiding_spot(self, tree_id: str, location: str):
        """
        Record a persistence mechanism (hiding spot).

        Args:
            tree_id: Tree where persistence was established
            location: Description of the hiding spot
        """
        spot = {"tree_id": tree_id, "location": location}
        self.hiding_spots.append(spot)
        self.add_indicator(f"{tree_id}:{location}", "persistence")

    def get_movement_path(self) -> list[dict[str, Any]]:
        """Get the complete movement path"""
        return self.movement_path

    def __str__(self):
        base_str = super().__str__()
        if self.visited_trees:
            base_str += f" [Visited: {len(self.visited_trees)} trees]"
        return base_str
