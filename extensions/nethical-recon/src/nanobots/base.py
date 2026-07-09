"""
Base classes for nanobots - automated response system.

This module provides the foundation for the nanobot system:
- Base nanobot class
- Action result tracking
- Confidence scoring
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NanobotMode(Enum):
    """Operating modes for nanobots"""

    DEFENSIVE = "defensive"  # 🛡️ Auto-block, rate limit, honeypot
    SCOUT = "scout"  # 🔍 Auto-enumerate, follow-up scans
    ADAPTIVE = "adaptive"  # 🧬 Learn patterns, ML-based detection
    FOREST_GUARD = "forest_guard"  # 🌳 Patrol trees, hunt threats


class ActionType(Enum):
    """Types of actions nanobots can take"""

    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    HONEYPOT = "honeypot"
    ALERT = "alert"
    ENUMERATE = "enumerate"
    FOREST_PATROL = "forest_patrol"
    THREAT_HUNT = "threat_hunt"
    LEARN_BASELINE = "learn_baseline"
    DETECT_ANOMALY = "detect_anomaly"


class ActionStatus(Enum):
    """Status of nanobot action"""

    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ActionResult:
    """Result of a nanobot action"""

    action_type: ActionType
    status: ActionStatus
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None

    def is_successful(self) -> bool:
        """Check if action was successful"""
        return self.status == ActionStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action_type": self.action_type.value,
            "status": self.status.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "error_message": self.error_message,
        }


class BaseNanobot(ABC):
    """
    Base class for all nanobots.

    Nanobots are autonomous agents that respond to threats automatically
    based on confidence levels and configured rules.
    """

    def __init__(self, nanobot_id: str, mode: NanobotMode, config: dict[str, Any] | None = None):
        """
        Initialize nanobot.

        Args:
            nanobot_id: Unique identifier for this nanobot
            mode: Operating mode (defensive, scout, adaptive, forest_guard)
            config: Optional configuration dictionary
        """
        self.nanobot_id = nanobot_id
        self.mode = mode
        self.config = config or {}
        self.is_active = False
        self.action_history: list[ActionResult] = []

        # Confidence thresholds for action
        self.auto_fire_threshold = self.config.get("auto_fire_threshold", 0.90)  # ≥90% - auto action
        self.propose_threshold = self.config.get("propose_threshold", 0.70)  # 70-89% - propose
        self.observe_threshold = self.config.get("observe_threshold", 0.0)  # <70% - observe

    @abstractmethod
    def can_handle(self, event: dict[str, Any]) -> bool:
        """
        Check if this nanobot can handle the given event.

        Args:
            event: Event data containing threat information

        Returns:
            True if this nanobot can handle the event
        """
        pass

    @abstractmethod
    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess threat level and return confidence score.

        Args:
            event: Event data containing threat information

        Returns:
            Confidence score (0.0 to 1.0)
        """
        pass

    @abstractmethod
    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Execute the nanobot action.

        Args:
            event: Event data containing threat information
            confidence: Assessed confidence level

        Returns:
            ActionResult with execution details
        """
        pass

    def should_auto_fire(self, confidence: float) -> bool:
        """Check if confidence is high enough for automatic action"""
        return confidence >= self.auto_fire_threshold

    def should_propose(self, confidence: float) -> bool:
        """Check if confidence warrants proposing action to hunter"""
        return self.propose_threshold <= confidence < self.auto_fire_threshold

    def should_observe(self, confidence: float) -> bool:
        """Check if confidence is too low for action"""
        return confidence < self.propose_threshold

    def process_event(self, event: dict[str, Any]) -> ActionResult | None:
        """
        Process an event and take appropriate action.

        Args:
            event: Event data containing threat information

        Returns:
            ActionResult if action was taken, None otherwise
        """
        if not self.is_active:
            return None

        if not self.can_handle(event):
            return None

        # Assess threat confidence
        confidence = self.assess_threat(event)

        # Decide action based on confidence
        if self.should_observe(confidence):
            # Just observe, no action
            result = ActionResult(
                action_type=ActionType.ALERT,
                status=ActionStatus.SKIPPED,
                confidence=confidence,
                details={"reason": "confidence_too_low", "event": event},
            )
        elif self.should_propose(confidence):
            # Propose action to hunter (create alert)
            result = ActionResult(
                action_type=ActionType.ALERT,
                status=ActionStatus.SUCCESS,
                confidence=confidence,
                details={"reason": "proposed_to_hunter", "event": event},
            )
        else:
            # Auto-fire (execute action)
            result = self.execute_action(event, confidence)

        # Record action history
        self.action_history.append(result)

        return result

    def activate(self):
        """Activate this nanobot"""
        self.is_active = True

    def deactivate(self):
        """Deactivate this nanobot"""
        self.is_active = False

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about this nanobot's actions"""
        total = len(self.action_history)
        if total == 0:
            return {"total_actions": 0, "success_rate": 0.0, "avg_confidence": 0.0}

        successes = sum(1 for r in self.action_history if r.is_successful())
        avg_confidence = sum(r.confidence for r in self.action_history) / total

        return {
            "nanobot_id": self.nanobot_id,
            "mode": self.mode.value,
            "total_actions": total,
            "successes": successes,
            "failures": total - successes,
            "success_rate": successes / total if total > 0 else 0.0,
            "avg_confidence": avg_confidence,
            "is_active": self.is_active,
        }

    def get_recent_actions(self, limit: int = 10) -> list[ActionResult]:
        """Get recent actions"""
        return self.action_history[-limit:]

    def clear_history(self):
        """Clear action history"""
        self.action_history.clear()
