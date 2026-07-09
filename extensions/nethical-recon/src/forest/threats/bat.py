"""
forest/threats/bat.py
Bat threat - represents night-time attacks.

The bat:
- Active when others sleep (off-hours attacks)
- Exploits reduced vigilance
- Uses echolocation (reconnaissance in darkness)
"""

from datetime import datetime
from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType


class Bat(BaseThreat):
    """
    Bat threat - Night-time attacks.

    Analogia: 🦇 Nietoperz - Aktywny gdy inni śpią
    """

    def __init__(
        self,
        threat_id: str,
        name: str,
        severity: ThreatSeverity = ThreatSeverity.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a Bat threat.

        Args:
            threat_id: Unique identifier
            name: Attack name/type
            severity: Severity level (default: MEDIUM)
            metadata: Additional metadata
        """
        super().__init__(threat_id, name, ThreatType.BAT, severity, metadata)

        # Bat-specific attributes
        self.attack_type = metadata.get("attack_type", "unknown") if metadata else "unknown"
        self.target_time_window = metadata.get("time_window", "night") if metadata else "night"

        # Activity tracking
        self.active_hours = []  # List of hours when bat was active (0-23)
        self.night_activity_count = 0
        self.day_activity_count = 0

        # Reconnaissance tracking
        self.recon_methods = []  # Echolocation methods used

    def get_description(self) -> str:
        """Get description of the Bat threat"""
        return (
            f"Night-time attack detected: {self.name} ({self.attack_type}). "
            f"This bat operates during {self.target_time_window} hours "
            f"when monitoring is reduced. "
            f"Night activity: {self.night_activity_count} events, "
            f"Day activity: {self.day_activity_count} events."
        )

    def get_behavior_pattern(self) -> str:
        """Get characteristic behavior pattern"""
        behaviors = [
            f"Attack: {self.attack_type}",
            f"Window: {self.target_time_window}",
            f"Night: {self.night_activity_count} events",
        ]

        if self.recon_methods:
            behaviors.append(f"Recon methods: {len(self.recon_methods)}")

        # Calculate activity ratio
        total = self.night_activity_count + self.day_activity_count
        if total > 0:
            night_ratio = (self.night_activity_count / total) * 100
            if night_ratio > 80:
                behaviors.append(f"⚠️ {night_ratio:.0f}% night activity!")

        return " | ".join(behaviors)

    def record_activity(self, timestamp: datetime = None):
        """
        Record bat activity.

        Args:
            timestamp: Time of activity (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        hour = timestamp.hour
        self.active_hours.append(hour)

        # Classify as night or day activity
        # Night: 22:00 - 06:00
        if hour >= 22 or hour < 6:
            self.night_activity_count += 1
        # Weekend/off-hours: Saturday/Sunday or 18:00-22:00
        elif timestamp.weekday() >= 5 or (18 <= hour < 22):
            self.night_activity_count += 1
        else:
            self.day_activity_count += 1

        self.update_last_seen()

        # Escalate if significant night activity
        if self.night_activity_count > 5 and self.severity == ThreatSeverity.MEDIUM:
            self.severity = ThreatSeverity.HIGH

    def add_recon_method(self, method: str):
        """
        Add a reconnaissance method used by the bat.

        Args:
            method: Description of recon method (echolocation)
        """
        if method not in self.recon_methods:
            self.recon_methods.append(method)
            self.add_indicator(method, "recon_method")

    def is_currently_night_hours(self) -> bool:
        """Check if current time is considered night hours"""
        now = datetime.now()
        hour = now.hour

        # Night: 22:00 - 06:00 or weekends
        return hour >= 22 or hour < 6 or now.weekday() >= 5

    def get_activity_pattern(self) -> dict[int, int]:
        """Get activity pattern by hour"""
        pattern = {hour: 0 for hour in range(24)}
        for hour in self.active_hours:
            pattern[hour] += 1
        return pattern

    def __str__(self):
        base_str = super().__str__()
        total_activity = self.night_activity_count + self.day_activity_count
        if total_activity > 0:
            night_percent = (self.night_activity_count / total_activity) * 100
            base_str += f" [Night: {night_percent:.0f}%]"
        return base_str
