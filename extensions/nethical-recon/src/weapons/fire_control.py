"""
Fire Control System
Controls weapon firing sequence and manages engagement

Provides automated and manual fire control for the marker gun,
including safety checks and engagement protocols.
"""

import datetime
from dataclasses import dataclass
from typing import Any

from .base import WeaponMode
from .marker_gun import MarkerGun
from .targeting import Target, TargetingSystem


@dataclass
class FireResult:
    """Result of a firing action"""

    success: bool
    target_id: str
    timestamp: str
    mode_used: str
    ammo_used: str
    hit: bool
    stain_id: str | None = None
    message: str = ""
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "target_id": self.target_id,
            "timestamp": self.timestamp,
            "mode_used": self.mode_used,
            "ammo_used": self.ammo_used,
            "hit": self.hit,
            "stain_id": self.stain_id,
            "message": self.message,
            "errors": self.errors,
        }


class FireControlSystem:
    """
    Fire control system for coordinated weapon operations

    Manages the complete firing sequence from target acquisition
    to engagement and post-firing analysis.
    """

    def __init__(self, marker_gun: MarkerGun, targeting_system: TargetingSystem):
        """
        Initialize fire control system

        Args:
            marker_gun: MarkerGun instance to control
            targeting_system: TargetingSystem for target management
        """
        self.marker_gun = marker_gun
        self.targeting_system = targeting_system
        self.fire_history: list[FireResult] = []
        self.auto_fire_enabled = False
        self.auto_fire_threshold = 0.90  # 90% confidence for auto-fire
        self.engagement_log: list[dict[str, Any]] = []

    def engage_target(
        self, target: Target, weapon_mode: str | None = None, ammo_color: str | None = None
    ) -> FireResult:
        """
        Engage a target with the marker gun

        Args:
            target: Target to engage
            weapon_mode: Optional weapon mode override
            ammo_color: Optional ammo color override

        Returns:
            FireResult with engagement outcome
        """
        timestamp = datetime.datetime.now().isoformat()

        # Validate target
        validation = self.targeting_system.validate_target(target)
        if not validation["valid"]:
            return FireResult(
                success=False,
                target_id=target.target_id,
                timestamp=timestamp,
                mode_used="NONE",
                ammo_used="NONE",
                hit=False,
                message="Target validation failed",
                errors=validation["reasons"],
            )

        # Lock target
        if not self.targeting_system.lock_target(target):
            return FireResult(
                success=False,
                target_id=target.target_id,
                timestamp=timestamp,
                mode_used="NONE",
                ammo_used="NONE",
                hit=False,
                message="Failed to lock target",
            )

        # Set weapon mode if specified
        if weapon_mode:
            mode_enum = WeaponMode[weapon_mode.upper()]
            if not self.marker_gun.set_mode(mode_enum):
                return FireResult(
                    success=False,
                    target_id=target.target_id,
                    timestamp=timestamp,
                    mode_used="NONE",
                    ammo_used="NONE",
                    hit=False,
                    message=f"Invalid weapon mode: {weapon_mode}",
                )
        else:
            # Use recommended mode
            recommended_mode = self.targeting_system.recommend_weapon_mode(target)
            self.marker_gun.set_mode(WeaponMode[recommended_mode])

        # Select ammo if specified
        if ammo_color:
            if not self.marker_gun.select_ammo(ammo_color):
                return FireResult(
                    success=False,
                    target_id=target.target_id,
                    timestamp=timestamp,
                    mode_used=self.marker_gun.current_mode.mode_name,
                    ammo_used="NONE",
                    hit=False,
                    message=f"Ammo color not loaded: {ammo_color}",
                )
        else:
            # Use recommended ammo
            recommended_ammo = self.targeting_system.recommend_ammo(target)
            self.marker_gun.select_ammo(recommended_ammo)

        # Fire weapon
        fire_result = self.marker_gun.fire(target.data)

        # Create result
        result = FireResult(
            success=fire_result.get("success", False),
            target_id=target.target_id,
            timestamp=timestamp,
            mode_used=fire_result.get("mode_used", "UNKNOWN"),
            ammo_used=fire_result.get("ammo_used", "UNKNOWN"),
            hit=fire_result.get("hit", False),
            stain_id=fire_result.get("stain", {}).get("tag_id") if fire_result.get("hit") else None,
            message=fire_result.get("message", ""),
        )

        # Log engagement
        self.fire_history.append(result)
        self.engagement_log.append({"timestamp": timestamp, "target": target.to_dict(), "result": result.to_dict()})

        # Unlock target
        self.targeting_system.unlock_target()

        return result

    def auto_engage(self) -> list[FireResult]:
        """
        Automatically engage high-confidence targets

        Only fires if auto_fire_enabled and target confidence
        meets or exceeds auto_fire_threshold.

        Returns:
            List of FireResult for each engagement
        """
        if not self.auto_fire_enabled:
            return []

        results = []

        # Get prioritized targets
        targets = self.targeting_system.prioritize_targets()

        for target in targets:
            # Check if target meets auto-fire criteria
            if target.confidence >= self.auto_fire_threshold:
                result = self.engage_target(target)
                results.append(result)

        return results

    def enable_auto_fire(self, threshold: float = 0.90):
        """
        Enable automatic firing mode

        Args:
            threshold: Minimum confidence required for auto-fire (default: 0.90)
        """
        self.auto_fire_enabled = True
        self.auto_fire_threshold = threshold

    def disable_auto_fire(self):
        """Disable automatic firing mode"""
        self.auto_fire_enabled = False

    def prepare_weapon(self, mode: str, ammo: str) -> bool:
        """
        Prepare weapon for firing

        Args:
            mode: Weapon mode (PNEUMATIC, CO2_SILENT, ELECTRIC)
            ammo: Ammo color (RED, PURPLE, ORANGE, etc.)

        Returns:
            True if preparation successful
        """
        # Set mode
        mode_enum = WeaponMode[mode.upper()]
        if not self.marker_gun.set_mode(mode_enum):
            return False

        # Select ammo
        if not self.marker_gun.select_ammo(ammo):
            return False

        # Arm weapon
        self.marker_gun.arm()
        self.marker_gun.safety_off()

        return True

    def safe_weapon(self):
        """Make weapon safe (safety on, disarm)"""
        self.marker_gun.safety_on()
        self.marker_gun.disarm()

    def get_engagement_statistics(self) -> dict[str, Any]:
        """Get engagement statistics"""
        total_engagements = len(self.fire_history)
        successful_hits = sum(1 for r in self.fire_history if r.hit)

        accuracy = (successful_hits / total_engagements * 100) if total_engagements > 0 else 0

        # Count by mode
        mode_counts = {}
        for result in self.fire_history:
            mode = result.mode_used
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        # Count by ammo
        ammo_counts = {}
        for result in self.fire_history:
            ammo = result.ammo_used
            ammo_counts[ammo] = ammo_counts.get(ammo, 0) + 1

        return {
            "total_engagements": total_engagements,
            "successful_hits": successful_hits,
            "accuracy_percent": round(accuracy, 2),
            "auto_fire_enabled": self.auto_fire_enabled,
            "auto_fire_threshold": self.auto_fire_threshold,
            "engagements_by_mode": mode_counts,
            "engagements_by_ammo": ammo_counts,
            "weapon_status": self.marker_gun.get_statistics(),
        }

    def get_recent_engagements(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent engagement logs"""
        return self.engagement_log[-count:] if self.engagement_log else []

    def clear_history(self):
        """Clear engagement history"""
        self.fire_history = []
        self.engagement_log = []
