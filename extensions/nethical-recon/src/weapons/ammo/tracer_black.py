"""
Black Tracer - Crow Marker
🖤 For crows (malware) in the canopy

Tag Format: CRW-[TYPE]-[TREE]-[DATE]
Use Case: Malware detected in forest canopy, crows in trees
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class BlackTracer(BaseTracer):
    """
    Black tracer ammunition for marking crows (canopy threats)

    Used specifically for marking threats detected in the
    forest canopy - malware hiding in tree crowns.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.BLACK
        self.color = "BLACK"
        self.marker_prefix = "CRW"
        self.description = "Crow marker - for malware in forest canopy"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create crow tag for target

        Args:
            target: Dictionary with target info (must include forest location)

        Returns:
            Tag dictionary with crow/canopy-specific fields
        """
        # Get crow type or threat type
        crow_type = target.get("crow_type", target.get("threat_type", "malware"))

        # Get tree/forest location
        forest_location = target.get("forest_location", {})
        tree_id = forest_location.get("tree", "unknown")

        # Generate identifier
        crow_id = hashlib.md5(crow_type.encode()).hexdigest()[:4]
        tree_id_short = tree_id[:8] if len(tree_id) > 8 else tree_id
        identifier = f"{crow_id}-{tree_id_short}"

        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "CROW",
            "threat_category": "CANOPY_THREAT",
            "severity": "HIGH",
            "recommended_action": "HUNT_AND_ELIMINATE",
        }

        # Add crow-specific fields
        tag["crow_type"] = crow_type
        tag["forest_location"] = forest_location

        if "tree" in forest_location:
            tag["tree_id"] = forest_location["tree"]
        if "branch" in forest_location:
            tag["branch_id"] = forest_location["branch"]
        if "crown" in forest_location:
            tag["crown_position"] = forest_location["crown"]

        if "behavior" in target:
            tag["crow_behavior"] = target["behavior"]
        if "patience_level" in target:
            tag["patience_level"] = target["patience_level"]
        if "hiding_method" in target:
            tag["hiding_method"] = target["hiding_method"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        BLACK TRACER USAGE GUIDELINES:

        When to use:
        - Malware detected in forest tree crowns
        - Patient, waiting threats (crow behavior)
        - Threats hiding in the canopy
        - Obfuscated malware in process trees
        - APT-style persistent threats

        Required target fields:
        - crow_type OR threat_type
        - forest_location (with tree, branch, crown info)
        - Optional: behavior, patience_level, hiding_method

        Severity: HIGH
        Action: Hunt and eliminate the crow from the canopy

        Note: Use this for forest-specific threat tracking
        """
