"""
Threat Enricher

Core enrichment engine that coordinates multiple threat intelligence providers.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from .providers import ThreatProvider, ThreatData


@dataclass
class EnrichmentResult:
    """Result of threat intelligence enrichment."""

    indicator: str
    indicator_type: str
    enriched: bool
    sources: list[str] = field(default_factory=list)
    threat_data: list[ThreatData] = field(default_factory=list)
    aggregated_threat_level: str = "unknown"
    aggregated_confidence: float = 0.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ThreatEnricher:
    """
    Threat Enricher

    Coordinates multiple threat intelligence providers to enrich
    indicators with threat intelligence data.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers: list[ThreatProvider] = []

    def add_provider(self, provider: ThreatProvider) -> None:
        """
        Add a threat intelligence provider.

        Args:
            provider: Threat provider instance
        """
        self.providers.append(provider)
        self.logger.info(f"Added provider: {provider.get_name()}")

    def enrich(self, indicator: str, indicator_type: str) -> EnrichmentResult:
        """
        Enrich an indicator with threat intelligence.

        Args:
            indicator: Indicator to enrich (IP, domain, etc.)
            indicator_type: Type of indicator

        Returns:
            Enrichment result
        """
        self.logger.info(f"Enriching {indicator_type}: {indicator}")

        result = EnrichmentResult(
            indicator=indicator,
            indicator_type=indicator_type,
            enriched=False,
        )

        # Query all providers
        for provider in self.providers:
            try:
                threat_data = provider.query(indicator, indicator_type)
                if threat_data:
                    result.threat_data.append(threat_data)
                    result.sources.append(provider.get_name())
                    result.enriched = True
            except Exception as e:
                self.logger.error(f"Error querying {provider.get_name()}: {e}")

        # Aggregate results
        if result.enriched:
            result.aggregated_threat_level = self._aggregate_threat_level(result.threat_data)
            result.aggregated_confidence = self._aggregate_confidence(result.threat_data)
            result.tags = self._aggregate_tags(result.threat_data)
            result.metadata = self._aggregate_metadata(result.threat_data)

        self.logger.info(f"Enrichment complete: {len(result.sources)} sources")
        return result

    def enrich_batch(self, indicators: list[tuple[str, str]]) -> list[EnrichmentResult]:
        """
        Enrich multiple indicators in batch.

        Args:
            indicators: List of (indicator, indicator_type) tuples

        Returns:
            List of enrichment results
        """
        self.logger.info(f"Batch enrichment: {len(indicators)} indicators")
        results = []

        for indicator, indicator_type in indicators:
            result = self.enrich(indicator, indicator_type)
            results.append(result)

        return results

    def _aggregate_threat_level(self, threat_data: list[ThreatData]) -> str:
        """Aggregate threat level from multiple sources."""
        if not threat_data:
            return "unknown"

        # Map threat levels to numeric scores
        level_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "unknown": 0,
        }

        # Take highest threat level
        max_score = max(level_scores.get(td.threat_level, 0) for td in threat_data)

        for level, score in level_scores.items():
            if score == max_score:
                return level

        return "unknown"

    def _aggregate_confidence(self, threat_data: list[ThreatData]) -> float:
        """Aggregate confidence scores from multiple sources."""
        if not threat_data:
            return 0.0

        # Average confidence weighted by number of sources
        total_confidence = sum(td.confidence for td in threat_data)
        return total_confidence / len(threat_data)

    def _aggregate_tags(self, threat_data: list[ThreatData]) -> list[str]:
        """Aggregate tags from multiple sources."""
        all_tags = set()
        for td in threat_data:
            all_tags.update(td.tags)
        return sorted(list(all_tags))

    def _aggregate_metadata(self, threat_data: list[ThreatData]) -> dict[str, Any]:
        """Aggregate metadata from multiple sources."""
        metadata = {
            "sources": {},
            "summary": {
                "total_sources": len(threat_data),
            },
        }

        for td in threat_data:
            metadata["sources"][td.source] = {
                "threat_level": td.threat_level,
                "confidence": td.confidence,
                "tags": td.tags,
                "metadata": td.metadata,
            }

        return metadata
