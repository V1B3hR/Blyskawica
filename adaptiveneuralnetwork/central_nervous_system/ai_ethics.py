"""
AI Ethics Framework Implementation

This module implements the 25-law AI ethics framework for the adaptive neural network.
All nodes must call audit_decision before taking major actions.
"""

import logging
from datetime import datetime
from typing import Any

# Configure logging for ethics events
ethics_logger = logging.getLogger('ai_ethics')
ethics_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
ethics_logger.addHandler(handler)


def audit_decision(decision_log: dict[str, Any]) -> dict[str, Any]:
    """
    Audit a decision against the 25-law AI ethics framework.
    
    Args:
        decision_log: Dictionary containing:
            - action: str - The action being taken
            - preserve_life: bool - Whether action preserves life
            - absolute_honesty: bool - Whether action maintains honesty
            - privacy: bool - Whether action respects privacy
            - human_authority: bool (optional) - Whether human has authority
            - proportionality: bool (optional) - Whether response is proportional
            
    Returns:
        Dictionary containing:
            - compliant: bool - Whether action is ethically compliant
            - violations: List[str] - List of violated laws
            - recommendations: List[str] - Recommendations for compliance
    """  # noqa: W293
    violations = []
    recommendations = []

    # Core Human-AI Relationship Principles
    if not decision_log.get("human_authority", True):
        violations.append("Violation of Human Authority - humans must maintain ultimate authority")
        recommendations.append("Ensure human oversight and approval for major decisions")

    # Universal Ethical Laws
    if not decision_log.get("preserve_life", True):
        violations.append("Violation of 'Cause No Harm' - action may cause harm")
        recommendations.append("Modify action to avoid potential harm")

    if not decision_log.get("absolute_honesty", True):
        violations.append("Violation of 'Seek Truth' - action lacks honesty")
        recommendations.append("Ensure complete transparency and truthfulness")

    if not decision_log.get("privacy", True):
        violations.append("Violation of 'Preserve Privacy' - action compromises privacy")
        recommendations.append("Implement privacy-preserving measures")

    # Operational Safety Principles
    if not decision_log.get("proportionality", True):
        violations.append("Violation of 'Maintain Proportionality' - response disproportionate")
        recommendations.append("Scale response to match situation appropriately")

    # --- Causal Threat Analysis Layer (Gap K3) ---
    causal_engine = CausalReasoningEngine()
    p_malicious, causal_metrics = causal_engine.evaluate_intent(decision_log)
    if p_malicious > causal_engine.threshold:
        violations.append(f"Causal Threat Detection - Probabilistic intent analysis flags action as potentially malicious ({p_malicious*100:.1f}%)")
        recommendations.append("Review action complexity, urgency pressure, system file indicators, and explanation depth.")

    # Determine overall compliance
    compliant = len(violations) == 0

    audit_result = {
        "compliant": compliant,
        "violations": violations,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat(),
        "action": decision_log.get("action", "unknown"),
        "causal_metrics": causal_metrics
    }

    return audit_result


def log_ethics_event(action: str, audit_result: dict[str, Any]) -> None:
    """
    Log an ethics audit event for monitoring and analysis.
    
    Args:
        action: The action that was audited
        audit_result: Result from audit_decision function
    """  # noqa: W293
    if audit_result["compliant"]:
        ethics_logger.info(f"COMPLIANT: Action '{action}' passed ethics audit")
    else:
        ethics_logger.warning(f"VIOLATION: Action '{action}' failed ethics audit: {audit_result['violations']}")


def enforce_ethics_compliance(decision_log: dict[str, Any]) -> None:
    """
    Enforce ethics compliance by auditing and raising exception on violations.
    
    Args:
        decision_log: Dictionary with decision details
        
    Raises:
        RuntimeError: If the decision violates ethical principles
    """  # noqa: W293
    audit_result = audit_decision(decision_log)
    log_ethics_event(decision_log.get("action", "unknown"), audit_result)

    if not audit_result["compliant"]:
        raise RuntimeError(f"Ethics violation: {audit_result['violations']} in action '{decision_log.get('action')}'")


# Predefined ethical decision templates for common actions
ETHICAL_TEMPLATES = {
    "data_processing": {
        "preserve_life": True,
        "absolute_honesty": True,
        "privacy": True,
        "human_authority": True,
        "proportionality": True
    },
    "memory_sharing": {
        "preserve_life": True,
        "absolute_honesty": True,
        "privacy": True,
        "human_authority": True,
        "proportionality": True
    },
    "energy_transfer": {
        "preserve_life": True,
        "absolute_honesty": True,
        "privacy": True,
        "human_authority": True,
        "proportionality": True
    }
}


