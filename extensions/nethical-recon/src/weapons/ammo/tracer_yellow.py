"""
Yellow Tracer - Backdoor Marker
🟡 For backdoors and persistent access mechanisms

Tag Format: BKD-[PORT]-[CVE]-[DATE]
Use Case: Backdoors, reverse shells, unauthorized access points
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class YellowTracer(BaseTracer):
    """
    Yellow tracer ammunition for marking backdoors

    Used for tagging backdoors, reverse shells, and other
    persistent unauthorized access mechanisms.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.YELLOW
        self.color = "YELLOW"
        self.marker_prefix = "BKD"
        self.description = "Backdoor marker - for unauthorized access points"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create backdoor tag for target

        Args:
            target: Dictionary with target info (port, service, cve, etc.)

        Returns:
            Tag dictionary with backdoor-specific fields
        """
        # Generate identifier from port and CVE
        parts = []

        if "port" in target:
            parts.append(str(target["port"]))
        if "cve" in target:
            parts.append(target["cve"].replace("CVE-", ""))
        if "service" in target:
            parts.append(hashlib.md5(target["service"].encode()).hexdigest()[:4])

        if not parts:
            if "ip" in target:
                parts.append(target["ip"].replace(".", "")[:8])
            else:
                parts.append(hashlib.md5(str(target).encode()).hexdigest()[:8])

        identifier = "-".join(parts)
        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "BACKDOOR",
            "threat_category": "PERSISTENCE_MECHANISM",
            "severity": "CRITICAL",
            "recommended_action": "CLOSE_AND_PATCH",
        }

        # Add backdoor-specific fields
        if "port" in target:
            tag["port"] = target["port"]
        if "service" in target:
            tag["service"] = target["service"]
        if "cve" in target:
            tag["cve"] = target["cve"]
        if "backdoor_type" in target:
            tag["backdoor_type"] = target["backdoor_type"]
        if "persistence_method" in target:
            tag["persistence_method"] = target["persistence_method"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        YELLOW TRACER USAGE GUIDELINES:

        When to use:
        - Detected backdoors or reverse shells
        - Unauthorized remote access services
        - Exploited vulnerabilities with persistence
        - Hidden administrative accounts
        - Suspicious listening ports

        Required target fields:
        - port OR service OR cve (at least one)
        - Optional: backdoor_type, persistence_method, ip

        Severity: CRITICAL
        Action: Immediate closure and patching
        """
