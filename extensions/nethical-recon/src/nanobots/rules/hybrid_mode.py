"""
Hybrid Mode - Intelligent decision logic combining rules and confidence.

Implements the hybrid decision system:
- ≥90% confidence: Auto-fire (nanobot acts autonomously)
- 70-89% confidence: Propose (suggest action to hunter)
- <70% confidence: Observe (monitor only)
"""

from enum import Enum
from typing import Any


class DecisionMode(Enum):
    """Decision modes based on confidence"""

    AUTO_FIRE = "auto_fire"  # ≥90% - nanobot acts autonomously
    PROPOSE = "propose"  # 70-89% - propose to hunter
    OBSERVE = "observe"  # <70% - monitor only


class HybridDecisionMaker:
    """
    Intelligent decision maker that combines rules, confidence, and context.

    The hybrid mode allows nanobots to:
    1. Act autonomously when confidence is high (≥90%)
    2. Propose actions when confidence is moderate (70-89%)
    3. Observe and learn when confidence is low (<70%)
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize hybrid decision maker.

        Args:
            config: Configuration options:
                - auto_fire_threshold: Threshold for auto-fire (default: 0.90)
                - propose_threshold: Threshold for propose (default: 0.70)
                - observe_threshold: Threshold for observe (default: 0.0)
                - context_weight: Weight for context in decision (default: 0.1)
        """
        self.config = config or {}

        self.auto_fire_threshold = self.config.get("auto_fire_threshold", 0.90)
        self.propose_threshold = self.config.get("propose_threshold", 0.70)
        self.observe_threshold = self.config.get("observe_threshold", 0.0)
        self.context_weight = self.config.get("context_weight", 0.1)

    def make_decision(
        self, base_confidence: float, event: dict[str, Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make a decision based on confidence, event, and context.

        Args:
            base_confidence: Base confidence level (0.0-1.0)
            event: Event data
            context: Optional additional context

        Returns:
            Decision with mode, adjusted confidence, and reasoning
        """
        # Adjust confidence based on context
        adjusted_confidence = self._adjust_confidence(base_confidence, event, context)

        # Determine decision mode
        mode = self._determine_mode(adjusted_confidence)

        # Generate reasoning
        reasoning = self._generate_reasoning(base_confidence, adjusted_confidence, mode, event, context)

        return {
            "mode": mode.value,
            "base_confidence": base_confidence,
            "adjusted_confidence": adjusted_confidence,
            "confidence_change": adjusted_confidence - base_confidence,
            "reasoning": reasoning,
            "should_act": mode == DecisionMode.AUTO_FIRE,
            "should_propose": mode == DecisionMode.PROPOSE,
            "should_observe": mode == DecisionMode.OBSERVE,
        }

    def _adjust_confidence(
        self, base_confidence: float, event: dict[str, Any], context: dict[str, Any] | None
    ) -> float:
        """
        Adjust confidence based on context.

        Context factors:
        - Historical behavior
        - Threat severity
        - Time of day
        - Source reputation
        """
        confidence = base_confidence

        if not context:
            return confidence

        # Historical behavior
        historical_threat = context.get("historical_threat_level", 0.0)
        if historical_threat > 0.7:
            confidence += self.context_weight
        elif historical_threat < 0.3:
            confidence -= self.context_weight * 0.5

        # Recent activity
        recent_incidents = context.get("recent_incidents", 0)
        if recent_incidents > 5:
            confidence += self.context_weight * 0.5

        # Time-based factors
        is_off_hours = context.get("is_off_hours", False)
        if is_off_hours:
            # More suspicious during off-hours
            confidence += self.context_weight * 0.3

        # Source reputation
        source_reputation = context.get("source_reputation", 0.5)  # 0-1 scale
        if source_reputation < 0.3:
            confidence += self.context_weight
        elif source_reputation > 0.7:
            confidence -= self.context_weight * 0.5

        # Critical infrastructure
        is_critical = context.get("is_critical_infrastructure", False)
        if is_critical:
            # Be more cautious with critical systems
            confidence += self.context_weight * 0.2

        # Cap at valid range
        return max(0.0, min(1.0, confidence))

    def _determine_mode(self, confidence: float) -> DecisionMode:
        """Determine decision mode based on confidence"""
        if confidence >= self.auto_fire_threshold:
            return DecisionMode.AUTO_FIRE
        elif confidence >= self.propose_threshold:
            return DecisionMode.PROPOSE
        else:
            return DecisionMode.OBSERVE

    def _generate_reasoning(
        self,
        base_confidence: float,
        adjusted_confidence: float,
        mode: DecisionMode,
        event: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> str:
        """Generate human-readable reasoning for the decision"""
        reasons = []

        # Base confidence
        if base_confidence >= 0.9:
            reasons.append("High initial confidence")
        elif base_confidence >= 0.7:
            reasons.append("Moderate initial confidence")
        else:
            reasons.append("Low initial confidence")

        # Context adjustments
        if context:
            if context.get("historical_threat_level", 0) > 0.7:
                reasons.append("History of threats from this source")

            if context.get("recent_incidents", 0) > 5:
                reasons.append("Multiple recent incidents")

            if context.get("is_off_hours", False):
                reasons.append("Activity during off-hours")

            if context.get("source_reputation", 0.5) < 0.3:
                reasons.append("Poor source reputation")

            if context.get("is_critical_infrastructure", False):
                reasons.append("Critical infrastructure target")

        # Event-specific factors
        if event.get("threat_score", 0) >= 8.0:
            reasons.append("High threat score")

        if event.get("known_malicious", False):
            reasons.append("Known malicious actor")

        # Mode explanation
        if mode == DecisionMode.AUTO_FIRE:
            action_text = "Taking autonomous action"
        elif mode == DecisionMode.PROPOSE:
            action_text = "Proposing action for hunter approval"
        else:
            action_text = "Observing and monitoring"

        reasoning = f"{action_text} ({adjusted_confidence*100:.1f}% confidence). " + "; ".join(reasons)

        return reasoning

    def should_escalate(self, decision: dict[str, Any]) -> bool:
        """
        Determine if decision should be escalated to hunter.

        Escalate if:
        - Mode is PROPOSE
        - Mode is AUTO_FIRE but confidence is close to threshold
        """
        mode = DecisionMode(decision["mode"])
        confidence = decision["adjusted_confidence"]

        if mode == DecisionMode.PROPOSE:
            return True

        # Escalate AUTO_FIRE decisions near threshold (within 5%)
        if mode == DecisionMode.AUTO_FIRE and confidence < self.auto_fire_threshold + 0.05:
            return True

        return False

    def get_thresholds(self) -> dict[str, float]:
        """Get current decision thresholds"""
        return {
            "auto_fire": self.auto_fire_threshold,
            "propose": self.propose_threshold,
            "observe": self.observe_threshold,
        }

    def update_thresholds(
        self, auto_fire: float | None = None, propose: float | None = None, observe: float | None = None
    ):
        """Update decision thresholds"""
        if auto_fire is not None:
            self.auto_fire_threshold = max(0.0, min(1.0, auto_fire))

        if propose is not None:
            self.propose_threshold = max(0.0, min(1.0, propose))

        if observe is not None:
            self.observe_threshold = max(0.0, min(1.0, observe))
