"""
Threat Actor Attribution
Identifies and attributes attacks to known threat actor groups
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class ThreatActorType(Enum):
    """Types of threat actors"""

    NATION_STATE = "nation_state"
    CYBERCRIMINAL = "cybercriminal"
    HACKTIVIST = "hacktivist"
    INSIDER = "insider"
    UNKNOWN = "unknown"


@dataclass
class ThreatActorProfile:
    """Profile of a known threat actor"""

    actor_id: str
    name: str
    aliases: list[str]
    actor_type: ThreatActorType
    motivation: str
    sophistication: str  # low, medium, high, expert
    origin_country: str | None
    first_seen: datetime
    last_seen: datetime
    known_ttps: list[str]  # Tactics, Techniques, Procedures
    known_tools: list[str]
    target_sectors: list[str]
    target_regions: list[str]


@dataclass
class Attribution:
    """Attribution result linking findings to threat actor"""

    finding_ids: list[UUID]
    actor: ThreatActorProfile
    confidence: float
    matching_indicators: list[str]
    reasoning: str
    timestamp: datetime


class ThreatActorAttributor:
    """
    Attributes security findings to known threat actors

    Features:
    - TTP-based attribution
    - Tool and infrastructure matching
    - Confidence scoring
    - Multi-finding correlation
    """

    def __init__(self, min_confidence: float = 0.6):
        """
        Initialize threat actor attributor

        Args:
            min_confidence: Minimum confidence threshold for attribution
        """
        self.min_confidence = min_confidence
        self._threat_actors = self._load_threat_actors()

    def _load_threat_actors(self) -> dict[str, ThreatActorProfile]:
        """Load known threat actor profiles"""
        # Sample threat actors (would be loaded from database/API in production)
        actors = {
            "APT28": ThreatActorProfile(
                actor_id="APT28",
                name="APT28",
                aliases=["Fancy Bear", "Sofacy", "Sednit"],
                actor_type=ThreatActorType.NATION_STATE,
                motivation="Espionage, Intelligence Gathering",
                sophistication="expert",
                origin_country="Russia",
                first_seen=datetime(2007, 1, 1),
                last_seen=datetime(2025, 12, 1),
                known_ttps=["spearphishing", "credential harvesting", "lateral movement", "data exfiltration"],
                known_tools=["X-Agent", "Sofacy", "Carberp"],
                target_sectors=["Government", "Military", "Defense", "Media"],
                target_regions=["Europe", "North America", "Middle East"],
            ),
            "APT29": ThreatActorProfile(
                actor_id="APT29",
                name="APT29",
                aliases=["Cozy Bear", "The Dukes"],
                actor_type=ThreatActorType.NATION_STATE,
                motivation="Espionage, Political Intelligence",
                sophistication="expert",
                origin_country="Russia",
                first_seen=datetime(2008, 1, 1),
                last_seen=datetime(2025, 11, 1),
                known_ttps=["spearphishing", "supply chain compromise", "steganography", "encrypted communication"],
                known_tools=["SeaDuke", "HammerDuke", "CloudDuke"],
                target_sectors=["Government", "Think Tanks", "Healthcare"],
                target_regions=["Global"],
            ),
            "Lazarus": ThreatActorProfile(
                actor_id="Lazarus",
                name="Lazarus Group",
                aliases=["Hidden Cobra", "Zinc"],
                actor_type=ThreatActorType.NATION_STATE,
                motivation="Financial Gain, Espionage",
                sophistication="expert",
                origin_country="North Korea",
                first_seen=datetime(2009, 1, 1),
                last_seen=datetime(2025, 12, 1),
                known_ttps=["destructive malware", "cryptocurrency theft", "supply chain attacks", "ransomware"],
                known_tools=["WannaCry", "Sony SPE Malware", "KEYMARBLE"],
                target_sectors=["Financial", "Cryptocurrency", "Media", "Defense"],
                target_regions=["Global"],
            ),
            "FIN7": ThreatActorProfile(
                actor_id="FIN7",
                name="FIN7",
                aliases=["Carbanak Group"],
                actor_type=ThreatActorType.CYBERCRIMINAL,
                motivation="Financial Gain",
                sophistication="high",
                origin_country=None,
                first_seen=datetime(2013, 1, 1),
                last_seen=datetime(2025, 10, 1),
                known_ttps=["phishing", "point of sale malware", "credential theft", "payment card theft"],
                known_tools=["Carbanak", "POWERSOURCE", "PILLOWMINT"],
                target_sectors=["Retail", "Hospitality", "Restaurant", "Financial"],
                target_regions=["North America", "Europe"],
            ),
            "Anonymous": ThreatActorProfile(
                actor_id="Anonymous",
                name="Anonymous",
                aliases=["Anon"],
                actor_type=ThreatActorType.HACKTIVIST,
                motivation="Political Activism, Social Justice",
                sophistication="medium",
                origin_country=None,
                first_seen=datetime(2003, 1, 1),
                last_seen=datetime(2025, 12, 1),
                known_ttps=["ddos attacks", "website defacement", "data leaks", "doxing"],
                known_tools=["LOIC", "HOIC", "SQLmap"],
                target_sectors=["Government", "Corporate", "Religious Organizations"],
                target_regions=["Global"],
            ),
        }
        return actors

    def attribute_findings(self, findings: list[dict[str, Any]]) -> list[Attribution]:
        """
        Attribute findings to threat actors

        Args:
            findings: List of finding dictionaries

        Returns:
            List of attribution results
        """
        attributions: list[Attribution] = []

        for actor in self._threat_actors.values():
            matching_findings: list[UUID] = []
            indicators: list[str] = []
            confidence_scores: list[float] = []

            for finding in findings:
                confidence, matches = self._calculate_actor_match(finding, actor)

                if confidence >= self.min_confidence:
                    matching_findings.append(finding.get("id"))
                    indicators.extend(matches)
                    confidence_scores.append(confidence)

            if matching_findings:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)

                attribution = Attribution(
                    finding_ids=matching_findings,
                    actor=actor,
                    confidence=avg_confidence,
                    matching_indicators=list(set(indicators)),  # Remove duplicates
                    reasoning=self._generate_reasoning(actor, indicators),
                    timestamp=datetime.now(),
                )
                attributions.append(attribution)

        # Sort by confidence
        attributions.sort(key=lambda a: a.confidence, reverse=True)
        return attributions

    def _calculate_actor_match(self, finding: dict[str, Any], actor: ThreatActorProfile) -> tuple[float, list[str]]:
        """Calculate match confidence between finding and actor"""
        confidence = 0.0
        matches: list[str] = []

        finding_type = finding.get("type", "").lower()
        techniques = [t.lower() for t in finding.get("techniques", [])]
        tools = [t.lower() for t in finding.get("tools", [])]
        target_sector = finding.get("target_sector", "").lower()

        # Check TTPs
        for ttp in actor.known_ttps:
            if ttp.lower() in finding_type or any(ttp.lower() in t for t in techniques):
                confidence += 0.3
                matches.append(f"TTP: {ttp}")

        # Check tools
        for tool in actor.known_tools:
            if tool.lower() in finding_type or any(tool.lower() in t for t in tools):
                confidence += 0.4
                matches.append(f"Tool: {tool}")

        # Check target sector
        if target_sector and any(sector.lower() == target_sector for sector in actor.target_sectors):
            confidence += 0.2
            matches.append(f"Target Sector: {target_sector}")

        # Normalize confidence
        confidence = min(confidence, 1.0)

        return confidence, matches

    def _generate_reasoning(self, actor: ThreatActorProfile, indicators: list[str]) -> str:
        """Generate human-readable attribution reasoning"""
        reasoning_parts = [
            f"Attribution to {actor.name} ({', '.join(actor.aliases)}) based on:",
        ]

        # Group indicators by type
        ttps = [i for i in indicators if i.startswith("TTP:")]
        tools = [i for i in indicators if i.startswith("Tool:")]
        targets = [i for i in indicators if i.startswith("Target Sector:")]

        if ttps:
            reasoning_parts.append(f"  - Known TTPs: {', '.join(ttps[:3])}")
        if tools:
            reasoning_parts.append(f"  - Known Tools: {', '.join(tools[:3])}")
        if targets:
            reasoning_parts.append(f"  - Target Profile: {', '.join(targets[:3])}")

        reasoning_parts.append(f"  - Actor Type: {actor.actor_type.value}")
        reasoning_parts.append(f"  - Sophistication: {actor.sophistication}")

        if actor.origin_country:
            reasoning_parts.append(f"  - Origin: {actor.origin_country}")

        return "\n".join(reasoning_parts)

    def generate_report(self, attribution: Attribution) -> str:
        """
        Generate attribution report

        Args:
            attribution: Attribution result

        Returns:
            Formatted report string
        """
        actor = attribution.actor

        lines = [
            "Threat Actor Attribution Report",
            "=" * 50,
            f"Actor: {actor.name}",
            f"Aliases: {', '.join(actor.aliases)}",
            f"Type: {actor.actor_type.value}",
            f"Confidence: {attribution.confidence:.2%}",
            f"Findings Attributed: {len(attribution.finding_ids)}",
            "",
            "Actor Profile:",
            f"  Motivation: {actor.motivation}",
            f"  Sophistication: {actor.sophistication}",
        ]

        if actor.origin_country:
            lines.append(f"  Origin: {actor.origin_country}")

        lines.extend(
            [
                f"  Active Since: {actor.first_seen.year}",
                f"  Last Seen: {actor.last_seen.strftime('%Y-%m')}",
                "",
                "Known TTPs:",
            ]
        )

        for ttp in actor.known_ttps[:5]:
            lines.append(f"  - {ttp}")

        lines.append("")
        lines.append("Known Tools:")
        for tool in actor.known_tools[:5]:
            lines.append(f"  - {tool}")

        lines.append("")
        lines.append("Target Sectors:")
        for sector in actor.target_sectors:
            lines.append(f"  - {sector}")

        lines.append("")
        lines.append("Attribution Reasoning:")
        lines.append(attribution.reasoning)

        lines.append("")
        lines.append("Matching Indicators:")
        for indicator in attribution.matching_indicators[:10]:
            lines.append(f"  - {indicator}")

        return "\n".join(lines)

    def export_to_stix(self, attribution: Attribution) -> dict[str, Any]:
        """
        Export attribution to STIX 2.1 format

        Args:
            attribution: Attribution to export

        Returns:
            STIX 2.1 threat actor object
        """
        actor = attribution.actor

        return {
            "type": "threat-actor",
            "id": f"threat-actor--{actor.actor_id}",
            "created": actor.first_seen.isoformat(),
            "modified": actor.last_seen.isoformat(),
            "name": actor.name,
            "aliases": actor.aliases,
            "threat_actor_types": [actor.actor_type.value],
            "sophistication": actor.sophistication,
            "resource_level": actor.sophistication,
            "primary_motivation": actor.motivation.split(",")[0].strip().lower().replace(" ", "-"),
            "goals": [actor.motivation],
            "description": self.generate_report(attribution),
        }
