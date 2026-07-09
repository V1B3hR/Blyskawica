"""
Lateral Movement Detection

Detects lateral movement attempts across the network, identifying potential
attacker movement between hosts and privilege escalation attempts.

Part of ROADMAP 5.0 Section V.14: Advanced Security Features
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class MovementType(Enum):
    """Types of lateral movement"""

    RDP = "rdp"  # Remote Desktop Protocol
    SSH = "ssh"  # Secure Shell
    SMB = "smb"  # Server Message Block
    WMI = "wmi"  # Windows Management Instrumentation
    PSEXEC = "psexec"  # PsExec execution
    PASS_THE_HASH = "pass_the_hash"
    PASS_THE_TICKET = "pass_the_ticket"
    REMOTE_SERVICE = "remote_service"
    SCHEDULED_TASK = "scheduled_task"


@dataclass
class MovementPattern:
    """Represents a detected lateral movement pattern"""

    pattern_id: UUID = field(default_factory=uuid4)
    movement_type: MovementType = MovementType.SSH
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_host: str = ""
    destination_host: str = ""
    username: str = ""
    severity: str = "medium"  # low, medium, high, critical
    confidence: float = 0.7
    description: str = ""
    indicators: list[str] = field(default_factory=list)
    path_length: int = 1  # Length of movement chain
    movement_chain: list[str] = field(default_factory=list)  # Sequence of hosts
    recommended_actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MovementChain:
    """Represents a chain of lateral movements"""

    chain_id: UUID = field(default_factory=uuid4)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime = field(default_factory=datetime.utcnow)
    origin_host: str = ""
    current_host: str = ""
    hosts_visited: list[str] = field(default_factory=list)
    movements: list[MovementPattern] = field(default_factory=list)
    username: str = ""
    risk_score: float = 0.0  # 0-100


class LateralMovementDetector:
    """
    Lateral Movement Detector

    Detects and tracks lateral movement across the network by analyzing:
    - Authentication patterns
    - Remote access attempts
    - Process execution on remote hosts
    - Credential usage patterns
    - Network connections

    Detection Techniques:
    - Time-based correlation
    - Hop pattern analysis
    - Credential reuse detection
    - Anomalous authentication tracking
    - Privilege escalation indicators
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize lateral movement detector

        Args:
            config: Configuration options
                - time_window_minutes: Time window for correlating events (default: 10)
                - min_confidence_threshold: Minimum confidence to report (default: 0.6)
                - track_chains: Track movement chains across hosts (default: True)
                - max_chain_age_hours: Maximum age of chain to track (default: 24)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.time_window_minutes = self.config.get("time_window_minutes", 10)
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.6)
        self.track_chains = self.config.get("track_chains", True)
        self.max_chain_age_hours = self.config.get("max_chain_age_hours", 24)

        # Track active movement chains
        self._active_chains: dict[str, MovementChain] = {}  # Key: username
        self._recent_authentications: list[dict[str, Any]] = []

        self.logger.info("Lateral Movement Detector initialized")

    def analyze_authentication(self, auth_event: dict[str, Any]) -> MovementPattern | None:
        """
        Analyze an authentication event for lateral movement indicators

        Args:
            auth_event: Authentication event data
                - timestamp: When the authentication occurred
                - username: User account
                - source_host: Source IP/hostname
                - destination_host: Target host
                - auth_type: Type of authentication (rdp, ssh, smb, etc.)
                - success: Whether authentication succeeded
                - source_process: Process that initiated the connection

        Returns:
            Movement pattern if lateral movement detected, None otherwise
        """
        timestamp = auth_event.get("timestamp", datetime.utcnow())
        username = auth_event.get("username", "")
        source_host = auth_event.get("source_host", "")
        destination_host = auth_event.get("destination_host", "")
        auth_type = auth_event.get("auth_type", "unknown")
        success = auth_event.get("success", False)

        # Only analyze successful authentications
        if not success:
            return None

        # Store for correlation
        self._recent_authentications.append(auth_event)
        self._cleanup_old_authentications()

        # Check for lateral movement indicators
        indicators = self._check_lateral_movement_indicators(auth_event)

        if not indicators:
            return None

        # Calculate confidence based on indicators
        confidence = self._calculate_confidence(indicators)

        if confidence < self.min_confidence_threshold:
            return None

        # Determine movement type
        movement_type = self._determine_movement_type(auth_type, auth_event)

        # Create movement pattern
        pattern = MovementPattern(
            movement_type=movement_type,
            timestamp=timestamp,
            source_host=source_host,
            destination_host=destination_host,
            username=username,
            severity=self._calculate_severity(confidence, indicators),
            confidence=confidence,
            description=f"Potential lateral movement via {movement_type.value} from {source_host} to {destination_host}",
            indicators=indicators,
            recommended_actions=self._generate_recommended_actions(movement_type, indicators),
            metadata=auth_event,
        )

        # Track movement chain if enabled
        if self.track_chains:
            self._update_movement_chain(username, pattern)

        self.logger.info(
            f"Lateral movement detected: {username} from {source_host} to {destination_host} "
            f"(confidence: {confidence:.2f})"
        )

        return pattern

    def analyze_remote_execution(self, execution_event: dict[str, Any]) -> MovementPattern | None:
        """
        Analyze remote code execution event for lateral movement

        Args:
            execution_event: Remote execution event data
                - timestamp: When execution occurred
                - username: User account
                - source_host: Source host
                - target_host: Target host
                - command: Command executed
                - process: Process name
                - execution_method: Method used (wmi, psexec, etc.)

        Returns:
            Movement pattern if lateral movement detected, None otherwise
        """
        timestamp = execution_event.get("timestamp", datetime.utcnow())
        username = execution_event.get("username", "")
        source_host = execution_event.get("source_host", "")
        target_host = execution_event.get("target_host", "")
        execution_method = execution_event.get("execution_method", "unknown")

        # Check for suspicious remote execution
        indicators = []

        # Remote execution is inherently suspicious
        indicators.append("remote_code_execution")

        # Check execution method
        suspicious_methods = ["wmi", "psexec", "dcom", "scheduled_task"]
        if execution_method.lower() in suspicious_methods:
            indicators.append(f"suspicious_method:{execution_method}")

        # Check for privilege escalation indicators
        if "admin" in username.lower() or "system" in username.lower():
            indicators.append("privileged_account")

        # Check command patterns
        command = execution_event.get("command", "")
        if any(
            pattern in command.lower()
            for pattern in ["powershell", "cmd.exe", "net use", "net user", "whoami", "ipconfig"]
        ):
            indicators.append("suspicious_command")

        confidence = 0.8  # Remote execution has high confidence

        # Determine movement type
        movement_type_map = {
            "wmi": MovementType.WMI,
            "psexec": MovementType.PSEXEC,
            "scheduled_task": MovementType.SCHEDULED_TASK,
        }
        movement_type = movement_type_map.get(execution_method.lower(), MovementType.REMOTE_SERVICE)

        pattern = MovementPattern(
            movement_type=movement_type,
            timestamp=timestamp,
            source_host=source_host,
            destination_host=target_host,
            username=username,
            severity="high",
            confidence=confidence,
            description=f"Remote execution via {execution_method} from {source_host} to {target_host}",
            indicators=indicators,
            recommended_actions=[
                "Investigate the remote execution",
                "Review command history on target host",
                "Check for additional compromised hosts",
                "Verify legitimacy of administrative actions",
            ],
            metadata=execution_event,
        )

        # Track movement chain
        if self.track_chains:
            self._update_movement_chain(username, pattern)

        self.logger.warning(
            f"Remote execution detected: {username} from {source_host} to {target_host} " f"via {execution_method}"
        )

        return pattern

    def get_movement_chains(self, username: str | None = None) -> list[MovementChain]:
        """
        Get tracked movement chains

        Args:
            username: Optional username to filter chains

        Returns:
            List of movement chains
        """
        self._cleanup_old_chains()

        if username:
            chain = self._active_chains.get(username)
            return [chain] if chain else []

        return list(self._active_chains.values())

    def _check_lateral_movement_indicators(self, auth_event: dict[str, Any]) -> list[str]:
        """Check for indicators of lateral movement"""
        indicators = []

        username = auth_event.get("username", "")
        source_host = auth_event.get("source_host", "")
        destination_host = auth_event.get("destination_host", "")

        # Check for rapid authentication from same user
        recent_same_user = [
            e for e in self._recent_authentications if e.get("username") == username and e != auth_event
        ]

        if len(recent_same_user) > 3:
            indicators.append("rapid_authentication_pattern")

        # Check for authentication from multiple sources
        unique_sources = set(e.get("source_host") for e in recent_same_user)
        if len(unique_sources) > 2:
            indicators.append("multiple_source_hosts")

        # Check for privileged account usage
        if any(priv in username.lower() for priv in ["admin", "root", "service", "system"]):
            indicators.append("privileged_account")

        # Check for non-standard authentication hours
        hour = auth_event.get("timestamp", datetime.utcnow()).hour
        if hour < 6 or hour > 22:
            indicators.append("off_hours_authentication")

        # Check for internal-to-internal authentication (lateral movement indicator)
        if self._is_internal_ip(source_host) and self._is_internal_ip(destination_host):
            indicators.append("internal_to_internal")

        # Check for credential reuse patterns
        if self._check_credential_reuse(username, source_host, destination_host):
            indicators.append("credential_reuse_pattern")

        return indicators

    def _determine_movement_type(self, auth_type: str, auth_event: dict[str, Any]) -> MovementType:
        """Determine the type of lateral movement"""
        auth_type_lower = auth_type.lower()

        if "rdp" in auth_type_lower:
            return MovementType.RDP
        elif "ssh" in auth_type_lower:
            return MovementType.SSH
        elif "smb" in auth_type_lower or "cifs" in auth_type_lower:
            return MovementType.SMB
        elif "wmi" in auth_type_lower:
            return MovementType.WMI
        else:
            return MovementType.REMOTE_SERVICE

    def _calculate_confidence(self, indicators: list[str]) -> float:
        """Calculate confidence score based on indicators"""
        if not indicators:
            return 0.0

        # Base confidence
        base_confidence = 0.4

        # Each indicator adds confidence
        indicator_weight = 0.15

        confidence = base_confidence + (len(indicators) * indicator_weight)

        # Cap at 1.0
        return min(1.0, confidence)

    def _calculate_severity(self, confidence: float, indicators: list[str]) -> str:
        """Calculate severity based on confidence and indicators"""
        # Check for high-risk indicators
        high_risk_indicators = ["privileged_account", "credential_reuse_pattern", "multiple_source_hosts"]

        has_high_risk = any(ind in indicators for ind in high_risk_indicators)

        if confidence > 0.85 or has_high_risk:
            return "critical"
        elif confidence > 0.75:
            return "high"
        elif confidence > 0.65:
            return "medium"
        else:
            return "low"

    def _generate_recommended_actions(self, movement_type: MovementType, indicators: list[str]) -> list[str]:
        """Generate recommended actions based on movement type and indicators"""
        actions = [
            "Verify legitimacy of the remote access",
            "Review account activity history",
            "Check for unauthorized privilege escalation",
        ]

        if "privileged_account" in indicators:
            actions.append("Immediately review privileged account usage")
            actions.append("Consider resetting privileged account credentials")

        if "credential_reuse_pattern" in indicators:
            actions.append("Investigate potential credential compromise")
            actions.append("Force password reset for affected accounts")

        if movement_type in [MovementType.WMI, MovementType.PSEXEC]:
            actions.append("Review remote execution policies")
            actions.append("Enable detailed process auditing")

        return actions

    def _update_movement_chain(self, username: str, pattern: MovementPattern) -> None:
        """Update or create movement chain for a user"""
        if username not in self._active_chains:
            # Create new chain
            chain = MovementChain(
                start_time=pattern.timestamp,
                end_time=pattern.timestamp,
                origin_host=pattern.source_host,
                current_host=pattern.destination_host,
                hosts_visited=[pattern.source_host, pattern.destination_host],
                movements=[pattern],
                username=username,
            )
            self._active_chains[username] = chain
        else:
            # Update existing chain
            chain = self._active_chains[username]
            chain.end_time = pattern.timestamp
            chain.current_host = pattern.destination_host

            if pattern.destination_host not in chain.hosts_visited:
                chain.hosts_visited.append(pattern.destination_host)

            chain.movements.append(pattern)

        # Update chain metrics
        chain = self._active_chains[username]
        pattern.path_length = len(chain.hosts_visited)
        pattern.movement_chain = chain.hosts_visited.copy()

        # Calculate risk score for chain
        chain.risk_score = self._calculate_chain_risk_score(chain)

    def _calculate_chain_risk_score(self, chain: MovementChain) -> float:
        """Calculate risk score for a movement chain"""
        # Base score
        score = 0.0

        # Length of chain (more hops = higher risk)
        score += min(40, len(chain.hosts_visited) * 5)

        # Number of movements
        score += min(30, len(chain.movements) * 3)

        # Time duration (longer active chain = higher risk)
        duration_hours = (chain.end_time - chain.start_time).total_seconds() / 3600
        score += min(20, duration_hours * 2)

        # Severity of movements
        high_severity_count = sum(1 for m in chain.movements if m.severity in ["high", "critical"])
        score += min(10, high_severity_count * 5)

        return min(100.0, score)

    def _cleanup_old_authentications(self) -> None:
        """Remove old authentication events outside time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.time_window_minutes)
        self._recent_authentications = [
            e for e in self._recent_authentications if e.get("timestamp", datetime.utcnow()) > cutoff_time
        ]

    def _cleanup_old_chains(self) -> None:
        """Remove old movement chains"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.max_chain_age_hours)

        expired_usernames = [
            username for username, chain in self._active_chains.items() if chain.end_time < cutoff_time
        ]

        for username in expired_usernames:
            del self._active_chains[username]

        if expired_usernames:
            self.logger.debug(f"Cleaned up {len(expired_usernames)} expired movement chains")

    def _is_internal_ip(self, host: str) -> bool:
        """Check if host is an internal IP address"""
        # Simplified check for internal IPs
        internal_prefixes = ["10.", "172.", "192.168.", "localhost", "127."]
        return any(host.startswith(prefix) for prefix in internal_prefixes)

    def _check_credential_reuse(self, username: str, source_host: str, destination_host: str) -> bool:
        """Check for credential reuse patterns"""
        # Check if same username has been used for multiple authentications recently
        recent_same_creds = [
            e
            for e in self._recent_authentications
            if e.get("username") == username
            and e.get("source_host") != source_host
            and e.get("destination_host") != destination_host
        ]

        return len(recent_same_creds) > 2
