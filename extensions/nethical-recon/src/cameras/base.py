"""
Base Camera Class
Provides the foundation for all camera implementations in Nethical Recon

Cameras are the "IR Night Vision" components that see into the dark web,
hidden services, and deep infrastructure that normal sensors can't detect.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any


class CameraMode(Enum):
    """Camera operational modes - different "vision" types"""

    NIGHT = "night"  # 🌙 Nocny - Shodan/Censys (hidden services)
    BAD_WEATHER = "bad_weather"  # 🌧️ Zła pogoda - theHarvester (OSINT through fog)
    THERMAL = "thermal"  # 🔥 Termowizja - Masscan + banner (hot/active ports)
    GHOST = "ghost"  # 👻 Widmo - DNS enumeration (invisible subdomains)
    XRAY = "xray"  # 🕳️ Rentgen - SSL/TLS (through encryption)
    MASK = "mask"  # 🎭 Maska - WAF detection (hidden protections)


class CameraStatus(Enum):
    """Camera operational status"""

    IDLE = "idle"
    SCANNING = "scanning"
    STOPPED = "stopped"
    ERROR = "error"
    PAUSED = "paused"


class CameraDiscovery:
    """Represents a discovery made by a camera"""

    def __init__(
        self, discovery_type: str, target: str, data: dict[str, Any], confidence: float = 1.0, severity: str = "INFO"
    ):
        self.timestamp = datetime.now()
        self.discovery_type = discovery_type  # service, subdomain, vulnerability, etc.
        self.target = target
        self.data = data
        self.confidence = confidence  # 0.0 to 1.0
        self.severity = severity  # INFO, WARNING, CRITICAL

    def to_dict(self) -> dict[str, Any]:
        """Convert discovery to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "discovery_type": self.discovery_type,
            "target": self.target,
            "data": self.data,
            "confidence": self.confidence,
            "severity": self.severity,
        }


class BaseCamera(ABC):
    """
    Abstract base class for all cameras (IR scanners)

    Cameras use various techniques to discover hidden infrastructure:
    - Night vision (Shodan/Censys) - sees in the dark
    - Bad weather vision (theHarvester) - sees through fog
    - Thermal vision (Masscan) - detects heat signatures
    - Ghost vision (DNS enum) - sees the invisible
    - X-ray vision (SSL analysis) - sees through walls
    - Mask detection (WAF detection) - sees hidden defenses
    """

    def __init__(self, name: str, mode: CameraMode, config: dict[str, Any] = None):
        """
        Initialize the camera

        Args:
            name: Unique name for this camera instance
            mode: Camera mode (night, thermal, ghost, etc.)
            config: Configuration dictionary for camera-specific settings
        """
        self.name = name
        self.mode = mode
        self.config = config or {}
        self.status = CameraStatus.IDLE
        self.discoveries: list[CameraDiscovery] = []
        self.logger = logging.getLogger(f"nethical.camera.{name}")
        self._initialize_logger()

    def _initialize_logger(self):
        """Initialize logging for this camera"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f"[%(asctime)s] [📷 {self.name}] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @abstractmethod
    def scan(self, target: str) -> dict[str, Any]:
        """
        Perform a scan on the target

        Args:
            target: Target domain, IP, or identifier

        Returns:
            Dict containing scan results
        """
        pass

    def start(self, target: str) -> bool:
        """
        Start the camera scanning

        Args:
            target: Target to scan

        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.status = CameraStatus.SCANNING
            self.logger.info(f"Camera {self.name} starting scan on {target}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start camera: {e}")
            self.status = CameraStatus.ERROR
            return False

    def stop(self) -> bool:
        """
        Stop the camera scanning

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            self.status = CameraStatus.STOPPED
            self.logger.info(f"Camera {self.name} stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop camera: {e}")
            return False

    def pause(self) -> bool:
        """
        Pause the camera

        Returns:
            bool: True if paused successfully, False otherwise
        """
        if self.status == CameraStatus.SCANNING:
            self.status = CameraStatus.PAUSED
            self.logger.info(f"Camera {self.name} paused")
            return True
        return False

    def resume(self) -> bool:
        """
        Resume the camera from paused state

        Returns:
            bool: True if resumed successfully, False otherwise
        """
        if self.status == CameraStatus.PAUSED:
            self.status = CameraStatus.SCANNING
            self.logger.info(f"Camera {self.name} resumed")
            return True
        return False

    def record_discovery(
        self, discovery_type: str, target: str, data: dict[str, Any], confidence: float = 1.0, severity: str = "INFO"
    ):
        """
        Record a discovery made by this camera

        Args:
            discovery_type: Type of discovery (service, subdomain, etc.)
            target: Target that was discovered
            data: Discovery data
            confidence: Confidence level (0.0 to 1.0)
            severity: Severity level (INFO, WARNING, CRITICAL)
        """
        discovery = CameraDiscovery(discovery_type, target, data, confidence, severity)
        self.discoveries.append(discovery)

        # Log based on severity
        if severity == "CRITICAL":
            self.logger.critical(f"Discovery: {discovery_type} on {target}")
        elif severity == "WARNING":
            self.logger.warning(f"Discovery: {discovery_type} on {target}")
        else:
            self.logger.info(f"Discovery: {discovery_type} on {target}")

        return discovery

    def get_discoveries(self, discovery_type: str | None = None, severity: str | None = None) -> list[CameraDiscovery]:
        """
        Get discoveries from this camera

        Args:
            discovery_type: Optional filter by discovery type
            severity: Optional filter by severity

        Returns:
            List of discoveries
        """
        results = self.discoveries

        if discovery_type:
            results = [d for d in results if d.discovery_type == discovery_type]

        if severity:
            results = [d for d in results if d.severity == severity]

        return results

    def clear_discoveries(self):
        """Clear all discoveries"""
        self.discoveries.clear()

    def get_status(self) -> dict[str, Any]:
        """
        Get current camera status

        Returns:
            Dictionary with status information
        """
        return {
            "name": self.name,
            "mode": self.mode.value,
            "status": self.status.value,
            "discovery_count": len(self.discoveries),
            "config": self.config,
        }

    def validate_config(self) -> bool:
        """
        Validate camera configuration (can be overridden)

        Returns:
            bool: True if config is valid, False otherwise
        """
        return True

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about discoveries

        Returns:
            Dictionary with statistics
        """
        total = len(self.discoveries)
        by_type = {}
        by_severity = {"INFO": 0, "WARNING": 0, "CRITICAL": 0}

        for discovery in self.discoveries:
            # Count by type
            by_type[discovery.discovery_type] = by_type.get(discovery.discovery_type, 0) + 1

            # Count by severity
            by_severity[discovery.severity] = by_severity.get(discovery.severity, 0) + 1

        return {"total_discoveries": total, "by_type": by_type, "by_severity": by_severity, "mode": self.mode.value}
