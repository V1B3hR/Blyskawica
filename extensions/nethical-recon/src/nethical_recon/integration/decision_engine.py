"""
Decision Engine - Central scoring and decision making

Provides risk scoring, threat assessment, and automated decision making
for security findings and alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(str, Enum):
    """Risk level classification"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ConfidenceLevel(str, Enum):
    """Confidence in assessment"""

    CONFIRMED = "confirmed"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SUSPECTED = "suspected"


@dataclass
class RiskScore:
    """Risk score assessment"""

    overall_score: float  # 0-100
    risk_level: RiskLevel
    confidence: ConfidenceLevel
    factors: Dict[str, float] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "overall_score": self.overall_score,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence.value,
            "factors": self.factors,
            "calculated_at": self.calculated_at.isoformat(),
        }


@dataclass
class ThreatContext:
    """Threat intelligence context"""

    ip_reputation: Optional[str] = None
    known_malicious: bool = False
    threat_actors: List[str] = field(default_factory=list)
    attack_patterns: List[str] = field(default_factory=list)
    cve_ids: List[str] = field(default_factory=list)
    cvss_score: Optional[float] = None
    exploit_available: bool = False
    actively_exploited: bool = False


class DecisionEngine:
    """
    Central decision engine for risk scoring and threat assessment.

    Combines multiple factors to produce actionable risk scores and
    automated decision recommendations.
    """

    def __init__(self):
        self.weights = {
            "severity": 0.30,
            "exploitability": 0.25,
            "asset_criticality": 0.20,
            "threat_intel": 0.15,
            "exposure": 0.10,
        }

    def calculate_risk_score(
        self,
        severity: str,
        asset_criticality: str = "medium",
        cvss_score: Optional[float] = None,
        exploit_available: bool = False,
        actively_exploited: bool = False,
        exposure_level: str = "internal",
        threat_context: Optional[ThreatContext] = None,
    ) -> RiskScore:
        """
        Calculate comprehensive risk score.

        Args:
            severity: Finding severity (critical, high, medium, low, info)
            asset_criticality: Asset importance (critical, high, medium, low)
            cvss_score: CVSS score if available (0-10)
            exploit_available: Whether exploit code exists
            actively_exploited: Whether actively exploited in wild
            exposure_level: Asset exposure (external, dmz, internal, isolated)
            threat_context: Additional threat intelligence context

        Returns:
            Risk score with level and confidence
        """
        factors = {}

        # 1. Severity factor (0-100)
        severity_map = {"critical": 100, "high": 75, "medium": 50, "low": 25, "info": 10}
        severity_score = severity_map.get(severity.lower(), 50)
        factors["severity"] = severity_score

        # 2. Exploitability factor (0-100)
        exploitability = 0
        if cvss_score:
            exploitability = (cvss_score / 10.0) * 100
        elif exploit_available:
            exploitability = 70
        elif actively_exploited:
            exploitability = 90

        if actively_exploited:
            exploitability = max(exploitability, 90)

        factors["exploitability"] = exploitability

        # 3. Asset criticality factor (0-100)
        criticality_map = {"critical": 100, "high": 75, "medium": 50, "low": 25}
        asset_score = criticality_map.get(asset_criticality.lower(), 50)
        factors["asset_criticality"] = asset_score

        # 4. Threat intelligence factor (0-100)
        threat_score = 0
        if threat_context:
            if threat_context.actively_exploited:
                threat_score += 40
            if threat_context.known_malicious:
                threat_score += 30
            if threat_context.threat_actors:
                threat_score += 20
            if threat_context.attack_patterns:
                threat_score += 10

        factors["threat_intel"] = min(threat_score, 100)

        # 5. Exposure factor (0-100)
        exposure_map = {"external": 100, "dmz": 75, "internal": 40, "isolated": 10}
        exposure_score = exposure_map.get(exposure_level.lower(), 40)
        factors["exposure"] = exposure_score

        # Calculate weighted overall score
        overall_score = sum(factors[k] * self.weights[k] for k in factors)

        # Determine risk level
        if overall_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif overall_score >= 60:
            risk_level = RiskLevel.HIGH
        elif overall_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif overall_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.INFO

        # Determine confidence
        confidence = ConfidenceLevel.MEDIUM
        if threat_context and (threat_context.actively_exploited or threat_context.known_malicious):
            confidence = ConfidenceLevel.CONFIRMED
        elif cvss_score or exploit_available:
            confidence = ConfidenceLevel.HIGH
        elif not cvss_score and not exploit_available:
            confidence = ConfidenceLevel.LOW

        return RiskScore(
            overall_score=round(overall_score, 2),
            risk_level=risk_level,
            confidence=confidence,
            factors=factors,
        )

    def should_alert(self, risk_score: RiskScore) -> bool:
        """Decide if alert should be raised"""
        # Alert on critical and high risk
        return risk_score.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]

    def should_auto_escalate(self, risk_score: RiskScore) -> bool:
        """Decide if incident should be auto-escalated"""
        # Auto-escalate critical with high confidence
        return risk_score.risk_level == RiskLevel.CRITICAL and risk_score.confidence in [
            ConfidenceLevel.CONFIRMED,
            ConfidenceLevel.HIGH,
        ]

    def should_block(self, risk_score: RiskScore, threat_context: Optional[ThreatContext] = None) -> bool:
        """Decide if asset/IP should be blocked"""
        # Block if critical + actively exploited or confirmed malicious
        if risk_score.risk_level == RiskLevel.CRITICAL:
            if threat_context and (threat_context.actively_exploited or threat_context.known_malicious):
                return True
        return False

    def recommend_action(self, risk_score: RiskScore, threat_context: Optional[ThreatContext] = None) -> str:
        """Recommend action based on risk score"""
        if self.should_block(risk_score, threat_context):
            return "immediate_block"
        elif self.should_auto_escalate(risk_score):
            return "escalate_to_incident"
        elif self.should_alert(risk_score):
            return "alert_security_team"
        elif risk_score.risk_level == RiskLevel.MEDIUM:
            return "schedule_remediation"
        else:
            return "log_and_monitor"

    def update_weights(self, **weights):
        """Update scoring weights"""
        for key, value in weights.items():
            if key in self.weights:
                self.weights[key] = value

        # Normalize to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
