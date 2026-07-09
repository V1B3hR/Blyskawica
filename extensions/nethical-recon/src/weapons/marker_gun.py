"""
Marker Gun - Main Weapon Class
Silent Marker System for tagging threats

🔫 Arsenal Cichego Myśliwego:
"Cichy, z tłumikiem, naboje tracer - raz trafiony, zawsze widoczny"
"""

import datetime
import hashlib
from typing import Any

from .base import BaseTracer, BaseWeaponMode, Stain, WeaponMode


class MarkerGun:
    """
    Main weapon class for the Silent Marker System

    The marker gun can fire in three modes:
    - PNEUMATIC (0 dB): Whisper mode for soft reconnaissance
    - CO2_SILENT (10 dB): Silent mode for medium strikes
    - ELECTRIC (20 dB): Lightning mode for hard strikes

    Uses colored tracer ammunition to mark threats permanently.
    """

    def __init__(self, name: str = "Silent Marker"):
        self.name = name
        self.serial_number = self._generate_serial()
        self.current_mode: BaseWeaponMode | None = None
        self.available_modes: dict[WeaponMode, BaseWeaponMode] = {}
        self.ammo_inventory: dict[str, BaseTracer] = {}
        self.current_ammo: BaseTracer | None = None
        self.shots_fired = 0
        self.hits_successful = 0
        self.stains_created: list[Stain] = []
        self.armed = False
        self.safety = True
        self.created_at = datetime.datetime.now()

    def _generate_serial(self) -> str:
        """
        Generate unique serial number for weapon

        Note: Uses MD5 for simplicity. For production, consider using
        uuid.uuid4() or a more secure hash function like SHA256.
        """
        timestamp = str(datetime.datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()

    def register_mode(self, mode_type: WeaponMode, mode: BaseWeaponMode):
        """Register a weapon firing mode"""
        self.available_modes[mode_type] = mode
        if self.current_mode is None:
            self.current_mode = mode

    def set_mode(self, mode_type: WeaponMode) -> bool:
        """Change weapon firing mode"""
        if mode_type in self.available_modes:
            self.current_mode = self.available_modes[mode_type]
            return True
        return False

    def load_ammo(self, tracer: BaseTracer):
        """Load tracer ammunition"""
        color = tracer.color
        self.ammo_inventory[color] = tracer
        if self.current_ammo is None:
            self.current_ammo = tracer

    def select_ammo(self, color: str) -> bool:
        """Select ammunition by color"""
        if color in self.ammo_inventory:
            self.current_ammo = self.ammo_inventory[color]
            return True
        return False

    def arm(self):
        """Arm the weapon"""
        self.armed = True

    def disarm(self):
        """Disarm the weapon"""
        self.armed = False

    def safety_off(self):
        """Turn safety off"""
        self.safety = False

    def safety_on(self):
        """Turn safety on"""
        self.safety = True

    def fire(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Fire weapon at target

        Args:
            target: Dictionary containing target information
                   (ip, hostname, file_hash, ports, etc.)

        Returns:
            Dictionary with fire result including stain information
        """
        # Safety checks
        if not self.armed:
            return {"success": False, "error": "Weapon not armed", "shots_fired": 0}

        if self.safety:
            return {"success": False, "error": "Safety is engaged", "shots_fired": 0}

        if self.current_mode is None:
            return {"success": False, "error": "No firing mode selected", "shots_fired": 0}

        if self.current_ammo is None:
            return {"success": False, "error": "No ammunition loaded", "shots_fired": 0}

        # Fire the weapon
        self.shots_fired += 1
        fire_result = self.current_mode.fire(target, self.current_ammo)

        if fire_result.get("hit", False):
            self.hits_successful += 1

            # Create stain/tag
            tag_data = self.current_ammo.create_tag(target)
            stain = Stain(
                tag_id=tag_data["tag_id"],
                marker_type=tag_data["marker_type"],
                color=self.current_ammo.color,
                target=target,
                weapon_mode=self.current_mode.mode_name,
                threat_score=target.get("threat_score", 0.0),
                confidence=target.get("confidence", 0.0),
            )

            # Add forest location if provided
            if "forest_location" in target:
                stain.forest_location = target["forest_location"]

            # Add detection info if provided
            if "detected_by" in target:
                stain.detected_by = target["detected_by"]

            self.stains_created.append(stain)
            self.current_ammo.increment_use()

            return {
                "success": True,
                "hit": True,
                "shots_fired": 1,
                "mode_used": self.current_mode.mode_name,
                "ammo_used": self.current_ammo.color,
                "noise_level_db": self.current_mode.noise_level,
                "stain": stain.to_dict(),
                "message": f"Target marked with {self.current_ammo.color} tracer",
            }
        else:
            return {
                "success": True,
                "hit": False,
                "shots_fired": 1,
                "mode_used": self.current_mode.mode_name,
                "ammo_used": self.current_ammo.color,
                "message": "Shot fired but missed target",
            }

    def get_stain(self, tag_id: str) -> Stain | None:
        """Retrieve stain by tag ID"""
        for stain in self.stains_created:
            if stain.tag_id == tag_id:
                return stain
        return None

    def get_all_stains(self) -> list[dict[str, Any]]:
        """Get all created stains"""
        return [stain.to_dict() for stain in self.stains_created]

    def get_stains_by_type(self, marker_type: str) -> list[dict[str, Any]]:
        """Get stains filtered by marker type"""
        return [stain.to_dict() for stain in self.stains_created if stain.marker_type == marker_type]

    def get_statistics(self) -> dict[str, Any]:
        """Get weapon usage statistics"""
        accuracy = (self.hits_successful / self.shots_fired * 100) if self.shots_fired > 0 else 0

        # Count stains by type
        stain_counts = {}
        for stain in self.stains_created:
            marker_type = stain.marker_type
            stain_counts[marker_type] = stain_counts.get(marker_type, 0) + 1

        return {
            "weapon_name": self.name,
            "serial_number": self.serial_number,
            "armed": self.armed,
            "safety": self.safety,
            "current_mode": self.current_mode.mode_name if self.current_mode else None,
            "current_ammo": self.current_ammo.color if self.current_ammo else None,
            "shots_fired": self.shots_fired,
            "hits_successful": self.hits_successful,
            "accuracy_percent": round(accuracy, 2),
            "stains_created": len(self.stains_created),
            "stains_by_type": stain_counts,
            "modes_available": list(self.available_modes.keys()),
            "ammo_loaded": list(self.ammo_inventory.keys()),
            "created_at": self.created_at.isoformat(),
        }

    def get_status(self) -> str:
        """Get weapon status string"""
        status_parts = []
        status_parts.append(f"🔫 {self.name} (S/N: {self.serial_number})")
        status_parts.append(f"   Armed: {'✅' if self.armed else '❌'}")
        status_parts.append(f"   Safety: {'🔒 ON' if self.safety else '🔓 OFF'}")

        if self.current_mode:
            status_parts.append(f"   Mode: {self.current_mode.mode_name} ({self.current_mode.noise_level} dB)")
        else:
            status_parts.append("   Mode: None")

        if self.current_ammo:
            status_parts.append(f"   Ammo: {self.current_ammo.color} ({self.current_ammo.tracer_type.value})")
        else:
            status_parts.append("   Ammo: None")

        status_parts.append(
            f"   Shots: {self.shots_fired} | Hits: {self.hits_successful} | Stains: {len(self.stains_created)}"
        )

        return "\n".join(status_parts)

    def reset_statistics(self):
        """Reset weapon statistics (does not clear stains)"""
        self.shots_fired = 0
        self.hits_successful = 0
