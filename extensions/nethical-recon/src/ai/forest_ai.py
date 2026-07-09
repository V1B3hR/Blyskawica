"""
Forest AI

Forest-specific artificial intelligence for tree health prediction,
branch anomaly detection, leaf pattern recognition, and threat analysis.
"""

import logging
from typing import Any


class ForestAI:
    """
    🌳 Forest-Specific AI Engine

    Provides:
    • Tree health prediction
    • Branch anomaly detection
    • Leaf pattern recognition
    • Threat type classification
    • Crow/Magpie behavior analysis
    • Squirrel path prediction
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def predict_tree_health(self, tree_data: dict[str, Any], historical_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Predict future tree health

        Args:
            tree_data: Current tree state
            historical_data: Historical health data

        Returns:
            Health prediction
        """
        current_health = tree_data.get("health", 1.0)
        threats = tree_data.get("threats", [])
        branches = tree_data.get("branches", [])

        # Calculate health trend
        if historical_data:
            health_values = [d.get("health", 1.0) for d in historical_data]
            if len(health_values) >= 2:
                trend = health_values[-1] - health_values[0]
            else:
                trend = 0.0
        else:
            trend = 0.0

        # Predict future health
        threat_impact = len(threats) * -0.1
        branch_impact = -0.05 if len(branches) < tree_data.get("expected_branches", 10) else 0.0

        predicted_health = max(0.0, min(1.0, current_health + trend + threat_impact + branch_impact))

        # Determine prediction outlook
        if predicted_health >= 0.8:
            outlook = "HEALTHY"
        elif predicted_health >= 0.6:
            outlook = "FAIR"
        elif predicted_health >= 0.4:
            outlook = "DEGRADED"
        else:
            outlook = "CRITICAL"

        return {
            "tree_id": tree_data.get("id", "unknown"),
            "current_health": current_health,
            "predicted_health": round(predicted_health, 2),
            "outlook": outlook,
            "trend": "IMPROVING" if trend > 0 else "DECLINING" if trend < 0 else "STABLE",
            "confidence": min(len(historical_data) / 10.0, 0.9),
            "risk_factors": self._identify_risk_factors(tree_data),
            "recommendations": self._tree_health_recommendations(outlook, tree_data),
        }

    def _identify_risk_factors(self, tree_data: dict) -> list[dict[str, Any]]:
        """Identify factors affecting tree health"""
        factors = []

        threats = tree_data.get("threats", [])
        if threats:
            factors.append(
                {
                    "factor": f"{len(threats)} active threat(s)",
                    "impact": "HIGH" if len(threats) > 2 else "MEDIUM",
                    "severity": max((t.get("severity", "LOW") for t in threats), default="LOW"),
                }
            )

        branches = tree_data.get("branches", [])
        expected = tree_data.get("expected_branches", 10)
        if len(branches) < expected * 0.7:
            factors.append({"factor": "Reduced branch count", "impact": "MEDIUM", "severity": "MEDIUM"})

        return factors

    def _tree_health_recommendations(self, outlook: str, tree_data: dict) -> list[str]:
        """Generate health recommendations"""
        recommendations = []

        if outlook == "CRITICAL":
            recommendations.extend(
                [
                    "🚨 URGENT: Tree health critical",
                    "Deploy nanobots immediately",
                    "Consider isolating tree",
                    "Alert Eagle for strategic assessment",
                ]
            )
        elif outlook == "DEGRADED":
            recommendations.extend(
                ["⚠️ Tree health degraded", "Increase monitoring frequency", "Deploy Owl for detailed analysis"]
            )
        elif outlook == "FAIR":
            recommendations.append("Monitor tree closely")
        else:
            recommendations.append("✅ Tree health good")

        return recommendations

    def detect_branch_anomalies(self, branch_data: list[dict[str, Any]], baseline: dict[str, Any]) -> dict[str, Any]:
        """
        Detect anomalies in branch behavior

        Args:
            branch_data: List of branches with their metrics
            baseline: Baseline branch behavior

        Returns:
            Anomaly detection results
        """
        anomalies = []

        for branch in branch_data:
            branch_anomalies = []

            # Check CPU usage
            cpu = branch.get("cpu_usage", 0)
            baseline_cpu = baseline.get("cpu_usage", 0.5)
            if cpu > baseline_cpu * 2:
                branch_anomalies.append(
                    {
                        "type": "HIGH_CPU",
                        "value": cpu,
                        "baseline": baseline_cpu,
                        "severity": "HIGH" if cpu > baseline_cpu * 3 else "MEDIUM",
                    }
                )

            # Check memory usage
            memory = branch.get("memory_usage", 0)
            baseline_memory = baseline.get("memory_usage", 0.5)
            if memory > baseline_memory * 2:
                branch_anomalies.append(
                    {
                        "type": "HIGH_MEMORY",
                        "value": memory,
                        "baseline": baseline_memory,
                        "severity": "HIGH" if memory > baseline_memory * 3 else "MEDIUM",
                    }
                )

            # Check network activity
            network = branch.get("network_connections", 0)
            baseline_network = baseline.get("network_connections", 10)
            if network > baseline_network * 2:
                branch_anomalies.append(
                    {"type": "HIGH_NETWORK", "value": network, "baseline": baseline_network, "severity": "MEDIUM"}
                )

            if branch_anomalies:
                anomalies.append(
                    {
                        "branch_id": branch.get("id", "unknown"),
                        "anomalies": branch_anomalies,
                        "total_anomalies": len(branch_anomalies),
                        "recommendations": self._branch_anomaly_recommendations(branch_anomalies),
                    }
                )

        return {
            "total_branches": len(branch_data),
            "anomalous_branches": len(anomalies),
            "anomalies": anomalies,
            "severity": "HIGH" if any(a.get("total_anomalies", 0) >= 2 for a in anomalies) else "MEDIUM",
        }

    def _branch_anomaly_recommendations(self, anomalies: list[dict]) -> list[str]:
        """Generate recommendations for branch anomalies"""
        recommendations = []

        for anomaly in anomalies:
            if anomaly["type"] == "HIGH_CPU":
                recommendations.append("🔍 Investigate process causing high CPU")
            elif anomaly["type"] == "HIGH_MEMORY":
                recommendations.append("🔍 Check for memory leak or malware")
            elif anomaly["type"] == "HIGH_NETWORK":
                recommendations.append("🔍 Analyze network connections for exfiltration")

        return recommendations

    def recognize_leaf_patterns(self, leaf_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Recognize patterns in leaf (thread/session/packet) behavior

        Args:
            leaf_data: List of leaf metrics

        Returns:
            Pattern recognition results
        """
        if not leaf_data:
            return {"patterns": [], "confidence": 0.0}

        patterns = []

        # Analyze leaf lifetimes
        lifetimes = [l.get("lifetime", 0) for l in leaf_data]
        avg_lifetime = sum(lifetimes) / len(lifetimes) if lifetimes else 0

        short_lived = sum(1 for l in lifetimes if l < avg_lifetime * 0.5)
        if short_lived > len(lifetimes) * 0.3:
            patterns.append(
                {
                    "pattern": "SHORT_LIVED_LEAVES",
                    "count": short_lived,
                    "insight": "Many short-lived threads/sessions detected",
                    "possible_threat": "Process spawning, scanning activity",
                }
            )

        # Analyze leaf resource usage
        high_resource_leaves = sum(1 for l in leaf_data if l.get("resource_usage", 0) > 0.7)
        if high_resource_leaves > 0:
            patterns.append(
                {
                    "pattern": "HIGH_RESOURCE_LEAVES",
                    "count": high_resource_leaves,
                    "insight": "Leaves consuming high resources",
                    "possible_threat": "Cryptominer, resource abuse",
                }
            )

        return {
            "total_leaves": len(leaf_data),
            "patterns": patterns,
            "average_lifetime": round(avg_lifetime, 2),
            "confidence": 0.7,
            "recommendations": self._leaf_pattern_recommendations(patterns),
        }

    def _leaf_pattern_recommendations(self, patterns: list[dict]) -> list[str]:
        """Generate recommendations for leaf patterns"""
        recommendations = []

        for pattern in patterns:
            if pattern["pattern"] == "SHORT_LIVED_LEAVES":
                recommendations.append("🔍 Investigate rapid process creation")
                recommendations.append("Check for scanning or enumeration activity")
            elif pattern["pattern"] == "HIGH_RESOURCE_LEAVES":
                recommendations.append("🔍 Check for cryptominer or resource abuse")
                recommendations.append("Deploy Parasite detector")

        return recommendations

    def analyze_crow_behavior(self, crow_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze crow (malware) behavior in forest

        Args:
            crow_data: Crow detection data

        Returns:
            Behavior analysis
        """
        location = crow_data.get("forest_location", {})
        behavior = crow_data.get("behavior", {})

        # Analyze patience (how long crow waits)
        patience_score = behavior.get("wait_time", 0) / 3600  # Hours
        if patience_score > 24:
            patience_level = "VERY_PATIENT"
        elif patience_score > 12:
            patience_level = "PATIENT"
        else:
            patience_level = "IMPATIENT"

        # Analyze stealth
        detection_attempts = behavior.get("detection_attempts", 0)
        stealth_level = "HIGH" if detection_attempts < 3 else "MEDIUM" if detection_attempts < 10 else "LOW"

        return {
            "crow_id": crow_data.get("id", "unknown"),
            "tree": location.get("tree"),
            "branch": location.get("branch"),
            "patience_level": patience_level,
            "patience_hours": patience_score,
            "stealth_level": stealth_level,
            "threat_assessment": self._assess_crow_threat(patience_level, stealth_level),
            "recommendations": self._crow_behavior_recommendations(patience_level, stealth_level),
        }

    def _assess_crow_threat(self, patience: str, stealth: str) -> str:
        """Assess threat level based on crow behavior"""
        if patience in ["VERY_PATIENT", "PATIENT"] and stealth == "HIGH":
            return "CRITICAL"
        elif patience == "PATIENT" or stealth == "HIGH":
            return "HIGH"
        else:
            return "MEDIUM"

    def _crow_behavior_recommendations(self, patience: str, stealth: str) -> list[str]:
        """Generate recommendations for crow behavior"""
        recommendations = []

        if patience in ["VERY_PATIENT", "PATIENT"]:
            recommendations.append("🐦‍⬛ Patient crow detected - advanced threat")
            recommendations.append("Deploy continuous monitoring")

        if stealth == "HIGH":
            recommendations.append("🔍 High stealth detected - use Owl for detection")

        recommendations.append("🔫 Mark with BLACK tracer immediately")

        return recommendations

    def predict_squirrel_path(self, squirrel_data: dict[str, Any], forest_map: dict[str, Any]) -> dict[str, Any]:
        """
        Predict lateral movement path of squirrel

        Args:
            squirrel_data: Squirrel detection data
            forest_map: Forest topology

        Returns:
            Path prediction
        """
        current_tree = squirrel_data.get("forest_location", {}).get("tree")
        visited_trees = squirrel_data.get("visited_trees", [])

        # Simple prediction based on connectivity
        all_trees = forest_map.get("trees", [])
        possible_targets = [t for t in all_trees if t.get("id") not in visited_trees]

        # Prioritize by connectivity and vulnerability
        scored_targets = []
        for tree in possible_targets:
            score = 0.0

            # Higher score for more connections
            score += len(tree.get("connections", [])) * 0.3

            # Higher score for lower security
            security = tree.get("security_level", 0.5)
            score += (1.0 - security) * 0.7

            scored_targets.append({"tree": tree.get("id"), "score": score, "security_level": security})

        scored_targets.sort(key=lambda x: x["score"], reverse=True)

        return {
            "squirrel_id": squirrel_data.get("id", "unknown"),
            "current_location": current_tree,
            "visited_count": len(visited_trees),
            "predicted_targets": scored_targets[:3],
            "confidence": 0.7,
            "timeframe": "1-4 hours",
            "recommendations": self._squirrel_path_recommendations(scored_targets[:3]),
        }

    def _squirrel_path_recommendations(self, targets: list[dict]) -> list[str]:
        """Generate recommendations for squirrel path"""
        recommendations = []

        if targets:
            top_target = targets[0]["tree"]
            recommendations.append(f"🐿️ Likely next target: {top_target}")
            recommendations.append(f"🛡️ Harden defenses on {top_target}")
            recommendations.append("Monitor network paths between trees")

        recommendations.append("🔫 Mark with BROWN tracer")

        return recommendations
