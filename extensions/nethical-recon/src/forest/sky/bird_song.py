"""
🎵 Bird Song - Alert Sound System

> "Each bird has its unique call - from chirp to roar"
"""

from enum import Enum
from typing import Any

from .base_bird import AlertLevel, BirdType


class BirdSong:
    """
    Bird Song Alert System

    Maps alert levels to bird sounds for intuitive threat communication
    """

    # Sound patterns for each alert level
    SOUNDS = {
        AlertLevel.INFO: {
            "sound": "chirp",
            "pattern": "♪",
            "volume": 1,
            "description": "Soft chirp - routine notification",
            "emoji": "🐦",
        },
        AlertLevel.WARNING: {
            "sound": "hoot",
            "pattern": "♪♪",
            "volume": 3,
            "description": "Owl hoot - unusual activity",
            "emoji": "🦉",
        },
        AlertLevel.ELEVATED: {
            "sound": "screech",
            "pattern": "♪♪♪!",
            "volume": 7,
            "description": "Falcon screech - suspicious behavior",
            "emoji": "🦅",
        },
        AlertLevel.CRITICAL: {
            "sound": "roar",
            "pattern": "♪♪♪!!!",
            "volume": 9,
            "description": "Eagle roar - active threat",
            "emoji": "🦅",
        },
        AlertLevel.BREACH: {
            "sound": "caw",
            "pattern": "♪♪♪♪!!!!",
            "volume": 10,
            "description": "Crow caws - confirmed compromise",
            "emoji": "🐦‍⬛",
        },
    }

    @classmethod
    def play_sound(cls, level: AlertLevel, bird_type: BirdType) -> str:
        """
        Generate sound representation for alert

        Args:
            level: Alert severity level
            bird_type: Type of bird making the call

        Returns:
            Sound representation string
        """
        sound_data = cls.SOUNDS.get(level, cls.SOUNDS[AlertLevel.INFO])

        bird_emoji = {BirdType.EAGLE: "🦅", BirdType.FALCON: "🦅", BirdType.OWL: "🦉", BirdType.SPARROW: "🐦"}

        emoji = bird_emoji.get(bird_type, "🐦")
        sound = sound_data["sound"].upper()
        pattern = sound_data["pattern"]

        return f"{emoji} [{sound}!] {pattern}"

    @classmethod
    def get_sound_info(cls, level: AlertLevel) -> dict[str, Any]:
        """Get detailed sound information for an alert level"""
        return cls.SOUNDS.get(level, cls.SOUNDS[AlertLevel.INFO]).copy()

    @classmethod
    def format_alert_message(cls, alert: Any) -> str:
        """
        Format an alert with appropriate bird song

        Args:
            alert: BirdAlert object

        Returns:
            Formatted alert message with sound
        """
        sound = cls.play_sound(alert.level, alert.bird_type)
        time_str = alert.timestamp.strftime("%H:%M:%S")

        return f"{sound} {time_str} - {alert.message}"

    @classmethod
    def volume_indicator(cls, level: AlertLevel) -> str:
        """
        Get visual volume indicator

        Returns:
            String like "🔊🔊🔊" for volume level
        """
        sound_data = cls.SOUNDS.get(level, cls.SOUNDS[AlertLevel.INFO])
        volume = sound_data["volume"]

        if volume <= 2:
            return "🔈"
        elif volume <= 5:
            return "🔉"
        else:
            return "🔊" * min(volume // 3, 3)


class AlertSeverity(Enum):
    """Alert severity classification"""

    ROUTINE = ("routine", 0)  # Normal operations
    NOTICE = ("notice", 1)  # Worth noting
    CONCERN = ("concern", 3)  # Requires attention
    URGENT = ("urgent", 7)  # Immediate attention
    EMERGENCY = ("emergency", 10)  # All hands on deck

    def __init__(self, name, priority):
        self.severity_name = name
        self.priority = priority


def get_alert_level_color(level: AlertLevel) -> str:
    """Get terminal color code for alert level"""
    colors = {
        AlertLevel.INFO: "\033[92m",  # Green
        AlertLevel.WARNING: "\033[93m",  # Yellow
        AlertLevel.ELEVATED: "\033[33m",  # Orange (dark yellow)
        AlertLevel.CRITICAL: "\033[91m",  # Red
        AlertLevel.BREACH: "\033[90m",  # Black/Gray
    }
    return colors.get(level, "\033[0m")


def format_colored_alert(alert: Any) -> str:
    """Format alert with terminal colors"""
    color = get_alert_level_color(alert.level)
    reset = "\033[0m"

    sound = BirdSong.play_sound(alert.level, alert.bird_type)
    time_str = alert.timestamp.strftime("%H:%M:%S")

    return f"{color}{sound} {time_str} - {alert.message}{reset}"


# Sound patterns as ASCII art
SOUND_PATTERNS = {
    "chirp": """
    ♪
    """,
    "hoot": """
    ♪ ♪
    """,
    "screech": """
    ♪♪♪
    ! ! !
    """,
    "roar": """
    ♪♪♪♪
    !!!!
    ▂▄▆█
    """,
    "caw": """
    ♪♪♪♪♪
    !!!!!
    ▂▄▆█▆▄▂
    """,
}


def visualize_sound(sound_type: str) -> str:
    """Get ASCII art visualization of sound"""
    return SOUND_PATTERNS.get(sound_type, SOUND_PATTERNS["chirp"])
