"""
Base Sensor Class
Provides the foundation for all sensor implementations in Nethical Recon
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any


class SensorStatus(Enum):
    """Sensor operational status"""

    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    PAUSED = "paused"


class SensorAlert:
    """Represents an alert raised by a sensor"""

    def __init__(self, severity: str, message: str, data: dict[str, Any] = None):
        self.timestamp = datetime.now()
        self.severity = severity  # INFO, WARNING, CRITICAL
        self.message = message
        self.data = data or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "message": self.message,
            "data": self.data,
        }


class BaseSensor(ABC):
    """
    Abstract base class for all sensors

    Sensors are the "eyes and ears" of Nethical Recon, monitoring various
    aspects of network and system activity.
    """

    def __init__(self, name: str, config: dict[str, Any] = None):
        """
        Initialize the sensor

        Args:
            name: Unique name for this sensor instance
            config: Configuration dictionary for sensor-specific settings
        """
        self.name = name
        self.config = config or {}
        self.status = SensorStatus.IDLE
        self.alerts: list[SensorAlert] = []
        self.logger = logging.getLogger(f"nethical.sensor.{name}")
        self._initialize_logger()

    def _initialize_logger(self):
        """Initialize logging for this sensor"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f"[%(asctime)s] [{self.name}] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @abstractmethod
    def start(self) -> bool:
        """
        Start the sensor monitoring

        Returns:
            bool: True if started successfully, False otherwise
        """
        pass

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the sensor monitoring

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        pass

    @abstractmethod
    def check(self) -> dict[str, Any]:
        """
        Perform a single check/scan

        Returns:
            Dict containing check results
        """
        pass

    def pause(self) -> bool:
        """
        Pause the sensor (optional, can be overridden)

        Returns:
            bool: True if paused successfully, False otherwise
        """
        if self.status == SensorStatus.RUNNING:
            self.status = SensorStatus.PAUSED
            self.logger.info(f"Sensor {self.name} paused")
            return True
        return False

    def resume(self) -> bool:
        """
        Resume the sensor from paused state

        Returns:
            bool: True if resumed successfully, False otherwise
        """
        if self.status == SensorStatus.PAUSED:
            self.status = SensorStatus.RUNNING
            self.logger.info(f"Sensor {self.name} resumed")
            return True
        return False

    def raise_alert(self, severity: str, message: str, data: dict[str, Any] = None):
        """
        Raise an alert from this sensor

        Args:
            severity: Alert severity (INFO, WARNING, CRITICAL)
            message: Alert message
            data: Additional data related to the alert
        """
        alert = SensorAlert(severity, message, data)
        self.alerts.append(alert)

        # Log based on severity
        if severity == "CRITICAL":
            self.logger.critical(message)
        elif severity == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return alert

    def get_alerts(self, severity: str | None = None) -> list[SensorAlert]:
        """
        Get alerts from this sensor

        Args:
            severity: Optional filter by severity

        Returns:
            List of alerts
        """
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()

    def get_status(self) -> dict[str, Any]:
        """
        Get current sensor status

        Returns:
            Dictionary with status information
        """
        return {"name": self.name, "status": self.status.value, "alert_count": len(self.alerts), "config": self.config}

    def validate_config(self) -> bool:
        """
        Validate sensor configuration (can be overridden)

        Returns:
            bool: True if config is valid, False otherwise
        """
        return True
