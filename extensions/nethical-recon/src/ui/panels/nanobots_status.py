"""
Nanobots Status Panel - Shows nanobot swarm status
"""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from ..base import UIColors


class NanobotsStatusPanel:
    """Panel showing nanobot status"""

    def __init__(self, active: int = 0, mode: str = "STANDBY"):
        self.active = active
        self.mode = mode

    def update(self, active: int = None, mode: str = None):
        """Update nanobot status"""
        if active is not None:
            self.active = active
        if mode is not None:
            self.mode = mode

    def get_mode_icon(self) -> str:
        """Get icon for current mode"""
        mode_icons = {"STANDBY": "⏸️", "DEFENSE": "🛡️", "SCOUT": "🔍", "ADAPTIVE": "🧬", "PATROL": "👁️"}
        return mode_icons.get(self.mode, "🤖")

    def render(self, width: int = 18) -> Panel:
        """Render the panel"""
        text = Text()

        # Active count
        text.append(f"🤖 {self.active} ACT\n", style=UIColors.NANOBOT)

        # Mode
        icon = self.get_mode_icon()
        text.append(f"{icon} {self.mode}", style="bold")

        return Panel(Align.center(text), title="NANOBOTS", border_style=UIColors.NANOBOT, padding=(0, 1), width=width)

    def render_compact(self) -> str:
        """Render compact text version"""
        icon = self.get_mode_icon()
        return f"🤖 {self.active} {icon} {self.mode}"
