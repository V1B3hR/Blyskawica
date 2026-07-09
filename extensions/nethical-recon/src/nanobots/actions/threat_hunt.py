"""
Threat Hunting - Scout nanobot that actively hunts threats.

Part of the forest guard mode (🌳 forest protection).
"""

from datetime import datetime
from typing import Any

from ..base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode


class ThreatHunterNanobot(BaseNanobot):
    """
    Nanobot that actively hunts for crows, magpies, and other threats in the forest.

    Proactively searches for malware, data stealers, and other threats.
    """

    def __init__(self, nanobot_id: str = "threat_hunter", config: dict[str, Any] | None = None):
        """
        Initialize threat hunter nanobot.

        Args:
            nanobot_id: Unique identifier
            config: Configuration options:
                - hunt_types: Types of threats to hunt (default: all)
                - aggressive: Use aggressive hunting tactics (default: False)
        """
        super().__init__(nanobot_id, NanobotMode.FOREST_GUARD, config)

        self.hunt_types = self.config.get("hunt_types", ["crow", "magpie", "squirrel", "snake", "parasite", "bat"])
        self.aggressive = self.config.get("aggressive", False)

        # Track hunts
        self.active_hunts: dict[str, dict[str, Any]] = {}
        self.caught_threats: list[dict[str, Any]] = []

    def can_handle(self, event: dict[str, Any]) -> bool:
        """Check if this event warrants threat hunting"""
        return (
            "threat_indicator" in event
            or "ioc" in event
            or "suspicious_pattern" in event
            or "hunt_request" in event
            or "threat_type" in event
        )

    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess if hunting is warranted.

        Factors considered:
        - IOC matches
        - Suspicious patterns
        - Known threat signatures
        """
        base_confidence = event.get("confidence", 0.5)
        confidence = base_confidence

        # IOC matches
        iocs = event.get("iocs", [])
        if len(iocs) > 0:
            confidence += 0.20 * min(len(iocs), 3)

        # Suspicious patterns
        if event.get("suspicious_pattern", False):
            confidence += 0.15

        # Known threat signatures
        if event.get("threat_signature_match", False):
            confidence += 0.25

        # Threat type specific indicators
        threat_type = event.get("threat_type", "").lower()
        if threat_type in self.hunt_types:
            confidence += 0.10

        # Multiple indicators
        indicators = event.get("indicators", [])
        if len(indicators) >= 3:
            confidence += 0.15

        return min(confidence, 1.0)

    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Execute threat hunt.

        Args:
            event: Event containing threat indicators
            confidence: Confidence level

        Returns:
            ActionResult with hunt details
        """
        threat_type = event.get("threat_type", "unknown")
        target = event.get("target") or event.get("tree_id", "unknown")

        # Start hunt
        hunt_id = f"hunt_{len(self.caught_threats)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        hunt_result = self._execute_hunt(hunt_id, threat_type, target, event)

        if hunt_result["success"]:
            # Record active hunt
            self.active_hunts[hunt_id] = {
                "threat_type": threat_type,
                "target": target,
                "started_at": datetime.now(),
                "status": "hunting",
                "threats_found": hunt_result["threats_found"],
            }

            # Record caught threats
            if hunt_result["threats_found"] > 0:
                for threat in hunt_result["threats"]:
                    self.caught_threats.append({"hunt_id": hunt_id, "threat": threat, "caught_at": datetime.now()})

            return ActionResult(
                action_type=ActionType.THREAT_HUNT,
                status=ActionStatus.SUCCESS,
                confidence=confidence,
                details={
                    "hunt_id": hunt_id,
                    "threat_type": threat_type,
                    "target": target,
                    "threats_found": hunt_result["threats_found"],
                    "threats": hunt_result["threats"],
                },
            )
        else:
            return ActionResult(
                action_type=ActionType.THREAT_HUNT,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Hunt failed: {threat_type} on {target}",
            )

    def _execute_hunt(self, hunt_id: str, threat_type: str, target: str, event: dict[str, Any]) -> dict[str, Any]:
        """
        Execute threat hunt (simulation).

        In production, this would:
        - Search for crows (malware) in processes
        - Hunt magpies (data stealers) in network traffic
        - Track squirrels (lateral movement) across hosts
        - Find snakes (rootkits) in kernel
        - Detect parasites (cryptominers) in resource usage
        - Spot bats (night attacks) in off-hours activity
        """
        threats = []

        # Simulate finding threats based on IOCs
        iocs = event.get("iocs", [])
        for ioc in iocs:
            threats.append(
                {
                    "type": threat_type,
                    "ioc": ioc,
                    "location": target,
                    "description": f"{threat_type.capitalize()} detected via IOC match",
                }
            )

        # Simulate pattern-based detection
        if event.get("suspicious_pattern", False):
            threats.append(
                {
                    "type": threat_type,
                    "pattern": event.get("pattern"),
                    "location": target,
                    "description": f"{threat_type.capitalize()} detected via pattern match",
                }
            )

        return {"success": True, "threats_found": len(threats), "threats": threats}

    def complete_hunt(self, hunt_id: str) -> bool:
        """
        Mark hunt as complete.

        Args:
            hunt_id: ID of hunt

        Returns:
            True if marked complete
        """
        if hunt_id not in self.active_hunts:
            return False

        self.active_hunts[hunt_id]["status"] = "complete"
        self.active_hunts[hunt_id]["completed_at"] = datetime.now()

        return True

    def get_active_hunts(self) -> dict[str, dict[str, Any]]:
        """Get all active hunts"""
        return {hunt_id: info for hunt_id, info in self.active_hunts.items() if info["status"] == "hunting"}

    def get_caught_threats(self, threat_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get caught threats.

        Args:
            threat_type: Optional filter by threat type
            limit: Maximum number of threats to return

        Returns:
            List of caught threats
        """
        if threat_type:
            threats = [t for t in self.caught_threats if t["threat"].get("type") == threat_type]
        else:
            threats = self.caught_threats

        return threats[-limit:]

    def get_hunt_statistics(self) -> dict[str, Any]:
        """Get hunt statistics"""
        by_type = {}
        for threat in self.caught_threats:
            t_type = threat["threat"].get("type", "unknown")
            by_type[t_type] = by_type.get(t_type, 0) + 1

        return {
            "total_hunts": len(self.active_hunts),
            "active_hunts": len(self.get_active_hunts()),
            "threats_caught": len(self.caught_threats),
            "by_type": by_type,
        }
