"""
Health Monitoring for Sensors
Tracks sensor health metrics and detects operational issues
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from enum import Enum

from .base import BaseSensor, SensorStatus


class HealthStatus(Enum):
    """Overall health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class SensorHealthMetrics:
    """Health metrics for a sensor"""

    def __init__(self, sensor_name: str):
        """
        Initialize health metrics

        Args:
            sensor_name: Name of the sensor
        """
        self.sensor_name = sensor_name
        self.last_check_time = datetime.now()
        self.uptime_start = datetime.now()

        # Performance metrics
        self.check_count = 0
        self.error_count = 0
        self.alert_count = 0

        # Response time tracking
        self.response_times: list[float] = []
        self.avg_response_time = 0.0
        self.max_response_time = 0.0

        # Status history
        self.status_changes: list[tuple[datetime, SensorStatus]] = []

        # Health score (0-100)
        self.health_score = 100.0
        self.health_status = HealthStatus.HEALTHY

    def record_check(self, response_time: float, success: bool):
        """
        Record a sensor check

        Args:
            response_time: Time taken for check in seconds
            success: Whether check was successful
        """
        self.check_count += 1
        self.last_check_time = datetime.now()

        if not success:
            self.error_count += 1

        # Track response time
        self.response_times.append(response_time)
        if len(self.response_times) > 100:
            self.response_times.pop(0)

        self.avg_response_time = sum(self.response_times) / len(self.response_times)
        self.max_response_time = max(self.response_times)

        # Update health score
        self._calculate_health_score()

    def record_alert(self):
        """Record that an alert was generated"""
        self.alert_count += 1

    def record_status_change(self, new_status: SensorStatus):
        """Record a status change"""
        self.status_changes.append((datetime.now(), new_status))

        # Keep only recent status changes
        cutoff = datetime.now() - timedelta(hours=24)
        self.status_changes = [(ts, status) for ts, status in self.status_changes if ts >= cutoff]

    def _calculate_health_score(self):
        """Calculate overall health score"""
        score = 100.0

        # Penalize for errors
        if self.check_count > 0:
            error_rate = self.error_count / self.check_count
            score -= error_rate * 30  # Up to -30 points for errors

        # Penalize for slow response times
        if self.avg_response_time > 5.0:
            score -= min(20, (self.avg_response_time - 5.0) * 2)  # Up to -20 points

        # Penalize for frequent status changes (instability)
        recent_changes = len([ts for ts, _ in self.status_changes if ts >= datetime.now() - timedelta(hours=1)])
        if recent_changes > 5:
            score -= min(20, (recent_changes - 5) * 4)  # Up to -20 points

        self.health_score = max(0.0, score)

        # Update health status
        if self.health_score >= 80:
            self.health_status = HealthStatus.HEALTHY
        elif self.health_score >= 60:
            self.health_status = HealthStatus.DEGRADED
        elif self.health_score >= 30:
            self.health_status = HealthStatus.UNHEALTHY
        else:
            self.health_status = HealthStatus.CRITICAL

    def get_uptime(self) -> float:
        """Get uptime in seconds"""
        return (datetime.now() - self.uptime_start).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "sensor_name": self.sensor_name,
            "health_score": self.health_score,
            "health_status": self.health_status.value,
            "uptime_seconds": self.get_uptime(),
            "check_count": self.check_count,
            "error_count": self.error_count,
            "alert_count": self.alert_count,
            "avg_response_time": self.avg_response_time,
            "max_response_time": self.max_response_time,
            "last_check": self.last_check_time.isoformat(),
            "status_changes_24h": len(self.status_changes),
        }


