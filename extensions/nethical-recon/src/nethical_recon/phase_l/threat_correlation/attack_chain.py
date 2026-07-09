"""
Attack Chain Detection - Cyber Kill Chain Analysis
Detects multi-stage attack patterns following the Cyber Kill Chain model
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class KillChainStage(Enum):
    """Cyber Kill Chain stages"""

    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_CONTROL = "command_and_control"
    ACTIONS_ON_OBJECTIVES = "actions_on_objectives"


@dataclass
class AttackChainNode:
    """Represents a single node in an attack chain"""

    finding_id: UUID
    stage: KillChainStage
    timestamp: datetime
    confidence: float
    techniques: list[str]
    indicators: dict[str, Any]


@dataclass
class AttackChain:
    """Represents a complete or partial attack chain"""

    chain_id: UUID
    stages: list[AttackChainNode]
    start_time: datetime
    end_time: datetime
    target_asset: str
    severity: str
    confidence: float
    description: str


class AttackChainDetector:
    """
    Detects multi-stage attack patterns using Cyber Kill Chain methodology

    Features:
    - Temporal correlation of findings
    - Pattern recognition across attack stages
    - Confidence scoring based on evidence
    - Attack chain visualization
    """

    def __init__(self, time_window_hours: int = 24, min_confidence: float = 0.7):
        """
        Initialize the attack chain detector

        Args:
            time_window_hours: Maximum time window for chain correlation
            min_confidence: Minimum confidence threshold for chain detection
        """
        self.time_window_hours = time_window_hours
        self.min_confidence = min_confidence
        self._stage_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> dict[KillChainStage, list[str]]:
        """Initialize detection patterns for each kill chain stage"""
        return {
            KillChainStage.RECONNAISSANCE: [
                "port_scan",
                "network_scan",
                "dns_enum",
                "subdomain_enum",
                "shodan_query",
                "censys_query",
                "whois_lookup",
            ],
            KillChainStage.WEAPONIZATION: ["exploit_code", "malware_compilation", "payload_creation"],
            KillChainStage.DELIVERY: ["phishing", "web_exploit", "malicious_attachment", "watering_hole"],
            KillChainStage.EXPLOITATION: [
                "vulnerability_exploit",
                "code_execution",
                "privilege_escalation",
                "buffer_overflow",
                "sql_injection",
                "rce",
            ],
            KillChainStage.INSTALLATION: ["backdoor", "trojan", "rootkit", "persistence_mechanism"],
            KillChainStage.COMMAND_CONTROL: ["c2_communication", "beacon", "callback", "reverse_shell"],
            KillChainStage.ACTIONS_ON_OBJECTIVES: [
                "data_exfiltration",
                "lateral_movement",
                "credential_theft",
                "ransomware",
                "data_destruction",
            ],
        }

    def detect_chains(self, findings: list[dict[str, Any]]) -> list[AttackChain]:
        """
        Detect attack chains from a list of findings

        Args:
            findings: List of finding dictionaries

        Returns:
            List of detected attack chains
        """
        # Classify findings by kill chain stage
        classified_findings = self._classify_findings(findings)

        # Build temporal graph of related findings
        chains = self._build_chains(classified_findings)

        # Filter by confidence threshold
        return [chain for chain in chains if chain.confidence >= self.min_confidence]

    def _classify_findings(self, findings: list[dict[str, Any]]) -> dict[KillChainStage, list[AttackChainNode]]:
        """Classify findings into kill chain stages"""
        classified: dict[KillChainStage, list[AttackChainNode]] = {stage: [] for stage in KillChainStage}

        for finding in findings:
            stage, confidence = self._determine_stage(finding)
            if stage and confidence >= self.min_confidence:
                node = AttackChainNode(
                    finding_id=finding.get("id"),
                    stage=stage,
                    timestamp=finding.get("timestamp", datetime.now()),
                    confidence=confidence,
                    techniques=finding.get("techniques", []),
                    indicators=finding.get("indicators", {}),
                )
                classified[stage].append(node)

        return classified

    def _determine_stage(self, finding: dict[str, Any]) -> tuple[KillChainStage | None, float]:
        """Determine the kill chain stage for a finding"""
        finding_type = finding.get("type", "").lower()
        techniques = [t.lower() for t in finding.get("techniques", [])]

        best_match = None
        best_confidence = 0.0

        for stage, patterns in self._stage_patterns.items():
            confidence = 0.0
            matches = 0

            # Check finding type
            if any(pattern in finding_type for pattern in patterns):
                confidence += 0.5
                matches += 1

            # Check techniques
            for technique in techniques:
                if any(pattern in technique for pattern in patterns):
                    confidence += 0.3
                    matches += 1

            # Normalize confidence
            if matches > 0:
                confidence = min(confidence / matches, 1.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = stage

        return best_match, best_confidence

    def _build_chains(self, classified: dict[KillChainStage, list[AttackChainNode]]) -> list[AttackChain]:
        """Build attack chains from classified findings"""
        from datetime import timedelta
        from uuid import uuid4

        chains: list[AttackChain] = []

        # Group findings by target asset
        by_asset: dict[str, list[AttackChainNode]] = {}
        for nodes in classified.values():
            for node in nodes:
                asset = node.indicators.get("target_asset", "unknown")
                if asset not in by_asset:
                    by_asset[asset] = []
                by_asset[asset].append(node)

        # Build chains for each asset
        for asset, nodes in by_asset.items():
            # Sort by timestamp
            nodes.sort(key=lambda n: n.timestamp)

            # Create chain if we have sequential stages
            if len(nodes) >= 2:
                chain = AttackChain(
                    chain_id=uuid4(),
                    stages=nodes,
                    start_time=nodes[0].timestamp,
                    end_time=nodes[-1].timestamp,
                    target_asset=asset,
                    severity=self._calculate_severity(nodes),
                    confidence=sum(n.confidence for n in nodes) / len(nodes),
                    description=self._generate_description(nodes),
                )

                # Check time window
                time_diff = (chain.end_time - chain.start_time).total_seconds() / 3600
                if time_diff <= self.time_window_hours:
                    chains.append(chain)

        return chains

    def _calculate_severity(self, nodes: list[AttackChainNode]) -> str:
        """Calculate overall severity based on stages present"""
        stages = {node.stage for node in nodes}

        # Critical if later stages are present
        if KillChainStage.ACTIONS_ON_OBJECTIVES in stages:
            return "CRITICAL"
        elif KillChainStage.COMMAND_CONTROL in stages:
            return "HIGH"
        elif KillChainStage.EXPLOITATION in stages:
            return "HIGH"
        elif len(stages) >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_description(self, nodes: list[AttackChainNode]) -> str:
        """Generate human-readable description of the attack chain"""
        stages = [node.stage.value for node in nodes]
        return f"Attack chain detected with {len(nodes)} stages: {' → '.join(stages)}"

    def visualize_chain(self, chain: AttackChain) -> str:
        """
        Generate a text-based visualization of an attack chain

        Args:
            chain: The attack chain to visualize

        Returns:
            String representation of the chain
        """
        lines = [
            f"Attack Chain: {chain.chain_id}",
            f"Target: {chain.target_asset}",
            f"Severity: {chain.severity}",
            f"Confidence: {chain.confidence:.2%}",
            f"Duration: {chain.start_time} → {chain.end_time}",
            "",
            "Chain Stages:",
        ]

        for i, node in enumerate(chain.stages, 1):
            lines.append(f"  {i}. {node.stage.value.upper()}")
            lines.append(f"     Time: {node.timestamp}")
            lines.append(f"     Confidence: {node.confidence:.2%}")
            if node.techniques:
                lines.append(f"     Techniques: {', '.join(node.techniques)}")
            lines.append("")

        return "\n".join(lines)
