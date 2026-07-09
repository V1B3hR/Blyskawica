"""
Purple Tracer - Evil AI Marker
🟣 For malicious AI agents and bots

Tag Format: EAI-[PATTERN]-[DATE]
Use Case: Evil AI, malicious bots, automated attacks
"""

import hashlib
from typing import Any

from ..base import BaseTracer, TracerType


class PurpleTracer(BaseTracer):
    """
    Purple tracer ammunition for marking evil AI and bots

    Used for detecting malicious AI agents, bots, and
    automated attack systems.
    """

    def __init__(self):
        super().__init__()
        self.tracer_type = TracerType.PURPLE
        self.color = "PURPLE"
        self.marker_prefix = "EAI"
        self.description = "Evil AI marker - for malicious bots and AI agents"

    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Create evil AI tag for target

        Args:
            target: Dictionary with target info (user_agent, behavior_pattern, etc.)

        Returns:
            Tag dictionary with AI/bot-specific fields
        """
        # Generate identifier from bot pattern or user agent
        if "user_agent" in target:
            identifier = hashlib.md5(target["user_agent"].encode()).hexdigest()[:8]
        elif "bot_signature" in target:
            identifier = target["bot_signature"][:8]
        elif "ip" in target:
            identifier = target["ip"].replace(".", "")
        else:
            identifier = hashlib.md5(str(target).encode()).hexdigest()[:8]

        tag_id = self.generate_tag_id(identifier)

        tag = {
            "tag_id": tag_id,
            "marker_type": self.tracer_type.value,
            "color": self.color,
            "target_type": "EVIL_AI",
            "threat_category": "AUTOMATED_THREAT",
            "severity": "HIGH",
            "recommended_action": "BLOCK_AND_MONITOR",
        }

        # Add AI/bot-specific fields
        if "user_agent" in target:
            tag["user_agent"] = target["user_agent"]
        if "bot_signature" in target:
            tag["bot_signature"] = target["bot_signature"]
        if "behavior_pattern" in target:
            tag["behavior_pattern"] = target["behavior_pattern"]
        if "request_rate" in target:
            tag["request_rate"] = target["request_rate"]
        if "bot_type" in target:
            tag["bot_type"] = target["bot_type"]

        return tag

    def get_usage_guidelines(self) -> str:
        """Get usage guidelines for this tracer"""
        return """
        PURPLE TRACER USAGE GUIDELINES:

        When to use:
        - Malicious bot traffic detected
        - Automated scraping/crawling attacks
        - AI-powered credential stuffing
        - DDoS bots and bot networks
        - Automated vulnerability scanners

        Required target fields:
        - user_agent OR bot_signature OR ip
        - Optional: behavior_pattern, request_rate, bot_type

        Severity: HIGH
        Action: Block and monitor for bot network patterns
        """
