"""
Targeting Screen - Weapon targeting interface
"""

from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..base import ThreatType, UIColors
from ..widgets.progress_bars import create_confidence_bar


class Target:
    """Represents a target for weapon system"""

    def __init__(
        self,
        ip: str,
        port: int = 0,
        target_type: str = "UNKNOWN",
        forest_location: dict[str, str] = None,
        threat: ThreatType | None = None,
        confidence: float = 0.0,
        previous_stains: int = 0,
        detected_by: str = "Unknown",
    ):
        self.ip = ip
        self.port = port
        self.target_type = target_type
        self.forest_location = forest_location or {}
        self.threat = threat
        self.confidence = confidence
        self.previous_stains = previous_stains
        self.detected_by = detected_by


class TargetingScreen:
    """Screen for targeting and weapon control"""

    def __init__(self):
        self.current_target: Target | None = None
        self.selected_weapon = "CO2 Silent"
        self.selected_ammo = "BLACK"  # Crow marker

        self.weapon_modes = {"1": ("Pneumatic", "💨"), "2": ("CO2 Silent", "🧊"), "3": ("Electric", "⚡")}

        self.ammo_types = {
            "R": ("Malware", "🔴"),
            "P": ("Evil AI", "🟣"),
            "O": ("Suspicious IP", "🟠"),
            "Y": ("Backdoor", "🟡"),
            "B": ("Hidden Svc", "🔵"),
            "C": ("Crow", "🖤"),
            "S": ("Squirrel", "🤎"),
        }

    def set_target(self, target: Target):
        """Set the current target"""
        self.current_target = target

    def select_weapon(self, key: str):
        """Select weapon mode"""
        if key in self.weapon_modes:
            self.selected_weapon = self.weapon_modes[key][0]

    def select_ammo(self, key: str):
        """Select ammo type"""
        if key.upper() in self.ammo_types:
            self.selected_ammo = self.ammo_types[key.upper()][0]

    def render_target_info(self) -> Panel:
        """Render current target information"""
        if not self.current_target:
            return Panel(
                Text("No target selected", style=UIColors.DIM), title="CURRENT TARGET", border_style=UIColors.BORDER
            )

        target = self.current_target
        text = Text()

        # Target address
        address = f"🎯 {target.ip}"
        if target.port:
            address += f":{target.port}"
        text.append(address + "\n", style="bold " + UIColors.HIGHLIGHT)

        # Type
        text.append(f"Type: {target.target_type}\n", style=UIColors.TEXT)

        # Forest location
        if target.forest_location:
            loc = target.forest_location
            forest_str = f"Forest: {loc.get('tree', '?')} → {loc.get('branch', '?')} → {loc.get('leaf', '?')}\n"
            text.append(forest_str, style=UIColors.FOREST)

        # Threat
        if target.threat:
            text.append(f"Threat: {target.threat.icon} {target.threat.description.upper()}\n", style=UIColors.CRITICAL)

        # Confidence
        conf_bar = create_confidence_bar(target.confidence)
        text.append(f"Confidence: {conf_bar} {int(target.confidence * 100)}%\n", style=UIColors.TEXT)

        # Previous stains
        stain_text = "NEW TARGET" if target.previous_stains == 0 else f"{target.previous_stains} previous stains"
        text.append(f"Previous stains: {stain_text}\n", style=UIColors.TEXT)

        # Detected by
        text.append(f"Detected by: {target.detected_by}", style=UIColors.BIRD)

        return Panel(text, title="CURRENT TARGET", border_style=UIColors.BORDER, padding=(0, 1))

    def render_weapon_selector(self) -> Panel:
        """Render weapon selection panel"""
        table = Table(show_header=False, box=None, padding=(0, 1))

        for key, (name, icon) in self.weapon_modes.items():
            selected = "◀─" if name == self.selected_weapon else "   "
            table.add_row(f"[{key}] {icon} {name}", selected)

        return Panel(table, title="SELECT WEAPON", border_style=UIColors.WEAPON, padding=(0, 1))

    def render_ammo_selector(self) -> Panel:
        """Render ammo selection panel"""
        table = Table(show_header=False, box=None, padding=(0, 1))

        for key, (name, icon) in self.ammo_types.items():
            selected = "◀─" if name == self.selected_ammo else "   "
            table.add_row(f"[{key}] {icon} {name}", selected)

        return Panel(table, title="SELECT AMMO", border_style=UIColors.WEAPON, padding=(0, 1))

    def render(self, console: Console):
        """Render the complete targeting screen"""
        console.clear()

        # Title
        console.print(
            Panel(
                Text("🔫 TARGETING SYSTEM", justify="center", style="bold"),
                border_style=UIColors.BORDER,
                subtitle="[⚡ ARMED]",
            )
        )

        # Target info
        console.print(self.render_target_info())
        console.print()

        # Weapon and ammo selection side by side
        layout = Layout()
        layout.split_row(Layout(self.render_weapon_selector()), Layout(self.render_ammo_selector()))
        console.print(layout)
        console.print()

        # Controls
        console.print("[SPACE] 🔫 FIRE    [T] Track    [F] Forest View    [ESC] Back", style=UIColors.DIM)

    def fire(self) -> dict[str, Any]:
        """Execute fire command"""
        if not self.current_target:
            return {"success": False, "error": "No target selected"}

        return {
            "success": True,
            "target": self.current_target.ip,
            "weapon": self.selected_weapon,
            "ammo": self.selected_ammo,
            "confidence": self.current_target.confidence,
        }
