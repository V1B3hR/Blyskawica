"""
ML-Based Anomaly Detection Service

Detects anomalous patterns in network traffic, host behavior, and security events
using machine learning baseline modeling and statistical outlier analysis.

Part of ROADMAP 5.0 Section V.14: Advanced Security Features
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""

    NETWORK_TRAFFIC = "network_traffic"
    PORT_SCAN = "port_scan"
    UNUSUAL_ACCESS = "unusual_access"
    DATA_EXFILTRATION = "data_exfiltration"
    LATERAL_MOVEMENT = "lateral_movement"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    BEHAVIORAL = "behavioral"
    STATISTICAL = "statistical"


@dataclass
class AnomalyEvent:
    """Represents a detected anomaly"""

    event_id: UUID = field(default_factory=uuid4)
    anomaly_type: AnomalyType = AnomalyType.BEHAVIORAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "medium"  # low, medium, high, critical
    confidence: float = 0.5  # 0.0 to 1.0
    source_asset: str = ""
    target_asset: str | None = None
    description: str = ""
    indicators: dict[str, Any] = field(default_factory=dict)
    baseline_deviation: float = 0.0  # Standard deviations from baseline
    recommended_actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BaselineProfile:
    """Baseline behavior profile for an asset or entity"""

    entity_id: str
    entity_type: str  # host, user, service, network_segment
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    observation_window_days: int = 30
    metrics: dict[str, Any] = field(default_factory=dict)  # Mean, std dev, percentiles
    normal_patterns: list[str] = field(default_factory=list)
    confidence_level: float = 0.0  # How well-established the baseline is


class AnomalyDetectionService:
    """
    ML-Based Anomaly Detection Service

    Features:
    - Baseline behavior modeling
    - Statistical outlier analysis
    - Multi-dimensional anomaly detection
    - Confidence scoring
    - Automatic baseline updates
    - Integration with existing threat intelligence

    Detection Methods:
    - Z-score analysis (statistical deviation)
    - Time series analysis
    - Behavioral pattern matching
    - Peer group comparison
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize anomaly detection service

        Args:
            config: Configuration options
                - sensitivity: Detection sensitivity (0.0-1.0), lower = more sensitive
                - baseline_window_days: Days of data for baseline (default: 30)
                - min_confidence_threshold: Minimum confidence to report (default: 0.6)
                - auto_update_baseline: Automatically update baselines (default: True)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.sensitivity = self.config.get("sensitivity", 0.5)
        self.baseline_window_days = self.config.get("baseline_window_days", 30)
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.6)
        self.auto_update_baseline = self.config.get("auto_update_baseline", True)

        # In-memory baseline storage (would use database in production)
        self._baselines: dict[str, BaselineProfile] = {}

        self.logger.info("Anomaly Detection Service initialized")

    def create_baseline(
        self, entity_id: str, entity_type: str, historical_data: list[dict[str, Any]]
    ) -> BaselineProfile:
        """
        Create a baseline profile from historical data

        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (host, user, service, etc.)
            historical_data: List of historical observations

        Returns:
            Baseline profile
        """
        self.logger.info(f"Creating baseline for {entity_type} {entity_id} with {len(historical_data)} observations")

        baseline = BaselineProfile(
            entity_id=entity_id,
            entity_type=entity_type,
            observation_window_days=self.baseline_window_days,
        )

        if not historical_data:
            self.logger.warning(f"No historical data for {entity_id}, baseline will be weak")
            baseline.confidence_level = 0.0
            self._baselines[entity_id] = baseline
            return baseline

        # Calculate baseline metrics (simplified - would use numpy/scipy in production)
        metrics = {}

        # Extract numeric features
        numeric_features = self._extract_numeric_features(historical_data)
        for feature_name, values in numeric_features.items():
            if values:
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = variance**0.5

                metrics[feature_name] = {
                    "mean": mean,
                    "std_dev": std_dev,
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

        # Identify normal patterns
        normal_patterns = self._identify_patterns(historical_data)

        baseline.metrics = metrics
        baseline.normal_patterns = normal_patterns
        baseline.confidence_level = min(1.0, len(historical_data) / 100.0)  # Confidence increases with data

        self._baselines[entity_id] = baseline
        self.logger.info(f"Baseline created for {entity_id} with confidence {baseline.confidence_level:.2f}")

        return baseline

    def detect_anomalies(self, entity_id: str, current_observations: list[dict[str, Any]]) -> list[AnomalyEvent]:
        """
        Detect anomalies in current observations against baseline

        Args:
            entity_id: Entity to check
            current_observations: Current activity to analyze

        Returns:
            List of detected anomalies
        """
        if entity_id not in self._baselines:
            self.logger.warning(f"No baseline for {entity_id}, cannot detect anomalies")
            return []

        baseline = self._baselines[entity_id]
        anomalies = []

        self.logger.debug(f"Analyzing {len(current_observations)} observations for {entity_id}")

        # Statistical anomaly detection
        for observation in current_observations:
            anomaly_events = self._check_statistical_anomalies(entity_id, baseline, observation)
            anomalies.extend(anomaly_events)

            # Behavioral pattern detection
            pattern_anomalies = self._check_behavioral_anomalies(entity_id, baseline, observation)
            anomalies.extend(pattern_anomalies)

        # Filter by confidence threshold
        filtered_anomalies = [a for a in anomalies if a.confidence >= self.min_confidence_threshold]

        self.logger.info(
            f"Detected {len(filtered_anomalies)} anomalies for {entity_id} "
            f"(filtered from {len(anomalies)} candidates)"
        )

        return filtered_anomalies

    def _check_statistical_anomalies(
        self, entity_id: str, baseline: BaselineProfile, observation: dict[str, Any]
    ) -> list[AnomalyEvent]:
        """Check for statistical outliers using Z-score analysis"""
        anomalies = []

        numeric_features = self._extract_numeric_features([observation])

        for feature_name, values in numeric_features.items():
            if not values or feature_name not in baseline.metrics:
                continue

            current_value = values[0]
            baseline_metrics = baseline.metrics[feature_name]

            mean = baseline_metrics["mean"]
            std_dev = baseline_metrics["std_dev"]

            if std_dev == 0:
                continue  # Cannot calculate Z-score with zero std dev

            # Calculate Z-score (standard deviations from mean)
            z_score = abs((current_value - mean) / std_dev)

            # Threshold depends on sensitivity (2.5 to 4.0 standard deviations)
            threshold = 2.5 + (1.5 * self.sensitivity)

            if z_score > threshold:
                # Statistical anomaly detected
                confidence = min(1.0, z_score / (threshold * 2))
                severity = self._calculate_severity(z_score, threshold)

                anomaly = AnomalyEvent(
                    anomaly_type=AnomalyType.STATISTICAL,
                    timestamp=observation.get("timestamp", datetime.utcnow()),
                    severity=severity,
                    confidence=confidence,
                    source_asset=entity_id,
                    description=f"Statistical anomaly in {feature_name}: {current_value:.2f} "
                    f"(baseline: {mean:.2f}±{std_dev:.2f})",
                    indicators={
                        "feature": feature_name,
                        "value": current_value,
                        "baseline_mean": mean,
                        "baseline_std_dev": std_dev,
                        "z_score": z_score,
                    },
                    baseline_deviation=z_score,
                    recommended_actions=[
                        "Investigate unusual activity",
                        "Compare with peer group behavior",
                        "Check for legitimate operational changes",
                    ],
                )

                anomalies.append(anomaly)
                self.logger.debug(f"Statistical anomaly: {feature_name}={current_value:.2f}, Z-score={z_score:.2f}")

        return anomalies

    def _check_behavioral_anomalies(
        self, entity_id: str, baseline: BaselineProfile, observation: dict[str, Any]
    ) -> list[AnomalyEvent]:
        """Check for behavioral pattern anomalies"""
        anomalies = []

        # Extract behavior patterns from observation
        observed_patterns = self._extract_patterns(observation)

        # Check for patterns not in baseline
        for pattern in observed_patterns:
            if pattern not in baseline.normal_patterns:
                # New/unusual pattern detected
                confidence = 0.7 if baseline.confidence_level > 0.5 else 0.5

                anomaly = AnomalyEvent(
                    anomaly_type=AnomalyType.BEHAVIORAL,
                    timestamp=observation.get("timestamp", datetime.utcnow()),
                    severity="medium",
                    confidence=confidence,
                    source_asset=entity_id,
                    description=f"Unusual behavioral pattern detected: {pattern}",
                    indicators={"pattern": pattern, "observation": observation},
                    recommended_actions=[
                        "Review activity logs",
                        "Verify if this is expected behavior",
                        "Check if similar patterns occur across multiple assets",
                    ],
                )

                anomalies.append(anomaly)
                self.logger.debug(f"Behavioral anomaly: {pattern}")

        return anomalies

    def update_baseline(self, entity_id: str, new_observations: list[dict[str, Any]]) -> None:
        """
        Update baseline with new observations

        Args:
            entity_id: Entity to update
            new_observations: New observations to incorporate
        """
        if entity_id not in self._baselines:
            self.logger.warning(f"No baseline for {entity_id} to update")
            return

        if not self.auto_update_baseline:
            self.logger.debug("Auto-update disabled, skipping baseline update")
            return

        baseline = self._baselines[entity_id]

        # Update metrics (simplified incremental update)
        numeric_features = self._extract_numeric_features(new_observations)

        for feature_name, new_values in numeric_features.items():
            if feature_name not in baseline.metrics:
                continue

            # Simple moving average update (would use more sophisticated methods in production)
            old_metrics = baseline.metrics[feature_name]
            old_count = old_metrics["count"]
            old_mean = old_metrics["mean"]

            new_count = len(new_values)
            new_mean = sum(new_values) / new_count if new_count > 0 else 0

            # Update mean
            total_count = old_count + new_count
            updated_mean = (old_mean * old_count + new_mean * new_count) / total_count

            baseline.metrics[feature_name]["mean"] = updated_mean
            baseline.metrics[feature_name]["count"] = total_count

        # Update patterns
        new_patterns = self._identify_patterns(new_observations)
        baseline.normal_patterns = list(set(baseline.normal_patterns + new_patterns))

        baseline.last_updated = datetime.utcnow()
        baseline.confidence_level = min(1.0, baseline.confidence_level + 0.01)  # Slowly increase confidence

        self.logger.info(f"Updated baseline for {entity_id}")

    def get_baseline(self, entity_id: str) -> BaselineProfile | None:
        """Get baseline profile for an entity"""
        return self._baselines.get(entity_id)

    def _extract_numeric_features(self, data: list[dict[str, Any]]) -> dict[str, list[float]]:
        """Extract numeric features from observations"""
        features: dict[str, list[float]] = {}

        for observation in data:
            for key, value in observation.items():
                if isinstance(value, (int, float)):
                    if key not in features:
                        features[key] = []
                    features[key].append(float(value))

        return features

    def _identify_patterns(self, data: list[dict[str, Any]]) -> list[str]:
        """Identify behavioral patterns in data"""
        patterns = []

        for observation in data:
            # Extract pattern identifiers
            pattern_elements = []

            if "action" in observation:
                pattern_elements.append(f"action:{observation['action']}")
            if "source" in observation:
                pattern_elements.append(f"source:{observation['source']}")
            if "destination" in observation:
                pattern_elements.append(f"dest:{observation['destination']}")

            if pattern_elements:
                pattern = "|".join(pattern_elements)
                patterns.append(pattern)

        return list(set(patterns))  # Return unique patterns

    def _extract_patterns(self, observation: dict[str, Any]) -> list[str]:
        """Extract patterns from a single observation"""
        return self._identify_patterns([observation])

    def _calculate_severity(self, z_score: float, threshold: float) -> str:
        """Calculate severity based on Z-score"""
        if z_score > threshold * 3:
            return "critical"
        elif z_score > threshold * 2:
            return "high"
        elif z_score > threshold * 1.5:
            return "medium"
        else:
            return "low"
