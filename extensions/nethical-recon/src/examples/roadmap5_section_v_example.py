"""
Example: Enterprise & Global Intelligence Features

Demonstrates the usage of Section V features including anomaly detection,
lateral movement detection, kill chain analysis, cloud discovery, and digital twin.
"""

from datetime import datetime, timedelta
from uuid import uuid4

# Enterprise Intelligence imports
from nethical_recon.enterprise import (
    AnomalyDetectionService,
    AnomalyType,
    LateralMovementDetector,
    MovementType,
    KillChainAnalyzer,
    KillChainPhase,
    AssetInventoryIntegration,
    AssetCriticality,
)

# Global Intelligence imports
from nethical_recon.global_intelligence import (
    OrganizationScanner,
    OrganizationScope,
    ScopeType,
    CloudAssetDiscovery,
    CloudProvider,
    ShadowITDetector,
    OrganizationRiskMapper,
    DigitalTwin,
)


def example_anomaly_detection():
    """Example: ML-based Anomaly Detection"""
    print("=" * 80)
    print("EXAMPLE 1: Anomaly Detection")
    print("=" * 80)

    # Initialize service
    service = AnomalyDetectionService(
        config={
            "sensitivity": 0.5,
            "baseline_window_days": 30,
            "min_confidence_threshold": 0.6,
        }
    )

    # Create baseline from historical data
    historical_data = [
        {"timestamp": datetime.utcnow(), "connections": 100, "bandwidth_mbps": 50},
        {"timestamp": datetime.utcnow(), "connections": 105, "bandwidth_mbps": 48},
        {"timestamp": datetime.utcnow(), "connections": 98, "bandwidth_mbps": 52},
        # ... more historical data
    ]

    baseline = service.create_baseline(entity_id="host-web-01", entity_type="host", historical_data=historical_data)

    print(f"\nBaseline created for host-web-01")
    print(f"  Confidence: {baseline.confidence_level:.2f}")
    print(f"  Metrics: {len(baseline.metrics)} features")

    # Detect anomalies in current observations
    current_observations = [
        {"timestamp": datetime.utcnow(), "connections": 500, "bandwidth_mbps": 200},  # Anomalous
    ]

    anomalies = service.detect_anomalies(entity_id="host-web-01", current_observations=current_observations)

    print(f"\nDetected {len(anomalies)} anomalies:")
    for anomaly in anomalies:
        print(f"\n  Anomaly ID: {anomaly.event_id}")
        print(f"    Type: {anomaly.anomaly_type.value}")
        print(f"    Severity: {anomaly.severity}")
        print(f"    Confidence: {anomaly.confidence:.2f}")
        print(f"    Deviation: {anomaly.baseline_deviation:.2f} σ")
        print(f"    Description: {anomaly.description}")


