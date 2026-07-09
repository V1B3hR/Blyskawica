"""
Forest Status Panel - Shows forest health and threats
"""

from rich.panel import Panel
from rich.text import Text

from ..base import UIColors


class ForestStatusPanel:
    """Panel showing forest status"""

    def __init__(self, trees: int = 0, branches: int = 0, leaves: int = 0, threats: dict[str, int] = None):
        self.trees = trees
        self.branches = branches
        self.leaves = leaves
        self.threats = threats or {}

    def update(self, trees: int = None, branches: int = None, leaves: int = None, threats: dict[str, int] = None):
        """Update forest status"""
        if trees is not None:
            self.trees = trees
        if branches is not None:
            self.branches = branches
        if leaves is not None:
            self.leaves = leaves
        if threats is not None:
            self.threats = threats

    def render(self, width: int = 70) -> Panel:
        """Render the panel"""
        text = Text()

        # Forest stats
        text.append(f"🌳 Trees: {self.trees} healthy  ", style=UIColors.FOREST)
        text.append(f"🌿 Branches: {self.branches}  ", style=UIColors.FOREST)
        text.append(f"🍃 Leaves: {self.leaves:,}\n", style=UIColors.FOREST)

        # Threats
        total_threats = sum(self.threats.values())
        if total_threats > 0:
            text.append("⚠️ Threats: ", style=UIColors.WARNING)

            threat_map = {
                "CROW": ("🐦‍⬛", "crows"),
                "SQUIRREL": ("🐿️", "squirrel"),
                "PARASITE": ("🐛", "parasites"),
                "MAGPIE": ("🐦", "magpies"),
                "SNAKE": ("🐍", "snakes"),
                "BAT": ("🦇", "bats"),
            }

            threat_strs = []
            for key, (icon, name) in threat_map.items():
                count = self.threats.get(key, 0)
                if count > 0:
                    threat_strs.append(f"{icon}x{count} ({name})")

            text.append("  ".join(threat_strs), style=UIColors.WARNING)
        else:
            text.append("✅ No threats detected", style=UIColors.SAFE)

        return Panel(text, title="FOREST STATUS", border_style=UIColors.FOREST, padding=(0, 1), width=width)

    def render_compact(self) -> str:
        """Render compact text version"""
        total_threats = sum(self.threats.values())
        return f"🌳 {self.trees} 🌿 {self.branches} 🍃 {self.leaves:,} ⚠️ {total_threats} threats"
