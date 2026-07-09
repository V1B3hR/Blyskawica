"""
Red Tracer - Malware Marker
🔴 For confirmed malicious files and processes

Tag Format: MAL-[HASH]-[DATE]
Use Case: Malware, trojans, viruses, ransomware
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class RedTracer(BaseTracer):
    """
    Red tracer ammunition for marking malware

    Used when malicious files or processes are detected.
    Creates permanent stains with malware-specific metadata.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.RED
        self.color = "RED"
        self.marker_prefix = "MAL"
        self.description = "Malware marker - for confirmed malicious files"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create malware tag for target

        Args:
            target: Dictionary with target info (must include 'file_hash' or 'process_name')

        Returns:
            Tag dictionary with malware-specific fields
        """
        # Generate identifier from hash or process name
        if "file_hash" in target:
            identifier = target["file_hash"][:8]
        elif "process_name" in target:
            identifier = hashlib.md5(target["process_name"].encode()).hexdigest()[:8]
        elif "ip" in target:
            identifier = target["ip"].replace(".", "")
        else:
            identifier = hashlib.md5(str(target).encode()).hexdigest()[:8]

        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "MALWARE",
            "threat_category": "MALICIOUS_CODE",
            "severity": "CRITICAL",
            "recommended_action": "QUARANTINE_AND_ANALYZE",
        }

        # Add malware-specific fields
        if "file_hash" in target:
            tag["file_hash"] = target["file_hash"]
        if "process_name" in target:
            tag["process_name"] = target["process_name"]
        if "file_path" in target:
            tag["file_path"] = target["file_path"]
        if "malware_family" in target:
            tag["malware_family"] = target["malware_family"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        RED TRACER USAGE GUIDELINES:

        When to use:
        - Confirmed malware detected by AV/EDR
        - Files with known malicious hashes
        - Processes exhibiting malicious behavior
        - Ransomware, trojans, worms, viruses

        Required target fields:
        - file_hash (preferred) OR process_name
        - Optional: file_path, malware_family

        Severity: CRITICAL
        Action: Immediate quarantine and analysis
        """