def example_lateral_movement():
    """Example: Lateral Movement Detection"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Lateral Movement Detection")
    print("=" * 80)

    # Initialize detector
    detector = LateralMovementDetector(
        config={"time_window_minutes": 10, "min_confidence_threshold": 0.6, "track_chains": True}
    )

    # Simulate authentication events
    auth_events = [
        {
            "timestamp": datetime.utcnow(),
            "username": "admin",
            "source_host": "192.168.1.10",
            "destination_host": "192.168.1.20",
            "auth_type": "rdp",
            "success": True,
        },
        {
            "timestamp": datetime.utcnow() + timedelta(minutes=2),
            "username": "admin",
            "source_host": "192.168.1.20",
            "destination_host": "192.168.1.30",
            "auth_type": "ssh",
            "success": True,
        },
        {
            "timestamp": datetime.utcnow() + timedelta(minutes=5),
            "username": "admin",
            "source_host": "192.168.1.30",
            "destination_host": "192.168.1.40",
            "auth_type": "smb",
            "success": True,
        },
    ]

    print("\nAnalyzing authentication events...")
    patterns = []
    for event in auth_events:
        pattern = detector.analyze_authentication(event)
        if pattern:
            patterns.append(pattern)
            print(f"\n  Lateral movement detected!")
            print(f"    From: {pattern.source_host} -> To: {pattern.destination_host}")
            print(f"    Method: {pattern.movement_type.value}")
            print(f"    Confidence: {pattern.confidence:.2f}")
            print(f"    Path length: {pattern.path_length}")

    # Get movement chains
    chains = detector.get_movement_chains(username="admin")
    print(f"\n  Movement chains tracked: {len(chains)}")
    for chain in chains:
        print(f"\n  Chain ID: {chain.chain_id}")
        print(f"    Path: {' -> '.join(chain.hosts_visited)}")
        print(f"    Risk score: {chain.risk_score:.1f}/100")
        print(f"    Duration: {(chain.end_time - chain.start_time).seconds}s")


def example_kill_chain():
    """Example: Kill Chain Analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Kill Chain Analysis")
    print("=" * 80)

    # Initialize analyzer
    analyzer = KillChainAnalyzer(
        config={"chain_timeout_hours": 48, "min_confidence_threshold": 0.5, "early_warning_phases": 3}
    )

    # Simulate attack progression
    events = [
        {"event_type": "port_scan", "source": "10.0.1.5", "target": "192.168.1.10"},
        {"event_type": "exploit_attempt", "source": "10.0.1.5", "target": "192.168.1.10"},
        {"event_type": "backdoor_install", "source": "10.0.1.5", "target": "192.168.1.10"},
        {"event_type": "c2_callback", "source": "192.168.1.10", "target": "evil-c2.com"},
    ]

    print("\nAnalyzing security events...")
    for event in events:
        event["timestamp"] = datetime.utcnow()
        kill_chain_event = analyzer.analyze_event(event)

        if kill_chain_event:
            print(f"\n  Kill chain phase detected: {kill_chain_event.phase.value}")
            print(f"    Event: {event['event_type']}")
            print(f"    Severity: {kill_chain_event.severity}")
            print(f"    Confidence: {kill_chain_event.confidence:.2f}")
            print(f"    MITRE techniques: {', '.join(kill_chain_event.mitre_techniques)}")

    # Get active attack chains
    chains = analyzer.get_attack_chains(active_only=True)
    print(f"\n  Active attack chains: {len(chains)}")
    for chain in chains:
        print(f"\n  Attack chain from {chain.attacker_id}:")
        print(f"    Phases detected: {[p.value for p in chain.phases_detected]}")
        print(f"    Risk score: {chain.risk_score:.1f}/100")
        print(f"    Completeness: {chain.completeness * 100:.1f}%")
        print(f"    Targets: {', '.join(chain.target_assets)}")


