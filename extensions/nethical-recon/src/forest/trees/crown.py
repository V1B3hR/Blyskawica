"""
forest/trees/crown.py
Crown class - provides an overview of a host.

The crown sits atop the tree and provides:
- Overall health monitoring
- Threat detection summary
- Resource utilization overview
"""

from datetime import datetime
from typing import Any

from ..base import ForestComponent


class Crown(ForestComponent):
    """
    Represents the overview and monitoring of a host.

    Analogia: 👑 Korona - The top of the tree, overseeing everything below
    """

    def __init__(self, crown_id: str, tree_hostname: str, metadata: dict[str, Any] | None = None):
        """
        Initialize a crown.

        Args:
            crown_id: Unique identifier
            tree_hostname: Hostname of the tree this crown oversees
            metadata: Additional metadata
        """
        super().__init__(crown_id, f"Crown of {tree_hostname}", metadata)
        self.tree_hostname = tree_hostname
        self.observations = []  # List of observations/alerts
        self.scan_history = []  # History of scans performed

    def get_type(self) -> str:
        """Return component type"""
        return "crown"

    def add_observation(self, observation: str, severity: str = "INFO"):
        """
        Add an observation/alert to the crown.

        Args:
            observation: Description of what was observed
            severity: Severity level (INFO, WARNING, CRITICAL)
        """
        obs = {"timestamp": datetime.now().isoformat(), "observation": observation, "severity": severity}
        self.observations.append(obs)
        self.last_updated = datetime.now()

    def add_scan_record(self, scan_type: str, results: dict[str, Any]):
        """
        Add a scan record to the history.

        Args:
            scan_type: Type of scan performed
            results: Scan results
        """
        record = {"timestamp": datetime.now().isoformat(), "scan_type": scan_type, "results": results}
        self.scan_history.append(record)

    def get_recent_observations(self, count: int = 10) -> list[dict[str, Any]]:
        """Get the most recent observations"""
        return self.observations[-count:]

    def get_recent_scans(self, count: int = 5) -> list[dict[str, Any]]:
        """Get the most recent scans"""
        return self.scan_history[-count:]

    def get_critical_observations(self) -> list[dict[str, Any]]:
        """Get all critical observations"""
        return [obs for obs in self.observations if obs["severity"] == "CRITICAL"]

    def clear_old_observations(self, days: int = 7):
        """Clear observations older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        self.observations = [
            obs for obs in self.observations if datetime.fromisoformat(obs["timestamp"]).timestamp() > cutoff
        ]

    def get_info(self) -> dict[str, Any]:
        """Get crown information as dictionary"""
        info = super().get_info()
        info.update(
            {
                "tree_hostname": self.tree_hostname,
                "total_observations": len(self.observations),
                "critical_observations": len(self.get_critical_observations()),
                "total_scans": len(self.scan_history),
                "recent_observations": self.get_recent_observations(5),
            }
        )
        return info

    def get_visual_status(self) -> str:
        """Get visual representation of crown status"""
        if self.has_threats():
            return "👑⚠️ Crown - THREATS DETECTED"
        elif len(self.get_critical_observations()) > 0:
            return "👑⚠️ Crown - Critical Observations"
        else:
            return "👑 Crown - All Clear"

    def __str__(self):
        threat_info = f" ({self.get_threat_count()} threats)" if self.has_threats() else ""
        obs_info = f" ({len(self.observations)} observations)"
        return f"👑 Crown of {self.tree_hostname}{threat_info}{obs_info}"
