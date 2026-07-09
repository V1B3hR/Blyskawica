"""
Birds Status Panel - Shows bird patrol status
"""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from ..base import UIColors


class BirdsStatusPanel:
    """Panel showing bird patrol status"""

    def __init__(self, birds: dict[str, str] = None):
        # Default birds and their status
        self.birds = birds or {"EAGLE": "PATROL", "FALCON": "HUNT", "OWL": "WATCH"}

    def update(self, bird: str, status: str):
        """Update a bird's status"""
        self.birds[bird] = status

    def get_bird_icon(self, bird: str) -> str:
        """Get icon for bird type"""
        icons = {"EAGLE": "🦅", "FALCON": "🦅", "OWL": "🦉", "SPARROW": "🐦"}
        return icons.get(bird, "🐦")

    def render(self, width: int = 16) -> Panel:
        """Render the panel"""
        text = Text()

        for i, (bird, status) in enumerate(self.birds.items()):
            if i > 0:
                text.append("\n")

            icon = self.get_bird_icon(bird)
            text.append(f"{icon} {status}", style=UIColors.BIRD)

        return Panel(Align.center(text), title="BIRDS", border_style=UIColors.BIRD, padding=(0, 1), width=width)

    def render_compact(self) -> str:
        """Render compact text version"""
        return " ".join([f"{self.get_bird_icon(bird)} {status}" for bird, status in self.birds.items()])
