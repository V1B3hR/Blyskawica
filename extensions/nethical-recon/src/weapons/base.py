"""
Base classes for weapon system components
"""

import datetime
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class TracerType(Enum):
    """Tracer ammunition types with color coding"""

    RED = "MALWARE"  # 🔴 Malware
    PURPLE = "EVIL_AI"  # 🟣 Evil AI/bots
    ORANGE = "SUSPICIOUS_IP"  # 🟠 Suspicious IPs
    YELLOW = "BACKDOOR"  # 🟡 Backdoors
    BLUE = "HIDDEN_SERVICE"  # 🔵 Hidden services
    WHITE = "UNKNOWN"  # ⚪ Unknown threats
    BLACK = "CROW"  # 🖤 Crows (canopy threats)
    BROWN = "SQUIRREL"  # 🤎 Squirrels (lateral movement)


class WeaponMode(Enum):
    """Weapon firing modes"""

    PNEUMATIC = "PNEUMATIC"  # 💨 Whisper (0 dB)
    CO2_SILENT = "CO2_SILENT"  # 🧊 Silent (10 dB)
    ELECTRIC = "ELECTRIC"  # ⚡ Lightning (20 dB)


class BaseWeaponMode(ABC):
    """Abstract base class for weapon modes"""

    def __init__(self):
        self.mode_name: str = ""
        self.noise_level: int = 0  # dB
        self.power_level: int = 0  # 1-10
        self.effective_range: int = 0  # meters
        self.description: str = ""

    @abstractmethod
    def fire(self, target: dict[str, Any], ammo: "BaseTracer") -> dict[str, Any]:
        """Fire weapon at target with specified ammo"""
        pass

    def get_info(self) -> dict[str, Any]:
        """Get weapon mode information"""
        return {
            "mode": self.mode_name,
            "noise_level_db": self.noise_level,
            "power_level": self.power_level,
            "effective_range_m": self.effective_range,
            "description": self.description,
        }


class BaseTracer(ABC):
    """Abstract base class for tracer ammunition"""

    def __init__(self):
        self.tracer_type: TracerType = None
        self.color: str = ""
        self.marker_prefix: str = ""
        self.description: str = ""
        self.use_count: int = 0

    @abstractmethod
    def create_tag(self, target: dict[str, Any]) -> dict[str, Any]:
        """Create a tag/stain for the target"""
        pass

    def get_info(self) -> dict[str, Any]:
        """Get tracer information"""
        return {
            "type": self.tracer_type.value if self.tracer_type else "UNKNOWN",
            "color": self.color,
            "prefix": self.marker_prefix,
            "description": self.description,
            "uses": self.use_count,
        }

    def increment_use(self):
        """Increment use counter"""
        self.use_count += 1

    def generate_tag_id(self, identifier: str) -> str:
        """
        Generate unique tag ID

        Note: Tag IDs use MD5 hashes in tracers for identifier generation.
        For production, consider using SHA256 or uuid for better collision resistance.
        """
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        return f"{self.marker_prefix}-{identifier}-{date_str}"


class Stain:
    """Represents a permanent stain/tag on a target"""

    def __init__(
        self,
        tag_id: str,
        marker_type: str,
        color: str,
        target: dict[str, Any],
        weapon_mode: str,
        threat_score: float,
        confidence: float,
    ):
        self.tag_id = tag_id
        self.marker_type = marker_type
        self.color = color
        self.timestamp_first_seen = datetime.datetime.now().isoformat()
        self.timestamp_last_seen = self.timestamp_first_seen
        self.hit_count = 1
        self.weapon_used = weapon_mode
        self.target = target
        self.threat_score = threat_score
        self.confidence = confidence
        self.status = "ACTIVE_THREAT"
        self.evidence = []
        self.linked_tags = []
        self.hunter_notes = ""
        self.detected_by = ""
        self.forest_location = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert stain to dictionary"""
        return {
            "tag_id": self.tag_id,
            "marker_type": self.marker_type,
            "color": self.color,
            "timestamp_first_seen": self.timestamp_first_seen,
            "timestamp_last_seen": self.timestamp_last_seen,
            "hit_count": self.hit_count,
            "weapon_used": self.weapon_used,
            "target": self.target,
            "forest_location": self.forest_location,
            "stain": {
                "threat_score": self.threat_score,
                "confidence": self.confidence,
                "evidence": self.evidence,
                "linked_tags": self.linked_tags,
            },
            "hunter_notes": self.hunter_notes,
            "detected_by": self.detected_by,
            "status": self.status,
        }

    def update_hit(self):
        """Update hit count and timestamp"""
        self.hit_count += 1
        self.timestamp_last_seen = datetime.datetime.now().isoformat()

    def add_evidence(self, evidence_item: str):
        """Add evidence to stain"""
        self.evidence.append({"timestamp": datetime.datetime.now().isoformat(), "evidence": evidence_item})

    def link_tag(self, tag_id: str):
        """Link another tag to this stain"""
        if tag_id not in self.linked_tags:
            self.linked_tags.append(tag_id)
