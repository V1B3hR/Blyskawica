"""
Alerts Feed Panel - Shows recent bird song alerts
"""

from rich.panel import Panel
from rich.text import Text

from ..base import Alert, BirdType, UIColors


class AlertsFeedPanel:
    """Panel showing recent alerts (bird songs)"""

    def __init__(self, max_alerts: int = 4):
        self.alerts: list[Alert] = []
        self.max_alerts = max_alerts

    def add_alert(self, alert: Alert):
        """Add a new alert"""
        self.alerts.insert(0, alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[: self.max_alerts]

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []

    def render(self, width: int = 70) -> Panel:
        """Render the panel"""
        text = Text()

        if not self.alerts:
            text.append("No recent alerts", style=UIColors.DIM)
        else:
            for i, alert in enumerate(self.alerts):
                if i > 0:
                    text.append("\n")

                # Format alert
                time_str = alert.timestamp.strftime("%H:%M")
                alert_text = (
                    f"{alert.bird.icon} {time_str} [{alert.bird.sound}] {alert.bird.bird_name}: {alert.message}"
                )

                # Color based on bird type
                if alert.bird in [BirdType.EAGLE, BirdType.FALCON]:
                    style = UIColors.CRITICAL
                elif alert.bird == BirdType.OWL:
                    style = UIColors.WARNING
                else:
                    style = UIColors.TEXT

                text.append(alert_text, style=style)

        return Panel(text, title="BIRD SONGS (Recent Alerts)", border_style=UIColors.BIRD, padding=(0, 1), width=width)

    def render_compact(self) -> list[str]:
        """Render compact text version"""
        return [str(alert) for alert in self.alerts]
