"""
Brown Tracer - Squirrel Marker
🤎 For squirrels (lateral movement)

Tag Format: SQR-[PATH]-[DATE]
Use Case: Lateral movement, host hopping, privilege escalation paths
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class BrownTracer(BaseTracer):
    """
    Brown tracer ammunition for marking squirrels (lateral movement)

    Used for tracking lateral movement between hosts, like a
    squirrel jumping between tree branches in the forest.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.BROWN
        self.color = "BROWN"
        self.marker_prefix = "SQR"
        self.description = "Squirrel marker - for lateral movement tracking"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create squirrel tag for target

        Args:
            target: Dictionary with target info (movement path, source, destination)

        Returns:
            Tag dictionary with lateral movement-specific fields
        """
        # Generate identifier from movement path
        if "movement_path" in target:
            path_hash = hashlib.md5(str(target["movement_path"]).encode()).hexdigest()[:8]
            identifier = f"path-{path_hash}"
        elif "source_host" in target and "dest_host" in target:
            src = target["source_host"].replace(".", "")[:4]
            dst = target["dest_host"].replace(".", "")[:4]
            identifier = f"{src}-to-{dst}"
        elif "forest_location" in target:
            forest_loc = target["forest_location"]
            tree_src = forest_loc.get("source_tree", "unk")[:4]
            tree_dst = forest_loc.get("dest_tree", "unk")[:4]
            identifier = f"{tree_src}-{tree_dst}"
        else:
            identifier = hashlib.md5(str(target).encode()).hexdigest()[:8]

        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "SQUIRREL",
            "threat_category": "LATERAL_MOVEMENT",
            "severity": "HIGH",
            "recommended_action": "ISOLATE_AND_CONTAIN",
        }

        # Add squirrel/lateral movement-specific fields
        if "movement_path" in target:
            tag["movement_path"] = target["movement_path"]
        if "source_host" in target:
            tag["source_host"] = target["source_host"]
        if "dest_host" in target:
            tag["dest_host"] = target["dest_host"]
        if "method" in target:
            tag["movement_method"] = target["method"]
        if "protocol" in target:
            tag["protocol"] = target["protocol"]
        if "credentials_used" in target:
            tag["credentials_used"] = target["credentials_used"]

        # Forest-specific location
        if "forest_location" in target:
            tag["forest_location"] = target["forest_location"]

        # Squirrel behavior
        if "jump_count" in target:
            tag["jump_count"] = target["jump_count"]
        if "persistence_method" in target:
            tag["persistence_method"] = target["persistence_method"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        BROWN TRACER USAGE GUIDELINES:

        When to use:
        - Lateral movement detected between hosts
        - Privilege escalation attempts
        - Pass-the-hash attacks
        - Remote execution (PSExec, WMI, etc.)
        - Network traversal patterns
        - "Squirrel jumping" between forest trees

        Required target fields:
        - movement_path OR (source_host AND dest_host)
        - Optional: method, protocol, credentials_used
        - Forest: source_tree, dest_tree in forest_location

        Severity: HIGH
        Action: Isolate affected hosts and contain the spread

        Note: Track the squirrel's path to identify attack progression
        """