class HealthMonitor:
    """
    Monitors health of all sensors
    """

    def __init__(self):
        """Initialize health monitor"""
        self.logger = logging.getLogger("nethical.health_monitor")
        self._initialize_logger()

        self.metrics: dict[str, SensorHealthMetrics] = {}
        self.alert_thresholds = {
            "health_score_critical": 30.0,
            "health_score_warning": 60.0,
            "error_rate_warning": 0.1,
            "error_rate_critical": 0.3,
            "response_time_warning": 5.0,
            "response_time_critical": 10.0,
        }

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [HealthMonitor] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_sensor(self, sensor: BaseSensor):
        """
        Register a sensor for health monitoring

        Args:
            sensor: Sensor to monitor
        """
        if sensor.name not in self.metrics:
            self.metrics[sensor.name] = SensorHealthMetrics(sensor.name)
            self.logger.info(f"Registered sensor for health monitoring: {sensor.name}")

    def unregister_sensor(self, sensor_name: str):
        """
        Unregister a sensor

        Args:
            sensor_name: Name of sensor to unregister
        """
        if sensor_name in self.metrics:
            del self.metrics[sensor_name]
            self.logger.info(f"Unregistered sensor: {sensor_name}")

    def record_check(self, sensor_name: str, response_time: float, success: bool):
        """
        Record a sensor check result

        Args:
            sensor_name: Name of the sensor
            response_time: Time taken in seconds
            success: Whether check was successful
        """
        if sensor_name not in self.metrics:
            return

        metrics = self.metrics[sensor_name]
        metrics.record_check(response_time, success)

        # Check for health alerts
        self._check_health_alerts(sensor_name, metrics)

    def record_status_change(self, sensor_name: str, new_status: SensorStatus):
        """
        Record a sensor status change

        Args:
            sensor_name: Name of the sensor
            new_status: New status
        """
        if sensor_name not in self.metrics:
            return

        self.metrics[sensor_name].record_status_change(new_status)

    def record_alert(self, sensor_name: str):
        """
        Record that a sensor generated an alert

        Args:
            sensor_name: Name of the sensor
        """
        if sensor_name not in self.metrics:
            return

        self.metrics[sensor_name].record_alert()

    def _check_health_alerts(self, sensor_name: str, metrics: SensorHealthMetrics):
        """Check if health alerts should be raised"""

        # Check health score
        if metrics.health_score <= self.alert_thresholds["health_score_critical"]:
            self.logger.critical(f"Sensor {sensor_name} health CRITICAL: score={metrics.health_score:.1f}")
        elif metrics.health_score <= self.alert_thresholds["health_score_warning"]:
            self.logger.warning(f"Sensor {sensor_name} health DEGRADED: score={metrics.health_score:.1f}")

        # Check error rate
        if metrics.check_count > 10:
            error_rate = metrics.error_count / metrics.check_count
            if error_rate >= self.alert_thresholds["error_rate_critical"]:
                self.logger.critical(f"Sensor {sensor_name} error rate CRITICAL: {error_rate*100:.1f}%")
            elif error_rate >= self.alert_thresholds["error_rate_warning"]:
                self.logger.warning(f"Sensor {sensor_name} error rate HIGH: {error_rate*100:.1f}%")

        # Check response time
        if metrics.avg_response_time >= self.alert_thresholds["response_time_critical"]:
            self.logger.critical(f"Sensor {sensor_name} response time CRITICAL: {metrics.avg_response_time:.2f}s")
        elif metrics.avg_response_time >= self.alert_thresholds["response_time_warning"]:
            self.logger.warning(f"Sensor {sensor_name} response time HIGH: {metrics.avg_response_time:.2f}s")

    def get_sensor_health(self, sensor_name: str) -> dict[str, Any] | None:
        """
        Get health metrics for a sensor

        Args:
            sensor_name: Name of the sensor

        Returns:
            Health metrics dictionary or None
        """
        if sensor_name not in self.metrics:
            return None

        return self.metrics[sensor_name].to_dict()

    def get_all_health(self) -> dict[str, dict[str, Any]]:
        """Get health metrics for all sensors"""
        return {name: metrics.to_dict() for name, metrics in self.metrics.items()}

    def get_health_summary(self) -> dict[str, Any]:
        """Get overall health summary"""
        if not self.metrics:
            return {
                "total_sensors": 0,
                "overall_health": "unknown",
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "critical": 0,
            }

        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0,
        }

        total_score = 0.0
        for metrics in self.metrics.values():
            status_counts[metrics.health_status] += 1
            total_score += metrics.health_score

        avg_score = total_score / len(self.metrics)

        # Determine overall health
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_health = "critical"
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_health = "unhealthy"
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_health = "degraded"
        else:
            overall_health = "healthy"

        return {
            "total_sensors": len(self.metrics),
            "average_health_score": avg_score,
            "overall_health": overall_health,
            "healthy": status_counts[HealthStatus.HEALTHY],
            "degraded": status_counts[HealthStatus.DEGRADED],
            "unhealthy": status_counts[HealthStatus.UNHEALTHY],
            "critical": status_counts[HealthStatus.CRITICAL],
        }

    def set_threshold(self, threshold_name: str, value: float):
        """
        Update a health threshold

        Args:
            threshold_name: Name of threshold to update
            value: New threshold value
        """
        if threshold_name in self.alert_thresholds:
            self.alert_thresholds[threshold_name] = value
            self.logger.info(f"Updated threshold {threshold_name} = {value}")
