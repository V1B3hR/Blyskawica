"""
forest/threats/magpie.py
Magpie threat - represents data stealers.

The magpie is:
- Attracted to "shiny" data (credentials, PII)
- Quick to grab and escape (exfiltration)
- Hoards treasures (data collection)
"""

from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType


class Magpie(BaseThreat):
    """
    Magpie threat - Data stealer.

    Analogia: 🐦 Sroka - Kradnie błyszczące rzeczy
    """

    def __init__(
        self,
        threat_id: str,
        name: str,
        severity: ThreatSeverity = ThreatSeverity.HIGH,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a Magpie threat.

        Args:
            threat_id: Unique identifier
            name: Data stealer name/type
            severity: Severity level (default: HIGH)
            metadata: Additional metadata
        """
        super().__init__(threat_id, name, ThreatType.MAGPIE, severity, metadata)

        # Magpie-specific attributes
        self.target_data_types = metadata.get("target_data_types", []) if metadata else []
        self.exfiltration_method = metadata.get("exfiltration_method") if metadata else None
        self.stolen_data_size = 0  # bytes

        # What the magpie has collected
        self.stolen_items = []  # List of data types stolen
        self.exfiltration_destinations = []  # Where data is being sent

    def get_description(self) -> str:
        """Get description of the Magpie threat"""
        targets = ", ".join(self.target_data_types) if self.target_data_types else "various data"
        return (
            f"Data stealer detected: {self.name}. "
            f"This magpie is attracted to: {targets}. "
            f"{'Exfiltration method: ' + self.exfiltration_method if self.exfiltration_method else 'Exfiltration method unknown.'}"
        )

    def get_behavior_pattern(self) -> str:
        """Get characteristic behavior pattern"""
        behaviors = ["Seeks 'shiny' valuable data", "Quick grab and escape tactics"]

        if self.stolen_items:
            behaviors.append(f"Stolen: {', '.join(self.stolen_items[:3])}")
        if self.stolen_data_size > 0:
            behaviors.append(f"Data volume: {self._format_size(self.stolen_data_size)}")
        if self.exfiltration_destinations:
            behaviors.append(f"Destinations: {len(self.exfiltration_destinations)}")

        return " | ".join(behaviors)

    def add_stolen_item(self, data_type: str, size_bytes: int = 0):
        """
        Record a stolen data item.

        Args:
            data_type: Type of data stolen (credentials, PII, credit_card, etc.)
            size_bytes: Size of stolen data in bytes
        """
        self.stolen_items.append(data_type)
        self.stolen_data_size += size_bytes
        self.add_indicator(data_type, "stolen_data_type")

    def add_exfiltration_destination(self, destination: str):
        """
        Add a destination where data is being sent.

        Args:
            destination: IP address, domain, or URL
        """
        if destination not in self.exfiltration_destinations:
            self.exfiltration_destinations.append(destination)
            self.add_indicator(destination, "exfiltration_dest")

    def _format_size(self, bytes_size: int) -> str:
        """Format bytes into human-readable size"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"

    def __str__(self):
        base_str = super().__str__()
        if self.stolen_items:
            base_str += f" [Stolen: {len(self.stolen_items)} types]"
        return base_str
