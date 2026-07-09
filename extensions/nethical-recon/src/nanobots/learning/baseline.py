"""
Baseline Learning - Adaptive nanobot that learns normal patterns.

Part of the adaptive mode (🧬 learning behavior).
"""

import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


class BaselineLearner:
    """
    Learns and maintains baselines of normal behavior.

    Baselines help identify anomalies by understanding what "normal" looks like:
    - Request rates
    - Resource usage
    - Access patterns
    - Time-based behavior
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize baseline learner.

        Args:
            config: Configuration options:
                - learning_period_days: Days to learn baseline (default: 7)
                - min_samples: Minimum samples needed (default: 100)
                - update_interval_hours: Hours between updates (default: 24)
        """
        self.config = config or {}

        self.learning_period_days = self.config.get("learning_period_days", 7)
        self.min_samples = self.config.get("min_samples", 100)
        self.update_interval_hours = self.config.get("update_interval_hours", 24)

        # Baseline data
        self.baselines: dict[str, dict[str, Any]] = {}
        self.samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.last_update: dict[str, datetime] = {}

    def record_observation(self, metric_name: str, value: float, context: dict[str, Any] | None = None):
        """
        Record an observation for baseline learning.

        Args:
            metric_name: Name of the metric (e.g., 'request_rate', 'cpu_usage')
            value: Observed value
            context: Optional context (time of day, source, etc.)
        """
        observation = {"timestamp": datetime.now(), "value": value, "context": context or {}}

        self.samples[metric_name].append(observation)

        # Clean old samples
        self._clean_old_samples(metric_name)

        # Update baseline if needed
        if self._should_update_baseline(metric_name):
            self._update_baseline(metric_name)

    def _clean_old_samples(self, metric_name: str):
        """Remove samples older than learning period"""
        cutoff = datetime.now() - timedelta(days=self.learning_period_days)

        self.samples[metric_name] = [s for s in self.samples[metric_name] if s["timestamp"] > cutoff]

    def _should_update_baseline(self, metric_name: str) -> bool:
        """Check if baseline should be updated"""
        # Need minimum samples
        if len(self.samples[metric_name]) < self.min_samples:
            return False

        # Check time since last update
        last_update = self.last_update.get(metric_name)
        if last_update:
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
            if hours_since_update < self.update_interval_hours:
                return False

        return True

    def _update_baseline(self, metric_name: str):
        """Update baseline for a metric"""
        samples = self.samples[metric_name]

        if not samples:
            return

        values = [s["value"] for s in samples]

        # Calculate statistics
        baseline = {
            "metric_name": metric_name,
            "sample_count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "updated_at": datetime.now(),
            "learning_period_days": self.learning_period_days,
        }

        # Calculate percentiles
        sorted_values = sorted(values)
        baseline["p25"] = sorted_values[len(sorted_values) // 4]
        baseline["p75"] = sorted_values[3 * len(sorted_values) // 4]
        baseline["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
        baseline["p99"] = sorted_values[int(len(sorted_values) * 0.99)]

        self.baselines[metric_name] = baseline
        self.last_update[metric_name] = datetime.now()

    def get_baseline(self, metric_name: str) -> dict[str, Any] | None:
        """
        Get baseline for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Baseline data or None
        """
        return self.baselines.get(metric_name)

    def is_anomalous(self, metric_name: str, value: float, sensitivity: float = 2.0) -> dict[str, Any]:
        """
        Check if a value is anomalous compared to baseline.

        Args:
            metric_name: Name of the metric
            value: Value to check
            sensitivity: Standard deviations from mean (default: 2.0)

        Returns:
            Dict with anomaly detection results
        """
        baseline = self.baselines.get(metric_name)

        if not baseline:
            return {"is_anomalous": False, "reason": "no_baseline", "confidence": 0.0}

        mean = baseline["mean"]
        stdev = baseline["stdev"]

        # Calculate z-score
        if stdev > 0:
            z_score = abs((value - mean) / stdev)
        else:
            z_score = 0

        # Check if anomalous
        is_anomalous = z_score > sensitivity

        # Determine severity
        if z_score > sensitivity * 2:
            severity = "critical"
            confidence = 0.95
        elif z_score > sensitivity * 1.5:
            severity = "high"
            confidence = 0.85
        elif z_score > sensitivity:
            severity = "medium"
            confidence = 0.70
        else:
            severity = "normal"
            confidence = 0.50

        return {
            "is_anomalous": is_anomalous,
            "severity": severity,
            "confidence": confidence if is_anomalous else 0.0,
            "z_score": z_score,
            "value": value,
            "baseline_mean": mean,
            "baseline_stdev": stdev,
            "deviation": value - mean,
            "deviation_percent": ((value - mean) / mean * 100) if mean > 0 else 0,
        }

    def get_all_baselines(self) -> dict[str, dict[str, Any]]:
        """Get all baselines"""
        return self.baselines.copy()

    def clear_baseline(self, metric_name: str) -> bool:
        """
        Clear baseline for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            True if cleared
        """
        if metric_name in self.baselines:
            del self.baselines[metric_name]
            self.samples[metric_name].clear()
            if metric_name in self.last_update:
                del self.last_update[metric_name]
            return True
        return False

    def clear_all_baselines(self):
        """Clear all baselines"""
        self.baselines.clear()
        self.samples.clear()
        self.last_update.clear()

    def export_baselines(self) -> dict[str, Any]:
        """
        Export baselines for persistence.

        Returns:
            Dictionary with all baseline data
        """
        return {
            "baselines": {
                name: {**baseline, "updated_at": baseline["updated_at"].isoformat()}
                for name, baseline in self.baselines.items()
            },
            "config": {
                "learning_period_days": self.learning_period_days,
                "min_samples": self.min_samples,
                "update_interval_hours": self.update_interval_hours,
            },
        }

    def import_baselines(self, data: dict[str, Any]) -> bool:
        """
        Import baselines from exported data.

        Args:
            data: Exported baseline data

        Returns:
            True if imported successfully
        """
        try:
            baselines = data.get("baselines", {})

            for name, baseline in baselines.items():
                # Convert timestamp back
                baseline["updated_at"] = datetime.fromisoformat(baseline["updated_at"])
                self.baselines[name] = baseline
                self.last_update[name] = baseline["updated_at"]

            return True
        except Exception:
            return False
