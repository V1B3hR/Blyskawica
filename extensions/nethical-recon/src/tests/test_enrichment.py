"""
Tests for Threat Intelligence Enrichment Module
"""

import pytest

from nethical_recon.enrichment import (
    ThreatEnricher,
    AbuseIPDBProvider,
    OTXProvider,
    GreyNoiseProvider,
    VirusTotalProvider,
    RiskScorer,
    EnrichmentPlugin,
    PluginRegistry,
    PluginMetadata,
)
from nethical_recon.enrichment.providers import ThreatData


class TestThreatProviders:
    """Tests for threat intelligence providers."""

    def test_abuseipdb_provider(self):
        """Test AbuseIPDB provider."""
        provider = AbuseIPDBProvider(api_key="test_key")
        assert provider.get_name() == "AbuseIPDB"

        result = provider.query("8.8.8.8", "ip")
        assert result is not None
        assert result.indicator == "8.8.8.8"
        assert result.indicator_type == "ip"

    def test_otx_provider(self):
        """Test OTX provider."""
        provider = OTXProvider(api_key="test_key")
        assert provider.get_name() == "AlienVault OTX"

        result = provider.query("example.com", "domain")
        assert result is not None
        assert result.indicator == "example.com"

    def test_greynoise_provider(self):
        """Test GreyNoise provider."""
        provider = GreyNoiseProvider(api_key="test_key")
        assert provider.get_name() == "GreyNoise"

        result = provider.query("1.1.1.1", "ip")
        assert result is not None

        # GreyNoise only supports IPs
        result_domain = provider.query("example.com", "domain")
        assert result_domain is None

    def test_virustotal_provider(self):
        """Test VirusTotal provider."""
        provider = VirusTotalProvider(api_key="test_key")
        assert provider.get_name() == "VirusTotal"

        result = provider.query("example.com", "domain")
        assert result is not None


class TestThreatEnricher:
    """Tests for threat enricher."""

    def test_enricher_initialization(self):
        """Test enricher initializes."""
        enricher = ThreatEnricher()
        assert len(enricher.providers) == 0

    def test_add_provider(self):
        """Test adding providers."""
        enricher = ThreatEnricher()
        provider = AbuseIPDBProvider()

        enricher.add_provider(provider)
        assert len(enricher.providers) == 1

    def test_enrich_indicator(self):
        """Test enriching an indicator."""
        enricher = ThreatEnricher()
        enricher.add_provider(AbuseIPDBProvider())
        enricher.add_provider(OTXProvider())

        result = enricher.enrich("8.8.8.8", "ip")

        assert result.indicator == "8.8.8.8"
        assert result.indicator_type == "ip"
        assert result.enriched is True
        assert len(result.sources) > 0

    def test_enrich_batch(self):
        """Test batch enrichment."""
        enricher = ThreatEnricher()
        enricher.add_provider(AbuseIPDBProvider())

        indicators = [
            ("8.8.8.8", "ip"),
            ("1.1.1.1", "ip"),
        ]

        results = enricher.enrich_batch(indicators)

        assert len(results) == 2
        assert all(r.enriched for r in results)

    def test_aggregate_threat_level(self):
        """Test threat level aggregation."""
        enricher = ThreatEnricher()

        threat_data = [
            ThreatData(
                indicator="test",
                indicator_type="ip",
                source="test",
                threat_level="high",
                confidence=0.8,
            ),
            ThreatData(
                indicator="test",
                indicator_type="ip",
                source="test2",
                threat_level="medium",
                confidence=0.6,
            ),
        ]

        level = enricher._aggregate_threat_level(threat_data)
        assert level == "high"  # Should take highest level

    def test_aggregate_confidence(self):
        """Test confidence aggregation."""
        enricher = ThreatEnricher()

        threat_data = [
            ThreatData(
                indicator="test",
                indicator_type="ip",
                source="test",
                threat_level="high",
                confidence=0.8,
            ),
            ThreatData(
                indicator="test",
                indicator_type="ip",
                source="test2",
                threat_level="medium",
                confidence=0.6,
            ),
        ]

        confidence = enricher._aggregate_confidence(threat_data)
        assert confidence == 0.7  # Average of 0.8 and 0.6


