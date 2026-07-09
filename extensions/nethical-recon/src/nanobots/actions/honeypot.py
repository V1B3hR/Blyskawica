"""
Honeypot Deployment - Defensive nanobot that deploys honeypots.

Part of the defensive mode (🛡️ antibody behavior).
"""

from datetime import datetime
from typing import Any

from ..base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode


class HoneypotNanobot(BaseNanobot):
    """
    Nanobot that automatically deploys honeypots to trap attackers.

    Deploys decoy services and monitors interactions to gather intelligence.
    """

    def __init__(self, nanobot_id: str = "honeypot_deployer", config: dict[str, Any] | None = None):
        """
        Initialize honeypot nanobot.

        Args:
            nanobot_id: Unique identifier
            config: Configuration options:
                - max_honeypots: Maximum number of active honeypots (default: 10)
                - honeypot_types: List of honeypot types to deploy
                - auto_deploy: Auto-deploy on suspicious activity (default: True)
        """
        super().__init__(nanobot_id, NanobotMode.DEFENSIVE, config)

        self.max_honeypots = self.config.get("max_honeypots", 10)
        self.honeypot_types = self.config.get("honeypot_types", ["ssh", "http", "ftp", "mysql", "smtp"])
        self.auto_deploy = self.config.get("auto_deploy", True)

        # Track deployed honeypots
        self.active_honeypots: dict[str, dict[str, Any]] = {}
        self.interactions: list[dict[str, Any]] = []

    def can_handle(self, event: dict[str, Any]) -> bool:
        """Check if this event warrants honeypot deployment"""
        # Deploy honeypots for reconnaissance attempts
        return (
            event.get("port_scan_detected", False)
            or event.get("recon_activity", False)
            or event.get("suspicious_probing", False)
            or "honeypot_trigger" in event
        )

    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess threat level for honeypot deployment.

        Factors considered:
        - Reconnaissance activity
        - Port scanning
        - Suspicious probing
        - Known attack patterns
        """
        base_confidence = event.get("confidence", 0.5)
        confidence = base_confidence

        # Strong indicators for honeypot deployment
        if event.get("port_scan_detected", False):
            confidence += 0.25

        if event.get("recon_activity", False):
            confidence += 0.20

        if event.get("suspicious_probing", False):
            confidence += 0.15

        # Multiple scan types
        scan_types = event.get("scan_types", [])
        if len(scan_types) > 2:
            confidence += 0.15

        # Targeting multiple ports
        ports_scanned = event.get("ports_scanned", [])
        if len(ports_scanned) > 10:
            confidence += 0.10

        return min(confidence, 1.0)

    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Deploy a honeypot.

        Args:
            event: Event triggering honeypot deployment
            confidence: Confidence level

        Returns:
            ActionResult with deployment details
        """
        # Check if we've reached max honeypots
        if len(self.active_honeypots) >= self.max_honeypots:
            return ActionResult(
                action_type=ActionType.HONEYPOT,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Max honeypots limit reached ({self.max_honeypots})",
            )

        # Determine honeypot type based on event
        honeypot_type = self._select_honeypot_type(event)

        # Deploy honeypot (simulation)
        honeypot_id = f"honeypot_{len(self.active_honeypots)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        success = self._deploy_honeypot(honeypot_id, honeypot_type, event)

        if success:
            self.active_honeypots[honeypot_id] = {
                "type": honeypot_type,
                "deployed_at": datetime.now(),
                "triggered_by": event.get("source_ip"),
                "port": self._get_honeypot_port(honeypot_type),
                "interactions": 0,
            }

            return ActionResult(
                action_type=ActionType.HONEYPOT,
                status=ActionStatus.SUCCESS,
                confidence=confidence,
                details={
                    "honeypot_id": honeypot_id,
                    "type": honeypot_type,
                    "port": self.active_honeypots[honeypot_id]["port"],
                    "total_active": len(self.active_honeypots),
                },
            )
        else:
            return ActionResult(
                action_type=ActionType.HONEYPOT,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Failed to deploy honeypot: {honeypot_type}",
            )

    def _select_honeypot_type(self, event: dict[str, Any]) -> str:
        """Select honeypot type based on event characteristics"""
        # Check which ports were scanned
        ports_scanned = event.get("ports_scanned", [])

        if 22 in ports_scanned:
            return "ssh"
        elif 80 in ports_scanned or 443 in ports_scanned:
            return "http"
        elif 21 in ports_scanned:
            return "ftp"
        elif 3306 in ports_scanned:
            return "mysql"
        elif 25 in ports_scanned:
            return "smtp"
        else:
            # Default to SSH honeypot
            return "ssh"

    def _get_honeypot_port(self, honeypot_type: str) -> int:
        """Get port for honeypot type"""
        port_map = {
            "ssh": 2222,  # Non-standard SSH port
            "http": 8080,  # Non-standard HTTP port
            "ftp": 2121,  # Non-standard FTP port
            "mysql": 3307,  # Non-standard MySQL port
            "smtp": 2525,  # Non-standard SMTP port
        }
        return port_map.get(honeypot_type, 9999)

    def _deploy_honeypot(self, honeypot_id: str, honeypot_type: str, event: dict[str, Any]) -> bool:
        """
        Deploy a honeypot (simulation).

        In production, this would:
        - Spin up a containerized honeypot service
        - Configure network rules
        - Set up logging and monitoring
        """
        # Simulation - always succeeds
        return True

    def record_interaction(self, honeypot_id: str, interaction_data: dict[str, Any]):
        """
        Record an interaction with a honeypot.

        Args:
            honeypot_id: ID of honeypot
            interaction_data: Details of the interaction
        """
        if honeypot_id not in self.active_honeypots:
            return

        self.active_honeypots[honeypot_id]["interactions"] += 1

        interaction = {"honeypot_id": honeypot_id, "timestamp": datetime.now(), "data": interaction_data}
        self.interactions.append(interaction)

    def deactivate_honeypot(self, honeypot_id: str) -> bool:
        """
        Deactivate a honeypot.

        Args:
            honeypot_id: ID of honeypot to deactivate

        Returns:
            True if deactivated
        """
        if honeypot_id in self.active_honeypots:
            del self.active_honeypots[honeypot_id]
            return True
        return False

    def get_active_honeypots(self) -> dict[str, dict[str, Any]]:
        """Get all active honeypots"""
        return self.active_honeypots.copy()

    def get_interactions(self, honeypot_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get honeypot interactions.

        Args:
            honeypot_id: Optional filter by honeypot ID
            limit: Maximum number of interactions to return

        Returns:
            List of interactions
        """
        if honeypot_id:
            interactions = [i for i in self.interactions if i["honeypot_id"] == honeypot_id]
        else:
            interactions = self.interactions

        return interactions[-limit:]

    def clear_all_honeypots(self) -> int:
        """
        Deactivate all honeypots.

        Returns:
            Number of honeypots deactivated
        """
        count = len(self.active_honeypots)
        self.active_honeypots.clear()
        return count
