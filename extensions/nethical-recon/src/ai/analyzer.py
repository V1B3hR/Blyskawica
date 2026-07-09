"""
AI Threat Analyzer

Provides threat scoring, pattern matching, correlation analysis,
and forest health monitoring capabilities.
"""

import logging
from datetime import datetime
from typing import Any


class ThreatAnalyzer:
    """
    🤖 AI Threat Analysis Engine

    Analyzes threats with:
    • Threat score calculation
    • Pattern matching against known threats
    • Correlation analysis
    • Forest health assessment
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.threat_patterns = self._load_threat_patterns()
        self.scoring_weights = {"severity": 0.3, "confidence": 0.25, "impact": 0.25, "prevalence": 0.2}

    def _load_threat_patterns(self) -> dict[str, Any]:
        """Load known threat patterns"""
        return {
            "crow": {
                "indicators": ["persistent", "hidden", "waiting"],
                "severity": "HIGH",
                "tactics": ["execution", "persistence"],
            },
            "magpie": {
                "indicators": ["data_access", "exfiltration", "credential_theft"],
                "severity": "CRITICAL",
                "tactics": ["collection", "exfiltration"],
            },
            "squirrel": {
                "indicators": ["lateral_movement", "jumping", "spreading"],
                "severity": "MEDIUM",
                "tactics": ["lateral_movement", "discovery"],
            },
            "snake": {
                "indicators": ["rootkit", "kernel_level", "deep_hiding"],
                "severity": "CRITICAL",
                "tactics": ["privilege_escalation", "defense_evasion"],
            },
            "parasite": {
                "indicators": ["resource_drain", "cryptomining", "cpu_spike"],
                "severity": "MEDIUM",
                "tactics": ["impact"],
            },
            "bat": {
                "indicators": ["night_activity", "off_hours", "stealth"],
                "severity": "HIGH",
                "tactics": ["execution", "command_and_control"],
            },
        }

    def calculate_threat_score(self, threat_data: dict[str, Any]) -> float:
        """
        Calculate comprehensive threat score (0.0-10.0)

        Args:
            threat_data: Dictionary with threat information
                - severity: LOW, MEDIUM, HIGH, CRITICAL
                - confidence: 0.0-1.0
                - impact: potential impact level
                - prevalence: how common is this threat

        Returns:
            Float score between 0.0 and 10.0
        """
        severity_map = {"LOW": 2.5, "MEDIUM": 5.0, "HIGH": 7.5, "CRITICAL": 10.0}
        impact_map = {"MINIMAL": 1.0, "LOW": 3.0, "MEDIUM": 5.0, "HIGH": 7.0, "CRITICAL": 10.0}

        severity_score = severity_map.get(threat_data.get("severity", "MEDIUM"), 5.0)
        confidence = threat_data.get("confidence", 0.5)
        impact_score = impact_map.get(threat_data.get("impact", "MEDIUM"), 5.0)
        prevalence = threat_data.get("prevalence", 0.5)

        # Weighted calculation
        score = (
            severity_score * self.scoring_weights["severity"]
            + confidence * 10 * self.scoring_weights["confidence"]
            + impact_score * self.scoring_weights["impact"]
            + prevalence * 10 * self.scoring_weights["prevalence"]
        )

        return round(min(10.0, max(0.0, score)), 2)

    def match_pattern(self, threat_data: dict[str, Any]) -> dict[str, Any] | None:
        """
        Match threat against known patterns

        Args:
            threat_data: Threat information including indicators

        Returns:
            Best matching pattern with confidence score
        """
        indicators = threat_data.get("indicators", [])
        if not indicators:
            return None

        best_match = None
        best_score = 0.0

        for threat_type, pattern in self.threat_patterns.items():
            # Calculate match score
            pattern_indicators = set(pattern["indicators"])
            threat_indicators = set(indicators)

            if pattern_indicators:
                match_score = len(pattern_indicators & threat_indicators) / len(pattern_indicators)

                if match_score > best_score:
                    best_score = match_score
                    best_match = {
                        "type": threat_type,
                        "pattern": pattern,
                        "match_score": round(match_score, 2),
                        "matched_indicators": list(pattern_indicators & threat_indicators),
                    }

        return best_match

    def correlate_threats(self, threats: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Correlate multiple threats to find relationships

        Args:
            threats: List of threat dictionaries

        Returns:
            List of correlated threat groups
        """
        correlations = []

        # Group by common indicators
        for i, threat1 in enumerate(threats):
            for threat2 in threats[i + 1 :]:
                common_indicators = set(threat1.get("indicators", [])) & set(threat2.get("indicators", []))

                if common_indicators:
                    correlations.append(
                        {
                            "threat1": threat1.get("id", "unknown"),
                            "threat2": threat2.get("id", "unknown"),
                            "common_indicators": list(common_indicators),
                            "correlation_strength": len(common_indicators),
                            "possible_campaign": len(common_indicators) >= 3,
                        }
                    )

        return correlations

    def assess_forest_health(self, forest_data: dict[str, Any]) -> dict[str, Any]:
        """
        Assess overall health of the forest (infrastructure)

        Args:
            forest_data: Forest information including trees, threats, etc.

        Returns:
            Health assessment report
        """
        trees = forest_data.get("trees", [])
        threats = forest_data.get("threats", [])

        total_trees = len(trees)
        healthy_trees = sum(1 for tree in trees if tree.get("health", 0) >= 0.7)
        critical_threats = sum(1 for threat in threats if threat.get("severity") == "CRITICAL")

        health_score = 0.0
        if total_trees > 0:
            health_score = (healthy_trees / total_trees) * 100

            # Penalize for threats
            threat_penalty = min(critical_threats * 5, 30)
            health_score = max(0, health_score - threat_penalty)

        status = "HEALTHY"
        if health_score < 50:
            status = "CRITICAL"
        elif health_score < 70:
            status = "WARNING"
        elif health_score < 85:
            status = "FAIR"

        return {
            "health_score": round(health_score, 2),
            "status": status,
            "total_trees": total_trees,
            "healthy_trees": healthy_trees,
            "threatened_trees": total_trees - healthy_trees,
            "critical_threats": critical_threats,
            "total_threats": len(threats),
            "assessment_time": datetime.now().isoformat(),
            "recommendations": self._generate_health_recommendations(health_score, critical_threats),
        }

    def _generate_health_recommendations(self, health_score: float, critical_threats: int) -> list[str]:
        """Generate recommendations based on health assessment"""
        recommendations = []

        if health_score < 50:
            recommendations.append("🚨 URGENT: Forest health critical. Deploy all nanobots immediately.")
            recommendations.append("🦅 Activate Eagle mode for strategic overview")

        if critical_threats > 0:
            recommendations.append(
                f"🔫 {critical_threats} critical threat(s) detected. Use marker weapons immediately."
            )
            recommendations.append("🦅 Deploy Falcon for rapid threat response")

        if health_score < 70:
            recommendations.append("🔍 Increase sensor sensitivity")
            recommendations.append("🦉 Activate Owl for night watch monitoring")

        if not recommendations:
            recommendations.append("✅ Forest health is good. Maintain current patrols.")

        return recommendations

    def analyze_threat(self, threat_data: dict[str, Any]) -> dict[str, Any]:
        """
        Comprehensive threat analysis

        Args:
            threat_data: Complete threat information

        Returns:
            Full analysis report
        """
        threat_score = self.calculate_threat_score(threat_data)
        pattern_match = self.match_pattern(threat_data)

        return {
            "threat_id": threat_data.get("id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "threat_score": threat_score,
            "severity": threat_data.get("severity", "MEDIUM"),
            "pattern_match": pattern_match,
            "confidence": threat_data.get("confidence", 0.5),
            "recommendations": self._generate_threat_recommendations(threat_score, pattern_match),
        }

    def _generate_threat_recommendations(self, score: float, pattern: dict | None) -> list[str]:
        """Generate action recommendations for a threat"""
        recommendations = []

        if score >= 8.0:
            recommendations.append("🔫 Mark with RED tracer immediately")
            recommendations.append("🤖 Deploy defensive nanobots")
            recommendations.append("🦅 Falcon alert - rapid response needed")
        elif score >= 6.0:
            recommendations.append("🔫 Mark with ORANGE tracer")
            recommendations.append("👁️ Increase monitoring")
            recommendations.append("🦉 Owl watch recommended")
        elif score >= 4.0:
            recommendations.append("📊 Continue monitoring")
            recommendations.append("🐦 Sparrow routine check")
        else:
            recommendations.append("ℹ️ Low priority - log only")

        if pattern:
            threat_type = pattern.get("type", "").upper()
            if threat_type == "CROW":
                recommendations.append("🐦‍⬛ Crow detected - deploy persistent monitoring")
            elif threat_type == "MAGPIE":
                recommendations.append("🐦 Magpie detected - protect sensitive data")
            elif threat_type == "SQUIRREL":
                recommendations.append("🐿️ Squirrel detected - monitor lateral movement")

        return recommendations
