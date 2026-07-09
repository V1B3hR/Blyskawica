"""
Auto-Tuning Engine for Sensors
Automatically adjusts detection thresholds based on baseline behavior
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from statistics import mean, stdev


class BaselineProfile:
    """Represents a baseline profile for a metric"""

    def __init__(self, metric_name: str, initial_threshold: float):
        """
        Initialize baseline profile

        Args:
            metric_name: Name of the metric
            initial_threshold: Initial threshold value
        """
        self.metric_name = metric_name
        self.threshold = initial_threshold
        self.values: list[tuple[datetime, float]] = []
        self.baseline_mean = initial_threshold
        self.baseline_std = 0.0
        self.last_calibration = datetime.now()

    def add_value(self, value: float):
        """Add a new metric value"""
        self.values.append((datetime.now(), value))

    def calibrate(self, lookback_hours: int = 24, std_multiplier: float = 2.0):
        """
        Calibrate threshold based on recent values

        Args:
            lookback_hours: Hours of data to consider
            std_multiplier: Standard deviations above mean for threshold
        """
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        recent_values = [v for ts, v in self.values if ts >= cutoff_time]

        if len(recent_values) < 10:
            return  # Not enough data

        self.baseline_mean = mean(recent_values)
        self.baseline_std = stdev(recent_values) if len(recent_values) > 1 else 0.0

        # Set threshold to mean + (std_multiplier * std)
        self.threshold = self.baseline_mean + (std_multiplier * self.baseline_std)
        self.last_calibration = datetime.now()

    def is_anomalous(self, value: float) -> bool:
        """Check if a value exceeds the threshold"""
        return value > self.threshold

    def cleanup_old_values(self, max_age_hours: int = 168):
        """Remove values older than max_age_hours (default 7 days)"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        self.values = [(ts, v) for ts, v in self.values if ts >= cutoff_time]


class AutoTuningEngine:
    """
    Automatic threshold tuning engine
    Learns normal behavior and adjusts detection thresholds adaptively
    """

    def __init__(self, calibration_interval: int = 3600):
        """
        Initialize auto-tuning engine

        Args:
            calibration_interval: Seconds between automatic calibrations
        """
        self.logger = logging.getLogger("nethical.auto_tuning")
        self._initialize_logger()

        self.calibration_interval = calibration_interval
        self.profiles: dict[str, BaselineProfile] = {}
        self.last_calibration = datetime.now()

        # Auto-tuning configuration
        self.config = {
            "enabled": True,
            "lookback_hours": 24,
            "std_multiplier": 2.0,
            "min_samples": 10,
            "max_data_age_hours": 168,  # 7 days
        }

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [AutoTuning] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_metric(self, metric_name: str, initial_threshold: float) -> bool:
        """
        Register a new metric for auto-tuning

        Args:
            metric_name: Unique name for the metric
            initial_threshold: Initial threshold value

        Returns:
            bool: True if registered successfully
        """
        if metric_name in self.profiles:
            self.logger.warning(f"Metric {metric_name} already registered")
            return False

        profile = BaselineProfile(metric_name, initial_threshold)
        self.profiles[metric_name] = profile
        self.logger.info(f"Registered metric: {metric_name} (threshold={initial_threshold})")
        return True

    def record_value(self, metric_name: str, value: float):
        """
        Record a metric value

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if metric_name not in self.profiles:
            self.logger.warning(f"Metric {metric_name} not registered")
            return

        profile = self.profiles[metric_name]
        profile.add_value(value)

        # Check if calibration is needed
        if self.config["enabled"]:
            time_since_calibration = (datetime.now() - self.last_calibration).total_seconds()
            if time_since_calibration >= self.calibration_interval:
                self.calibrate_all()

    def is_anomalous(self, metric_name: str, value: float) -> tuple[bool, dict[str, Any]]:
        """
        Check if a value is anomalous

        Args:
            metric_name: Name of the metric
            value: Value to check

        Returns:
            Tuple of (is_anomalous, details)
        """
        if metric_name not in self.profiles:
            return False, {"error": "Metric not registered"}

        profile = self.profiles[metric_name]
        is_anomalous = profile.is_anomalous(value)

        details = {
            "value": value,
            "threshold": profile.threshold,
            "baseline_mean": profile.baseline_mean,
            "baseline_std": profile.baseline_std,
            "deviation": (value - profile.baseline_mean) / profile.baseline_std if profile.baseline_std > 0 else 0,
            "is_anomalous": is_anomalous,
        }

        return is_anomalous, details

    def calibrate_metric(self, metric_name: str):
        """
        Calibrate a specific metric

        Args:
            metric_name: Name of the metric to calibrate
        """
        if metric_name not in self.profiles:
            self.logger.warning(f"Metric {metric_name} not registered")
            return

        profile = self.profiles[metric_name]
        old_threshold = profile.threshold

        profile.calibrate(lookback_hours=self.config["lookback_hours"], std_multiplier=self.config["std_multiplier"])

        new_threshold = profile.threshold
        if abs(new_threshold - old_threshold) > 0.01:
            self.logger.info(f"Calibrated {metric_name}: threshold {old_threshold:.2f} → {new_threshold:.2f}")

    def calibrate_all(self):
        """Calibrate all registered metrics"""
        self.logger.info("Starting auto-calibration of all metrics")

        for metric_name in self.profiles:
            self.calibrate_metric(metric_name)

            # Cleanup old values
            profile = self.profiles[metric_name]
            profile.cleanup_old_values(self.config["max_data_age_hours"])

        self.last_calibration = datetime.now()
        self.logger.info("Auto-calibration completed")

    def get_threshold(self, metric_name: str) -> float | None:
        """
        Get current threshold for a metric

        Args:
            metric_name: Name of the metric

        Returns:
            Current threshold or None if not registered
        """
        if metric_name not in self.profiles:
            return None
        return self.profiles[metric_name].threshold

    def set_threshold(self, metric_name: str, threshold: float):
        """
        Manually set threshold for a metric

        Args:
            metric_name: Name of the metric
            threshold: New threshold value
        """
        if metric_name not in self.profiles:
            self.logger.warning(f"Metric {metric_name} not registered")
            return

        self.profiles[metric_name].threshold = threshold
        self.logger.info(f"Manually set threshold for {metric_name}: {threshold}")

    def get_profile_stats(self, metric_name: str) -> dict[str, Any] | None:
        """
        Get statistics for a metric profile

        Args:
            metric_name: Name of the metric

        Returns:
            Profile statistics or None if not registered
        """
        if metric_name not in self.profiles:
            return None

        profile = self.profiles[metric_name]
        return {
            "metric_name": metric_name,
            "threshold": profile.threshold,
            "baseline_mean": profile.baseline_mean,
            "baseline_std": profile.baseline_std,
            "sample_count": len(profile.values),
            "last_calibration": profile.last_calibration.isoformat(),
        }

    def get_all_statistics(self) -> dict[str, Any]:
        """Get statistics for all profiles"""
        return {
            "enabled": self.config["enabled"],
            "calibration_interval": self.calibration_interval,
            "total_metrics": len(self.profiles),
            "last_calibration": self.last_calibration.isoformat(),
            "profiles": {name: self.get_profile_stats(name) for name in self.profiles},
        }

    def enable(self):
        """Enable auto-tuning"""
        self.config["enabled"] = True
        self.logger.info("Auto-tuning enabled")

    def disable(self):
        """Disable auto-tuning"""
        self.config["enabled"] = False
        self.logger.info("Auto-tuning disabled")

    def configure(self, **kwargs):
        """
        Update configuration

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                self.logger.info(f"Updated config: {key} = {value}")
