"""
MITRE ATT&CK Mapping
Maps findings and attack patterns to MITRE ATT&CK framework
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import UUID


class MitreTactic(Enum):
    """MITRE ATT&CK Tactics"""

    RECONNAISSANCE = "TA0043"
    RESOURCE_DEVELOPMENT = "TA0042"
    INITIAL_ACCESS = "TA0001"
    EXECUTION = "TA0002"
    PERSISTENCE = "TA0003"
    PRIVILEGE_ESCALATION = "TA0004"
    DEFENSE_EVASION = "TA0005"
    CREDENTIAL_ACCESS = "TA0006"
    DISCOVERY = "TA0007"
    LATERAL_MOVEMENT = "TA0008"
    COLLECTION = "TA0009"
    COMMAND_AND_CONTROL = "TA0011"
    EXFILTRATION = "TA0010"
    IMPACT = "TA0040"


@dataclass
class MitreTechnique:
    """MITRE ATT&CK Technique"""

    technique_id: str
    name: str
    tactic: MitreTactic
    description: str
    detection: str
    mitigation: str


@dataclass
class MitreMapping:
    """Mapping between finding and MITRE ATT&CK"""

    finding_id: UUID
    techniques: list[MitreTechnique]
    tactics: list[MitreTactic]
    confidence: float
    evidence: list[str]


class MitreAttackMapper:
    """
    Maps security findings to MITRE ATT&CK framework

    Features:
    - Automatic technique identification
    - Tactic-level categorization
    - Confidence scoring
    - Detection and mitigation recommendations
    """

    def __init__(self):
        """Initialize MITRE ATT&CK mapper with technique database"""
        self._techniques = self._load_techniques()
        self._technique_patterns = self._initialize_patterns()

    def _load_techniques(self) -> dict[str, MitreTechnique]:
        """Load MITRE ATT&CK techniques database"""
        # Subset of common techniques (would be loaded from file/API in production)
        techniques = {
            "T1595": MitreTechnique(
                technique_id="T1595",
                name="Active Scanning",
                tactic=MitreTactic.RECONNAISSANCE,
                description="Adversaries may execute active reconnaissance scans to gather information",
                detection="Monitor network traffic for scanning patterns",
                mitigation="Use network segmentation and firewall rules",
            ),
            "T1590": MitreTechnique(
                technique_id="T1590",
                name="Gather Victim Network Information",
                tactic=MitreTactic.RECONNAISSANCE,
                description="Information about victim's network infrastructure",
                detection="Monitor for DNS queries and WHOIS lookups",
                mitigation="Limit publicly available infrastructure information",
            ),
            "T1190": MitreTechnique(
                technique_id="T1190",
                name="Exploit Public-Facing Application",
                tactic=MitreTactic.INITIAL_ACCESS,
                description="Exploit vulnerabilities in Internet-facing applications",
                detection="Monitor for exploitation attempts",
                mitigation="Keep software updated, use WAF",
            ),
            "T1059": MitreTechnique(
                technique_id="T1059",
                name="Command and Scripting Interpreter",
                tactic=MitreTactic.EXECUTION,
                description="Abuse command interpreters to execute commands",
                detection="Monitor process execution and command line arguments",
                mitigation="Restrict script execution policies",
            ),
            "T1071": MitreTechnique(
                technique_id="T1071",
                name="Application Layer Protocol",
                tactic=MitreTactic.COMMAND_AND_CONTROL,
                description="Use application layer protocols for C2 communication",
                detection="Monitor network traffic for anomalous patterns",
                mitigation="Use network intrusion detection systems",
            ),
            "T1055": MitreTechnique(
                technique_id="T1055",
                name="Process Injection",
                tactic=MitreTactic.DEFENSE_EVASION,
                description="Inject code into processes to evade detection",
                detection="Monitor for suspicious process behavior",
                mitigation="Use application whitelisting",
            ),
            "T1110": MitreTechnique(
                technique_id="T1110",
                name="Brute Force",
                tactic=MitreTactic.CREDENTIAL_ACCESS,
                description="Use brute force to obtain credentials",
                detection="Monitor for multiple failed login attempts",
                mitigation="Implement account lockout policies",
            ),
            "T1083": MitreTechnique(
                technique_id="T1083",
                name="File and Directory Discovery",
                tactic=MitreTactic.DISCOVERY,
                description="Enumerate files and directories",
                detection="Monitor file system access patterns",
                mitigation="Implement least privilege access",
            ),
            "T1021": MitreTechnique(
                technique_id="T1021",
                name="Remote Services",
                tactic=MitreTactic.LATERAL_MOVEMENT,
                description="Use remote services to move laterally",
                detection="Monitor remote service authentication",
                mitigation="Use multi-factor authentication",
            ),
            "T1567": MitreTechnique(
                technique_id="T1567",
                name="Exfiltration Over Web Service",
                tactic=MitreTactic.EXFILTRATION,
                description="Exfiltrate data via web services",
                detection="Monitor outbound web traffic",
                mitigation="Implement data loss prevention",
            ),
            "T1486": MitreTechnique(
                technique_id="T1486",
                name="Data Encrypted for Impact",
                tactic=MitreTactic.IMPACT,
                description="Encrypt data to impact availability",
                detection="Monitor for mass file encryption",
                mitigation="Maintain offline backups",
            ),
        }
        return techniques

    def _initialize_patterns(self) -> dict[str, list[str]]:
        """Initialize keyword patterns for technique matching"""
        return {
            "T1595": ["port scan", "network scan", "ping sweep", "active scan"],
            "T1590": ["dns enum", "subdomain", "whois", "network info"],
            "T1190": ["exploit", "vulnerability", "rce", "sql injection", "xss"],
            "T1059": ["command execution", "script", "powershell", "bash"],
            "T1071": ["c2", "command and control", "beacon", "callback"],
            "T1055": ["process injection", "dll injection", "code injection"],
            "T1110": ["brute force", "password spray", "credential stuffing"],
            "T1083": ["file discovery", "directory listing", "enumerate files"],
            "T1021": ["lateral movement", "remote desktop", "ssh", "psexec"],
            "T1567": ["data exfiltration", "data upload", "file transfer"],
            "T1486": ["ransomware", "encryption", "crypto"],
        }

    def map_finding(self, finding: dict[str, Any]) -> MitreMapping:
        """
        Map a finding to MITRE ATT&CK techniques

        Args:
            finding: Finding dictionary with type, description, techniques

        Returns:
            MITRE mapping with identified techniques and tactics
        """
        finding_id = finding.get("id")
        finding_type = finding.get("type", "").lower()
        description = finding.get("description", "").lower()
        techniques_list = [t.lower() for t in finding.get("techniques", [])]

        # Identify matching techniques
        matched_techniques: list[MitreTechnique] = []
        evidence: list[str] = []

        for tech_id, patterns in self._technique_patterns.items():
            confidence = 0.0
            matches: list[str] = []

            # Check patterns against finding data
            for pattern in patterns:
                if pattern in finding_type:
                    confidence += 0.4
                    matches.append(f"type: {pattern}")
                if pattern in description:
                    confidence += 0.3
                    matches.append(f"description: {pattern}")
                for technique in techniques_list:
                    if pattern in technique:
                        confidence += 0.3
                        matches.append(f"technique: {pattern}")

            if confidence > 0:
                technique = self._techniques[tech_id]
                matched_techniques.append(technique)
                evidence.extend(matches)

        # Extract unique tactics
        tactics = list(set(t.tactic for t in matched_techniques))

        # Calculate overall confidence
        overall_confidence = min(len(matched_techniques) * 0.25, 1.0) if matched_techniques else 0.0

        return MitreMapping(
            finding_id=finding_id,
            techniques=matched_techniques,
            tactics=tactics,
            confidence=overall_confidence,
            evidence=evidence,
        )

    def map_attack_chain(self, chain: Any) -> dict[MitreTactic, list[MitreTechnique]]:
        """
        Map an entire attack chain to MITRE ATT&CK

        Args:
            chain: AttackChain object

        Returns:
            Dictionary mapping tactics to techniques
        """
        tactic_map: dict[MitreTactic, list[MitreTechnique]] = {}

        for node in chain.stages:
            for technique_name in node.techniques:
                # Find matching technique
                for tech in self._techniques.values():
                    if technique_name.lower() in tech.name.lower():
                        if tech.tactic not in tactic_map:
                            tactic_map[tech.tactic] = []
                        if tech not in tactic_map[tech.tactic]:
                            tactic_map[tech.tactic].append(tech)

        return tactic_map

    def generate_report(self, mapping: MitreMapping) -> str:
        """
        Generate MITRE ATT&CK mapping report

        Args:
            mapping: MITRE mapping to report on

        Returns:
            Formatted report string
        """
        lines = [
            "MITRE ATT&CK Mapping Report",
            "=" * 50,
            f"Finding ID: {mapping.finding_id}",
            f"Confidence: {mapping.confidence:.2%}",
            "",
            "Tactics:",
        ]

        for tactic in mapping.tactics:
            lines.append(f"  - {tactic.value}: {tactic.name}")

        lines.append("")
        lines.append("Techniques:")

        for technique in mapping.techniques:
            lines.append(f"  {technique.technique_id} - {technique.name}")
            lines.append(f"    Tactic: {technique.tactic.name}")
            lines.append(f"    Description: {technique.description}")
            lines.append(f"    Detection: {technique.detection}")
            lines.append(f"    Mitigation: {technique.mitigation}")
            lines.append("")

        if mapping.evidence:
            lines.append("Evidence:")
            for ev in mapping.evidence[:5]:  # Limit to 5 pieces of evidence
                lines.append(f"  - {ev}")

        return "\n".join(lines)

    def export_to_stix(self, mapping: MitreMapping) -> dict[str, Any]:
        """
        Export mapping to STIX 2.1 format

        Args:
            mapping: MITRE mapping to export

        Returns:
            STIX 2.1 bundle dictionary
        """
        from datetime import datetime

        stix_objects = []

        # Create attack pattern objects for each technique
        for technique in mapping.techniques:
            stix_objects.append(
                {
                    "type": "attack-pattern",
                    "id": f"attack-pattern--{technique.technique_id}",
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "name": technique.name,
                    "description": technique.description,
                    "external_references": [
                        {
                            "source_name": "mitre-attack",
                            "external_id": technique.technique_id,
                            "url": f"https://attack.mitre.org/techniques/{technique.technique_id}/",
                        }
                    ],
                    "kill_chain_phases": [
                        {"kill_chain_name": "mitre-attack", "phase_name": technique.tactic.name.lower()}
                    ],
                }
            )

        return {"type": "bundle", "id": f"bundle--{mapping.finding_id}", "objects": stix_objects}
