"""
ML Anomaly Detection - Adaptive nanobot using machine learning for anomaly detection.

Part of the adaptive mode (🧬 learning behavior).

Note: This is a lightweight implementation that doesn't require heavy ML libraries.
For production, consider integrating sklearn, tensorflow, or other ML frameworks.
"""

import math
from collections import deque
from datetime import datetime
from typing import Any


class SimpleMLAnomalyDetector:
    """
    Simple machine learning-based anomaly detector.

    Uses lightweight algorithms for anomaly detection:
    - Moving average with deviation
    - Simple pattern recognition
    - Feature-based scoring

    For production use, integrate proper ML libraries like sklearn.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize ML anomaly detector.

        Args:
            config: Configuration options:
                - window_size: Size of moving window (default: 100)
                - sensitivity: Detection sensitivity (default: 0.8)
                - features: List of features to track
        """
        self.config = config or {}

        self.window_size = self.config.get("window_size", 100)
        self.sensitivity = self.config.get("sensitivity", 0.8)
        self.features = self.config.get("features", ["request_rate", "error_rate", "response_time", "bandwidth"])

        # Data windows for each feature
        self.feature_windows: dict[str, deque] = {feature: deque(maxlen=self.window_size) for feature in self.features}

        # Anomaly history
        self.anomaly_history: list[dict[str, Any]] = []

        # Model state
        self.is_trained = False
        self.training_samples = 0

    def train(self, samples: list[dict[str, Any]]):
        """
        Train the detector on normal samples.

        Args:
            samples: List of normal behavior samples
        """
        for sample in samples:
            for feature in self.features:
                if feature in sample:
                    self.feature_windows[feature].append(sample[feature])

        self.training_samples = len(samples)
        self.is_trained = True

    def predict(self, sample: dict[str, Any]) -> dict[str, Any]:
        """
        Predict if sample is anomalous.

        Args:
            sample: Sample to evaluate

        Returns:
            Prediction with confidence and anomaly details
        """
        if not self.is_trained:
            return {"is_anomalous": False, "confidence": 0.0, "reason": "not_trained"}

        # Calculate anomaly scores for each feature
        feature_scores = {}
        for feature in self.features:
            if feature in sample:
                score = self._calculate_anomaly_score(feature, sample[feature])
                feature_scores[feature] = score

        if not feature_scores:
            return {"is_anomalous": False, "confidence": 0.0, "reason": "no_features"}

        # Aggregate scores
        avg_score = sum(feature_scores.values()) / len(feature_scores)
        max_score = max(feature_scores.values())

        # Determine if anomalous
        threshold = self.sensitivity
        is_anomalous = avg_score > threshold or max_score > threshold * 1.5

        # Calculate confidence
        if is_anomalous:
            confidence = min(avg_score / threshold, 1.0)
        else:
            confidence = 0.0

        # Determine severity
        if max_score > 0.9:
            severity = "critical"
        elif max_score > 0.75:
            severity = "high"
        elif max_score > 0.6:
            severity = "medium"
        else:
            severity = "low"

        # Identify anomalous features
        anomalous_features = [feature for feature, score in feature_scores.items() if score > threshold]

        result = {
            "is_anomalous": is_anomalous,
            "confidence": confidence,
            "severity": severity,
            "avg_score": avg_score,
            "max_score": max_score,
            "feature_scores": feature_scores,
            "anomalous_features": anomalous_features,
            "timestamp": datetime.now(),
        }

        # Record anomaly
        if is_anomalous:
            self.anomaly_history.append({**result, "sample": sample})

        # Update windows with this sample
        for feature in self.features:
            if feature in sample:
                self.feature_windows[feature].append(sample[feature])

        return result

    def _calculate_anomaly_score(self, feature: str, value: float) -> float:
        """
        Calculate anomaly score for a feature value.

        Uses moving average and standard deviation.

        Args:
            feature: Feature name
            value: Feature value

        Returns:
            Anomaly score (0.0-1.0)
        """
        window = self.feature_windows[feature]

        if len(window) < 2:
            return 0.0

        # Calculate statistics
        mean = sum(window) / len(window)
        variance = sum((x - mean) ** 2 for x in window) / len(window)
        stdev = math.sqrt(variance)

        if stdev == 0:
            return 0.0

        # Calculate z-score
        z_score = abs((value - mean) / stdev)

        # Normalize to 0-1 range (using sigmoid-like function)
        # z_score of 3 = ~0.95, z_score of 2 = ~0.76, z_score of 1 = ~0.38
        score = 1 - (1 / (1 + (z_score / 3)))

        return min(score, 1.0)

    def learn_from_feedback(self, sample: dict[str, Any], is_anomalous: bool):
        """
        Learn from feedback (supervised learning).

        Args:
            sample: Sample
            is_anomalous: True if anomalous (ground truth)
        """
        # In a full ML implementation, this would update the model
        # For now, we adjust sensitivity based on feedback

        prediction = self.predict(sample)
        predicted_anomalous = prediction["is_anomalous"]

        # Adjust sensitivity based on false positives/negatives
        if predicted_anomalous and not is_anomalous:
            # False positive - increase sensitivity threshold
            self.sensitivity = min(self.sensitivity + 0.01, 0.95)
        elif not predicted_anomalous and is_anomalous:
            # False negative - decrease sensitivity threshold
            self.sensitivity = max(self.sensitivity - 0.01, 0.5)

    def get_statistics(self) -> dict[str, Any]:
        """Get detector statistics"""
        return {
            "is_trained": self.is_trained,
            "training_samples": self.training_samples,
            "window_size": self.window_size,
            "sensitivity": self.sensitivity,
            "features_tracked": len(self.features),
            "anomalies_detected": len(self.anomaly_history),
            "window_fill": {
                feature: len(window) / self.window_size for feature, window in self.feature_windows.items()
            },
        }

    def get_anomaly_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get recent anomaly history.

        Args:
            limit: Maximum number of anomalies to return

        Returns:
            List of detected anomalies
        """
        return self.anomaly_history[-limit:]

    def clear_history(self):
        """Clear anomaly history"""
        self.anomaly_history.clear()

    def reset(self):
        """Reset the detector"""
        for window in self.feature_windows.values():
            window.clear()

        self.anomaly_history.clear()
        self.is_trained = False
        self.training_samples = 0
