"""
Example: Attack Surface Mapping and Threat Enrichment

Demonstrates the usage of new ROADMAP5 Section II features:
- Attack surface mapping
- Technology fingerprinting
- Baseline management
- Threat intelligence enrichment
- Risk scoring
"""

from nethical_recon.attack_surface import (
    AttackSurfaceMapper,
    BaselineManager,
    TechnologyFingerprinter,
    ServiceDetector,
    CMSDetector,
)
from nethical_recon.enrichment import (
    ThreatEnricher,
    AbuseIPDBProvider,
    OTXProvider,
    GreyNoiseProvider,
    VirusTotalProvider,
    RiskScorer,
    PluginRegistry,
)


def example_technology_fingerprinting():
    """Example 1: Technology Fingerprinting"""
    print("=" * 80)
    print("Example 1: Technology Fingerprinting")
    print("=" * 80)

    fingerprinter = TechnologyFingerprinter()

    # Fingerprint a website (would need actual URL in production)
    # results = fingerprinter.fingerprint("https://example.com")

    # Demonstrate with mock data
    print("\nDetected Technologies:")
    print("  - nginx 1.21.0 (web_server) - Confidence: 0.9")
    print("    Evidence: ['Header Server: nginx/1.21.0']")
    print("  - WordPress (cms) - Confidence: 0.8")
    print("    Evidence: ['Body pattern: wp-content', 'Body pattern: wp-includes']")


def example_service_detection():
    """Example 2: Service Detection"""
    print("\n" + "=" * 80)
    print("Example 2: Service Detection")
    print("=" * 80)

    detector = ServiceDetector()

    # Detect services on common ports
    services = detector.analyze_ports("example.com", [80, 443, 22, 3306])

    print("\nDetected Services:")
    for svc in services:
        print(f"  Port {svc['port']}: {svc['service']} ({svc['protocol']})")


def example_cms_detection():
    """Example 3: CMS Detection"""
    print("\n" + "=" * 80)
    print("Example 3: CMS Detection")
    print("=" * 80)

    detector = CMSDetector()

    # Detect CMS (would need actual URL in production)
    # cms_result = detector.detect_cms("https://example.com")

    print("\nCMS Detection Result:")
    print("  Detected: Yes")
    print("  CMS: WordPress")
    print("  Version: Unknown")
    print("  Confidence: 0.85")


def example_attack_surface_mapping():
    """Example 4: Attack Surface Mapping"""
    print("\n" + "=" * 80)
    print("Example 4: Attack Surface Mapping")
    print("=" * 80)

    mapper = AttackSurfaceMapper()

    # Map attack surface (would need actual target in production)
    # snapshot = mapper.map_surface("https://example.com", ports=[80, 443, 22])

    print("\nAttack Surface Snapshot:")
    print("  Snapshot ID: snapshot_example.com_20260110_120000")
    print("  Target: example.com")
    print("  Total Assets: 4")
    print("\n  Assets:")
    print("    - web_example.com (web_application)")
    print("      Technologies: nginx, WordPress, PHP")
    print("    - service_example.com_80 (service)")
    print("      Service: HTTP")
    print("    - service_example.com_443 (service)")
    print("      Service: HTTPS")
    print("    - service_example.com_22 (service)")
    print("      Service: SSH")


def example_baseline_management():
    """Example 5: Baseline Management"""
    print("\n" + "=" * 80)
    print("Example 5: Baseline Management")
    print("=" * 80)

    manager = BaselineManager(storage_path="/tmp/example_baselines")

    # In production, you would:
    # 1. Create initial baseline
    # baseline_name = manager.create_baseline(snapshot, "production_baseline")
    #
    # 2. Later, detect changes
    # changes = manager.detect_changes(baseline_name, current_snapshot)

    print("\nBaseline Management:")
    print("  1. Create baseline from snapshot")
    print("     baseline_name = manager.create_baseline(snapshot, 'production')")
    print("\n  2. Detect changes later")
    print("     changes = manager.detect_changes('production', current_snapshot)")
    print("\n  3. Analyze results")
    print("     - New assets: 2 (potential shadow IT)")
    print("     - Removed assets: 0")
    print("     - Changed assets: 1 (configuration drift)")
    print("     - Risk score: 45.0 (Medium)")


def example_threat_enrichment():
    """Example 6: Threat Intelligence Enrichment"""
    print("\n" + "=" * 80)
    print("Example 6: Threat Intelligence Enrichment")
    print("=" * 80)

    enricher = ThreatEnricher()

    # Add providers (would use API keys from environment in production)
    enricher.add_provider(AbuseIPDBProvider())
    enricher.add_provider(OTXProvider())
    enricher.add_provider(GreyNoiseProvider())
    enricher.add_provider(VirusTotalProvider())

    # Enrich an IP address
    # result = enricher.enrich("8.8.8.8", "ip")

    print("\nThreat Enrichment Result:")
    print("  Indicator: 8.8.8.8 (ip)")
    print("  Enriched: Yes")
    print("  Sources: ['AbuseIPDB', 'AlienVault OTX', 'GreyNoise', 'VirusTotal']")
    print("  Threat Level: low")
    print("  Confidence: 0.85")
    print("  Tags: ['dns', 'benign', 'public-resolver']")


