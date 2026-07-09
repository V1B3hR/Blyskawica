"""
White Tracer - Unknown Threat Marker
⚪ For unknown or unclassified threats

Tag Format: UNK-[ID]-[DATE]
Use Case: Unknown threats, anomalies requiring investigation
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class WhiteTracer(BaseTracer):
    """
    White tracer ammunition for marking unknown threats

    Used for tagging anomalies and threats that don't fit
    other categories or require further investigation.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.WHITE
        self.color = "WHITE"
        self.marker_prefix = "UNK"
        self.description = "Unknown threat marker - for anomalies requiring investigation"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create unknown threat tag for target

        Args:
            target: Dictionary with target info (any available data)

        Returns:
            Tag dictionary with generic threat fields
        """
        # Generate identifier from available data
        if "anomaly_id" in target:
            identifier = target["anomaly_id"][:8]
        elif "ip" in target:
            identifier = target["ip"].replace(".", "")
        elif "identifier" in target:
            identifier = str(target["identifier"])[:8]
        else:
            identifier = hashlib.md5(str(target).encode()).hexdigest()[:8]

        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "UNKNOWN",
            "threat_category": "ANOMALY",
            "severity": "MEDIUM",
            "recommended_action": "INVESTIGATE_AND_CLASSIFY",
        }

        # Add any available fields
        if "ip" in target:
            tag["ip"] = target["ip"]
        if "anomaly_type" in target:
            tag["anomaly_type"] = target["anomaly_type"]
        if "anomaly_score" in target:
            tag["anomaly_score"] = target["anomaly_score"]
        if "detection_method" in target:
            tag["detection_method"] = target["detection_method"]
        if "description" in target:
            tag["description"] = target["description"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        WHITE TRACER USAGE GUIDELINES:

        When to use:
        - Anomalies that don't fit other categories
        - Unknown threat patterns
        - Events requiring further investigation
        - First-time observations
        - Suspicious but unconfirmed activity

        Required target fields:
        - Any available identifying information
        - Optional: anomaly_type, anomaly_score, detection_method

        Severity: MEDIUM (default)
        Action: Investigate and reclassify with appropriate colored tracer
        """
