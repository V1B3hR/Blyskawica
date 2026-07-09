"""
Orange Tracer - Suspicious IP Marker
🟠 For suspicious IP addresses and sources

Tag Format: SIP-[IP]-[SCORE]-[DATE]
Use Case: Suspicious IPs, known bad actors, anomalous sources
"""

from typing import Any

from ..base import BaseTracer, TracerType


class OrangeTracer(BaseTracer):
    """
    Orange tracer ammunition for marking suspicious IPs

    Used for tagging IP addresses that exhibit suspicious
    behavior or match threat intelligence feeds.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.ORANGE
        self.color = "ORANGE"
        self.marker_prefix = "SIP"
        self.description = "Suspicious IP marker - for anomalous sources"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create suspicious IP tag for target

        Args:
            target: Dictionary with target info (must include 'ip')

        Returns:
            Tag dictionary with IP-specific fields
        """
        # Get IP address
        ip = target.get("ip", "UNKNOWN")

        # Get threat score
        threat_score = target.get("threat_score", 0)
        score_label = "HIGH" if threat_score >= 7 else "MEDIUM" if threat_score >= 4 else "LOW"

        # Generate tag ID
        identifier = f"{ip.replace('.', '')}-{score_label}"
        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "SUSPICIOUS_IP",
            "threat_category": "NETWORK_THREAT",
            "severity": score_label,
            "recommended_action": "MONITOR_AND_RATE_LIMIT",
        }

        # Add IP-specific fields
        tag["ip_address"] = ip
        tag["threat_score"] = threat_score

        if "country" in target:
            tag["country"] = target["country"]
        if "asn" in target:
            tag["asn"] = target["asn"]
        if "reputation" in target:
            tag["reputation"] = target["reputation"]
        if "attack_types" in target:
            tag["attack_types"] = target["attack_types"]
        if "first_seen" in target:
            tag["first_seen"] = target["first_seen"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        ORANGE TRACER USAGE GUIDELINES:

        When to use:
        - IPs with suspicious behavior patterns
        - Sources matching threat intelligence feeds
        - Repeated failed authentication attempts
        - Port scanning sources
        - Anomalous traffic patterns

        Required target fields:
        - ip (required)
        - threat_score (recommended)
        - Optional: country, asn, reputation, attack_types

        Severity: VARIABLE (based on threat_score)
        Action: Monitor and apply rate limiting
        """