def example_batch_enrichment():
    """Example 7: Batch Enrichment"""
    print("\n" + "=" * 80)
    print("Example 7: Batch Enrichment")
    print("=" * 80)

    enricher = ThreatEnricher()
    enricher.add_provider(AbuseIPDBProvider())
    enricher.add_provider(OTXProvider())

    indicators = [
        ("8.8.8.8", "ip"),
        ("1.1.1.1", "ip"),
        ("example.com", "domain"),
    ]

    # results = enricher.enrich_batch(indicators)

    print("\nBatch Enrichment Results:")
    print("  Processing 3 indicators...")
    print("\n  Results:")
    print("    1. 8.8.8.8 (ip) - Threat Level: low, Confidence: 0.85")
    print("    2. 1.1.1.1 (ip) - Threat Level: low, Confidence: 0.82")
    print("    3. example.com (domain) - Threat Level: low, Confidence: 0.75")


def example_risk_scoring():
    """Example 8: Risk Scoring"""
    print("\n" + "=" * 80)
    print("Example 8: Risk Scoring")
    print("=" * 80)

    scorer = RiskScorer()

    asset = {
        "asset_id": "db_server_1",
        "asset_type": "service",
        "host": "db.example.com",
        "port": 3306,  # MySQL - high risk port
        "services": [{"service": "mysql"}],
        "technologies": [{"name": "MySQL", "category": "database", "version": None}],
    }

    enrichment_data = {
        "aggregated_threat_level": "medium",
        "aggregated_confidence": 0.7,
        "sources": ["AbuseIPDB"],
    }

    # risk_score = scorer.score_asset(asset, enrichment_data)

    print("\nRisk Score Result:")
    print("  Asset: db_server_1 (service)")
    print("  Overall Score: 62.5")
    print("  Risk Level: HIGH")
    print("\n  Risk Factors:")
    print("    1. Threat Intelligence (score: 28.0, weight: 2.0)")
    print("       - Threat level: medium (confidence: 0.7)")
    print("       - Evidence: ['AbuseIPDB']")
    print("\n    2. Exposure (score: 40.0, weight: 1.5)")
    print("       - High-risk port 3306 exposed")
    print("       - Service: mysql")
    print("\n    3. Configuration (score: 10.0, weight: 1.0)")
    print("       - Unversioned technology: MySQL")
    print("\n  Recommendations:")
    print("    - Investigate threat intelligence alerts")
    print("    - Reduce attack surface by closing unnecessary ports")
    print("    - Review and harden configuration")


def example_plugin_system():
    """Example 9: Plugin System"""
    print("\n" + "=" * 80)
    print("Example 9: Custom Threat Feed Plugin")
    print("=" * 80)

    registry = PluginRegistry()

    # In production, you would create a custom plugin:
    # class MyThreatFeedPlugin(EnrichmentPlugin):
    #     def get_metadata(self):
    #         return PluginMetadata(
    #             name="MyThreatFeed",
    #             version="1.0.0",
    #             author="Security Team",
    #             description="Internal threat feed",
    #             supported_indicators=["ip", "domain"],
    #         )
    #
    #     def initialize(self, config):
    #         # Setup connection
    #         return True
    #
    #     def query(self, indicator, indicator_type):
    #         # Query custom feed
    #         return ThreatData(...)
    #
    #     def shutdown(self):
    #         pass

    # Register plugin
    # registry.register_plugin(MyThreatFeedPlugin(), config={...})

    print("\nPlugin System:")
    print("  1. Create custom plugin class")
    print("     class MyThreatFeedPlugin(EnrichmentPlugin): ...")
    print("\n  2. Register plugin")
    print("     registry.register_plugin(plugin, config={...})")
    print("\n  3. Query all plugins")
    print("     results = registry.query_all_plugins('8.8.8.8', 'ip')")
    print("\n  Benefits:")
    print("    - Easy integration of internal threat feeds")
    print("    - Consistent interface across all sources")
    print("    - Hot reload support")
    print("    - Lifecycle management")


def main():
    """Run all examples"""
    print("\n")
    print("*" * 80)
    print("ROADMAP5 Section II Examples")
    print("Attack Surface Mapping & Threat Intelligence Enrichment")
    print("*" * 80)

    example_technology_fingerprinting()
    example_service_detection()
    example_cms_detection()
    example_attack_surface_mapping()
    example_baseline_management()
    example_threat_enrichment()
    example_batch_enrichment()
    example_risk_scoring()
    example_plugin_system()

    print("\n" + "*" * 80)
    print("Examples Complete!")
    print("*" * 80)
    print("\nFor API usage, see:")
    print("  - POST /api/v1/attack-surface/map")
    print("  - POST /api/v1/enrichment/enrich")
    print("  - POST /api/v1/enrichment/risk-score")
    print("\nDocumentation: docs/PHASE_ROADMAP5_II_SUMMARY.md")
    print("*" * 80 + "\n")


if __name__ == "__main__":
    main()
