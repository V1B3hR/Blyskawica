"""
Correlation Engine for Sensors
Detects multi-stage attack patterns by correlating events from multiple sensors
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from collections import defaultdict

from .base import SensorAlert


class AttackPattern:
    """Represents a multi-stage attack pattern"""

    def __init__(self, name: str, stages: list[dict[str, Any]], time_window: int = 3600):
        """
        Initialize attack pattern

        Args:
            name: Pattern name
            stages: List of stage definitions (severity, message patterns)
            time_window: Time window in seconds to correlate events
        """
        self.name = name
        self.stages = stages
        self.time_window = time_window
        self.detected_instances = []

    def matches_stage(self, stage_idx: int, alert: SensorAlert) -> bool:
        """Check if alert matches a specific stage"""
        if stage_idx >= len(self.stages):
            return False

        stage = self.stages[stage_idx]

        # Check severity match
        if "severity" in stage and alert.severity != stage["severity"]:
            return False

        # Check message pattern match
        if "message_pattern" in stage:
            pattern = stage["message_pattern"].lower()
            if pattern not in alert.message.lower():
                return False

        return True


class CorrelationEngine:
    """
    Correlation engine for detecting multi-stage attacks
    """

    def __init__(self):
        """Initialize the correlation engine"""
        self.logger = logging.getLogger("nethical.correlation_engine")
        self._initialize_logger()

        # Registered attack patterns
        self.patterns: dict[str, AttackPattern] = {}

        # Alert history for correlation
        self.alert_history: list[tuple[datetime, SensorAlert, str]] = []  # (timestamp, alert, sensor_name)

        # Detected multi-stage attacks
        self.detected_attacks: list[dict[str, Any]] = []

        # Register default patterns
        self._register_default_patterns()

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [CorrelationEngine] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _register_default_patterns(self):
        """Register default attack patterns"""

        # Port scan followed by exploitation attempt
        recon_exploit = AttackPattern(
            name="recon_then_exploit",
            stages=[
                {"severity": "WARNING", "message_pattern": "port scan"},
                {"severity": "CRITICAL", "message_pattern": "exploit"},
            ],
            time_window=3600,  # 1 hour
        )
        self.register_pattern(recon_exploit)

        # Brute force followed by successful access
        brute_force_success = AttackPattern(
            name="brute_force_success",
            stages=[
                {"severity": "WARNING", "message_pattern": "failed login"},
                {"severity": "CRITICAL", "message_pattern": "successful"},
            ],
            time_window=1800,  # 30 minutes
        )
        self.register_pattern(brute_force_success)

        # Data exfiltration pattern
        data_exfil = AttackPattern(
            name="data_exfiltration",
            stages=[
                {"severity": "WARNING", "message_pattern": "unusual data access"},
                {"severity": "WARNING", "message_pattern": "large transfer"},
                {"severity": "CRITICAL", "message_pattern": "external connection"},
            ],
            time_window=7200,  # 2 hours
        )
        self.register_pattern(data_exfil)

    def register_pattern(self, pattern: AttackPattern) -> bool:
        """
        Register a new attack pattern

        Args:
            pattern: Attack pattern to register

        Returns:
            bool: True if registered successfully
        """
        if pattern.name in self.patterns:
            self.logger.warning(f"Pattern {pattern.name} already registered")
            return False

        self.patterns[pattern.name] = pattern
        self.logger.info(f"Registered attack pattern: {pattern.name}")
        return True

    def add_alert(self, alert: SensorAlert, sensor_name: str):
        """
        Add an alert for correlation

        Args:
            alert: Sensor alert
            sensor_name: Name of sensor that generated the alert
        """
        self.alert_history.append((datetime.now(), alert, sensor_name))

        # Clean up old alerts
        self._cleanup_old_alerts()

        # Check for pattern matches
        self._check_patterns()

    def _cleanup_old_alerts(self):
        """Remove alerts older than the largest time window"""
        if not self.alert_history:
            return

        # Find the largest time window
        max_window = max(pattern.time_window for pattern in self.patterns.values()) if self.patterns else 3600

        cutoff_time = datetime.now() - timedelta(seconds=max_window)
        self.alert_history = [(ts, alert, sensor) for ts, alert, sensor in self.alert_history if ts >= cutoff_time]

    def _check_patterns(self):
        """Check if any patterns are matched in recent alerts"""
        for pattern_name, pattern in self.patterns.items():
            self._check_pattern(pattern)

    def _check_pattern(self, pattern: AttackPattern):
        """Check a specific pattern against alert history"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=pattern.time_window)

        # Get alerts within time window
        recent_alerts = [(ts, alert, sensor) for ts, alert, sensor in self.alert_history if ts >= cutoff_time]

        if len(recent_alerts) < len(pattern.stages):
            return

        # Try to find a sequence matching all stages
        for i in range(len(recent_alerts) - len(pattern.stages) + 1):
            stage_matches = []

            for stage_idx in range(len(pattern.stages)):
                alert_idx = i + stage_idx
                if alert_idx >= len(recent_alerts):
                    break

                ts, alert, sensor = recent_alerts[alert_idx]
                if pattern.matches_stage(stage_idx, alert):
                    stage_matches.append(
                        {"stage": stage_idx, "timestamp": ts.isoformat(), "alert": alert.to_dict(), "sensor": sensor}
                    )

            # If all stages matched, record the attack
            if len(stage_matches) == len(pattern.stages):
                attack = {
                    "pattern_name": pattern.name,
                    "detected_at": current_time.isoformat(),
                    "stages": stage_matches,
                    "severity": "CRITICAL",
                    "confidence": 0.9,
                }

                # Check if not already detected
                if not self._is_duplicate_detection(attack):
                    self.detected_attacks.append(attack)
                    self.logger.critical(f"Detected multi-stage attack: {pattern.name}")

    def _is_duplicate_detection(self, attack: dict[str, Any]) -> bool:
        """Check if this attack was already detected recently"""
        pattern_name = attack["pattern_name"]
        detected_time = datetime.fromisoformat(attack["detected_at"])

        for existing in self.detected_attacks[-10:]:  # Check last 10 detections
            if existing["pattern_name"] == pattern_name:
                existing_time = datetime.fromisoformat(existing["detected_at"])
                if (detected_time - existing_time).total_seconds() < 60:  # Within 1 minute
                    return True

        return False

    def get_detected_attacks(self, min_severity: str | None = None) -> list[dict[str, Any]]:
        """
        Get detected multi-stage attacks

        Args:
            min_severity: Optional minimum severity filter

        Returns:
            List of detected attacks
        """
        if min_severity:
            return [a for a in self.detected_attacks if a["severity"] == min_severity]
        return self.detected_attacks.copy()

    def clear_detections(self):
        """Clear detected attacks"""
        self.detected_attacks.clear()
        self.logger.info("Cleared all attack detections")

    def get_statistics(self) -> dict[str, Any]:
        """Get correlation engine statistics"""
        return {
            "registered_patterns": len(self.patterns),
            "alert_history_size": len(self.alert_history),
            "detected_attacks": len(self.detected_attacks),
            "patterns": list(self.patterns.keys()),
        }
