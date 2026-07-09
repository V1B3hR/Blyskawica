"""
Tracer Ammunition Module
Colored markers for different threat types
"""

from .tracer_black import BlackTracer
from .tracer_blue import BlueTracer
from .tracer_brown import BrownTracer
from .tracer_orange import OrangeTracer
from .tracer_purple import PurpleTracer
from .tracer_red import RedTracer
from .tracer_white import WhiteTracer
from .tracer_yellow import YellowTracer

__all__ = [
    "RedTracer",
    "PurpleTracer",
    "OrangeTracer",
    "YellowTracer",
    "BlueTracer",
    "WhiteTracer",
    "BlackTracer",
    "BrownTracer",
]
