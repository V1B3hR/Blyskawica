"""
IP Blocking Action - Defensive nanobot that blocks suspicious IPs.

Part of the defensive mode (🛡️ antibody behavior).
"""

import ipaddress
import subprocess
from typing import Any

from ..base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode


class IPBlockerNanobot(BaseNanobot):
    """
    Nanobot that automatically blocks suspicious IP addresses.

    Uses iptables (Linux) or pf (BSD) to block IPs based on threat assessment.
    """

    def __init__(self, nanobot_id: str = "ip_blocker", config: dict[str, Any] | None = None):
        """
        Initialize IP blocker nanobot.

        Args:
            nanobot_id: Unique identifier
            config: Configuration options:
                - method: 'iptables', 'pf', or 'simulation' (default: simulation)
                - whitelist: List of IPs to never block
                - max_blocks: Maximum number of IPs to block
        """
        super().__init__(nanobot_id, NanobotMode.DEFENSIVE, config)

        self.method = self.config.get("method", "simulation")  # simulation, iptables, pf
        self.whitelist = self.config.get("whitelist", [])
        self.max_blocks = self.config.get("max_blocks", 1000)
        self.blocked_ips: list[str] = []

    def can_handle(self, event: dict[str, Any]) -> bool:
        """Check if this event contains an IP to potentially block"""
        # Event must have 'source_ip' or 'ip' field
        return "source_ip" in event or "ip" in event

    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess threat level based on event data.

        Factors considered:
        - Threat score from event
        - Port scanning behavior
        - Brute force attempts
        - Known malicious patterns
        """
        base_confidence = event.get("confidence", 0.5)
        threat_score = event.get("threat_score", 5.0)  # 0-10 scale

        # Increase confidence based on threat indicators
        confidence = base_confidence

        # Port scanning
        if event.get("port_scan_detected", False):
            confidence += 0.2

        # Brute force
        if event.get("brute_force_attempt", False):
            confidence += 0.25

        # Multiple failed auth attempts
        failed_attempts = event.get("failed_auth_attempts", 0)
        if failed_attempts >= 5:
            confidence += 0.15
        elif failed_attempts >= 3:
            confidence += 0.10

        # High threat score
        if threat_score >= 8.0:
            confidence += 0.2
        elif threat_score >= 6.0:
            confidence += 0.1

        # Known malicious IP
        if event.get("known_malicious", False):
            confidence += 0.3

        # Cap at 1.0
        return min(confidence, 1.0)

    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Block the IP address.

        Args:
            event: Event containing IP to block
            confidence: Confidence level

        Returns:
            ActionResult with blocking details
        """
        # Extract IP
        ip = event.get("source_ip") or event.get("ip")

        if not ip:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message="No IP address found in event",
            )

        # Validate IP
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Invalid IP address: {ip}",
            )

        # Check whitelist
        if ip in self.whitelist:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.SKIPPED,
                confidence=confidence,
                details={"reason": "whitelisted", "ip": ip},
            )

        # Check if already blocked
        if ip in self.blocked_ips:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.SKIPPED,
                confidence=confidence,
                details={"reason": "already_blocked", "ip": ip},
            )

        # Check max blocks limit
        if len(self.blocked_ips) >= self.max_blocks:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Max blocks limit reached ({self.max_blocks})",
            )

        # Execute blocking based on method
        if self.method == "simulation":
            success = self._simulate_block(ip)
        elif self.method == "iptables":
            success = self._block_with_iptables(ip)
        elif self.method == "pf":
            success = self._block_with_pf(ip)
        else:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Unknown blocking method: {self.method}",
            )

        if success:
            self.blocked_ips.append(ip)
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.SUCCESS,
                confidence=confidence,
                details={
                    "ip": ip,
                    "method": self.method,
                    "reason": event.get("reason", "threat_detected"),
                    "threat_score": event.get("threat_score", 0),
                    "total_blocked": len(self.blocked_ips),
                },
            )
        else:
            return ActionResult(
                action_type=ActionType.BLOCK_IP,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message=f"Failed to block IP: {ip}",
            )

    def _simulate_block(self, ip: str) -> bool:
        """Simulate IP blocking (for testing)"""
        return True

    def _block_with_iptables(self, ip: str) -> bool:
        """
        Block IP using iptables (Linux).

        Requires root privileges.
        """
        try:
            # Add rule to DROP packets from IP
            subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True, capture_output=True, timeout=10
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _block_with_pf(self, ip: str) -> bool:
        """
        Block IP using pf (BSD/macOS).

        Requires root privileges.
        """
        try:
            # Add IP to blocked table
            subprocess.run(["pfctl", "-t", "blocked_ips", "-T", "add", ip], check=True, capture_output=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def unblock_ip(self, ip: str) -> bool:
        """
        Unblock a previously blocked IP.

        Args:
            ip: IP address to unblock

        Returns:
            True if unblocked successfully
        """
        if ip not in self.blocked_ips:
            return False

        if self.method == "simulation":
            success = True
        elif self.method == "iptables":
            success = self._unblock_with_iptables(ip)
        elif self.method == "pf":
            success = self._unblock_with_pf(ip)
        else:
            return False

        if success:
            self.blocked_ips.remove(ip)

        return success

    def _unblock_with_iptables(self, ip: str) -> bool:
        """Unblock IP using iptables"""
        try:
            subprocess.run(
                ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True, capture_output=True, timeout=10
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _unblock_with_pf(self, ip: str) -> bool:
        """Unblock IP using pf"""
        try:
            subprocess.run(
                ["pfctl", "-t", "blocked_ips", "-T", "delete", ip], check=True, capture_output=True, timeout=10
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_blocked_ips(self) -> list[str]:
        """Get list of currently blocked IPs"""
        return self.blocked_ips.copy()

    def clear_all_blocks(self) -> int:
        """
        Clear all blocked IPs.

        Returns:
            Number of IPs unblocked
        """
        count = 0
        ips_to_unblock = self.blocked_ips.copy()

        for ip in ips_to_unblock:
            if self.unblock_ip(ip):
                count += 1

        return count
