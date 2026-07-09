"""
Kill Chain Analysis and Detection

Analyzes attack patterns and maps them to the cyber kill chain framework
to detect and track multi-stage attacks across the infrastructure.

Part of ROADMAP 5.0 Section V.14: Advanced Security Features
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class KillChainPhase(Enum):
    """Phases of the cyber kill chain (Lockheed Martin model)"""

    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_AND_CONTROL = "command_and_control"
    ACTIONS_ON_OBJECTIVES = "actions_on_objectives"


@dataclass
class KillChainEvent:
    """Represents an event in the kill chain"""

    event_id: UUID = field(default_factory=uuid4)
    phase: KillChainPhase = KillChainPhase.RECONNAISSANCE
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_asset: str = ""
    target_asset: str = ""
    description: str = ""
    indicators: list[str] = field(default_factory=list)
    severity: str = "medium"
    confidence: float = 0.7
    mitre_techniques: list[str] = field(default_factory=list)  # MITRE ATT&CK technique IDs
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackChain:
    """Represents a complete or partial attack chain"""

    chain_id: UUID = field(default_factory=uuid4)
    start_time: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    attacker_id: str = ""  # IP, user, or identifier
    target_assets: list[str] = field(default_factory=list)
    events: list[KillChainEvent] = field(default_factory=list)
    phases_detected: set[KillChainPhase] = field(default_factory=set)
    completeness: float = 0.0  # 0.0 to 1.0, how much of the chain is visible
    risk_score: float = 0.0  # 0-100
    status: str = "active"  # active, contained, completed
    recommended_actions: list[str] = field(default_factory=list)


class KillChainAnalyzer:
    """
    Kill Chain Analyzer

    Detects and tracks multi-stage attacks by analyzing security events
    and mapping them to the cyber kill chain framework.

    Features:
    - Event classification by kill chain phase
    - Attack chain correlation and tracking
    - Completeness assessment
    - Risk scoring based on chain progression
    - Integration with MITRE ATT&CK framework
    - Early warning for advanced persistent threats (APTs)

    Detection Capabilities:
    - Reconnaissance: Scanning, enumeration, information gathering
    - Weaponization: Malware creation, exploit preparation
    - Delivery: Phishing, exploit kits, watering holes
    - Exploitation: Vulnerability exploitation, code execution
    - Installation: Backdoor installation, persistence mechanisms
    - C2: Command and control communications
    - Actions: Data exfiltration, lateral movement, objective achievement
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize kill chain analyzer

        Args:
            config: Configuration options
                - chain_timeout_hours: Hours before chain is considered inactive (default: 48)
                - min_confidence_threshold: Minimum confidence to include event (default: 0.5)
                - correlation_time_window_hours: Time window for correlating events (default: 72)
                - early_warning_phases: Phases that trigger early warnings (default: 3)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.chain_timeout_hours = self.config.get("chain_timeout_hours", 48)
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.5)
        self.correlation_time_window_hours = self.config.get("correlation_time_window_hours", 72)
        self.early_warning_phases = self.config.get("early_warning_phases", 3)

        # Track active attack chains
        self._active_chains: dict[str, AttackChain] = {}  # Key: attacker_id
        self._recent_events: list[KillChainEvent] = []

        self.logger.info("Kill Chain Analyzer initialized")

    def analyze_event(self, event: dict[str, Any]) -> KillChainEvent | None:
        """
        Analyze a security event and classify it in the kill chain

        Args:
            event: Security event data
                - timestamp: When the event occurred
                - event_type: Type of event (scan, exploit, connection, etc.)
                - source: Source IP/host
                - target: Target IP/host
                - indicators: List of indicators (optional)
                - details: Additional event details

        Returns:
            Classified kill chain event or None if not relevant
        """
        timestamp = event.get("timestamp", datetime.utcnow())
        event_type = event.get("event_type", "")
        source = event.get("source", "")
        target = event.get("target", "")

        # Classify event to kill chain phase
        phase = self._classify_event_phase(event)

        if phase is None:
            return None

        # Extract indicators
        indicators = event.get("indicators", [])
        if not indicators:
            indicators = self._extract_indicators(event)

        # Calculate confidence
        confidence = self._calculate_event_confidence(event, phase)

        if confidence < self.min_confidence_threshold:
            return None

        # Map to MITRE ATT&CK techniques
        mitre_techniques = self._map_to_mitre(event, phase)

        kill_chain_event = KillChainEvent(
            phase=phase,
            timestamp=timestamp,
            source_asset=source,
            target_asset=target,
            description=self._generate_event_description(event, phase),
            indicators=indicators,
            severity=self._calculate_event_severity(phase, confidence),
            confidence=confidence,
            mitre_techniques=mitre_techniques,
            metadata=event,
        )

        # Track event
        self._recent_events.append(kill_chain_event)
        self._cleanup_old_events()

        # Update or create attack chain
        self._update_attack_chain(source, kill_chain_event)

        self.logger.info(f"Kill chain event detected: {phase.value} from {source} (confidence: {confidence:.2f})")

        return kill_chain_event

    def get_attack_chains(self, attacker_id: str | None = None, active_only: bool = True) -> list[AttackChain]:
        """
        Get tracked attack chains

        Args:
            attacker_id: Optional attacker ID to filter
            active_only: Only return active chains

        Returns:
            List of attack chains
        """
        self._cleanup_inactive_chains()

        if attacker_id:
            chain = self._active_chains.get(attacker_id)
            if chain and (not active_only or chain.status == "active"):
                return [chain]
            return []

        chains = list(self._active_chains.values())

        if active_only:
            chains = [c for c in chains if c.status == "active"]

        return chains

    def get_chain_by_target(self, target_asset: str) -> list[AttackChain]:
        """Get attack chains targeting a specific asset"""
        return [chain for chain in self._active_chains.values() if target_asset in chain.target_assets]

    def _classify_event_phase(self, event: dict[str, Any]) -> KillChainPhase | None:
        """Classify an event to a kill chain phase"""
        event_type = event.get("event_type", "").lower()
        details = event.get("details", {})

        # Reconnaissance indicators
        if any(
            keyword in event_type for keyword in ["scan", "probe", "enumeration", "whois", "dns_query", "discovery"]
        ):
            return KillChainPhase.RECONNAISSANCE

        # Delivery indicators
        if any(keyword in event_type for keyword in ["phish", "email", "download", "upload", "file_transfer"]):
            return KillChainPhase.DELIVERY

        # Exploitation indicators
        if any(keyword in event_type for keyword in ["exploit", "vulnerability", "overflow", "injection", "rce"]):
            return KillChainPhase.EXPLOITATION

        # Installation indicators
        if any(
            keyword in event_type
            for keyword in ["install", "persistence", "backdoor", "registry", "scheduled_task", "service_create"]
        ):
            return KillChainPhase.INSTALLATION

        # Command and Control indicators
        if any(
            keyword in event_type
            for keyword in [
                "c2",
                "c&c",
                "beacon",
                "callback",
                "reverse_shell",
                "tunnel",
                "proxy",
            ]
        ):
            return KillChainPhase.COMMAND_AND_CONTROL

        # Actions on Objectives indicators
        if any(
            keyword in event_type
            for keyword in [
                "exfiltration",
                "data_theft",
                "lateral",
                "privilege_escalation",
                "credential_dump",
                "ransom",
            ]
        ):
            return KillChainPhase.ACTIONS_ON_OBJECTIVES

        return None

    def _extract_indicators(self, event: dict[str, Any]) -> list[str]:
        """Extract indicators from an event"""
        indicators = []
        event_type = event.get("event_type", "")

        # Add event type as indicator
        indicators.append(f"event_type:{event_type}")

        # Check for suspicious patterns
        details = event.get("details", {})

        if "port" in details:
            indicators.append(f"port:{details['port']}")

        if "protocol" in details:
            indicators.append(f"protocol:{details['protocol']}")

        if "command" in details:
            indicators.append("command_execution")

        if "file" in details or "filename" in details:
            indicators.append("file_activity")

        return indicators

    def _calculate_event_confidence(self, event: dict[str, Any], phase: KillChainPhase) -> float:
        """Calculate confidence for event classification"""
        base_confidence = 0.6

        # Increase confidence based on indicators
        indicators = event.get("indicators", [])
        indicator_count = len(indicators)

        confidence = base_confidence + (indicator_count * 0.05)

        # Certain phases are easier to detect with high confidence
        high_confidence_phases = [KillChainPhase.RECONNAISSANCE, KillChainPhase.EXPLOITATION]

        if phase in high_confidence_phases:
            confidence += 0.1

        return min(1.0, confidence)

    def _calculate_event_severity(self, phase: KillChainPhase, confidence: float) -> str:
        """Calculate event severity based on phase and confidence"""
        # Later phases in the kill chain are more severe
        phase_severity = {
            KillChainPhase.RECONNAISSANCE: "low",
            KillChainPhase.WEAPONIZATION: "medium",
            KillChainPhase.DELIVERY: "medium",
            KillChainPhase.EXPLOITATION: "high",
            KillChainPhase.INSTALLATION: "high",
            KillChainPhase.COMMAND_AND_CONTROL: "critical",
            KillChainPhase.ACTIONS_ON_OBJECTIVES: "critical",
        }

        base_severity = phase_severity.get(phase, "medium")

        # Adjust based on confidence
        if confidence > 0.9:
            # High confidence can elevate severity
            if base_severity == "medium":
                return "high"
            elif base_severity == "low":
                return "medium"

        return base_severity

    def _map_to_mitre(self, event: dict[str, Any], phase: KillChainPhase) -> list[str]:
        """Map event and phase to MITRE ATT&CK techniques"""
        techniques = []

        # Map kill chain phases to common MITRE techniques
        phase_technique_map = {
            KillChainPhase.RECONNAISSANCE: ["T1595", "T1590", "T1592", "T1589"],
            KillChainPhase.DELIVERY: ["T1566", "T1189", "T1091"],
            KillChainPhase.EXPLOITATION: ["T1190", "T1203", "T1212"],
            KillChainPhase.INSTALLATION: ["T1547", "T1543", "T1574"],
            KillChainPhase.COMMAND_AND_CONTROL: ["T1071", "T1573", "T1090"],
            KillChainPhase.ACTIONS_ON_OBJECTIVES: ["T1048", "T1020", "T1041", "T1486"],
        }

        techniques = phase_technique_map.get(phase, [])

        return techniques

    def _generate_event_description(self, event: dict[str, Any], phase: KillChainPhase) -> str:
        """Generate human-readable description of the event"""
        event_type = event.get("event_type", "unknown")
        source = event.get("source", "unknown")
        target = event.get("target", "unknown")

        return f"{phase.value.replace('_', ' ').title()}: {event_type} from {source} to {target}"

    def _update_attack_chain(self, attacker_id: str, event: KillChainEvent) -> None:
        """Update or create attack chain for an attacker"""
        if attacker_id not in self._active_chains:
            # Create new attack chain
            chain = AttackChain(
                start_time=event.timestamp,
                last_activity=event.timestamp,
                attacker_id=attacker_id,
                target_assets=[event.target_asset] if event.target_asset else [],
                events=[event],
                phases_detected={event.phase},
            )
            self._active_chains[attacker_id] = chain

            self.logger.info(f"New attack chain created for attacker {attacker_id}")
        else:
            # Update existing chain
            chain = self._active_chains[attacker_id]
            chain.last_activity = event.timestamp
            chain.events.append(event)
            chain.phases_detected.add(event.phase)

            if event.target_asset and event.target_asset not in chain.target_assets:
                chain.target_assets.append(event.target_asset)

        # Update chain metrics
        chain = self._active_chains[attacker_id]
        self._update_chain_metrics(chain)

        # Check for early warnings
        if len(chain.phases_detected) >= self.early_warning_phases:
            self.logger.warning(
                f"EARLY WARNING: Attack chain for {attacker_id} has reached {len(chain.phases_detected)} "
                f"phases. Potential APT activity detected!"
            )

    def _update_chain_metrics(self, chain: AttackChain) -> None:
        """Update attack chain metrics"""
        # Calculate completeness (how much of kill chain is visible)
        total_phases = len(KillChainPhase)
        detected_phases = len(chain.phases_detected)
        chain.completeness = detected_phases / total_phases

        # Calculate risk score
        risk_score = 0.0

        # Base score from number of phases
        risk_score += detected_phases * 10

        # Bonus for later-stage phases
        critical_phases = {
            KillChainPhase.INSTALLATION,
            KillChainPhase.COMMAND_AND_CONTROL,
            KillChainPhase.ACTIONS_ON_OBJECTIVES,
        }

        critical_phases_detected = len(chain.phases_detected & critical_phases)
        risk_score += critical_phases_detected * 15

        # Number of targets
        risk_score += min(20, len(chain.target_assets) * 5)

        # Duration of attack
        duration_hours = (chain.last_activity - chain.start_time).total_seconds() / 3600
        risk_score += min(15, duration_hours * 0.5)

        chain.risk_score = min(100.0, risk_score)

        # Generate recommended actions
        chain.recommended_actions = self._generate_chain_recommendations(chain)

    def _generate_chain_recommendations(self, chain: AttackChain) -> list[str]:
        """Generate recommended actions for an attack chain"""
        recommendations = [
            "Immediately investigate all affected assets",
            "Review security logs for additional indicators",
            "Assess the scope of the attack",
        ]

        # Phase-specific recommendations
        if KillChainPhase.RECONNAISSANCE in chain.phases_detected:
            recommendations.append("Monitor for follow-up attacks after reconnaissance")

        if KillChainPhase.EXPLOITATION in chain.phases_detected:
            recommendations.append("Patch exploited vulnerabilities immediately")
            recommendations.append("Isolate compromised systems")

        if KillChainPhase.INSTALLATION in chain.phases_detected:
            recommendations.append("Search for and remove persistence mechanisms")
            recommendations.append("Conduct full system forensics")

        if KillChainPhase.COMMAND_AND_CONTROL in chain.phases_detected:
            recommendations.append("Block C2 communications at network perimeter")
            recommendations.append("Identify and contain all compromised hosts")

        if KillChainPhase.ACTIONS_ON_OBJECTIVES in chain.phases_detected:
            recommendations.append("CRITICAL: Activate incident response procedures")
            recommendations.append("Assess data exfiltration and damage")
            recommendations.append("Consider engaging forensics experts")

        # Risk-based recommendations
        if chain.risk_score > 80:
            recommendations.append("Escalate to senior security team immediately")
            recommendations.append("Consider bringing in external incident response team")

        if len(chain.target_assets) > 5:
            recommendations.append("Check for additional compromised systems")
            recommendations.append("Implement network segmentation")

        return recommendations

    def _cleanup_old_events(self) -> None:
        """Remove old events outside correlation window"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.correlation_time_window_hours)
        self._recent_events = [e for e in self._recent_events if e.timestamp > cutoff_time]

    def _cleanup_inactive_chains(self) -> None:
        """Mark inactive attack chains"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.chain_timeout_hours)

        for attacker_id, chain in self._active_chains.items():
            if chain.last_activity < cutoff_time and chain.status == "active":
                chain.status = "inactive"
                self.logger.info(f"Attack chain for {attacker_id} marked as inactive")
