"""
Threat Intelligence Enrichment Module

Provides functionality for enriching security data with threat intelligence
from multiple sources including AbuseIPDB, OTX, GreyNoise, VirusTotal, and more.
"""

from .enricher import ThreatEnricher, EnrichmentResult
from .providers import (
    AbuseIPDBProvider,
    OTXProvider,
    GreyNoiseProvider,
    VirusTotalProvider,
    ThreatProvider,
)
from .scoring import RiskScorer, RiskScore
from .plugin_api import EnrichmentPlugin, PluginRegistry, PluginMetadata

__all__ = [
    "ThreatEnricher",
    "EnrichmentResult",
    "AbuseIPDBProvider",
    "OTXProvider",
    "GreyNoiseProvider",
    "VirusTotalProvider",
    "ThreatProvider",
    "RiskScorer",
    "RiskScore",
    "EnrichmentPlugin",
    "PluginRegistry",
    "PluginMetadata",
]
