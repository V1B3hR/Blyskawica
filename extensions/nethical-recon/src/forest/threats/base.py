"""
forest/threats/base.py
Base threat classes for the Forest threat detection system.

Threats represent various types of security risks detected in the forest:
- Crows: Malware lurking in the canopy
- Magpies: Data stealers
- Squirrels: Lateral movement
- Snakes: Rootkits
- Parasites: Cryptominers
- Bats: Night-time attacks
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any


class ThreatType(Enum):
    """Types of threats in the forest"""

    CROW = "crow"  # 🐦‍⬛ Malware lurking
    MAGPIE = "magpie"  # 🐦 Data stealer
    SQUIRREL = "squirrel"  # 🐿️ Lateral movement
    SNAKE = "snake"  # 🐍 Rootkit
    PARASITE = "parasite"  # 🐛 Cryptominer/Resource abuse
    BAT = "bat"  # 🦇 Night-time attack
    UNKNOWN = "unknown"  # ❓ Unclassified threat


class ThreatSeverity(Enum):
    """Severity levels for threats"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseThreat(ABC):
    """Base class for all threat types"""

    def __init__(
        self,
        threat_id: str,
        name: str,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a threat.

        Args:
            threat_id: Unique identifier for this threat
            name: Human-readable name
            threat_type: Type of threat
            severity: Severity level
            metadata: Additional metadata
        """
        self.threat_id = threat_id
        self.name = name
        self.threat_type = threat_type
        self.severity = severity
        self.metadata = metadata or {}

        self.detected_at = datetime.now()
        self.last_seen = datetime.now()
        self.detection_count = 1

        # Location in forest
        self.tree_id = None
        self.branch_id = None
        self.leaf_id = None

        # Threat characteristics
        self.confidence = 0.0  # 0.0 to 1.0
        self.risk_score = 0.0  # 0.0 to 10.0
        self.indicators = []  # List of IOCs (Indicators of Compromise)

        # Status
        self.is_active = True
        self.is_contained = False
        self.is_mitigated = False

    @abstractmethod
    def get_description(self) -> str:
        """Get a description of this threat"""
        pass

    @abstractmethod
    def get_behavior_pattern(self) -> str:
        """Get the characteristic behavior pattern of this threat"""
        pass

    def set_location(self, tree_id: str, branch_id: str | None = None, leaf_id: str | None = None):
        """
        Set the location of this threat in the forest.

        Args:
            tree_id: Tree (host) where threat was found
            branch_id: Optional branch (process/service) where threat was found
            leaf_id: Optional leaf (thread/session) where threat was found
        """
        self.tree_id = tree_id
        self.branch_id = branch_id
        self.leaf_id = leaf_id

    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen = datetime.now()
        self.detection_count += 1

    def add_indicator(self, indicator: str, indicator_type: str = "generic"):
        """
        Add an indicator of compromise (IOC).

        Args:
            indicator: The IOC value (IP, hash, domain, etc.)
            indicator_type: Type of IOC (ip, hash, domain, file, process, etc.)
        """
        ioc = {"value": indicator, "type": indicator_type, "added_at": datetime.now().isoformat()}
        self.indicators.append(ioc)

    def set_confidence(self, confidence: float):
        """Set confidence level (0.0 to 1.0)"""
        self.confidence = max(0.0, min(1.0, confidence))

    def set_risk_score(self, score: float):
        """Set risk score (0.0 to 10.0, similar to CVSS)"""
        self.risk_score = max(0.0, min(10.0, score))

    def mark_contained(self):
        """Mark threat as contained"""
        self.is_contained = True

    def mark_mitigated(self):
        """Mark threat as mitigated"""
        self.is_mitigated = True
        self.is_active = False

    def mark_active(self):
        """Mark threat as active again"""
        self.is_active = True
        self.is_contained = False
        self.is_mitigated = False

    def get_icon(self) -> str:
        """Get emoji icon for this threat type"""
        icons = {
            ThreatType.CROW: "🐦‍⬛",
            ThreatType.MAGPIE: "🐦",
            ThreatType.SQUIRREL: "🐿️",
            ThreatType.SNAKE: "🐍",
            ThreatType.PARASITE: "🐛",
            ThreatType.BAT: "🦇",
            ThreatType.UNKNOWN: "❓",
        }
        return icons.get(self.threat_type, "❓")

    def get_severity_color(self) -> str:
        """Get color representation of severity"""
        colors = {
            ThreatSeverity.INFO: "🟢",
            ThreatSeverity.LOW: "🟡",
            ThreatSeverity.MEDIUM: "🟠",
            ThreatSeverity.HIGH: "🔴",
            ThreatSeverity.CRITICAL: "⚫",
        }
        return colors.get(self.severity, "⚪")

    def get_info(self) -> dict[str, Any]:
        """Get threat information as dictionary"""
        return {
            "threat_id": self.threat_id,
            "name": self.name,
            "type": self.threat_type.value,
            "severity": self.severity.value,
            "icon": self.get_icon(),
            "detected_at": self.detected_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "detection_count": self.detection_count,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "is_active": self.is_active,
            "is_contained": self.is_contained,
            "is_mitigated": self.is_mitigated,
            "location": {"tree_id": self.tree_id, "branch_id": self.branch_id, "leaf_id": self.leaf_id},
            "indicators": self.indicators,
            "description": self.get_description(),
            "behavior": self.get_behavior_pattern(),
        }

    def __str__(self):
        status = "🔒" if self.is_contained else "⚠️" if self.is_active else "✓"
        return f"{status} {self.get_icon()} {self.name} ({self.severity.value}) - Confidence: {self.confidence:.0%}"
