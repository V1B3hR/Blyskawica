"""
Settings Screen - Configuration and preferences
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..base import UIColors


class SettingsScreen:
    """Screen for settings and configuration"""

    def __init__(self):
        self.settings: dict[str, Any] = {
            "auto_response": True,
            "alert_sounds": True,
            "stealth_mode": False,
            "confidence_threshold": 0.7,
            "nanobot_mode": "DEFENSE",
            "weapon_mode": "CO2 Silent",
            "bird_patrol": True,
            "forest_monitoring": True,
            "log_level": "INFO",
        }
        self.selected_index = 0

    def set_setting(self, key: str, value: Any):
        """Update a setting"""
        if key in self.settings:
            self.settings[key] = value

    def toggle_bool_setting(self, key: str):
        """Toggle a boolean setting"""
        if key in self.settings and isinstance(self.settings[key], bool):
            self.settings[key] = not self.settings[key]

    def next_setting(self):
        """Move to next setting"""
        self.selected_index = (self.selected_index + 1) % len(self.settings)

    def prev_setting(self):
        """Move to previous setting"""
        self.selected_index = (self.selected_index - 1) % len(self.settings)

    def render_settings_list(self) -> Panel:
        """Render settings list"""
        table = Table(show_header=True, box=None, padding=(0, 1))
        table.add_column("Setting", style=UIColors.TEXT)
        table.add_column("Value", style=UIColors.HIGHLIGHT)

        for i, (key, value) in enumerate(self.settings.items()):
            selected = "► " if i == self.selected_index else "  "

            # Format key
            key_display = key.replace("_", " ").title()

            # Format value
            if isinstance(value, bool):
                value_display = "✅ ON" if value else "❌ OFF"
            else:
                value_display = str(value)

            table.add_row(f"{selected}{key_display}", value_display)

        return Panel(table, title="SETTINGS", border_style=UIColors.BORDER, padding=(0, 1))

    def render_help(self) -> Panel:
        """Render help text"""
        text = Text()

        text.append("Settings Guide:\n\n", style="bold")

        help_text = [
            "Auto Response: Enable nanobots automatic response",
            "Alert Sounds: Enable bird song audio alerts",
            "Stealth Mode: Reduce detection signatures",
            "Confidence Threshold: Minimum confidence for auto-fire (0.0-1.0)",
            "Nanobot Mode: DEFENSE, SCOUT, ADAPTIVE, or PATROL",
            "Weapon Mode: Pneumatic, CO2 Silent, or Electric",
            "Bird Patrol: Enable bird surveillance system",
            "Forest Monitoring: Enable continuous forest health checks",
            "Log Level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        ]

        for help_line in help_text:
            text.append("• " + help_line + "\n", style=UIColors.TEXT)

        return Panel(text, title="HELP", border_style=UIColors.DIM, padding=(0, 1))

    def render(self, console: Console):
        """Render the complete settings screen"""
        console.clear()

        # Title
        console.print(
            Panel(Text("⚙️ SETTINGS - Configuration", justify="center", style="bold"), border_style=UIColors.BORDER)
        )
        console.print()

        # Settings list and help
        from rich.columns import Columns

        console.print(Columns([self.render_settings_list(), self.render_help()]))
        console.print()

        # Controls
        console.print("[↑/↓] Navigate    [SPACE] Toggle    [ENTER] Edit    [S] Save    [B] Back", style=UIColors.DIM)

    def save_settings(self) -> bool:
        """Save settings (placeholder)"""
        # In real implementation, this would save to a config file
        return True

    def load_settings(self) -> bool:
        """Load settings (placeholder)"""
        # In real implementation, this would load from a config file
        return True