class TestRiskScorer:
    """Tests for risk scoring."""

    def test_risk_scorer_initialization(self):
        """Test risk scorer initializes."""
        scorer = RiskScorer()
        assert scorer is not None

    def test_score_asset_basic(self):
        """Test basic asset scoring."""
        scorer = RiskScorer()

        asset = {
            "asset_id": "test_asset",
            "asset_type": "service",
            "port": 22,
            "services": [{"service": "ssh"}],
            "technologies": [],
        }

        score = scorer.score_asset(asset)

        assert score.asset_id == "test_asset"
        assert score.asset_type == "service"
        assert score.overall_score >= 0
        assert score.risk_level in ["low", "medium", "high", "critical"]

    def test_score_with_enrichment(self):
        """Test scoring with threat intelligence."""
        scorer = RiskScorer()

        asset = {
            "asset_id": "test_asset",
            "asset_type": "host",
            "port": 80,
        }

        enrichment_data = {
            "aggregated_threat_level": "high",
            "aggregated_confidence": 0.9,
            "sources": ["AbuseIPDB", "OTX"],
        }

        score = scorer.score_asset(asset, enrichment_data)

        assert score.overall_score > 0
        assert len(score.factors) > 0
        assert any(f.category == "threat_intel" for f in score.factors)

    def test_risk_level_determination(self):
        """Test risk level determination from score."""
        scorer = RiskScorer()

        assert scorer._determine_risk_level(90) == "critical"
        assert scorer._determine_risk_level(60) == "high"
        assert scorer._determine_risk_level(35) == "medium"
        assert scorer._determine_risk_level(10) == "low"

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        scorer = RiskScorer()

        asset = {
            "asset_id": "test_asset",
            "asset_type": "service",
            "port": 3389,  # High-risk port (RDP)
        }

        score = scorer.score_asset(asset)

        assert len(score.recommendations) > 0


class TestPluginAPI:
    """Tests for plugin API."""

    def test_plugin_registry_initialization(self):
        """Test plugin registry initializes."""
        registry = PluginRegistry()
        assert len(registry.plugins) == 0

    def test_register_plugin(self):
        """Test plugin registration."""
        registry = PluginRegistry()

        # Create a simple test plugin
        class TestPlugin(EnrichmentPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="TestPlugin",
                    version="1.0.0",
                    author="Test",
                    description="Test plugin",
                    supported_indicators=["ip"],
                )

            def initialize(self, config):
                return True

            def query(self, indicator, indicator_type):
                return ThreatData(
                    indicator=indicator,
                    indicator_type=indicator_type,
                    source="TestPlugin",
                    threat_level="low",
                    confidence=0.5,
                )

            def shutdown(self):
                pass

        plugin = TestPlugin()
        success = registry.register_plugin(plugin)

        assert success is True
        assert "TestPlugin" in registry.plugins

    def test_unregister_plugin(self):
        """Test plugin unregistration."""
        registry = PluginRegistry()

        class TestPlugin(EnrichmentPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="TestPlugin",
                    version="1.0.0",
                    author="Test",
                    description="Test plugin",
                    supported_indicators=["ip"],
                )

            def initialize(self, config):
                return True

            def query(self, indicator, indicator_type):
                return None

            def shutdown(self):
                pass

        plugin = TestPlugin()
        registry.register_plugin(plugin)

        success = registry.unregister_plugin("TestPlugin")
        assert success is True
        assert "TestPlugin" not in registry.plugins

    def test_list_plugins(self):
        """Test listing plugins."""
        registry = PluginRegistry()

        class TestPlugin(EnrichmentPlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="TestPlugin",
                    version="1.0.0",
                    author="Test",
                    description="Test plugin",
                    supported_indicators=["ip"],
                )

            def initialize(self, config):
                return True

            def query(self, indicator, indicator_type):
                return None

            def shutdown(self):
                pass

        plugin = TestPlugin()
        registry.register_plugin(plugin)

        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "TestPlugin"