def example_asset_inventory():
    """Example: Asset Inventory Integration"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Asset Inventory & CMDB Integration")
    print("=" * 80)

    # Initialize integration
    integration = AssetInventoryIntegration(config={"cmdb_type": "custom", "match_threshold": 0.7})

    # Load assets from CMDB
    asset_count = integration.load_assets_from_cmdb()
    print(f"\nLoaded {asset_count} assets from CMDB")

    # Enrich reconnaissance data
    recon_data = {
        "ip": "192.168.1.10",
        "hostname": "web-prod-01",
        "services": ["HTTP", "HTTPS", "SSH"],
        "operating_system": "Ubuntu 22.04",
    }

    enriched = integration.enrich_reconnaissance_data(recon_data)

    print(f"\nEnrichment result:")
    if enriched.cmdb_data:
        print(f"  Asset matched: {enriched.cmdb_data.name}")
        print(f"    Criticality: {enriched.cmdb_data.criticality.value}")
        print(f"    Owner: {enriched.cmdb_data.owner}")
        print(f"    Department: {enriched.cmdb_data.department}")
        print(f"    Compliance: {', '.join(enriched.cmdb_data.compliance_requirements)}")
        print(f"    Match confidence: {enriched.match_confidence:.2f}")

        if enriched.discrepancies:
            print(f"\n  Discrepancies detected: {len(enriched.discrepancies)}")
            for disc in enriched.discrepancies:
                print(f"    - {disc}")

    # Calculate business impact
    impact_score = integration.calculate_business_impact_score(asset_identifier="192.168.1.10", finding_severity="high")
    print(f"\n  Business impact score: {impact_score:.1f}/100")


def example_organization_scan():
    """Example: Organization-Wide Scanning"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Organization-Wide Reconnaissance")
    print("=" * 80)

    # Initialize scanner
    scanner = OrganizationScanner(config={"passive_only": True, "max_subdomains": 10000})

    # Define organization scope
    scope = OrganizationScope(
        scope_type=ScopeType.DOMAIN,
        primary_domain="example.com",
        additional_domains=["example.org"],
        organization_name="Example Corporation",
    )

    print(f"\nScanning organization: {scope.organization_name}")
    print(f"  Primary domain: {scope.primary_domain}")

    # Perform scan
    result = scanner.scan_organization(scope)

    print(f"\n  Scan completed: {result.status}")
    print(f"  Duration: {(result.end_time - result.start_time).total_seconds():.1f}s")
    print(f"\n  Statistics:")
    print(f"    Total assets: {result.statistics['total_assets']}")
    print(f"    Subdomains: {result.statistics['subdomains']}")
    print(f"    IP addresses: {result.statistics['ip_addresses']}")

    print(f"\n  Sample subdomains (first 5):")
    for subdomain in result.subdomains[:5]:
        print(f"    - {subdomain}")


def example_cloud_discovery():
    """Example: Multi-Cloud Asset Discovery"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Multi-Cloud Asset Discovery")
    print("=" * 80)

    # Initialize discovery
    discovery = CloudAssetDiscovery(config={"regions": ["us-east-1", "eu-west-1"]})

    print("\nDiscovering AWS assets...")
    aws_result = discovery.discover_aws_assets(accounts=["123456789012"])

    print(f"  Status: {aws_result.status}")
    print(f"  Regions scanned: {', '.join(aws_result.regions_scanned)}")
    print(f"\n  Statistics:")
    print(f"    Total assets: {aws_result.statistics['total_assets']}")
    print(f"    Public assets: {aws_result.statistics['public_assets']}")
    print(f"    Assets with risks: {aws_result.statistics['assets_with_risks']}")

    print(f"\n  Discovered assets:")
    for asset in aws_result.assets[:5]:
        print(f"\n    {asset.resource_type.value}: {asset.name}")
        print(f"      Region: {asset.region}")
        print(f"      Public: {asset.public_access}")
        if asset.risk_indicators:
            print(f"      Risks: {', '.join(asset.risk_indicators)}")


def example_shadow_it():
    """Example: Shadow IT Detection"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Shadow IT Detection")
    print("=" * 80)

    # Initialize detector
    detector = ShadowITDetector(
        config={
            "authorized_domains": ["*.example.com", "*.example.org"],
            "min_confidence_threshold": 0.6,
        }
    )

    # Discovered subdomains
    discovered_subdomains = [
        "www.example.com",  # Authorized
        "api.example.com",  # Authorized
        "rogue.example.net",  # Unauthorized
        "shadow.otherdomain.com",  # Unauthorized
    ]

    print("\nDetecting unauthorized subdomains...")
    findings = detector.detect_unauthorized_subdomains(discovered_subdomains)

    print(f"  Shadow IT findings: {len(findings)}")
    for finding in findings:
        print(f"\n    Resource: {finding.resource_identifier}")
        print(f"      Type: {finding.shadow_it_type.value}")
        print(f"      Severity: {finding.severity}")
        print(f"      Confidence: {finding.confidence:.2f}")
        print(f"      Risk factors: {', '.join(finding.risk_factors[:2])}")


