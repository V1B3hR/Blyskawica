"""
Targeting System
Target acquisition and validation for the Silent Marker

Provides targeting intelligence and target validation
before firing the marker gun.
"""

import datetime
from dataclasses import dataclass
from typing import Any


@dataclass
class Target:
    """Represents a target for marking"""

    def __init__(self, target_data: dict[str, Any]):
        """Initialize target from data dictionary"""
        self.data = target_data
        self.target_id = target_data.get("target_id", self._generate_id())
        self.ip = target_data.get("ip")
        self.hostname = target_data.get("hostname")
        self.threat_score = target_data.get("threat_score", 0.0)
        self.confidence = target_data.get("confidence", 0.0)
        self.threat_type = target_data.get("threat_type", "UNKNOWN")
        self.detected_by = target_data.get("detected_by", "UNKNOWN")
        self.forest_location = target_data.get("forest_location", {})
        self.acquisition_time = datetime.datetime.now()
        self.validated = False

    def _generate_id(self) -> str:
        """
        Generate unique target ID

        Note: Uses MD5 for simplicity. For production, consider using
        uuid.uuid4() for better uniqueness guarantees.
        """
        import hashlib

        timestamp = str(datetime.datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        """Convert target to dictionary"""
        return {
            "target_id": self.target_id,
            "ip": self.ip,
            "hostname": self.hostname,
            "threat_score": self.threat_score,
            "confidence": self.confidence,
            "threat_type": self.threat_type,
            "detected_by": self.detected_by,
            "forest_location": self.forest_location,
            "acquisition_time": self.acquisition_time.isoformat(),
            "validated": self.validated,
            "additional_data": self.data,
        }


class TargetingSystem:
    """
    Target acquisition and validation system

    Manages target identification, validation, and prioritization
    for the marker gun system.
    """

    def __init__(self):
        self.active_targets: list[Target] = []
        self.locked_target: Target | None = None
        self.target_history: list[Target] = []
        self.validation_rules = {
            "min_threat_score": 3.0,
            "min_confidence": 0.5,
            "require_ip_or_hostname": True,
            "require_threat_type": False,
        }

    def acquire_target(self, target_data: dict[str, Any]) -> Target:
        """
        Acquire a new target

        Args:
            target_data: Dictionary with target information

        Returns:
            Target object
        """
        target = Target(target_data)
        self.active_targets.append(target)
        return target

    def validate_target(self, target: Target) -> dict[str, Any]:
        """
        Validate if target meets engagement criteria

        Args:
            target: Target to validate

        Returns:
            Validation result dictionary
        """
        validation_result = {"valid": True, "reasons": [], "warnings": []}

        # Check threat score
        if target.threat_score < self.validation_rules["min_threat_score"]:
            validation_result["valid"] = False
            validation_result["reasons"].append(
                f"Threat score ({target.threat_score}) below minimum ({self.validation_rules['min_threat_score']})"
            )

        # Check confidence
        if target.confidence < self.validation_rules["min_confidence"]:
            validation_result["warnings"].append(f"Low confidence ({target.confidence}), recommend caution")

        # Check IP or hostname
        if self.validation_rules["require_ip_or_hostname"]:
            if not target.ip and not target.hostname:
                validation_result["valid"] = False
                validation_result["reasons"].append("No IP address or hostname provided")

        # Check threat type
        if self.validation_rules["require_threat_type"]:
            if target.threat_type == "UNKNOWN":
                validation_result["warnings"].append("Threat type is unknown")

        # Mark as validated if valid
        if validation_result["valid"]:
            target.validated = True

        return validation_result

    def lock_target(self, target: Target) -> bool:
        """
        Lock onto a target for firing

        Args:
            target: Target to lock

        Returns:
            True if successfully locked
        """
        # Validate target first
        validation = self.validate_target(target)

        if not validation["valid"]:
            return False

        self.locked_target = target
        return True

    def unlock_target(self):
        """Release current target lock"""
        if self.locked_target:
            self.target_history.append(self.locked_target)
        self.locked_target = None

    def get_locked_target(self) -> Target | None:
        """Get currently locked target"""
        return self.locked_target

    def prioritize_targets(self) -> list[Target]:
        """
        Prioritize active targets by threat score and confidence

        Returns:
            List of targets sorted by priority (highest first)
        """

        def priority_score(target: Target) -> float:
            return target.threat_score * target.confidence

        return sorted(self.active_targets, key=priority_score, reverse=True)

    def get_top_target(self) -> Target | None:
        """Get highest priority target"""
        prioritized = self.prioritize_targets()
        return prioritized[0] if prioritized else None

    def remove_target(self, target_id: str):
        """Remove target from active targets"""
        self.active_targets = [t for t in self.active_targets if t.target_id != target_id]
        if self.locked_target and self.locked_target.target_id == target_id:
            self.unlock_target()

    def clear_targets(self):
        """Clear all active targets"""
        self.target_history.extend(self.active_targets)
        self.active_targets = []
        self.locked_target = None

    def get_target_count(self) -> int:
        """Get number of active targets"""
        return len(self.active_targets)

    def get_statistics(self) -> dict[str, Any]:
        """Get targeting system statistics"""
        return {
            "active_targets": len(self.active_targets),
            "locked_target": self.locked_target.target_id if self.locked_target else None,
            "total_acquired": len(self.active_targets) + len(self.target_history),
            "validation_rules": self.validation_rules,
        }

    def set_validation_rule(self, rule_name: str, value: Any):
        """Update validation rule"""
        if rule_name in self.validation_rules:
            self.validation_rules[rule_name] = value

    def recommend_ammo(self, target: Target) -> str:
        """
        Recommend tracer color based on target type

        Args:
            target: Target to analyze

        Returns:
            Recommended tracer color
        """
        threat_type = target.threat_type.upper()

        if "MALWARE" in threat_type or "VIRUS" in threat_type or "TROJAN" in threat_type:
            return "RED"
        elif "BOT" in threat_type or "AI" in threat_type:
            return "PURPLE"
        elif "IP" in threat_type or "SOURCE" in threat_type:
            return "ORANGE"
        elif "BACKDOOR" in threat_type or "SHELL" in threat_type:
            return "YELLOW"
        elif "HIDDEN" in threat_type or "SHADOW" in threat_type:
            return "BLUE"
        elif "CROW" in threat_type or "CANOPY" in threat_type:
            return "BLACK"
        elif "SQUIRREL" in threat_type or "LATERAL" in threat_type:
            return "BROWN"
        else:
            return "WHITE"

    def recommend_weapon_mode(self, target: Target) -> str:
        """
        Recommend weapon mode based on target characteristics

        Args:
            target: Target to analyze

        Returns:
            Recommended weapon mode
        """
        # High priority/confidence -> Electric
        if target.threat_score >= 8.0 and target.confidence >= 0.85:
            return "ELECTRIC"
        # Medium priority -> CO2 Silent
        elif target.threat_score >= 5.0:
            return "CO2_SILENT"
        # Low priority/reconnaissance -> Pneumatic
        else:
            return "PNEUMATIC"
