"""
Electric Mode - Lightning (20 dB)
⚡ Hard Strike - Maximum impact

Characteristics:
- Noise Level: 20 dB (quiet conversation level)
- Power Level: 9/10 (high)
- Effective Range: 150 meters
- Use Case: High-priority threats, when impact matters more than stealth
"""

import random
from typing import Any

from ..base import BaseTracer, BaseWeaponMode


class ElectricMode(BaseWeaponMode):
    """
    Electric weapon mode - electromagnetic accelerator

    This is the most powerful mode, using electromagnetic
    acceleration for maximum velocity and penetration.
    Higher noise but devastating marking capability.
    """

    def __init__(self):
        super().__init__()
        self.mode_name = "ELECTRIC"
        self.noise_level = 20  # dB - quiet but noticeable
        self.power_level = 9  # 1-10 scale
        self.effective_range = 150  # meters
        self.description = "Lightning mode - Electromagnetic accelerator"
        self.hit_probability = 0.96  # 96% base hit rate

    def fire(self, target: dict[str, Any], ammo: BaseTracer) -> dict[str, Any]:
        """
        Fire weapon in electric mode

        Args:
            target: Target information dictionary
            ammo: Tracer ammunition to fire

        Returns:
            Dictionary with fire result
        """
        # Calculate hit based on probability
        hit = random.random() < self.hit_probability

        # Electric mode delivers maximum impact
        result = {
            "hit": hit,
            "mode": self.mode_name,
            "noise_level_db": self.noise_level,
            "power_level": self.power_level,
            "effective_range_m": self.effective_range,
            "stealth_rating": 4,  # Lower stealth
            "detection_risk": "MODERATE",
            "ammo_type": ammo.tracer_type.value if ammo.tracer_type else "UNKNOWN",
        }

        if hit:
            result["status"] = "TARGET_MARKED"
            result["message"] = f"Lightning strike! Target heavily marked with {ammo.color} tracer."
            result["penetration"] = "HIGH"
            result["marker_durability"] = "PERMANENT"
        else:
            result["status"] = "MISS"
            result["message"] = "Shot missed - rare occurrence with electric mode"

        return result

    def get_tactical_info(self) -> dict[str, str]:
        """Get tactical information for this mode"""
        return {
            "best_for": "High-priority threats, critical targets, when certainty is needed",
            "advantages": "Maximum power, best accuracy, longest range, permanent marks",
            "disadvantages": "Higher noise level, increased detection risk",
            "recommended_ammo": "Red (confirmed malware), Purple (evil AI), Yellow (backdoors)",
            "operational_guidance": "Use for critical threats when immediate, certain marking is required",
        }
