"""
Main Dashboard - TABLET MYŚLIWEGO Command Center
Central command and control interface for Nethical Hunter
"""

import time

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .base import Alert, BirdType, SystemStatus, ThreatLevel, UIColors
from .panels import (
    AlertsFeedPanel,
    BirdsStatusPanel,
    ForestStatusPanel,
    NanobotsStatusPanel,
    SensorsStatusPanel,
    ThreatLevelPanel,
    WeaponStatusPanel,
)
from .screens import ForestViewScreen, SettingsScreen, StainReportScreen, TargetingScreen


class Dashboard:
    """
    Main Command Center Dashboard

    The central hub for all hunter operations - fast, readable, and organized by categories.
    This is where big decisions are made.
    """

    def __init__(self):
        self.console = Console()
        self.status = SystemStatus()

        # Initialize panels
        self.threat_panel = ThreatLevelPanel(self.status.threat_score)
        self.sensors_panel = SensorsStatusPanel(
            self.status.sensors_online, self.status.sensors_total, self.status.cameras_online
        )
        self.nanobots_panel = NanobotsStatusPanel(self.status.nanobots_active, self.status.nanobots_mode)
        self.birds_panel = BirdsStatusPanel(self.status.birds_status)
        self.alerts_panel = AlertsFeedPanel(max_alerts=4)
        self.forest_panel = ForestStatusPanel(
            self.status.forest_trees, self.status.forest_branches, self.status.forest_leaves, self.status.forest_threats
        )
        self.weapon_panel = WeaponStatusPanel(
            self.status.weapon_mode, self.status.weapon_status, self.status.weapon_stealth, self.status.ammo_counts
        )

        # Initialize screens
        self.targeting_screen = TargetingScreen()
        self.stain_report_screen = StainReportScreen()
        self.forest_view_screen = ForestViewScreen()
        self.settings_screen = SettingsScreen()

        self.current_screen = "dashboard"

    def update_status(self, status: SystemStatus):
        """Update system status"""
        self.status = status

        # Update all panels
        self.threat_panel.update(status.threat_score)
        self.sensors_panel.update(status.sensors_online, status.sensors_total, status.cameras_online)
        self.nanobots_panel.update(status.nanobots_active, status.nanobots_mode)
        self.forest_panel.update(
            status.forest_trees, status.forest_branches, status.forest_leaves, status.forest_threats
        )
        self.weapon_panel.update(status.weapon_mode, status.weapon_status, status.weapon_stealth, status.ammo_counts)

    def add_alert(self, alert: Alert):
        """Add a new alert to the feed"""
        self.alerts_panel.add_alert(alert)

    def render_header(self) -> Panel:
        """Render dashboard header"""
        title = Text()
        title.append("🎯 NETHICAL HUNTER v3.0 - COMMAND CENTER", style="bold white")

        # Live indicator
        status_text = Text()
        status_text.append("     [🔴 LIVE]", style="bold red")

        return Panel(Align.center(title), border_style=UIColors.BORDER, subtitle=status_text)

    def render_status_row(self) -> Layout:
        """Render top status row with key metrics"""
        layout = Layout()
        layout.split_row(
            Layout(self.threat_panel.render(width=20), name="threat"),
            Layout(self.sensors_panel.render(width=22), name="sensors"),
            Layout(self.nanobots_panel.render(width=18), name="nanobots"),
            Layout(self.birds_panel.render(width=16), name="birds"),
        )
        return layout

    def render_footer(self) -> Panel:
        """Render dashboard footer with navigation"""
        text = Text()
        text.append("[1]📡Sensors ", style=UIColors.SENSOR)
        text.append("[2]🔴Cameras ", style=UIColors.CAMERA)
        text.append("[3]🌳Forest ", style=UIColors.FOREST)
        text.append("[4]🦅Sky ", style=UIColors.BIRD)
        text.append("[5]🤖Nano ", style=UIColors.NANOBOT)
        text.append("[6]🔫Weapon", style=UIColors.WEAPON)

        return Panel(Align.center(text), border_style=UIColors.DIM)

    def render_dashboard(self) -> Layout:
        """Render the complete dashboard layout"""
        # Create main layout
        layout = Layout()

        # Split into header, body, footer
        layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))

        # Header
        layout["header"].update(self.render_header())

        # Body - split into sections
        layout["body"].split_column(
            Layout(name="status_row", size=7),
            Layout(name="forest", size=5),
            Layout(name="alerts", size=8),
            Layout(name="weapon", size=5),
        )

        # Status row
        layout["body"]["status_row"].update(self.render_status_row())

        # Forest status
        layout["body"]["forest"].update(self.forest_panel.render(width=76))

        # Alerts feed
        layout["body"]["alerts"].update(self.alerts_panel.render(width=76))

        # Weapon status
        layout["body"]["weapon"].update(self.weapon_panel.render(width=76))

        # Footer
        layout["footer"].update(self.render_footer())

        return layout

    def render(self):
        """Render the dashboard"""
        if self.current_screen == "dashboard":
            return self.render_dashboard()
        elif self.current_screen == "targeting":
            self.targeting_screen.render(self.console)
        elif self.current_screen == "stain_report":
            self.stain_report_screen.render(self.console)
        elif self.current_screen == "forest_view":
            self.forest_view_screen.render(self.console)
        elif self.current_screen == "settings":
            self.settings_screen.render(self.console)

    def show(self):
        """Display the dashboard"""
        if self.current_screen == "dashboard":
            self.console.print(self.render_dashboard())
        else:
            self.render()

    def run_live(self, refresh_rate: float = 1.0):
        """Run dashboard with live updates"""
        with Live(self.render_dashboard(), console=self.console, refresh_per_second=refresh_rate, screen=True) as live:
            try:
                while True:
                    live.update(self.render_dashboard())
                    # In a real implementation, this would handle input and updates
                    time.sleep(1 / refresh_rate)
            except KeyboardInterrupt:
                pass

    def switch_screen(self, screen: str):
        """Switch to a different screen"""
        valid_screens = ["dashboard", "targeting", "stain_report", "forest_view", "settings"]
        if screen in valid_screens:
            self.current_screen = screen


