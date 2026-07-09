"""
CO2 Silent Mode - Silent (10 dB)
🧊 Medium Hit - Balanced performance

Characteristics:
- Noise Level: 10 dB (very quiet, whisper-level)
- Power Level: 6/10 (medium)
- Effective Range: 100 meters
- Use Case: Standard operations, balanced stealth and effectiveness
"""

import random
from typing import Any

from ..base import BaseTracer, BaseWeaponMode


class CO2SilentMode(BaseWeaponMode):
    """
    CO2 Silent weapon mode - pressurized CO2 delivery

    This is the balanced mode, using CO2 cartridges for reliable
    delivery with good stealth characteristics. The workhorse
    mode for most marking operations.
    """

    def __init__(self):
        super().__init__()
        self.mode_name = "CO2_SILENT"
        self.noise_level = 10  # dB - very quiet
        self.power_level = 6  # 1-10 scale
        self.effective_range = 100  # meters
        self.description = "Silent mode - CO2-powered balanced delivery"
        self.hit_probability = 0.92  # 92% base hit rate

    def fire(self, target: dict[str, Any], ammo: BaseTracer) -> dict[str, Any]:
        """
        Fire weapon in CO2 silent mode

        Args:
            target: Target information dictionary
            ammo: Tracer ammunition to fire

        Returns:
            Dictionary with fire result
        """
        # Calculate hit based on probability
        hit = random.random() < self.hit_probability

        # CO2 mode offers balanced performance
        result = {
            "hit": hit,
            "mode": self.mode_name,
            "noise_level_db": self.noise_level,
            "power_level": self.power_level,
            "effective_range_m": self.effective_range,
            "stealth_rating": 7,  # Good stealth
            "detection_risk": "LOW",
            "ammo_type": ammo.tracer_type.value if ammo.tracer_type else "UNKNOWN",
        }

        if hit:
            result["status"] = "TARGET_MARKED"
            result["message"] = f"Silent strike successful. Target marked with {ammo.color} tracer."
            result["penetration"] = "MEDIUM"
        else:
            result["status"] = "MISS"
            result["message"] = "Shot missed - environmental factors or evasion"

        return result

    def get_tactical_info(self) -> dict[str, str]:
        """Get tactical information for this mode"""
        return {
            "best_for": "Standard operations, most threats, balanced approach",
            "advantages": "Balanced power/stealth, reliable, good range",
            "disadvantages": "Not the quietest or most powerful",
            "recommended_ammo": "Red (malware), Orange (suspicious IPs), Black (crows)",
            "operational_guidance": "Default mode for most marking operations",
        }
