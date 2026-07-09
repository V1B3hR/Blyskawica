"""
forest/threats/detector.py
Threat detector for the Forest system.

Detects various threats in the forest canopy:
- Crows (malware)
- Magpies (data stealers)
- Squirrels (lateral movement)
- Snakes (rootkits)
- Parasites (cryptominers)
- Bats (night attacks)
"""

from datetime import datetime
from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType
from .bat import Bat
from .crow import Crow
from .magpie import Magpie
from .parasite import Parasite
from .snake import Snake
from .squirrel import Squirrel


class ThreatDetector:
    """
    Detects and tracks threats in the forest canopy.

    Analogia: 🦅 Sokolim okiem wykrywa zagrożenia w koronach drzew
    """

    def __init__(self):
        """Initialize the threat detector"""
        self.detected_threats = {}  # threat_id -> Threat
        self.detection_rules = []
        self.detection_history = []

    def detect_crow(
        self,
        threat_id: str,
        name: str,
        malware_family: str = "Unknown",
        severity: ThreatSeverity = ThreatSeverity.HIGH,
        metadata: dict[str, Any] | None = None,
    ) -> Crow:
        """
        Detect a Crow (malware) threat.

        Args:
            threat_id: Unique identifier
            name: Malware name
            malware_family: Malware family
            severity: Severity level
            metadata: Additional metadata

        Returns:
            Crow threat object
        """
        if metadata is None:
            metadata = {}
        metadata["malware_family"] = malware_family

        crow = Crow(threat_id, name, severity, metadata)
        self.detected_threats[threat_id] = crow
        self._log_detection(crow)
        return crow

    def detect_magpie(
        self,
        threat_id: str,
        name: str,
        target_data_types: list[str] = None,
        severity: ThreatSeverity = ThreatSeverity.HIGH,
        metadata: dict[str, Any] | None = None,
    ) -> Magpie:
        """
        Detect a Magpie (data stealer) threat.

        Args:
            threat_id: Unique identifier
            name: Data stealer name
            target_data_types: Types of data being targeted
            severity: Severity level
            metadata: Additional metadata

        Returns:
            Magpie threat object
        """
        if metadata is None:
            metadata = {}
        metadata["target_data_types"] = target_data_types or []

        magpie = Magpie(threat_id, name, severity, metadata)
        self.detected_threats[threat_id] = magpie
        self._log_detection(magpie)
        return magpie

    def detect_squirrel(
        self,
        threat_id: str,
        name: str,
        technique: str = "Unknown",
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Squirrel:
        """
        Detect a Squirrel (lateral movement) threat.

        Args:
            threat_id: Unique identifier
            name: Lateral movement technique name
            technique: Movement technique
            severity: Severity level
            metadata: Additional metadata

        Returns:
            Squirrel threat object
        """
        if metadata is None:
            metadata = {}
        metadata["technique"] = technique

        squirrel = Squirrel(threat_id, name, severity, metadata)
        self.detected_threats[threat_id] = squirrel
        self._log_detection(squirrel)
        return squirrel

    def detect_snake(
        self,
        threat_id: str,
        name: str,
        rootkit_type: str = "unknown",
        severity: ThreatSeverity = ThreatSeverity.CRITICAL,
        metadata: dict[str, Any] | None = None,
    ) -> Snake:
        """
        Detect a Snake (rootkit) threat.

        Args:
            threat_id: Unique identifier
            name: Rootkit name
            rootkit_type: Type of rootkit
            severity: Severity level
            metadata: Additional metadata

        Returns:
            Snake threat object
        """
        if metadata is None:
            metadata = {}
        metadata["rootkit_type"] = rootkit_type

        snake = Snake(threat_id, name, severity, metadata)
        self.detected_threats[threat_id] = snake
        self._log_detection(snake)
        return snake

    def detect_parasite(
        self,
        threat_id: str,
        name: str,
        parasite_type: str = "cryptominer",
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Parasite:
        """
        Detect a Parasite (cryptominer) threat.

        Args:
            threat_id: Unique identifier
            name: Parasite name
            parasite_type: Type of parasite
            severity: Severity level
            metadata: Additional metadata

        Returns:
            Parasite threat object
        """
        if metadata is None:
            metadata = {}
        metadata["parasite_type"] = parasite_type

        parasite = Parasite(threat_id, name, severity, metadata)
        self.detected_threats[threat_id] = parasite
        self._log_detection(parasite)
        return parasite

    def detect_bat(
        self,
        threat_id: str,
        name: str,
        attack_type: str = "unknown",
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> Bat:
        """
        Detect a Bat (night attack) threat.

        Args:
            threat_id: Unique identifier
            name: Attack name
            attack_type: Type of attack
            severity: Severity level
            metadata: Additional metadata

        Returns:
            Bat threat object
        """
        if metadata is None:
            metadata = {}
        metadata["attack_type"] = attack_type

        bat = Bat(threat_id, name, severity, metadata)
        self.detected_threats[threat_id] = bat
        self._log_detection(bat)
        return bat

    def get_threat(self, threat_id: str) -> BaseThreat | None:
        """Get a specific threat by ID"""
        return self.detected_threats.get(threat_id)

    def get_all_threats(self) -> list[BaseThreat]:
        """Get all detected threats"""
        return list(self.detected_threats.values())

    def get_active_threats(self) -> list[BaseThreat]:
        """Get all active threats"""
        return [t for t in self.detected_threats.values() if t.is_active]

    def get_threats_by_type(self, threat_type: ThreatType) -> list[BaseThreat]:
        """Get all threats of a specific type"""
        return [t for t in self.detected_threats.values() if t.threat_type == threat_type]

    def get_threats_by_severity(self, severity: ThreatSeverity) -> list[BaseThreat]:
        """Get all threats of a specific severity"""
        return [t for t in self.detected_threats.values() if t.severity == severity]

    def get_critical_threats(self) -> list[BaseThreat]:
        """Get all critical threats"""
        return self.get_threats_by_severity(ThreatSeverity.CRITICAL)

    def remove_threat(self, threat_id: str):
        """Remove a threat from detected threats"""
        if threat_id in self.detected_threats:
            del self.detected_threats[threat_id]

    def get_threat_summary(self) -> dict[str, Any]:
        """Get summary of all detected threats"""
        by_type = {}
        by_severity = {}

        for threat in self.detected_threats.values():
            # Count by type
            type_name = threat.threat_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1

            # Count by severity
            sev_name = threat.severity.value
            by_severity[sev_name] = by_severity.get(sev_name, 0) + 1

        return {
            "total_threats": len(self.detected_threats),
            "active_threats": len(self.get_active_threats()),
            "by_type": by_type,
            "by_severity": by_severity,
            "critical_count": len(self.get_critical_threats()),
        }

    def _log_detection(self, threat: BaseThreat):
        """Log a threat detection"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "threat_id": threat.threat_id,
            "threat_type": threat.threat_type.value,
            "threat_name": threat.name,
            "severity": threat.severity.value,
        }
        self.detection_history.append(log_entry)

    def get_detection_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent detection history"""
        return self.detection_history[-limit:]

    def __str__(self):
        summary = self.get_threat_summary()
        return f"🔍 ThreatDetector: {summary['total_threats']} threats detected ({summary['active_threats']} active, {summary['critical_count']} critical)"
