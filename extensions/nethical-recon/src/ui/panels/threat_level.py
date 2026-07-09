"""
Threat Level Panel - Shows current threat assessment
"""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from ..widgets.threat_indicator import ThreatIndicator


class ThreatLevelPanel:
    """Panel showing current threat level"""

    def __init__(self, score: float = 0.0):
        self.indicator = ThreatIndicator(score)

    def update(self, score: float):
        """Update threat score"""
        self.indicator.update_score(score)

    def render(self, width: int = 20) -> Panel:
        """Render the panel"""
        text = Text()

        # Threat icon and level
        text.append(
            f"{self.indicator.level.icon} {self.indicator.level.label}\n", style=f"bold {self.indicator.get_color()}"
        )

        # Score
        text.append(f"Score: {self.indicator.score:.1f}", style=self.indicator.get_color())

        return Panel(
            Align.center(text),
            title="THREAT LEVEL",
            border_style=self.indicator.get_color(),
            padding=(0, 1),
            width=width,
        )

    def render_compact(self) -> str:
        """Render compact text version"""
        return f"{self.indicator.level.icon} {self.indicator.level.label} (Score: {self.indicator.score:.1f})"
