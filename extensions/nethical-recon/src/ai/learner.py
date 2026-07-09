"""
AI Pattern Learner

Learns patterns from threats, adjusts baselines, reduces false positives,
and identifies crow behavior patterns.
"""

import logging
from datetime import datetime
from typing import Any


class PatternLearner:
    """
    📚 AI Pattern Learning Engine

    Provides:
    • Pattern learning from threats
    • Baseline adjustment
    • False positive reduction
    • Crow pattern identification
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.learned_patterns = []
        self.baseline = {}
        self.false_positive_signatures = []

    def learn_pattern(self, threat_data: dict[str, Any]) -> dict[str, Any]:
        """
        Learn a new pattern from threat data

        Args:
            threat_data: Threat information

        Returns:
            Learned pattern
        """
        pattern = {
            "pattern_id": f"pattern_{len(self.learned_patterns) + 1}",
            "learned_at": datetime.now().isoformat(),
            "threat_type": threat_data.get("type"),
            "indicators": threat_data.get("indicators", []),
            "behavior_signature": self._extract_behavior_signature(threat_data),
            "frequency": 1,
            "last_seen": datetime.now().isoformat(),
            "confidence": 0.5,  # Initial confidence
        }

        # Check if similar pattern exists
        existing = self._find_similar_pattern(pattern)
        if existing:
            existing["frequency"] += 1
            existing["last_seen"] = datetime.now().isoformat()
            existing["confidence"] = min(existing["confidence"] + 0.1, 1.0)
            return existing
        else:
            self.learned_patterns.append(pattern)
            return pattern

    def _extract_behavior_signature(self, threat_data: dict) -> dict[str, Any]:
        """Extract behavioral signature from threat"""
        return {
            "actions": threat_data.get("actions", []),
            "targets": threat_data.get("targets", []),
            "timing": threat_data.get("timing_pattern", "unknown"),
            "persistence_method": threat_data.get("persistence", "none"),
        }

    def _find_similar_pattern(self, new_pattern: dict) -> dict:
        """Find similar existing pattern"""
        for pattern in self.learned_patterns:
            if pattern["threat_type"] == new_pattern["threat_type"]:
                # Check indicator similarity
                existing_indicators = set(pattern["indicators"])
                new_indicators = set(new_pattern["indicators"])

                if existing_indicators and new_indicators:
                    similarity = len(existing_indicators & new_indicators) / len(existing_indicators | new_indicators)
                    if similarity >= 0.7:
                        return pattern
        return None

    def adjust_baseline(self, current_data: dict[str, Any], historical_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Adjust system baseline based on current and historical data

        Args:
            current_data: Current system metrics
            historical_data: Historical baseline data

        Returns:
            Adjusted baseline
        """
        if not historical_data:
            self.baseline = current_data
            return {"baseline": self.baseline, "status": "INITIALIZED", "confidence": 0.5}

        # Calculate averages from historical data
        metrics = {}
        for key in current_data.keys():
            historical_values = [d.get(key, 0) for d in historical_data if key in d]
            if historical_values:
                avg = sum(historical_values) / len(historical_values)
                std_dev = (sum((x - avg) ** 2 for x in historical_values) / len(historical_values)) ** 0.5

                metrics[key] = {
                    "average": avg,
                    "std_dev": std_dev,
                    "current": current_data.get(key, 0),
                    "deviation": abs(current_data.get(key, 0) - avg) / (std_dev if std_dev > 0 else 1),
                }

        self.baseline = {k: v["average"] for k, v in metrics.items()}

        # Identify anomalies
        anomalies = [k for k, v in metrics.items() if v["deviation"] > 2.0]

        return {
            "baseline": self.baseline,
            "metrics": metrics,
            "anomalies": anomalies,
            "status": "ADJUSTED",
            "confidence": min(len(historical_data) / 100.0, 0.95),
            "data_points": len(historical_data),
        }

    def reduce_false_positives(self, alerts: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Identify and reduce false positives

        Args:
            alerts: List of alerts to analyze

        Returns:
            Analysis with false positive candidates
        """
        false_positive_candidates = []

        for alert in alerts:
            fp_score = self._calculate_fp_probability(alert)

            if fp_score >= 0.7:
                false_positive_candidates.append(
                    {
                        "alert_id": alert.get("id"),
                        "fp_probability": fp_score,
                        "reasons": self._explain_fp_reasons(alert, fp_score),
                        "recommendation": "SUPPRESS" if fp_score >= 0.9 else "REVIEW",
                    }
                )

        # Update false positive signatures
        for candidate in false_positive_candidates:
            if candidate["fp_probability"] >= 0.9:
                self._add_fp_signature(candidate)

        return {
            "total_alerts": len(alerts),
            "false_positive_candidates": false_positive_candidates,
            "fp_rate": len(false_positive_candidates) / len(alerts) if alerts else 0,
            "signatures_updated": len([c for c in false_positive_candidates if c["fp_probability"] >= 0.9]),
        }

    def _calculate_fp_probability(self, alert: dict) -> float:
        """Calculate false positive probability"""
        fp_score = 0.0

        # Check against known FP signatures
        for signature in self.false_positive_signatures:
            if self._matches_signature(alert, signature):
                fp_score += 0.5

        # Low severity but high frequency
        if alert.get("severity") == "LOW" and alert.get("frequency", 0) > 10:
            fp_score += 0.3

        # Never acted upon
        if not alert.get("actions_taken") and alert.get("age_hours", 0) > 24:
            fp_score += 0.2

        return min(fp_score, 1.0)

    def _matches_signature(self, alert: dict, signature: dict) -> bool:
        """Check if alert matches FP signature"""
        return alert.get("type") == signature.get("type") and alert.get("source") == signature.get("source")

    def _explain_fp_reasons(self, alert: dict, score: float) -> list[str]:
        """Explain why alert might be false positive"""
        reasons = []

        if score >= 0.5:
            reasons.append("Matches known false positive signature")
        if alert.get("severity") == "LOW":
            reasons.append("Low severity alert")
        if alert.get("frequency", 0) > 10:
            reasons.append("High frequency, likely benign")
        if not alert.get("actions_taken"):
            reasons.append("No actions taken despite age")

        return reasons

    def _add_fp_signature(self, candidate: dict):
        """Add new false positive signature"""
        alert_id = candidate.get("alert_id")
        # In real implementation, would extract signature from alert
        signature = {
            "type": "learned_fp",
            "added_at": datetime.now().isoformat(),
            "confidence": candidate.get("fp_probability"),
        }
        self.false_positive_signatures.append(signature)

    def identify_crow_patterns(self, crow_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Identify behavior patterns specific to crows (malware)

        Args:
            crow_data: List of crow (malware) detections

        Returns:
            Crow behavior patterns
        """
        if not crow_data:
            return {"patterns": [], "confidence": 0.0, "message": "No crow data available"}

        patterns = []

        # Analyze timing patterns
        timing_pattern = self._analyze_crow_timing(crow_data)
        if timing_pattern:
            patterns.append(timing_pattern)

        # Analyze persistence patterns
        persistence_pattern = self._analyze_crow_persistence(crow_data)
        if persistence_pattern:
            patterns.append(persistence_pattern)

        # Analyze target patterns
        target_pattern = self._analyze_crow_targets(crow_data)
        if target_pattern:
            patterns.append(target_pattern)

        return {
            "patterns": patterns,
            "total_crows_analyzed": len(crow_data),
            "confidence": min(len(crow_data) / 20.0, 0.95),
            "recommendations": self._generate_crow_recommendations(patterns),
        }

    def _analyze_crow_timing(self, crow_data: list[dict]) -> dict:
        """Analyze when crows are most active"""
        hours = [
            datetime.fromisoformat(c.get("timestamp", datetime.now().isoformat())).hour
            for c in crow_data
            if c.get("timestamp")
        ]

        if not hours:
            return None

        # Find most common hours
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        most_active_hour = max(hour_counts, key=hour_counts.get)

        time_of_day = "night" if 22 <= most_active_hour or most_active_hour <= 6 else "day"

        return {
            "pattern_type": "TIMING",
            "most_active_hour": most_active_hour,
            "time_of_day": time_of_day,
            "frequency": hour_counts[most_active_hour],
            "insight": f"Crows most active during {time_of_day} hours (around {most_active_hour:02d}:00)",
        }

    def _analyze_crow_persistence(self, crow_data: list[dict]) -> dict:
        """Analyze crow persistence methods"""
        persistence_methods = [c.get("persistence_method") for c in crow_data if c.get("persistence_method")]

        if not persistence_methods:
            return None

        most_common = max(set(persistence_methods), key=persistence_methods.count)

        return {
            "pattern_type": "PERSISTENCE",
            "method": most_common,
            "frequency": persistence_methods.count(most_common),
            "insight": f"Crows primarily use {most_common} for persistence",
        }

    def _analyze_crow_targets(self, crow_data: list[dict]) -> dict:
        """Analyze crow target preferences"""
        targets = []
        for crow in crow_data:
            target = crow.get("forest_location", {}).get("tree")
            if target:
                targets.append(target)

        if not targets:
            return None

        most_targeted = max(set(targets), key=targets.count)

        return {
            "pattern_type": "TARGETING",
            "most_targeted_tree": most_targeted,
            "frequency": targets.count(most_targeted),
            "insight": f"Crows prefer targeting {most_targeted}",
        }

    def _generate_crow_recommendations(self, patterns: list[dict]) -> list[str]:
        """Generate recommendations based on crow patterns"""
        recommendations = []

        for pattern in patterns:
            if pattern["pattern_type"] == "TIMING":
                if pattern["time_of_day"] == "night":
                    recommendations.append("🦉 Deploy Owl for enhanced night watch")
                else:
                    recommendations.append("🦅 Increase Falcon patrols during day hours")

            elif pattern["pattern_type"] == "PERSISTENCE":
                recommendations.append(f"🔒 Harden {pattern['method']} mechanisms")

            elif pattern["pattern_type"] == "TARGETING":
                recommendations.append(f"🛡️ Increase defenses on {pattern['most_targeted_tree']}")

        if not recommendations:
            recommendations.append("Continue baseline monitoring")

        return recommendations

    def export_learned_knowledge(self) -> dict[str, Any]:
        """
        Export all learned knowledge

        Returns:
            Complete learned knowledge base
        """
        return {
            "export_time": datetime.now().isoformat(),
            "patterns": self.learned_patterns,
            "baseline": self.baseline,
            "false_positive_signatures": self.false_positive_signatures,
            "stats": {
                "total_patterns": len(self.learned_patterns),
                "total_fp_signatures": len(self.false_positive_signatures),
                "baseline_metrics": len(self.baseline),
            },
        }

    def import_learned_knowledge(self, knowledge_base: dict[str, Any]) -> bool:
        """
        Import learned knowledge

        Args:
            knowledge_base: Previously exported knowledge

        Returns:
            Success status
        """
        try:
            self.learned_patterns = knowledge_base.get("patterns", [])
            self.baseline = knowledge_base.get("baseline", {})
            self.false_positive_signatures = knowledge_base.get("false_positive_signatures", [])
            return True
        except Exception as e:
            self.logger.error(f"Failed to import knowledge: {e}")
            return False
