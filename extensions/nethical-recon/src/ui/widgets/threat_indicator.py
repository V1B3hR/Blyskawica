"""
Threat indicator widget for displaying threat levels
"""

from rich.panel import Panel
from rich.text import Text

from ..base import ThreatLevel, UIColors, calculate_threat_level


class ThreatIndicator:
    """Visual threat level indicator"""

    def __init__(self, score: float = 0.0, max_score: float = 10.0):
        self.score = score
        self.max_score = max_score
        self.level = calculate_threat_level(score)

    def update_score(self, score: float):
        """Update the threat score"""
        self.score = score
        self.level = calculate_threat_level(score)

    def get_color(self) -> str:
        """Get color for current threat level"""
        color_map = {
            ThreatLevel.INFO: UIColors.SAFE,
            ThreatLevel.WARNING: UIColors.WARNING,
            ThreatLevel.ELEVATED: UIColors.ELEVATED,
            ThreatLevel.CRITICAL: UIColors.CRITICAL,
            ThreatLevel.BREACH: UIColors.BREACH,
        }
        return color_map.get(self.level, UIColors.TEXT)

    def render_simple(self) -> str:
        """Render simple text representation"""
        return f"{self.level.icon} {self.level.label}"

    def render_detailed(self) -> str:
        """Render detailed representation with score"""
        return f"{self.level.icon} {self.level.label}\nScore: {self.score:.1f}"

    def render_panel(self, title: str = "THREAT LEVEL") -> Panel:
        """Render as Rich panel"""
        text = Text()
        text.append(f"{self.level.icon} {self.level.label}\n", style=f"bold {self.get_color()}")
        text.append(f"Score: {self.score:.1f}", style=self.get_color())

        return Panel(text, title=title, border_style=self.get_color(), padding=(0, 1))

    def __str__(self) -> str:
        return self.render_simple()

    def __repr__(self) -> str:
        return f"ThreatIndicator(score={self.score}, level={self.level.label})"


def render_threat_bar(score: float, width: int = 20) -> str:
    """
    Render a threat level bar

    Args:
        score: Threat score (0-10)
        width: Width of the bar

    Returns:
        Visual threat bar
    """
    score = max(0.0, min(10.0, score))
    filled = int((score / 10.0) * width)

    # Color the bar based on threat level
    level = calculate_threat_level(score)

    if level == ThreatLevel.INFO:
        char = "▓"
    elif level == ThreatLevel.WARNING:
        char = "▓"
    elif level == ThreatLevel.ELEVATED:
        char = "▓"
    elif level == ThreatLevel.CRITICAL:
        char = "█"
    else:  # BREACH
        char = "█"

    return char * filled + "░" * (width - filled)
