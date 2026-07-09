"""
Adaptive Behavior for Nanobots
Learns from feedback and adapts behavior
"""

import logging
from typing import Any
from datetime import datetime
from collections import defaultdict


class BehaviorProfile:
    """Behavior profile for adaptive learning"""

    def __init__(self, action_type: str):
        self.action_type = action_type
        self.success_count = 0
        self.failure_count = 0
        self.total_executions = 0
        self.success_rate = 0.0
        self.last_updated = datetime.now()

    def record_outcome(self, success: bool):
        """Record action outcome"""
        self.total_executions += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.success_rate = self.success_count / self.total_executions
        self.last_updated = datetime.now()


class AdaptiveBehavior:
    """
    Adaptive behavior system for nanobots
    Learns from feedback and adjusts strategies
    """

    def __init__(self):
        """Initialize adaptive behavior system"""
        self.logger = logging.getLogger("nethical.adaptive_behavior")
        self._initialize_logger()

        # Behavior profiles
        self.profiles: dict[str, BehaviorProfile] = {}

        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.2

        # Statistics
        self.total_adaptations = 0
        self.feedback_count = 0

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [AdaptiveBehavior] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_profile(self, action_type: str) -> BehaviorProfile:
        """Get or create behavior profile"""
        if action_type not in self.profiles:
            self.profiles[action_type] = BehaviorProfile(action_type)
        return self.profiles[action_type]

    def record_feedback(self, action_type: str, success: bool, context: dict[str, Any]):
        """
        Record feedback on action execution

        Args:
            action_type: Type of action executed
            success: Whether action was successful
            context: Additional context
        """
        profile = self.get_profile(action_type)
        profile.record_outcome(success)

        self.feedback_count += 1

        # Adapt if needed
        if profile.total_executions % 10 == 0:
            self._adapt_behavior(action_type, profile)

        self.logger.debug(
            f"Feedback recorded for {action_type}: {'SUCCESS' if success else 'FAILURE'} "
            f"(success rate: {profile.success_rate:.2%})"
        )

    def _adapt_behavior(self, action_type: str, profile: BehaviorProfile):
        """Adapt behavior based on profile"""
        # Adjust parameters based on success rate
        if profile.success_rate < 0.5:
            self.logger.warning(
                f"Low success rate for {action_type} ({profile.success_rate:.2%}), " f"increasing exploration"
            )
            self.exploration_rate = min(0.5, self.exploration_rate + 0.05)
            self.total_adaptations += 1
        elif profile.success_rate > 0.8:
            self.logger.info(
                f"High success rate for {action_type} ({profile.success_rate:.2%}), " f"decreasing exploration"
            )
            self.exploration_rate = max(0.05, self.exploration_rate - 0.02)
            self.total_adaptations += 1

    def should_explore(self, action_type: str) -> bool:
        """
        Decide if nanobot should explore vs exploit

        Args:
            action_type: Type of action

        Returns:
            True if should explore new strategies
        """
        import random

        profile = self.get_profile(action_type)

        # More exploration for new actions
        if profile.total_executions < 10:
            return random.random() < 0.5

        # Use exploration rate for established actions
        return random.random() < self.exploration_rate

    def get_best_action(self, available_actions: list[str]) -> str:
        """
        Select best action based on learned behavior

        Args:
            available_actions: List of available actions

        Returns:
            Selected action type
        """
        if not available_actions:
            return None

        # Get profiles for all actions
        action_scores = {}
        for action in available_actions:
            profile = self.get_profile(action)
            # Score based on success rate and exploration bonus
            score = profile.success_rate
            if profile.total_executions < 5:
                score += 0.3  # Bonus for exploration
            action_scores[action] = score

        # Select action with highest score
        best_action = max(action_scores, key=action_scores.get)
        return best_action

    def get_statistics(self) -> dict[str, Any]:
        """Get adaptive behavior statistics"""
        return {
            "total_adaptations": self.total_adaptations,
            "feedback_count": self.feedback_count,
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate,
            "profiles": {
                action: {
                    "success_rate": profile.success_rate,
                    "total_executions": profile.total_executions,
                    "success_count": profile.success_count,
                    "failure_count": profile.failure_count,
                }
                for action, profile in self.profiles.items()
            },
        }
