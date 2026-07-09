"""
Discovery Enrichment Pipeline for Cameras
Enriches raw discoveries with additional context and intelligence
"""

import logging
from datetime import datetime
from typing import Any
import socket

from .base import CameraDiscovery


class EnrichmentProvider:
    """Base class for enrichment providers"""

    def __init__(self, name: str):
        """
        Initialize enrichment provider

        Args:
            name: Name of the provider
        """
        self.name = name
        self.enabled = True

    def enrich(self, discovery: CameraDiscovery) -> dict[str, Any]:
        """
        Enrich a discovery

        Args:
            discovery: Discovery to enrich

        Returns:
            Enrichment data
        """
        raise NotImplementedError


class DNSEnrichmentProvider(EnrichmentProvider):
    """Enriches discoveries with DNS information"""

    def __init__(self):
        super().__init__("dns")

    def enrich(self, discovery: CameraDiscovery) -> dict[str, Any]:
        """Add DNS resolution data"""
        enrichment = {}
        target = discovery.target

        try:
            # Try to resolve hostname to IP
            if not self._is_ip(target):
                ip_addresses = socket.gethostbyname_ex(target)[2]
                enrichment["resolved_ips"] = ip_addresses
            else:
                # Try reverse DNS
                hostname, _, _ = socket.gethostbyaddr(target)
                enrichment["reverse_dns"] = hostname
        except (socket.gaierror, socket.herror):
            enrichment["dns_error"] = "Resolution failed"

        return enrichment

    def _is_ip(self, target: str) -> bool:
        """Check if target is an IP address"""
        try:
            socket.inet_aton(target)
            return True
        except socket.error:
            return False


class GeoIPEnrichmentProvider(EnrichmentProvider):
    """Enriches discoveries with geographic location (mock implementation)"""

    def __init__(self):
        super().__init__("geoip")

    def enrich(self, discovery: CameraDiscovery) -> dict[str, Any]:
        """Add geographic location data"""
        # Mock implementation - in production, use MaxMind GeoIP or similar
        return {
            "geo_location": {
                "country": "Unknown",
                "city": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0,
                "note": "GeoIP lookup not implemented",
            }
        }


class ThreatIntelEnrichmentProvider(EnrichmentProvider):
    """Enriches discoveries with threat intelligence (mock implementation)"""

    def __init__(self):
        super().__init__("threat_intel")

    def enrich(self, discovery: CameraDiscovery) -> dict[str, Any]:
        """Add threat intelligence data"""
        # Mock implementation - in production, integrate with threat feeds
        return {
            "threat_intel": {
                "is_known_malicious": False,
                "threat_score": 0,
                "categories": [],
                "note": "Threat intel lookup not implemented",
            }
        }


class MetadataEnrichmentProvider(EnrichmentProvider):
    """Enriches discoveries with metadata"""

    def __init__(self):
        super().__init__("metadata")

    def enrich(self, discovery: CameraDiscovery) -> dict[str, Any]:
        """Add metadata"""
        return {
            "metadata": {
                "enriched_at": datetime.now().isoformat(),
                "discovery_age_seconds": (datetime.now() - discovery.timestamp).total_seconds(),
                "target_type": self._classify_target(discovery.target),
            }
        }

    def _classify_target(self, target: str) -> str:
        """Classify the target type"""
        if self._is_ip(target):
            return "ip_address"
        elif "." in target:
            return "domain"
        else:
            return "unknown"

    def _is_ip(self, target: str) -> bool:
        """Check if target is an IP address"""
        try:
            socket.inet_aton(target)
            return True
        except socket.error:
            return False


