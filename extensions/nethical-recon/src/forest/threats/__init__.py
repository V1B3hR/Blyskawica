"""
forest/threats/__init__.py
Threats module initialization.
"""

from .base import BaseThreat, ThreatSeverity, ThreatType
from .bat import Bat
from .crow import Crow
from .detector import ThreatDetector
from .magpie import Magpie
from .parasite import Parasite
from .snake import Snake
from .squirrel import Squirrel

__all__ = [
    "BaseThreat",
    "ThreatType",
    "ThreatSeverity",
    "Crow",
    "Magpie",
    "Squirrel",
    "Snake",
    "Parasite",
    "Bat",
    "ThreatDetector",
]
