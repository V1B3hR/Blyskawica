"""
Base UI components and utilities for Nethical Hunter Command Center
"""

from datetime import datetime
from enum import Enum


class ThreatLevel(Enum):
    """Threat level indicators"""

    INFO = ("🟢", "INFO", 0)
    WARNING = ("🟡", "WARNING", 1)
    ELEVATED = ("🟠", "ELEVATED", 2)
    CRITICAL = ("🔴", "CRITICAL", 3)
    BREACH = ("⚫", "BREACH", 4)

    def __init__(self, icon: str, label: str, severity: int):
        self.icon = icon
        self.label = label
        self.severity = severity


class BirdType(Enum):
    """Bird types for alerts"""

    SPARROW = ("🐦", "chirp", "Sparrow")
    OWL = ("🦉", "hoot...", "Owl")
    FALCON = ("🦅", "SCREECH!", "Falcon")
    EAGLE = ("🦅", "ROAR!!", "Eagle")
    CROW = ("🐦‍⬛", "CAW!", "Crow")

    def __init__(self, icon: str, sound: str, bird_name: str):
        self.icon = icon
        self.sound = sound
        self.bird_name = bird_name


class ThreatType(Enum):
    """Forest threat types"""

    CROW = ("🐦‍⬛", "crow", "Malware waiting")
    MAGPIE = ("🐦", "magpie", "Data Stealer")
    SQUIRREL = ("🐿️", "squirrel", "Lateral Movement")
    SNAKE = ("🐍", "snake", "Rootkit")
    PARASITE = ("🐛", "parasite", "Cryptominer")
    BAT = ("🦇", "bat", "Night-time Attack")

    def __init__(self, icon: str, code: str, description: str):
        self.icon = icon
        self.code = code
        self.description = description


class Alert:
    """Alert/Bird Song representation"""

    def __init__(
        self, bird: BirdType, message: str, timestamp: datetime | None = None, level: ThreatLevel = ThreatLevel.INFO
    ):
        self.bird = bird
        self.message = message
        self.timestamp = timestamp or datetime.now()
        self.level = level

    def __str__(self) -> str:
        time_str = self.timestamp.strftime("%H:%M")
        return f"{self.bird.icon} {time_str} [{self.bird.sound}] {self.bird.bird_name}: {self.message}"


class SystemStatus:
    """Overall system status for dashboard"""

    def __init__(self):
        self.threat_level: ThreatLevel = ThreatLevel.INFO
        self.threat_score: float = 0.0
        self.sensors_online: int = 0
        self.sensors_total: int = 0
        self.cameras_online: int = 0
        self.nanobots_active: int = 0
        self.nanobots_mode: str = "STANDBY"
        self.birds_status: dict[str, str] = {}
        self.forest_trees: int = 0
        self.forest_branches: int = 0
        self.forest_leaves: int = 0
        self.forest_threats: dict[str, int] = {}
        self.weapon_status: str = "ARMED"
        self.weapon_mode: str = "CO2 Silent"
        self.weapon_stealth: int = 50
        self.ammo_counts: dict[str, int] = {}
        self.recent_alerts: list[Alert] = []


class UIColors:
    """Color scheme for the UI"""

    # Threat levels
    SAFE = "green"
    WARNING = "yellow"
    ELEVATED = "bright_yellow"
    CRITICAL = "red"
    BREACH = "bright_red"

    # Components
    SENSOR = "cyan"
    CAMERA = "red"
    NANOBOT = "bright_magenta"
    WEAPON = "bright_yellow"
    FOREST = "green"
    BIRD = "bright_cyan"

    # General
    BORDER = "bright_blue"
    TEXT = "white"
    DIM = "bright_black"
    HIGHLIGHT = "bright_white"


def calculate_threat_level(score: float) -> ThreatLevel:
    """Calculate threat level from score"""
    if score < 3.0:
        return ThreatLevel.INFO
    elif score < 5.0:
        return ThreatLevel.WARNING
    elif score < 7.0:
        return ThreatLevel.ELEVATED
    elif score < 9.0:
        return ThreatLevel.CRITICAL
    else:
        return ThreatLevel.BREACH


def format_time(dt: datetime | None = None) -> str:
    """Format datetime for display"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%H:%M")


def format_date(dt: datetime | None = None) -> str:
    """Format date for display"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
