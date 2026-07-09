"""
Pneumatic Mode - Whisper (0 dB)
💨 Soft Recon - The quietest approach

Characteristics:
- Noise Level: 0 dB (completely silent)
- Power Level: 3/10 (soft)
- Effective Range: 50 meters
- Use Case: Stealthy reconnaissance, minimal detection risk
"""

import random
from typing import Any

from ..base import BaseTracer, BaseWeaponMode


class PneumaticMode(BaseWeaponMode):
    """
    Pneumatic weapon mode - silent air-powered marker

    This is the quietest mode, using compressed air to deliver
    the tracer with minimal noise and signature. Perfect for
    reconnaissance where stealth is paramount.
    """

    def __init__(self):
        super().__init__()
        self.mode_name = "PNEUMATIC"
        self.noise_level = 0  # dB - completely silent
        self.power_level = 3  # 1-10 scale
        self.effective_range = 50  # meters
        self.description = "Whisper mode - Silent air-powered delivery"
        self.hit_probability = 0.85  # 85% base hit rate

    def fire(self, target: dict[str, Any], ammo: BaseTracer) -> dict[str, Any]:
        """
        Fire weapon in pneumatic mode

        Args:
            target: Target information dictionary
            ammo: Tracer ammunition to fire

        Returns:
            Dictionary with fire result
        """
        # Calculate hit based on probability
        hit = random.random() < self.hit_probability

        # Pneumatic mode has lower power but higher stealth
        result = {
            "hit": hit,
            "mode": self.mode_name,
            "noise_level_db": self.noise_level,
            "power_level": self.power_level,
            "effective_range_m": self.effective_range,
            "stealth_rating": 10,  # Maximum stealth
            "detection_risk": "MINIMAL",
            "ammo_type": ammo.tracer_type.value if ammo.tracer_type else "UNKNOWN",
        }

        if hit:
            result["status"] = "TARGET_MARKED"
            result["message"] = f"Silent mark delivered. Target tagged with {ammo.color} tracer."
        else:
            result["status"] = "MISS"
            result["message"] = "Shot missed - wind deflection or target movement"

        return result

    def get_tactical_info(self) -> dict[str, str]:
        """Get tactical information for this mode"""
        return {
            "best_for": "Stealth operations, reconnaissance, low-priority threats",
            "advantages": "Completely silent, minimal detection risk, high stealth",
            "disadvantages": "Lower power, shorter effective range",
            "recommended_ammo": "Blue (hidden services), White (unknown)",
            "operational_guidance": "Use when detection must be avoided at all costs",
        }
