"""
Threat Intelligence Enrichment Module

Provides functionality for enriching security data with threat intelligence
from multiple sources including AbuseIPDB, OTX, GreyNoise, VirusTotal, and more.
"""

from .enricher import EnrichmentResult, ThreatEnricher
from .plugin_api import EnrichmentPlugin, PluginMetadata, PluginRegistry
from .providers import (
    AbuseIPDBProvider,
    GreyNoiseProvider,
    OTXProvider,
    ThreatProvider,
    VirusTotalProvider,
)
from .scoring import RiskScore, RiskScorer

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
