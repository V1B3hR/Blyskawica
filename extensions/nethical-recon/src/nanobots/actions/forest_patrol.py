"""
Forest Patrol - Scout nanobot that patrols tree branches.

Part of the forest guard mode (🌳 forest protection).
"""

from datetime import datetime
from typing import Any

from ..base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode


class ForestPatrolNanobot(BaseNanobot):
    """
    Nanobot that patrols forest trees looking for threats in branches.

    Monitors tree health, branch activity, and leaf status.
    """

    def __init__(self, nanobot_id: str = "forest_patrol", config: dict[str, Any] | None = None):
        """
        Initialize forest patrol nanobot.

        Args:
            nanobot_id: Unique identifier
            config: Configuration options:
                - patrol_interval: Seconds between patrols (default: 60)
                - max_trees: Maximum trees to patrol (default: 100)
        """
        super().__init__(nanobot_id, NanobotMode.FOREST_GUARD, config)

        self.patrol_interval = self.config.get("patrol_interval", 60)
        self.max_trees = self.config.get("max_trees", 100)

        # Track patrol status
        self.patrolled_trees: dict[str, dict[str, Any]] = {}
        self.patrol_findings: list[dict[str, Any]] = []
        self.last_patrol: datetime | None = None

    def can_handle(self, event: dict[str, Any]) -> bool:
        """Check if this event is forest-related"""
        return "tree_id" in event or "branch_id" in event or "forest_event" in event or "patrol_request" in event

    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess if patrol is needed.

        Factors considered:
        - Tree health status
        - Suspicious branch activity
        - Threats detected in crown
        """
        base_confidence = event.get("confidence", 0.5)
        confidence = base_confidence

        # Tree health issues
        tree_health = event.get("tree_health", 100)
        if tree_health < 50:
            confidence += 0.25
        elif tree_health < 70:
            confidence += 0.15

        # Suspicious branch activity
        if event.get("suspicious_branch", False):
            confidence += 0.20

        # Threats in crown
        threats = event.get("threats_in_crown", [])
        if len(threats) > 0:
            confidence += 0.15 * min(len(threats), 3)

        # Resource anomalies
        if event.get("resource_anomaly", False):
            confidence += 0.10

        return min(confidence, 1.0)

    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Execute patrol on forest tree.

        Args:
            event: Event containing tree/branch info
            confidence: Confidence level

        Returns:
            ActionResult with patrol details
        """
        tree_id = event.get("tree_id")
        if not tree_id:
            return ActionResult(
                action_type=ActionType.FOREST_PATROL,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message="No tree_id found in event",
            )

        # Check if we're patrolling too many trees
        if len(self.patrolled_trees) >= self.max_trees:
            return ActionResult(
                action_type=ActionType.FOREST_PATROL,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Max trees limit reached ({self.max_trees})",
            )

        # Patrol the tree
        patrol_result = self._patrol_tree(tree_id, event)

        if patrol_result["success"]:
            # Record patrol
            self.patrolled_trees[tree_id] = {
                "last_patrol": datetime.now(),
                "patrol_count": self.patrolled_trees.get(tree_id, {}).get("patrol_count", 0) + 1,
                "findings": patrol_result["findings"],
            }

            # Record any findings
            if patrol_result["findings"]:
                self.patrol_findings.extend(patrol_result["findings"])

            self.last_patrol = datetime.now()

            return ActionResult(
                action_type=ActionType.FOREST_PATROL,
                status=ActionStatus.SUCCESS,
                confidence=confidence,
                details={
                    "tree_id": tree_id,
                    "findings_count": len(patrol_result["findings"]),
                    "findings": patrol_result["findings"],
                    "patrol_count": self.patrolled_trees[tree_id]["patrol_count"],
                },
            )
        else:
            return ActionResult(
                action_type=ActionType.FOREST_PATROL,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Failed to patrol tree: {tree_id}",
            )

    def _patrol_tree(self, tree_id: str, event: dict[str, Any]) -> dict[str, Any]:
        """
        Patrol a tree (simulation).

        In production, this would:
        - Check tree health (CPU, memory, disk)
        - Inspect branches (processes, services)
        - Examine leaves (threads, sessions)
        - Look for threats in crown (anomalies)
        """
        findings = []

        # Simulate finding threats
        if event.get("threats_in_crown"):
            for threat in event["threats_in_crown"]:
                findings.append(
                    {"type": "threat_detected", "threat": threat, "location": "crown", "timestamp": datetime.now()}
                )

        # Check tree health
        tree_health = event.get("tree_health", 100)
        if tree_health < 70:
            findings.append({"type": "low_health", "health_score": tree_health, "timestamp": datetime.now()})

        return {"success": True, "findings": findings}

    def get_patrol_status(self) -> dict[str, Any]:
        """Get patrol status"""
        return {
            "trees_patrolled": len(self.patrolled_trees),
            "total_findings": len(self.patrol_findings),
            "last_patrol": self.last_patrol.isoformat() if self.last_patrol else None,
            "active": self.is_active,
        }

    def get_tree_status(self, tree_id: str) -> dict[str, Any] | None:
        """
        Get patrol status for a specific tree.

        Args:
            tree_id: Tree identifier

        Returns:
            Patrol status or None
        """
        return self.patrolled_trees.get(tree_id)

    def get_recent_findings(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get recent patrol findings.

        Args:
            limit: Maximum number of findings to return

        Returns:
            List of findings
        """
        return self.patrol_findings[-limit:]
