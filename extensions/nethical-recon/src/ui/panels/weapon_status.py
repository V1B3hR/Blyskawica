"""
Weapon Status Panel - Shows weapon and ammo status
"""

from rich.panel import Panel
from rich.text import Text

from ..base import UIColors
from ..widgets.progress_bars import create_stealth_bar


class WeaponStatusPanel:
    """Panel showing weapon status"""

    def __init__(self, mode: str = "CO2 Silent", status: str = "ARMED", stealth: int = 50, ammo: dict[str, int] = None):
        self.mode = mode
        self.status = status
        self.stealth = stealth
        self.ammo = ammo or {}

    def update(self, mode: str = None, status: str = None, stealth: int = None, ammo: dict[str, int] = None):
        """Update weapon status"""
        if mode is not None:
            self.mode = mode
        if status is not None:
            self.status = status
        if stealth is not None:
            self.stealth = stealth
        if ammo is not None:
            self.ammo = ammo

    def get_mode_icon(self) -> str:
        """Get icon for weapon mode"""
        mode_icons = {"Pneumatic": "💨", "CO2 Silent": "🧊", "Electric": "⚡"}
        return mode_icons.get(self.mode, "🔫")

    def render(self, width: int = 70) -> Panel:
        """Render the panel"""
        text = Text()

        # Weapon mode and status
        icon = self.get_mode_icon()
        status_color = UIColors.SAFE if self.status == "ARMED" else UIColors.WARNING
        text.append(f"🔫 {self.mode} [{self.status}]    ", style=status_color)

        # Ammo counts
        ammo_colors = {
            "RED": "🔴",
            "PURPLE": "🟣",
            "ORANGE": "🟠",
            "YELLOW": "🟡",
            "BLUE": "🔵",
            "BLACK": "🖤",
            "BROWN": "🤎",
        }

        ammo_text = "Ammo: "
        for color, icon in ammo_colors.items():
            count = self.ammo.get(color, 0)
            ammo_text += f"{icon}x{count} "

        text.append(ammo_text.strip() + "\n", style=UIColors.WEAPON)

        # Stealth bar
        stealth_bar = create_stealth_bar(self.stealth, width=10)
        text.append(f"Stealth: [{stealth_bar}] {self.stealth}%", style=UIColors.TEXT)

        return Panel(text, title="WEAPON STATUS", border_style=UIColors.WEAPON, padding=(0, 1), width=width)

    def render_compact(self) -> str:
        """Render compact text version"""
        icon = self.get_mode_icon()
        return f"🔫 {self.mode} [{self.status}] Stealth: {self.stealth}%"