def create_demo_status() -> SystemStatus:
    """Create demo system status for testing"""
    status = SystemStatus()
    status.threat_level = ThreatLevel.ELEVATED
    status.threat_score = 6.2
    status.sensors_online = 16
    status.sensors_total = 16
    status.cameras_online = 4
    status.nanobots_active = 847
    status.nanobots_mode = "DEFENSE"
    status.birds_status = {"EAGLE": "PATROL", "FALCON": "HUNT", "OWL": "WATCH"}
    status.forest_trees = 12
    status.forest_branches = 847
    status.forest_leaves = 12453
    status.forest_threats = {"CROW": 2, "SQUIRREL": 1, "PARASITE": 0}
    status.weapon_status = "ARMED"
    status.weapon_mode = "CO2 Silent"
    status.weapon_stealth = 50
    status.ammo_counts = {"RED": 12, "PURPLE": 5, "ORANGE": 20, "YELLOW": 8, "BLACK": 15, "BROWN": 10}
    return status


def create_demo_alerts() -> list:
    """Create demo alerts for testing"""
    return [
        Alert(BirdType.FALCON, "Port scan from 192.168.1.105", level=ThreatLevel.ELEVATED),
        Alert(BirdType.OWL, "Unusual night activity on DB-Server", level=ThreatLevel.WARNING),
        Alert(BirdType.EAGLE, "Lateral movement! 🐿️ on tree-03", level=ThreatLevel.CRITICAL),
        Alert(BirdType.SPARROW, "Normal heartbeat all trees", level=ThreatLevel.INFO),
    ]


if __name__ == "__main__":
    # Demo mode
    dashboard = Dashboard()

    # Load demo data
    demo_status = create_demo_status()
    dashboard.update_status(demo_status)

    # Add demo alerts
    for alert in create_demo_alerts():
        dashboard.add_alert(alert)

    # Show dashboard
    dashboard.show()
