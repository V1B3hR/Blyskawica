"""
forest/threats/crow.py
Crow threat - represents malware lurking in the canopy.

The crow is:
- Patient, waiting for the perfect moment
- Hides in shadows (obfuscation)
- Intelligent, learns the environment
"""

from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType


class Crow(BaseThreat):
    """
    Crow threat - Malware lurking quietly.

    Analogia: 🐦‍⬛ Kruk - Czarny ptak czyhający cicho
    """

    def __init__(
        self,
        threat_id: str,
        name: str,
        severity: ThreatSeverity = ThreatSeverity.HIGH,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a Crow threat.

        Args:
            threat_id: Unique identifier
            name: Malware name/type
            severity: Severity level (default: HIGH)
            metadata: Additional metadata
        """
        super().__init__(threat_id, name, ThreatType.CROW, severity, metadata)

        # Crow-specific attributes
        self.malware_family = metadata.get("malware_family", "Unknown") if metadata else "Unknown"
        self.persistence_method = metadata.get("persistence_method") if metadata else None
        self.obfuscation_level = metadata.get("obfuscation_level", "low") if metadata else "low"
        self.command_and_control = metadata.get("c2_server") if metadata else None

        # Behavior tracking
        self.is_dormant = False
        self.activation_time = None
        self.exfiltration_detected = False

    def get_description(self) -> str:
        """Get description of the Crow threat"""
        return (
            f"Malware detected: {self.name} ({self.malware_family}). "
            f"This crow is lurking in the canopy, waiting patiently. "
            f"Obfuscation level: {self.obfuscation_level}. "
            f"{'C&C Server: ' + self.command_and_control if self.command_and_control else 'No C&C detected yet.'}"
        )

    def get_behavior_pattern(self) -> str:
        """Get characteristic behavior pattern"""
        behaviors = [
            "Patient and observant",
            "Hides in shadows (obfuscated code)",
            "Waits for ideal moment to strike",
            "Learns system environment",
        ]

        if self.persistence_method:
            behaviors.append(f"Persistence: {self.persistence_method}")
        if self.command_and_control:
            behaviors.append(f"Communicates with C&C: {self.command_and_control}")
        if self.exfiltration_detected:
            behaviors.append("⚠️ Data exfiltration detected!")

        return " | ".join(behaviors)

    def mark_dormant(self):
        """Mark the crow as dormant (sleeping)"""
        self.is_dormant = True

    def mark_active_exfiltration(self):
        """Mark that data exfiltration has been detected"""
        self.exfiltration_detected = True
        if self.severity.value in ["low", "medium"]:
            self.severity = ThreatSeverity.HIGH

    def set_c2_server(self, c2_server: str):
        """Set command and control server"""
        self.command_and_control = c2_server
        self.add_indicator(c2_server, "c2_server")

    def __str__(self):
        base_str = super().__str__()
        if self.is_dormant:
            base_str += " [DORMANT]"
        if self.exfiltration_detected:
            base_str += " [EXFILTRATING]"
        return base_str
