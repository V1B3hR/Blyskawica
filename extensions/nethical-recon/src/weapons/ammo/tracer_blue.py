"""
Blue Tracer - Hidden Service Marker
🔵 For hidden and undocumented services

Tag Format: HID-[SERVICE]-[RISK]-[DATE]
Use Case: Hidden services, shadow IT, undocumented endpoints
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class BlueTracer(BaseTracer):
    """
    Blue tracer ammunition for marking hidden services

    Used for tagging undocumented services, shadow IT,
    and hidden endpoints that may pose security risks.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.BLUE
        self.color = "BLUE"
        self.marker_prefix = "HID"
        self.description = "Hidden service marker - for undocumented endpoints"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create hidden service tag for target

        Args:
            target: Dictionary with target info (service, port, hostname, etc.)

        Returns:
            Tag dictionary with hidden service-specific fields
        """
        # Generate identifier from service info
        if "service" in target:
            service_id = hashlib.md5(target["service"].encode()).hexdigest()[:8]
        elif "hostname" in target:
            service_id = hashlib.md5(target["hostname"].encode()).hexdigest()[:8]
        elif "port" in target:
            service_id = f"port{target['port']}"
        else:
            service_id = hashlib.md5(str(target).encode()).hexdigest()[:8]

        # Determine risk level
        risk_score = target.get("risk_score", 5)
        risk_level = "HIGH" if risk_score >= 7 else "MEDIUM" if risk_score >= 4 else "LOW"

        identifier = f"{service_id}-{risk_level}"
        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "HIDDEN_SERVICE",
            "threat_category": "SHADOW_IT",
            "severity": risk_level,
            "recommended_action": "DOCUMENT_AND_ASSESS",
        }

        # Add hidden service-specific fields
        if "service" in target:
            tag["service_name"] = target["service"]
        if "port" in target:
            tag["port"] = target["port"]
        if "hostname" in target:
            tag["hostname"] = target["hostname"]
        if "discovery_method" in target:
            tag["discovery_method"] = target["discovery_method"]
        if "documented" in target:
            tag["documented"] = target["documented"]

        tag["risk_score"] = risk_score

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        BLUE TRACER USAGE GUIDELINES:

        When to use:
        - Undocumented services discovered
        - Shadow IT infrastructure
        - Hidden API endpoints
        - Unauthorized web services
        - Rogue devices on network

        Required target fields:
        - service OR hostname OR port (at least one)
        - risk_score (recommended)
        - Optional: discovery_method, documented

        Severity: VARIABLE (based on risk_score)
        Action: Document and assess security posture
        """
