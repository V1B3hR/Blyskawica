"""
Alert Escalation - Defensive nanobot that escalates alerts.

Part of the defensive mode (🛡️ antibody behavior).
"""

from datetime import datetime
from enum import Enum
from typing import Any

from ..base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"  # 🟢 Low severity
    WARNING = "warning"  # 🟡 Medium severity
    ELEVATED = "elevated"  # 🟠 High severity
    CRITICAL = "critical"  # 🔴 Critical severity
    BREACH = "breach"  # ⚫ Active breach


class AlertNanobot(BaseNanobot):
    """
    Nanobot that escalates alerts to hunters and monitoring systems.

    Manages alert levels and notifications based on threat severity.
    """

    def __init__(self, nanobot_id: str = "alert_escalator", config: dict[str, Any] | None = None):
        """
        Initialize alert nanobot.

        Args:
            nanobot_id: Unique identifier
            config: Configuration options:
                - alert_channels: List of alert channels (default: ['log'])
                - min_level: Minimum level to alert on (default: WARNING)
        """
        super().__init__(nanobot_id, NanobotMode.DEFENSIVE, config)

        self.alert_channels = self.config.get("alert_channels", ["log"])
        self.min_level = AlertLevel[self.config.get("min_level", "WARNING").upper()]

        # Track alerts
        self.active_alerts: list[dict[str, Any]] = []
        self.alert_count_by_level: dict[str, int] = {level.value: 0 for level in AlertLevel}

    def can_handle(self, event: dict[str, Any]) -> bool:
        """All events can be alerted on"""
        return True

    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess threat level for alerting.

        All events get alerted if they meet min_level threshold.
        """
        base_confidence = event.get("confidence", 0.5)
        threat_score = event.get("threat_score", 5.0)

        # Map threat score to confidence
        if threat_score >= 9.0:
            confidence = 0.95
        elif threat_score >= 7.0:
            confidence = 0.85
        elif threat_score >= 5.0:
            confidence = 0.70
        elif threat_score >= 3.0:
            confidence = 0.50
        else:
            confidence = base_confidence

        return confidence

    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Escalate alert.

        Args:
            event: Event to alert on
            confidence: Confidence level

        Returns:
            ActionResult with alert details
        """
        # Determine alert level based on confidence and event
        alert_level = self._determine_alert_level(event, confidence)

        # Check if we should alert
        if not self._should_alert(alert_level):
            return ActionResult(
                action_type=ActionType.ALERT,
                status=ActionStatus.SKIPPED,
                confidence=confidence,
                details={"reason": "below_min_level", "level": alert_level.value},
            )

        # Create alert
        alert = {
            "alert_id": f"alert_{len(self.active_alerts)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "level": alert_level.value,
            "confidence": confidence,
            "timestamp": datetime.now(),
            "source": event.get("source_ip") or event.get("source", "unknown"),
            "event_type": event.get("type", "unknown"),
            "description": event.get("description", "Threat detected"),
            "details": event,
        }

        # Send alert through channels
        success = self._send_alert(alert)

        if success:
            self.active_alerts.append(alert)
            self.alert_count_by_level[alert_level.value] += 1

            return ActionResult(
                action_type=ActionType.ALERT,
                status=ActionStatus.SUCCESS,
                confidence=confidence,
                details={
                    "alert_id": alert["alert_id"],
                    "level": alert_level.value,
                    "channels": self.alert_channels,
                    "total_alerts": len(self.active_alerts),
                },
            )
        else:
            return ActionResult(
                action_type=ActionType.ALERT,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message="Failed to send alert",
            )

    def _determine_alert_level(self, event: dict[str, Any], confidence: float) -> AlertLevel:
        """Determine appropriate alert level"""
        threat_score = event.get("threat_score", 0)

        # Check for breach indicators
        if event.get("breach_detected", False) or confidence >= 0.95:
            return AlertLevel.BREACH

        # Critical threats
        if threat_score >= 9.0 or confidence >= 0.90:
            return AlertLevel.CRITICAL

        # High severity
        if threat_score >= 7.0 or confidence >= 0.75:
            return AlertLevel.ELEVATED

        # Medium severity
        if threat_score >= 5.0 or confidence >= 0.60:
            return AlertLevel.WARNING

        # Low severity
        return AlertLevel.INFO

    def _should_alert(self, alert_level: AlertLevel) -> bool:
        """Check if we should alert based on minimum level"""
        level_order = [AlertLevel.INFO, AlertLevel.WARNING, AlertLevel.ELEVATED, AlertLevel.CRITICAL, AlertLevel.BREACH]
        return level_order.index(alert_level) >= level_order.index(self.min_level)

    def _send_alert(self, alert: dict[str, Any]) -> bool:
        """
        Send alert through configured channels.

        In production, this would send to:
        - Logging systems
        - Email/SMS
        - Slack/Teams
        - SIEM systems
        - Dashboard updates
        """
        # Simulation - log to console
        level_emoji = {"info": "🟢", "warning": "🟡", "elevated": "🟠", "critical": "🔴", "breach": "⚫"}

        emoji = level_emoji.get(alert["level"], "⚪")
        print(f"{emoji} ALERT [{alert['level'].upper()}]: {alert['description']}")

        return True

    def get_active_alerts(self, level: AlertLevel | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get active alerts.

        Args:
            level: Optional filter by alert level
            limit: Maximum number of alerts to return

        Returns:
            List of alerts
        """
        if level:
            alerts = [a for a in self.active_alerts if a["level"] == level.value]
        else:
            alerts = self.active_alerts

        return alerts[-limit:]

    def get_alert_statistics(self) -> dict[str, Any]:
        """Get alert statistics"""
        return {
            "total_alerts": len(self.active_alerts),
            "by_level": self.alert_count_by_level.copy(),
            "recent_alerts": len(
                [a for a in self.active_alerts if (datetime.now() - a["timestamp"]).total_seconds() < 3600]
            ),
        }

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: ID of alert to acknowledge

        Returns:
            True if acknowledged
        """
        for alert in self.active_alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now()
                return True
        return False

    def clear_old_alerts(self, hours: int = 24) -> int:
        """
        Clear alerts older than specified hours.

        Args:
            hours: Age threshold in hours

        Returns:
            Number of alerts cleared
        """
        cutoff = datetime.now().timestamp() - (hours * 3600)

        old_count = len(self.active_alerts)
        self.active_alerts = [a for a in self.active_alerts if a["timestamp"].timestamp() > cutoff]

        return old_count - len(self.active_alerts)
