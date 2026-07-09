"""
Sensor Manager
Orchestrates multiple sensors and manages their lifecycle
"""

import logging
import threading
import time
from typing import Any

from .base import BaseSensor, SensorStatus


class SensorManager:
    """
    Manages multiple sensors, coordinates their operation,
    and aggregates their alerts.
    """

    def __init__(self):
        """Initialize the Sensor Manager"""
        self.sensors: dict[str, BaseSensor] = {}
        self.logger = logging.getLogger("nethical.sensor_manager")
        self._initialize_logger()
        self._monitoring_thread = None
        self._stop_monitoring = False

    def _initialize_logger(self):
        """Initialize logging for the manager"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [SensorManager] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_sensor(self, sensor: BaseSensor) -> bool:
        """
        Register a new sensor

        Args:
            sensor: Sensor instance to register

        Returns:
            bool: True if registered successfully
        """
        if sensor.name in self.sensors:
            self.logger.warning(f"Sensor {sensor.name} already registered")
            return False

        self.sensors[sensor.name] = sensor
        self.logger.info(f"Registered sensor: {sensor.name}")
        return True

    def unregister_sensor(self, name: str) -> bool:
        """
        Unregister a sensor

        Args:
            name: Name of the sensor to unregister

        Returns:
            bool: True if unregistered successfully
        """
        if name not in self.sensors:
            self.logger.warning(f"Sensor {name} not found")
            return False

        # Stop sensor if running
        sensor = self.sensors[name]
        if sensor.status == SensorStatus.RUNNING:
            sensor.stop()

        del self.sensors[name]
        self.logger.info(f"Unregistered sensor: {name}")
        return True

    def start_sensor(self, name: str) -> bool:
        """
        Start a specific sensor

        Args:
            name: Name of the sensor to start

        Returns:
            bool: True if started successfully
        """
        if name not in self.sensors:
            self.logger.error(f"Sensor {name} not found")
            return False

        sensor = self.sensors[name]
        if sensor.start():
            self.logger.info(f"Started sensor: {name}")
            return True
        else:
            self.logger.error(f"Failed to start sensor: {name}")
            return False

    def stop_sensor(self, name: str) -> bool:
        """
        Stop a specific sensor

        Args:
            name: Name of the sensor to stop

        Returns:
            bool: True if stopped successfully
        """
        if name not in self.sensors:
            self.logger.error(f"Sensor {name} not found")
            return False

        sensor = self.sensors[name]
        if sensor.stop():
            self.logger.info(f"Stopped sensor: {name}")
            return True
        else:
            self.logger.error(f"Failed to stop sensor: {name}")
            return False

    def start_all(self) -> int:
        """
        Start all registered sensors

        Returns:
            int: Number of sensors started successfully
        """
        count = 0
        for name in self.sensors:
            if self.start_sensor(name):
                count += 1

        self.logger.info(f"Started {count}/{len(self.sensors)} sensors")
        return count

    def stop_all(self) -> int:
        """
        Stop all running sensors

        Returns:
            int: Number of sensors stopped successfully
        """
        count = 0
        for name in self.sensors:
            if self.stop_sensor(name):
                count += 1

        self.logger.info(f"Stopped {count}/{len(self.sensors)} sensors")
        return count

    def get_sensor(self, name: str) -> BaseSensor | None:
        """
        Get a sensor by name

        Args:
            name: Name of the sensor

        Returns:
            Sensor instance or None if not found
        """
        return self.sensors.get(name)

    def list_sensors(self) -> list[str]:
        """
        List all registered sensor names

        Returns:
            List of sensor names
        """
        return list(self.sensors.keys())

    def get_all_alerts(self, severity: str | None = None) -> dict[str, list]:
        """
        Get alerts from all sensors

        Args:
            severity: Optional filter by severity

        Returns:
            Dictionary mapping sensor names to their alerts
        """
        alerts = {}
        for name, sensor in self.sensors.items():
            sensor_alerts = sensor.get_alerts(severity)
            if sensor_alerts:
                alerts[name] = [a.to_dict() for a in sensor_alerts]

        return alerts

    def get_status_all(self) -> dict[str, Any]:
        """
        Get status of all sensors

        Returns:
            Dictionary with status of all sensors
        """
        status = {}
        for name, sensor in self.sensors.items():
            status[name] = sensor.get_status()

        return status

    def clear_all_alerts(self):
        """Clear alerts from all sensors"""
        for sensor in self.sensors.values():
            sensor.clear_alerts()

        self.logger.info("Cleared alerts from all sensors")

    def health_check(self) -> dict[str, Any]:
        """
        Perform health check on all sensors

        Returns:
            Dictionary with health status
        """
        health = {"total_sensors": len(self.sensors), "running": 0, "stopped": 0, "error": 0, "paused": 0, "idle": 0}

        for sensor in self.sensors.values():
            status = sensor.status
            if status == SensorStatus.RUNNING:
                health["running"] += 1
            elif status == SensorStatus.STOPPED:
                health["stopped"] += 1
            elif status == SensorStatus.ERROR:
                health["error"] += 1
            elif status == SensorStatus.PAUSED:
                health["paused"] += 1
            elif status == SensorStatus.IDLE:
                health["idle"] += 1

        health["healthy"] = health["error"] == 0
        return health

    def start_monitoring(self, interval: int = 60):
        """
        Start continuous monitoring thread

        Args:
            interval: Check interval in seconds
        """
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self.logger.warning("Monitoring already running")
            return

        self._stop_monitoring = False
        self._monitoring_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self._monitoring_thread.start()
        self.logger.info(f"Started monitoring with {interval}s interval")

    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        self.logger.info("Stopped monitoring")

    def _monitor_loop(self, interval: int):
        """
        Internal monitoring loop

        Args:
            interval: Check interval in seconds
        """
        while not self._stop_monitoring:
            try:
                # Perform health check
                health = self.health_check()

                # Log any sensors in error state
                for name, sensor in self.sensors.items():
                    if sensor.status == SensorStatus.ERROR:
                        self.logger.error(f"Sensor {name} is in ERROR state")

                # Check for critical alerts
                critical_alerts = self.get_all_alerts(severity="CRITICAL")
                if critical_alerts:
                    self.logger.critical(f"Critical alerts from {len(critical_alerts)} sensors")

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

            # Sleep for interval
            time.sleep(interval)