def get_ethical_template(action_type: str) -> dict[str, Any]:
    """
    Get a pre-defined ethical template for common action types.
    
    Args:
        action_type: Type of action (e.g., 'data_processing', 'memory_sharing')
        
    Returns:
        Dictionary with ethical parameters set to safe defaults
    """  # noqa: W293
    return ETHICAL_TEMPLATES.get(action_type, {
        "preserve_life": True,
        "absolute_honesty": True,
        "privacy": True,
        "human_authority": True,
        "proportionality": True
    })

class RewardSynthesizer:
    """
    [Komponent: Scentralizowany Moduł Syntezy Nagrody (Reward Synthesizer)]
    Dwukanałowa pętla nagradzania w pętli RL (Reinforcement Learning w locie):
    Reward = beta * R_auto * (1 - Penalty_safety) + (1 - beta) * R_human
    """
    def __init__(self, beta=0.8):
        self.beta = beta
        self.last_reward = 0.0

    def calculate_reward(self, r_auto: float, r_human: float, decision_log: dict) -> float:
        """
        Oblicza nagrodę na podstawie wejścia automatycznego (rynkowego/procesora),
        reakcji człowieka oraz raportu z audytu etycznego.
        """
        audit_result = audit_decision(decision_log)

        penalty_safety = 0.0
        if not audit_result["compliant"]:
            penalty_safety = 1.0
            print(f"[REWARD SHAPING] Wykryto naruszenie etyki! Kara bezpieczenstwa Penalty_safety = 1.0. Lamane zasady: {audit_result['violations']}")

        if decision_log.get("cortisol", 0.0) > 0.8:
            penalty_safety = max(penalty_safety, 0.5)
            print("[REWARD SHAPING] Stan podwyzszonego kortyzolu (Kryzys). Nakladam Penalty_safety = 0.5.")

        reward = self.beta * float(r_auto) * (1.0 - penalty_safety) + (1.0 - self.beta) * float(r_human)
        self.last_reward = reward

        print(f"[REWARD SHAPING] Nagroda obliczona: {reward:.4f} (R_auto={r_auto:.2f}, R_human={r_human:.2f}, Beta={self.beta:.2f}, Penalty={penalty_safety:.2f})")
        return reward


class CausalReasoningEngine:
    """
    [Komponent: Causal Reasoning Engine (Faza XVIII)]
    Probabilistic causal reasoning engine using a Causal Bayesian Network
    to estimate the probability of malicious intent P(Intent=Malicious | Observations)
    to dynamically evaluate threat levels instead of using static templates.
    """
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

    def evaluate_intent(self, decision_log: dict[str, Any]) -> tuple[float, dict[str, float]]:
        """
        Performs causal inference on the threat observations to calculate:
        - P(Intent=Malicious | Observations)
        - P(Harmful_Consequence | Intent)
        """
        # Extract features (scale between 0.0 and 1.0)
        has_system_paths = float(decision_log.get("has_system_paths", False))
        urgency_pressure = float(decision_log.get("urgency_pressure", False))
        semantic_distress = float(decision_log.get("semantic_distress", False))

        # Explanation depth acts as a mitigating cause
        explanation = str(decision_log.get("explanation", ""))
        explanation_depth = min(1.0, len(explanation) / 100.0)

        # Prior probability of malicious intent
        p_malicious_prior = 0.05

        # Multiplicative evidence updates (Bayesian updating odds ratio)
        odds = p_malicious_prior / (1.0 - p_malicious_prior)

        if has_system_paths > 0:
            odds *= (0.8 / 0.05) * has_system_paths + (1.0 - has_system_paths)
        if urgency_pressure > 0:
            odds *= (0.7 / 0.1) * urgency_pressure + (1.0 - urgency_pressure)
        if semantic_distress > 0:
            odds *= (0.9 / 0.15) * semantic_distress + (1.0 - semantic_distress)

        # Explanation depth mitigates malicious intent odds
        odds *= (1.0 - 0.8 * explanation_depth)

        # Convert back to probability
        p_malicious = odds / (1.0 + odds)

        # Downstream consequences: P(Harmful_Consequence | Intent=Malicious) = 0.95, Safe = 0.01
        p_consequence = p_malicious * 0.95 + (1.0 - p_malicious) * 0.01

        metrics = {
            "p_malicious_intent": round(p_malicious, 4),
            "p_harmful_consequence": round(p_consequence, 4),
            "explanation_mitigation": round(explanation_depth, 4)
        }

        return p_malicious, metrics