def example_risk_mapping():
    """Example: Organization Risk Mapping"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Organization Risk Mapping")
    print("=" * 80)

    # Initialize mapper
    mapper = OrganizationRiskMapper(config={"compliance_frameworks": ["PCI-DSS", "HIPAA"]})

    # Sample assets and vulnerabilities
    assets = [
        {"id": "asset1", "department": "Engineering", "criticality": "high", "public_access": True},
        {"id": "asset2", "department": "Engineering", "criticality": "medium", "public_access": False},
        {"id": "asset3", "department": "Finance", "criticality": "critical", "public_access": False},
    ]

    vulnerabilities = [
        {"asset_id": "asset1", "severity": "high", "type": "sql_injection"},
        {"asset_id": "asset1", "severity": "medium", "type": "xss"},
    ]

    print("\nCreating risk map...")
    risk_map = mapper.create_risk_map(
        assets=assets, vulnerabilities=vulnerabilities, organization_name="Example Corporation"
    )

    print(f"\n  Organization: {risk_map.organization_name}")
    print(f"  Overall risk score: {risk_map.overall_risk_score:.1f}/100")
    print(f"  Total assets: {risk_map.total_assets}")
    print(f"  High-risk assets: {risk_map.high_risk_assets}")
    print(f"  Attack surface score: {risk_map.attack_surface_score:.1f}/100")

    print(f"\n  Risk Zones:")
    for zone in risk_map.zones:
        print(f"\n    {zone.name}:")
        print(f"      Risk level: {zone.risk_level}")
        print(f"      Risk score: {zone.risk_score:.1f}/100")
        print(f"      Assets: {zone.asset_count} ({zone.critical_assets} critical)")
        print(f"      Mitigation priority: {zone.mitigation_priority}/10")

    print(f"\n  Top Recommendations:")
    for rec in risk_map.recommendations[:3]:
        print(f"    - {rec}")


def example_digital_twin():
    """Example: Organization Digital Twin"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Organization Digital Twin")
    print("=" * 80)

    # Initialize digital twin
    twin = DigitalTwin(config={"organization_name": "Example Corporation", "enable_simulation": True})

    # Sample infrastructure
    assets = [
        {"id": "web-dmz", "name": "web-dmz", "asset_type": "server", "public_access": True},
        {"id": "app-server", "name": "app-server", "asset_type": "server", "connections": ["web-dmz"]},
        {"id": "db-server", "name": "db-server", "asset_type": "database", "connections": ["app-server"]},
    ]

    print("\nCreating digital twin...")
    twin_id = twin.create_twin(assets=assets)

    state = twin.get_twin_state()
    print(f"  Twin ID: {twin_id}")
    print(f"  Organization: {state['organization']}")
    print(f"  Assets: {state['asset_count']}")
    print(f"  Relationships: {state['relationship_count']}")

    # Simulate attack path
    print("\n  Simulating attack path from web-dmz to db-server...")
    attack_sim = twin.simulate_attack_path(entry_point="web-dmz", target="db-server")

    print(f"    Paths found: {attack_sim['paths_found']}")
    if attack_sim["paths"]:
        for i, path in enumerate(attack_sim["paths"][:2], 1):
            print(f"\n    Path {i}: {' -> '.join(path['path'])}")
            print(f"      Feasibility: {path['feasibility_score']:.1f}/100")
            print(f"      Difficulty: {path['difficulty']}")

    # Simulate infrastructure change
    print("\n  Simulating infrastructure change...")
    change_impact = twin.simulate_change_impact({"asset_id": "app-server", "change_type": "remove"})

    print(f"    Changed asset: {change_impact['changed_asset']}")
    print(f"    Directly affected: {change_impact['directly_affected']}")
    print(f"    Risk assessment: {change_impact['risk_assessment']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("NETHICAL RECON - SECTION V EXAMPLES")
    print("Enterprise & Global Intelligence Features")
    print("=" * 80)

    # Run examples
    example_anomaly_detection()
    example_lateral_movement()
    example_kill_chain()
    example_asset_inventory()
    example_organization_scan()
    example_cloud_discovery()
    example_shadow_it()
    example_risk_mapping()
    example_digital_twin()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
