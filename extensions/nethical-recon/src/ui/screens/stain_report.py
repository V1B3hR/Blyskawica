"""
Stain Report Screen - Shows hunting session statistics
"""

from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..base import UIColors


class StainReportScreen:
    """Screen for stain reports and statistics"""

    def __init__(self, session_date: str = None):
        self.session_date = session_date or datetime.now().strftime("%Y-%m-%d")
        self.statistics: dict[str, int] = {}
        self.forest_map: dict[str, tuple] = {}  # tree_name: (status, threats)
        self.top_threats: list[dict] = []

    def set_statistics(self, stats: dict[str, int]):
        """Set stain statistics"""
        self.statistics = stats

    def set_forest_map(self, forest_map: dict[str, tuple]):
        """Set forest threat map"""
        self.forest_map = forest_map

    def set_top_threats(self, threats: list[dict]):
        """Set top threats list"""
        self.top_threats = threats

    def render_statistics(self) -> Panel:
        """Render statistics panel"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(justify="left")
        table.add_column(justify="left")
        table.add_column(justify="left")

        # Row 1
        table.add_row(
            f"🔴 Malware: {self.statistics.get('MALWARE', 0)}",
            f"🟣 Evil AI: {self.statistics.get('EVIL_AI', 0)}",
            f"🟠 Susp IP: {self.statistics.get('SUSPICIOUS_IP', 0)}",
        )

        # Row 2
        table.add_row(
            f"🟡 Backdoor: {self.statistics.get('BACKDOOR', 0)}",
            f"🔵 Hidden: {self.statistics.get('HIDDEN', 0)}",
            f"🖤 Crows: {self.statistics.get('CROW', 0)}",
        )

        # Row 3
        total = sum(self.statistics.values())
        table.add_row(f"🤎 Squirrels: {self.statistics.get('SQUIRREL', 0)}", "", f"⚪ TOTAL: {total}")

        return Panel(table, title="STATISTICS", border_style=UIColors.BORDER, padding=(0, 1))

    def render_forest_map(self) -> Panel:
        """Render forest threat map"""
        if not self.forest_map:
            return Panel(
                Text("No forest data available", style=UIColors.DIM),
                title="FOREST THREAT MAP",
                border_style=UIColors.FOREST,
            )

        text = Text()

        # Display trees in a row
        tree_displays = []
        for tree_name, (status, threats) in self.forest_map.items():
            tree_icon = "🌳" if status == "healthy" else "⚠️"
            threat_icon = threats if threats else "✅"
            tree_displays.append(
                f"{tree_icon} {tree_name}\n  │{threat_icon if threat_icon != '✅' else threat_icon}\n  └─{threat_icon}"
            )

        text.append("  ".join(tree_displays[:5]), style=UIColors.FOREST)  # Max 5 trees per row

        return Panel(text, title="FOREST THREAT MAP", border_style=UIColors.FOREST, padding=(0, 1))

    def render_top_threats(self) -> Panel:
        """Render top threats table"""
        if not self.top_threats:
            return Panel(
                Text("No threats detected", style=UIColors.SAFE),
                title="TOP THREATS (by Bird Detection)",
                border_style=UIColors.BORDER,
            )

        text = Text()
        text.append("─" * 70 + "\n", style=UIColors.DIM)

        for threat in self.top_threats[:10]:  # Top 10
            bird = threat.get("detected_by", "?")
            tag = threat.get("tag", "?")
            target = threat.get("target", "?")
            score = threat.get("score", 0.0)
            description = threat.get("description", "?")

            line = f"{bird} {tag:20} | {target:20} | Score: {score:.1f} | {description}\n"
            text.append(line, style=UIColors.TEXT)

        text.append("─" * 70, style=UIColors.DIM)

        return Panel(text, title="TOP THREATS (by Bird Detection)", border_style=UIColors.BORDER, padding=(0, 1))

    def render(self, console: Console):
        """Render the complete stain report screen"""
        console.clear()

        # Title
        console.print(
            Panel(
                Text(f"🎨 STAIN REPORT - Hunting Session {self.session_date}", justify="center", style="bold"),
                border_style=UIColors.BORDER,
            )
        )
        console.print()

        # Statistics
        console.print(self.render_statistics())
        console.print()

        # Forest map
        console.print(self.render_forest_map())
        console.print()

        # Top threats
        console.print(self.render_top_threats())
        console.print()

        # Controls
        console.print("[E] Export    [A] AI Analysis    [F] Forest View    [B] Back", style=UIColors.DIM)