class EnrichmentPipeline:
    """
    Pipeline for enriching camera discoveries with additional context
    """

    def __init__(self):
        """Initialize enrichment pipeline"""
        self.logger = logging.getLogger("nethical.enrichment_pipeline")
        self._initialize_logger()

        # Enrichment providers
        self.providers: dict[str, EnrichmentProvider] = {}

        # Statistics
        self.total_enrichments = 0
        self.total_errors = 0
        self.enrichments_by_provider: dict[str, int] = {}

        # Register default providers
        self._register_defaults()

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [EnrichmentPipeline] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _register_defaults(self):
        """Register default enrichment providers"""
        self.register_provider(DNSEnrichmentProvider())
        self.register_provider(GeoIPEnrichmentProvider())
        self.register_provider(ThreatIntelEnrichmentProvider())
        self.register_provider(MetadataEnrichmentProvider())

    def register_provider(self, provider: EnrichmentProvider) -> bool:
        """
        Register an enrichment provider

        Args:
            provider: Provider to register

        Returns:
            bool: True if registered successfully
        """
        if provider.name in self.providers:
            self.logger.warning(f"Provider {provider.name} already registered")
            return False

        self.providers[provider.name] = provider
        self.enrichments_by_provider[provider.name] = 0
        self.logger.info(f"Registered enrichment provider: {provider.name}")
        return True

    def unregister_provider(self, provider_name: str) -> bool:
        """
        Unregister an enrichment provider

        Args:
            provider_name: Name of provider to remove

        Returns:
            bool: True if removed successfully
        """
        if provider_name not in self.providers:
            self.logger.warning(f"Provider {provider_name} not found")
            return False

        del self.providers[provider_name]
        self.logger.info(f"Unregistered provider: {provider_name}")
        return True

    def enable_provider(self, provider_name: str):
        """Enable a provider"""
        if provider_name in self.providers:
            self.providers[provider_name].enabled = True
            self.logger.info(f"Enabled provider: {provider_name}")

    def disable_provider(self, provider_name: str):
        """Disable a provider"""
        if provider_name in self.providers:
            self.providers[provider_name].enabled = False
            self.logger.info(f"Disabled provider: {provider_name}")

    def enrich(self, discovery: CameraDiscovery) -> dict[str, Any]:
        """
        Enrich a discovery with all available providers

        Args:
            discovery: Discovery to enrich

        Returns:
            Enriched discovery data
        """
        enriched_data = discovery.to_dict()
        enrichments = {}

        for provider_name, provider in self.providers.items():
            if not provider.enabled:
                continue

            try:
                provider_data = provider.enrich(discovery)
                enrichments.update(provider_data)
                self.enrichments_by_provider[provider_name] += 1
            except Exception as e:
                self.logger.error(f"Error in provider {provider_name}: {e}")
                self.total_errors += 1
                enrichments[f"{provider_name}_error"] = str(e)

        enriched_data["enrichments"] = enrichments
        self.total_enrichments += 1

        return enriched_data

    def enrich_batch(self, discoveries: list[CameraDiscovery]) -> list[dict[str, Any]]:
        """
        Enrich multiple discoveries

        Args:
            discoveries: List of discoveries to enrich

        Returns:
            List of enriched discoveries
        """
        self.logger.info(f"Enriching batch of {len(discoveries)} discoveries")
        enriched = []

        for discovery in discoveries:
            try:
                enriched_data = self.enrich(discovery)
                enriched.append(enriched_data)
            except Exception as e:
                self.logger.error(f"Failed to enrich discovery: {e}")
                self.total_errors += 1
                # Include original data even if enrichment fails
                enriched.append(discovery.to_dict())

        return enriched

    def get_statistics(self) -> dict[str, Any]:
        """Get enrichment statistics"""
        return {
            "total_enrichments": self.total_enrichments,
            "total_errors": self.total_errors,
            "error_rate": (self.total_errors / self.total_enrichments if self.total_enrichments > 0 else 0.0),
            "registered_providers": len(self.providers),
            "enabled_providers": sum(1 for p in self.providers.values() if p.enabled),
            "enrichments_by_provider": self.enrichments_by_provider.copy(),
            "providers": {
                name: {"enabled": provider.enabled, "enrichments": self.enrichments_by_provider.get(name, 0)}
                for name, provider in self.providers.items()
            },
        }

    def reset_statistics(self):
        """Reset statistics"""
        self.total_enrichments = 0
        self.total_errors = 0
        self.enrichments_by_provider = {name: 0 for name in self.providers}
        self.logger.info("Reset enrichment statistics")
