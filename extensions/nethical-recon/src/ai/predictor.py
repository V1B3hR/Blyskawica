"""
AI Threat Predictor

Predicts next attacks, forecasts risk trends, and analyzes threat evolution.
"""

import logging
from datetime import datetime, timedelta
from typing import Any


class ThreatPredictor:
    """
    🔮 AI Threat Prediction Engine

    Provides:
    • Next attack prediction
    • Risk forecasting
    • Trend analysis
    • Threat evolution tracking
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historical_data = []

    def predict_next_attack(self, threat_history: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Predict next likely attack based on historical patterns

        Args:
            threat_history: List of historical threats

        Returns:
            Prediction with confidence and timeframe
        """
        if not threat_history:
            return {
                "prediction": "UNKNOWN",
                "confidence": 0.0,
                "timeframe": "N/A",
                "reasoning": "Insufficient historical data",
            }

        # Analyze patterns
        threat_types = [t.get("type") for t in threat_history if t.get("type")]
        most_common = max(set(threat_types), key=threat_types.count) if threat_types else "unknown"

        # Calculate average time between attacks
        timestamps = [
            datetime.fromisoformat(t.get("timestamp", datetime.now().isoformat()))
            for t in threat_history
            if t.get("timestamp")
        ]

        avg_interval = timedelta(days=1)  # Default
        if len(timestamps) > 1:
            intervals = [(timestamps[i + 1] - timestamps[i]) for i in range(len(timestamps) - 1)]
            avg_interval = sum(intervals, timedelta()) / len(intervals) if intervals else timedelta(days=1)

        next_attack_time = datetime.now() + avg_interval

        confidence = min(len(threat_history) / 10.0, 0.95)  # More data = higher confidence

        return {
            "prediction": most_common,
            "confidence": round(confidence, 2),
            "timeframe": next_attack_time.isoformat(),
            "likely_target": self._predict_target(threat_history),
            "reasoning": f"Based on {len(threat_history)} historical incidents",
            "preventive_actions": self._suggest_preventive_actions(most_common),
        }

    def _predict_target(self, threat_history: list[dict]) -> str:
        """Predict most likely target"""
        targets = [t.get("target", {}).get("hostname", "unknown") for t in threat_history if t.get("target")]

        if targets:
            return max(set(targets), key=targets.count)
        return "unknown"

    def _suggest_preventive_actions(self, threat_type: str) -> list[str]:
        """Suggest actions to prevent predicted attack"""
        actions = {
            "crow": ["Increase process monitoring", "Deploy additional nanobots", "Review execution policies"],
            "magpie": ["Enhance data access controls", "Monitor data exfiltration paths", "Review DLP policies"],
            "squirrel": ["Strengthen network segmentation", "Monitor lateral movement paths", "Review access controls"],
        }
        return actions.get(threat_type, ["Increase general monitoring"])

    def forecast_risk(self, current_state: dict[str, Any], days_ahead: int = 7) -> dict[str, Any]:
        """
        Forecast risk level for upcoming period

        Args:
            current_state: Current security state
            days_ahead: Number of days to forecast

        Returns:
            Risk forecast
        """
        current_risk = current_state.get("risk_score", 5.0)
        threats = current_state.get("threats", [])
        trend = current_state.get("trend", "stable")

        # Calculate forecast
        if trend == "increasing":
            forecast_risk = min(current_risk * 1.2, 10.0)
            outlook = "DETERIORATING"
        elif trend == "decreasing":
            forecast_risk = max(current_risk * 0.8, 0.0)
            outlook = "IMPROVING"
        else:
            forecast_risk = current_risk
            outlook = "STABLE"

        return {
            "current_risk": current_risk,
            "forecast_risk": round(forecast_risk, 2),
            "forecast_period": f"{days_ahead} days",
            "outlook": outlook,
            "confidence": 0.75,
            "factors": self._identify_risk_factors(current_state),
            "mitigation_strategies": self._suggest_mitigation(forecast_risk),
        }

    def _identify_risk_factors(self, state: dict) -> list[dict[str, Any]]:
        """Identify factors contributing to risk"""
        factors = []

        threat_count = len(state.get("threats", []))
        if threat_count > 5:
            factors.append({"factor": "High threat volume", "impact": "HIGH", "contribution": 0.3})

        health_score = state.get("forest", {}).get("health_score", 100)
        if health_score < 70:
            factors.append({"factor": "Degraded forest health", "impact": "MEDIUM", "contribution": 0.2})

        return factors

    def _suggest_mitigation(self, risk_level: float) -> list[str]:
        """Suggest mitigation strategies"""
        if risk_level >= 7.0:
            return [
                "Deploy all available nanobots",
                "Activate Eagle mode for strategic response",
                "Increase sensor sensitivity to maximum",
                "Prepare incident response team",
            ]
        elif risk_level >= 5.0:
            return ["Increase monitoring frequency", "Deploy Falcon for rapid response", "Review security controls"]
        else:
            return ["Maintain current posture", "Continue routine patrols"]

    def analyze_trend(self, time_series_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze threat trends over time

        Args:
            time_series_data: Time-series threat data

        Returns:
            Trend analysis
        """
        if not time_series_data:
            return {"trend": "UNKNOWN", "confidence": 0.0}

        # Simple trend analysis
        scores = [d.get("score", 0) for d in time_series_data]

        if len(scores) < 2:
            return {"trend": "INSUFFICIENT_DATA", "confidence": 0.0}

        # Calculate moving average
        recent_avg = sum(scores[-3:]) / min(3, len(scores))
        older_avg = sum(scores[:3]) / min(3, len(scores))

        if recent_avg > older_avg * 1.2:
            trend = "INCREASING"
        elif recent_avg < older_avg * 0.8:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "confidence": 0.8,
            "recent_average": round(recent_avg, 2),
            "historical_average": round(older_avg, 2),
            "data_points": len(scores),
            "outlook": self._generate_outlook(trend),
        }

    def _generate_outlook(self, trend: str) -> str:
        """Generate human-readable outlook"""
        outlooks = {
            "INCREASING": "Threat activity is rising. Prepare for increased incidents.",
            "DECREASING": "Threat activity is declining. Security measures are effective.",
            "STABLE": "Threat activity is stable. Maintain current security posture.",
        }
        return outlooks.get(trend, "Unable to determine outlook")

    def predict_threat_evolution(self, threat_data: dict[str, Any]) -> dict[str, Any]:
        """
        Predict how a threat might evolve

        Args:
            threat_data: Current threat information

        Returns:
            Evolution prediction
        """
        threat_type = threat_data.get("type", "unknown")
        current_stage = threat_data.get("stage", "initial")

        evolution_paths = {
            "crow": ["reconnaissance", "persistence", "execution", "exfiltration"],
            "magpie": ["discovery", "collection", "staging", "exfiltration"],
            "squirrel": ["initial_access", "discovery", "lateral_movement", "collection"],
            "snake": ["initial_access", "privilege_escalation", "defense_evasion", "persistence"],
            "parasite": ["execution", "persistence", "impact"],
            "bat": ["reconnaissance", "resource_development", "execution"],
        }

        path = evolution_paths.get(threat_type, ["unknown"])
        current_idx = path.index(current_stage) if current_stage in path else 0

        next_stages = path[current_idx + 1 :] if current_idx < len(path) - 1 else []

        return {
            "threat_type": threat_type,
            "current_stage": current_stage,
            "next_stages": next_stages,
            "estimated_timeline": f"{len(next_stages) * 24} hours",
            "warning_signs": self._identify_warning_signs(threat_type, next_stages),
            "countermeasures": self._suggest_countermeasures(threat_type, next_stages),
        }

    def _identify_warning_signs(self, threat_type: str, stages: list[str]) -> list[str]:
        """Identify warning signs for next stages"""
        if not stages:
            return []

        signs = {
            "persistence": ["Registry modifications", "Scheduled task creation", "Service installation"],
            "execution": ["Unusual process spawning", "Script execution", "Command-line activity"],
            "exfiltration": ["Unusual network traffic", "Large data transfers", "External connections"],
            "lateral_movement": ["Multiple authentication attempts", "Remote connections", "Share enumeration"],
        }

        return signs.get(stages[0], ["Monitor for unusual activity"])

    def _suggest_countermeasures(self, threat_type: str, stages: list[str]) -> list[str]:
        """Suggest countermeasures for predicted evolution"""
        if not stages:
            return ["Maintain current defenses"]

        measures = {
            "persistence": ["Monitor registry changes", "Lock down startup locations"],
            "execution": ["Application whitelisting", "Monitor process creation"],
            "exfiltration": ["DLP controls", "Egress filtering", "Network monitoring"],
            "lateral_movement": ["Network segmentation", "Credential protection"],
        }

        return measures.get(stages[0], ["Increase monitoring"])
