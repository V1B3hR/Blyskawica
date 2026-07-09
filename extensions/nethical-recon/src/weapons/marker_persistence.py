"""
Marker Persistence Validation for Weapons
Validates that markers remain persistent and detectable
"""

import logging
from typing import Any
from datetime import datetime, timedelta


class MarkerPersistenceValidator:
    """Validates marker persistence"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.marker_persistence")
        self._initialize_logger()
        self.markers: dict[str, dict[str, Any]] = {}
        self.validation_count = 0

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [MarkerPersistence] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_marker(self, marker_id: str, marker_data: dict[str, Any]):
        """Register a new marker"""
        self.markers[marker_id] = {
            "data": marker_data,
            "created_at": datetime.now(),
            "last_validated": None,
            "validation_count": 0,
            "is_persistent": True,
        }
        self.logger.info(f"Registered marker: {marker_id}")

    def validate_marker(self, marker_id: str) -> dict[str, Any]:
        """Validate marker persistence"""
        if marker_id not in self.markers:
            return {"valid": False, "error": "Marker not found"}

        marker = self.markers[marker_id]
        marker["last_validated"] = datetime.now()
        marker["validation_count"] += 1
        self.validation_count += 1

        # Check if marker is still detectable
        age = (datetime.now() - marker["created_at"]).total_seconds()
        max_age = marker["data"].get("max_age_seconds", 86400)  # 24 hours default

        is_persistent = age < max_age
        marker["is_persistent"] = is_persistent

        return {
            "valid": is_persistent,
            "marker_id": marker_id,
            "age_seconds": age,
            "validation_count": marker["validation_count"],
            "last_validated": marker["last_validated"].isoformat(),
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get persistence statistics"""
        persistent_count = sum(1 for m in self.markers.values() if m["is_persistent"])
        return {
            "total_markers": len(self.markers),
            "persistent_markers": persistent_count,
            "validation_count": self.validation_count,
            "persistence_rate": persistent_count / len(self.markers) if self.markers else 0.0,
        }
