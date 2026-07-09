"""
Weapons Modes Module
"""

from .co2_silent import CO2SilentMode
from .electric import ElectricMode
from .pneumatic import PneumaticMode

__all__ = ["PneumaticMode", "CO2SilentMode", "ElectricMode"]
