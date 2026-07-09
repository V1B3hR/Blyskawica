#!/usr/bin/env python3
"""
examples/forest_basic_example.py

Comprehensive example demonstrating the Forest module functionality.

This example shows:
1. Creating a forest and trees
2. Building tree hierarchy (trunks, branches, leaves)
3. Detecting various threat types
4. Health monitoring
5. Forest mapping and visualization
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forest import Branch, BranchType, Crown, ForestManager, HealthChecker, ThreatSeverity, Tree, Trunk


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_basic_forest():
    """Example 1: Create a basic forest with trees"""
    print_section("Example 1: Basic Forest Creation")

    # Create forest manager
    manager = ForestManager("Production Infrastructure")
    print(f"✓ Created forest: {manager.forest_name}")

    # Create first tree (web server)
    web_tree = Tree(tree_id="tree-web-01", hostname="web-server-01", ip_address="192.168.1.100", os_type="Ubuntu 22.04")

    # Add trunk
    trunk = Trunk(
        trunk_id="trunk-web-01",
        os_name="Ubuntu",
        os_version="22.04",
        kernel_version="5.15.0-91",
        metadata={"architecture": "x86_64"},
    )
    web_tree.set_trunk(trunk)

    # Add crown
    crown = Crown(crown_id="crown-web-01", tree_hostname="web-server-01")
    crown.add_observation("Server started", severity="INFO")
    web_tree.set_crown(crown)

    # Add branches (services)
    nginx_branch = Branch(
        branch_id="branch-nginx",
        name="nginx",
        branch_type=BranchType.SERVICE,
        metadata={"port": 80, "protocol": "TCP", "user": "www-data"},
    )
    nginx_branch.update_resources(cpu_percent=5.2, memory_mb=128.0)
    web_tree.add_branch(nginx_branch)

    php_branch = Branch(
        branch_id="branch-php-fpm",
        name="php-fpm",
        branch_type=BranchType.PROCESS,
        metadata={"pid": 1234, "user": "www-data"},
    )
    php_branch.update_resources(cpu_percent=12.5, memory_mb=256.0)
    web_tree.add_branch(php_branch)

    # Update tree statistics
    web_tree.update_statistics(cpu=45.0, memory=60.0, disk=35.0)

    # Add tree to forest
    manager.add_tree(web_tree)
    print(f"✓ Added tree: {web_tree.hostname}")
    print(f"  - Trunk: {trunk}")
    print(f"  - Crown: {crown}")
    print(f"  - Branches: {len(web_tree.branches)}")
    print(f"  - Health: {web_tree.health_score:.1f}%")

    # Create second tree (database server)
    db_tree = Tree(
        tree_id="tree-db-01", hostname="db-server-01", ip_address="192.168.1.101", os_type="PostgreSQL Server"
    )

    # Add PostgreSQL service
    postgres_branch = Branch(
        branch_id="branch-postgres",
        name="postgresql",
        branch_type=BranchType.SERVICE,
        metadata={"port": 5432, "protocol": "TCP"},
    )
    postgres_branch.update_resources(cpu_percent=25.0, memory_mb=1024.0)
    db_tree.add_branch(postgres_branch)

    db_tree.update_statistics(cpu=30.0, memory=70.0, disk=55.0)
    manager.add_tree(db_tree)
    print(f"\n✓ Added tree: {db_tree.hostname}")
    print(f"  - Branches: {len(db_tree.branches)}")
    print(f"  - Health: {db_tree.health_score:.1f}%")

    # Show forest overview
    print("\n" + manager.get_visual_overview())

    return manager


def example_2_threat_detection(manager):
    """Example 2: Detect various threats"""
    print_section("Example 2: Threat Detection")

    # Get trees
    web_tree = manager.get_tree_by_hostname("web-server-01")
    db_tree = manager.get_tree_by_hostname("db-server-01")

    # 1. Detect a Crow (malware)
    print("🐦‍⬛ Detecting Crow (Malware)...")
    crow = manager.threat_detector.detect_crow(
        threat_id="crow-001",
        name="Suspicious Process",
        malware_family="Trojan.Generic",
        severity=ThreatSeverity.HIGH,
        metadata={"c2_server": "185.220.101.50", "obfuscation_level": "high"},
    )
    crow.set_c2_server("evil-c2.example.com")
    crow.set_confidence(0.85)
    crow.set_risk_score(8.5)

    # Attach to web server
    manager.detect_threat(crow, web_tree.component_id, "branch-nginx")
    print(f"  ✓ {crow}")
    print(f"    Confidence: {crow.confidence:.0%}, Risk: {crow.risk_score}/10")

    # 2. Detect a Magpie (data stealer)
    print("\n🐦 Detecting Magpie (Data Stealer)...")
    magpie = manager.threat_detector.detect_magpie(
        threat_id="magpie-001",
        name="Credential Harvester",
        target_data_types=["credentials", "session_tokens", "api_keys"],
        severity=ThreatSeverity.HIGH,
    )
    magpie.add_stolen_item("credentials", 2048)
    magpie.add_stolen_item("session_tokens", 512)
    magpie.add_exfiltration_destination("192.0.2.100")
    magpie.set_confidence(0.92)
    magpie.set_risk_score(7.8)

    manager.detect_threat(magpie, web_tree.component_id)
    print(f"  ✓ {magpie}")
    print(f"    Stolen items: {len(magpie.stolen_items)}")
    print(f"    Exfiltration destinations: {len(magpie.exfiltration_destinations)}")

    # 3. Detect a Squirrel (lateral movement)
    print("\n🐿️ Detecting Squirrel (Lateral Movement)...")
    squirrel = manager.threat_detector.detect_squirrel(
        threat_id="squirrel-001",
        name="Pass-the-Hash Attack",
        technique="Pass-the-Hash",
        severity=ThreatSeverity.MEDIUM,
        metadata={"credential_type": "NTLM hash"},
    )
    squirrel.add_movement(web_tree.component_id, db_tree.component_id)
    squirrel.add_hiding_spot(db_tree.component_id, "/tmp/.hidden_backdoor")
    squirrel.set_confidence(0.78)
    squirrel.set_risk_score(6.5)

    manager.detect_threat(squirrel, db_tree.component_id)
    print(f"  ✓ {squirrel}")
    print(f"    Trees visited: {len(squirrel.visited_trees)}")
    print(f"    Movement path: {' → '.join([m['to'] for m in squirrel.movement_path])}")

    # 4. Detect a Snake (rootkit)
    print("\n🐍 Detecting Snake (Rootkit)...")
    snake = manager.threat_detector.detect_snake(
        threat_id="snake-001",
        name="Kernel Rootkit",
        rootkit_type="kernel",
        severity=ThreatSeverity.CRITICAL,
        metadata={"kernel_level": True, "privilege_level": "kernel"},
    )
    snake.add_hidden_process("backdoor", 9999)
    snake.add_hidden_file("/lib/modules/evil.ko")
    snake.add_hidden_network("0.0.0.0:31337")
    snake.set_confidence(0.95)
    snake.set_risk_score(9.5)

    manager.detect_threat(snake, db_tree.component_id)
    print(f"  ✓ {snake}")
    print(f"    Hidden processes: {len(snake.hidden_processes)}")
    print(f"    Hidden files: {len(snake.hidden_files)}")

    # 5. Detect a Parasite (cryptominer)
    print("\n🐛 Detecting Parasite (Cryptominer)...")
    parasite = manager.threat_detector.detect_parasite(
        threat_id="parasite-001",
        name="XMRig Miner",
        parasite_type="cryptominer",
        severity=ThreatSeverity.MEDIUM,
        metadata={"cryptocurrency": "Monero"},
    )
    parasite.update_resource_usage(cpu=85.0, gpu=90.0, network_mbps=5.2)
    parasite.set_mining_details("Monero", "pool.supportxmr.com")
    parasite.estimate_cost(electricity_cost_per_kwh=0.12)
    parasite.set_confidence(0.88)
    parasite.set_risk_score(5.5)

    manager.detect_threat(parasite, web_tree.component_id)
    print(f"  ✓ {parasite}")
    print(f"    CPU: {parasite.cpu_usage_percent:.1f}%, GPU: {parasite.gpu_usage_percent:.1f}%")
    print(f"    Estimated cost: ${parasite.estimated_cost_per_day:.2f}/day")

    # 6. Detect a Bat (night attack)
    print("\n🦇 Detecting Bat (Night Attack)...")
    bat = manager.threat_detector.detect_bat(
        threat_id="bat-001",
        name="Off-Hours Reconnaissance",
        attack_type="reconnaissance",
        severity=ThreatSeverity.MEDIUM,
    )
    # Simulate night activity
    from datetime import datetime, timedelta

    night_time = datetime.now().replace(hour=2, minute=30)
    bat.record_activity(night_time)
    bat.record_activity(night_time + timedelta(minutes=5))
    bat.record_activity(night_time + timedelta(minutes=10))
    bat.add_recon_method("port_scanning")
    bat.add_recon_method("service_enumeration")
    bat.set_confidence(0.75)
    bat.set_risk_score(4.5)

    manager.detect_threat(bat, web_tree.component_id)
    print(f"  ✓ {bat}")
    print(f"    Night activity: {bat.night_activity_count} events")
    print(f"    Recon methods: {len(bat.recon_methods)}")

    # Show threat summary
    print("\n📊 Threat Summary:")
    summary = manager.threat_detector.get_threat_summary()
    print(f"  Total threats: {summary['total_threats']}")
    print(f"  Active threats: {summary['active_threats']}")
    print(f"  Critical threats: {summary['critical_count']}")
    print(f"  By type: {summary['by_type']}")
    print(f"  By severity: {summary['by_severity']}")


def example_3_health_monitoring(manager):
    """Example 3: Health monitoring"""
    print_section("Example 3: Health Monitoring")

    health_checker = HealthChecker()

    # Check all trees
    all_trees = manager.get_all_trees()
    print(f"Checking health of {len(all_trees)} trees...\n")

    for tree in all_trees:
        result = health_checker.check_component(tree)
        print(f"🌳 {tree.hostname}")
        print(f"   Health: {result['health_score']:.1f}% ({result['health_grade'].upper()})")
        print(f"   Status: {result['status']}")
        print(f"   Threats: {result['threat_count']}")
        if result["issues"]:
            print(f"   Issues: {', '.join(result['issues'])}")
        print()

    # Get overall summary
    summary = health_checker.get_health_summary(all_trees)
    print("📊 Overall Health Summary:")
    print(f"   Average health: {summary['average_health']:.1f}%")
    print(f"   Unhealthy count: {summary['unhealthy_count']}")
    print(f"   Compromised count: {summary['compromised_count']}")
    print(f"   By grade: {summary['by_grade']}")
    print(f"   By status: {summary['by_status']}")


def example_4_forest_mapping(manager):
    """Example 4: Forest mapping and topology"""
    print_section("Example 4: Forest Mapping")

    # Access the forest map
    forest_map = manager.forest_map

    # Define network segments
    web_tree = manager.get_tree_by_hostname("web-server-01")
    db_tree = manager.get_tree_by_hostname("db-server-01")

    forest_map.add_network_segment("DMZ", [web_tree.component_id])
    forest_map.add_network_segment("Internal", [db_tree.component_id])
    print("✓ Defined network segments: DMZ, Internal")

    # Define tree relationships
    forest_map.add_tree_relationship(web_tree.component_id, db_tree.component_id)
    print(f"✓ Defined relationship: {web_tree.hostname} ↔ {db_tree.hostname}")

    # Get forest summary
    summary = forest_map.get_forest_summary()
    print("\n📊 Forest Summary:")
    print(f"   Total trees: {summary['total_trees']}")
    print(f"   Total branches: {summary['total_branches']}")
    print(f"   Total leaves: {summary['total_leaves']}")
    print(f"   Total threats: {summary['total_threats']}")
    print(f"   Average health: {summary['average_health']:.1f}%")

    # Get threat map
    threat_map = forest_map.get_threat_map()
    if threat_map:
        print("\n⚠️  Threat Map:")
        for tree_id, threat_info in threat_map.items():
            print(f"   {threat_info['hostname']} ({threat_info['ip_address']})")
            print(f"     - Direct threats: {threat_info['direct_threats']}")
            print(f"     - Threatened branches: {threat_info['threatened_branches']}")
            print(f"     - Health: {threat_info['health_score']:.1f}%")

    # Show visual map
    print("\n" + forest_map.get_visual_map())


def example_5_tree_visualization(manager):
    """Example 5: Tree visualization"""
    print_section("Example 5: Tree Visualization")

    web_tree = manager.get_tree_by_hostname("web-server-01")
    if web_tree:
        print(web_tree.get_visual_representation())

    db_tree = manager.get_tree_by_hostname("db-server-01")
    if db_tree:
        print("\n")
        print(db_tree.get_visual_representation())


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  🌳 Forest Module - Comprehensive Example")
    print("=" * 70)

    try:
        # Run examples in sequence
        manager = example_1_basic_forest()
        example_2_threat_detection(manager)
        example_3_health_monitoring(manager)
        example_4_forest_mapping(manager)
        example_5_tree_visualization(manager)

        # Final summary
        print_section("Final Summary")
        print(manager.get_visual_overview())

        print("\n✅ All examples completed successfully!")
        print("\n💡 Tips:")
        print("   - Use ForestManager to orchestrate your infrastructure")
        print("   - Regularly update tree statistics for accurate health scores")
        print("   - Monitor threat detector for new threats")
        print("   - Use HealthChecker to identify unhealthy components")
        print("   - Leverage ForestMap for topology visualization")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
