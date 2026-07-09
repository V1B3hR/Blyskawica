#!/usr/bin/env python3
"""
🦅 Eye in the Sky - Example Usage

Demonstrates the bird surveillance system (FALA 8)
"""

import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, "/home/runner/work/nethical-recon/nethical-recon")

from forest.sky import (
    Eagle,
    Falcon,
    FlightController,
    Owl,
    create_sky_surveillance,
)
from forest.visualization import render_sky_view, render_threat_map


def create_demo_forest_data():
    """Create demo forest data for testing"""
    return {
        "overall_health": 0.75,
        "trees": [
            {
                "name": "web-01",
                "health": 0.65,
                "online": True,
                "response_time_ms": 45,
                "threats": [{"type": "crow", "confidence": 0.85}],
                "resources": {"cpu_percent": 75, "memory_percent": 60, "disk_percent": 70},
            },
            {
                "name": "db-01",
                "health": 0.90,
                "online": True,
                "response_time_ms": 25,
                "threats": [],
                "resources": {"cpu_percent": 45, "memory_percent": 70, "disk_percent": 55},
            },
            {
                "name": "api-01",
                "health": 0.80,
                "online": True,
                "response_time_ms": 35,
                "threats": [{"type": "squirrel", "confidence": 0.72}],
                "resources": {"cpu_percent": 55, "memory_percent": 65, "disk_percent": 88},
            },
            {
                "name": "mail-01",
                "health": 0.95,
                "online": True,
                "response_time_ms": 30,
                "threats": [],
                "resources": {"cpu_percent": 30, "memory_percent": 50, "disk_percent": 45},
            },
            {
                "name": "file-01",
                "health": 0.70,
                "online": True,
                "response_time_ms": 50,
                "threats": [{"type": "parasite", "confidence": 0.68}],
                "resources": {"cpu_percent": 92, "memory_percent": 75, "disk_percent": 90},
            },
            {
                "name": "auth-01",
                "health": 0.85,
                "online": True,
                "response_time_ms": 20,
                "threats": [],
                "resources": {"cpu_percent": 40, "memory_percent": 55, "disk_percent": 50},
            },
        ],
        "threats": {"crows": 1, "squirrels": 1, "parasites": 1, "bats": 0},
        "new_threats": [
            {
                "type": "crow",
                "location": "web-01",
                "confidence": 0.85,
                "location_detail": {"tree": "web-01", "branch": "nginx"},
            }
        ],
        "network_activity": {
            "port_scans": [
                {
                    "source_ip": "192.168.1.105",
                    "target_tree": "web-01",
                    "port_count": 50,
                    "scan_type": "syn_scan",
                    "timestamp": datetime.now().isoformat(),
                }
            ],
            "unusual_connections": [],
        },
        "auth_failures": [],
        "recent_events": [],
    }


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_basic_deployment():
    """Example 1: Basic bird deployment"""
    print_header("Example 1: Basic Bird Deployment")

    # Create controller
    controller = FlightController()
    print("✅ Flight Controller created")

    # Deploy individual birds
    eagle = controller.deploy_eagle("Eagle-Alpha")
    print(f"✅ Deployed: {eagle}")

    falcon = controller.deploy_falcon("Falcon-Hunter")
    print(f"✅ Deployed: {falcon}")

    owl = controller.deploy_owl("Owl-Watcher")
    print(f"✅ Deployed: {owl}")

    sparrow = controller.deploy_sparrow("Sparrow-Scout")
    print(f"✅ Deployed: {sparrow}")

    # Activate all
    controller.activate_all()
    print("\n✅ All birds activated and in flight")

    # Show status
    status = controller.get_fleet_status()
    print("\n📊 Fleet Status:")
    print(f"   Active birds: {status['active_birds']}/{status['total_birds']}")
    print(f"   Eagle: {status['fleet_composition']['eagle']}")
    print(f"   Falcons: {status['fleet_composition']['falcons']}")
    print(f"   Owls: {status['fleet_composition']['owls']}")
    print(f"   Sparrows: {status['fleet_composition']['sparrows']}")


def example_2_standard_fleet():
    """Example 2: Deploy standard fleet"""
    print_header("Example 2: Standard Fleet Deployment")

    # Quick deployment
    sky = create_sky_surveillance()
    print("✅ Standard fleet deployed and activated")

    status = sky.get_fleet_status()
    print("\n📊 Standard Fleet:")
    print(f"   Total birds: {status['total_birds']}")
    print(f"   All systems active: {status['controller_active']}")

    for name, bird_status in status["birds"].items():
        bird_type = bird_status["type"].upper()
        is_active = "✅" if bird_status["active"] else "❌"
        flight_mode = bird_status["flight_mode"].upper()
        print(f"   {is_active} {name} [{bird_type}] - {flight_mode}")


def example_3_forest_scan():
    """Example 3: Scan forest with all birds"""
    print_header("Example 3: Full Forest Scan")

    # Deploy fleet
    sky = create_sky_surveillance()
    print("✅ Fleet deployed\n")

    # Create demo data
    forest_data = create_demo_forest_data()
    print(f"🌳 Forest: {len(forest_data['trees'])} trees, {sum(forest_data['threats'].values())} threats\n")

    # Scan
    print("🔍 Scanning forest with all birds...\n")
    results = sky.scan_forest(forest_data)

    # Show results by bird type
    print("📋 SCAN RESULTS:\n")

    print(f"🦅 Eagle Alerts: {len(results['eagle'])}")
    for alert in results["eagle"]:
        print(f"   {alert}")

    print(f"\n🦅 Falcon Alerts: {len(results['falcon'])}")
    for alert in results["falcon"][:5]:  # Show first 5
        print(f"   {alert}")

    print(f"\n🦉 Owl Alerts: {len(results['owl'])}")
    for alert in results["owl"][:3]:
        print(f"   {alert}")

    print(f"\n🐦 Sparrow Alerts: {len(results['sparrow'])}")
    for alert in results["sparrow"][:3]:
        print(f"   {alert}")

    print(f"\n📊 TOTAL ALERTS: {len(results['all'])}")


def example_4_eagle_executive_report():
    """Example 4: Eagle executive report"""
    print_header("Example 4: Eagle Executive Report")

    # Deploy eagle
    from forest.sky.base_bird import FlightMode

    eagle = Eagle("Eagle-Command")
    eagle.take_flight(FlightMode.SOARING)
    print("✅ Eagle deployed for strategic assessment\n")

    # Create data and scan
    forest_data = create_demo_forest_data()
    alerts = eagle.scan(forest_data)
    print(f"🦅 Eagle detected {len(alerts)} strategic issues\n")

    # Generate executive report
    report = eagle.generate_executive_report(forest_data)

    print("📊 EXECUTIVE SUMMARY")
    print("=" * 70)
    print(f"Threat Level: {report['overall_status']['threat_emoji']} {report['overall_status']['threat_level']}")
    print(f"Forest Health: {report['overall_status']['forest_health']}")
    print()
    print("Infrastructure:")
    print(f"  Total Trees: {report['infrastructure']['total_trees']}")
    print(f"  Healthy: {report['infrastructure']['healthy_trees']}")
    print(f"  Compromised: {report['infrastructure']['compromised_trees']}")
    print()
    print("Threats:")
    print(f"  Total: {report['threats']['total']}")
    print(f"  Crows (Malware): {report['threats']['crows']}")
    print(f"  Squirrels (Lateral): {report['threats']['squirrels']}")
    print()
    print("Strategic Recommendations:")
    for i, rec in enumerate(report["strategic_recommendations"], 1):
        print(f"  {i}. {rec}")


def example_5_falcon_hunting():
    """Example 5: Falcon hunting target"""
    print_header("Example 5: Falcon Active Hunting")

    # Deploy falcon
    falcon = Falcon("Falcon-Hunter")
    from forest.sky.base_bird import FlightMode

    falcon.take_flight(FlightMode.HUNTING)
    print("✅ Falcon deployed in hunting mode\n")

    # Create target
    target = {"type": "malware", "confidence": 0.92, "ip": "192.168.1.105", "location": "web-01"}

    print(f"🎯 Target acquired: {target['type']} on {target['location']}")
    print(f"   Confidence: {target['confidence']*100:.0f}%\n")

    # Hunt target
    hunt_result = falcon.hunt_target(target)

    print("🦅 FALCON HUNT RESULT:")
    print(f"   Status: {hunt_result['status'].upper()}")
    print(f"   Recommendation: {hunt_result['recommendation']}")
    print(f"   Weapon: {hunt_result.get('weapon_type', 'N/A')}")
    print()
    print("   Findings:")
    for finding in hunt_result["findings"]:
        print(f"     • {finding}")

    # Quick response
    print("\n⚡ QUICK RESPONSE ACTIONS:")
    actions = falcon.quick_response({"type": "malware", "severity": "critical"})
    for i, action in enumerate(actions, 1):
        print(f"   {i}. {action}")


def example_6_owl_observation():
    """Example 6: Owl stealth observation"""
    print_header("Example 6: Owl Stealth Observation")

    # Deploy owl
    owl = Owl("Owl-Silent")
    from forest.sky.base_bird import FlightMode

    owl.take_flight(FlightMode.WATCHING)
    print("✅ Owl deployed in stealth mode\n")

    # Create target for observation
    target = {"type": "suspicious_process", "name": "unknown.exe", "pid": 4521, "tree": "web-01"}

    print(f"👁️  Target for observation: {target['name']}")
    print(f"   Location: {target['tree']}, PID: {target['pid']}\n")

    # Deep observation
    observation = owl.deep_observation(target, duration_minutes=30)

    print("🦉 OWL OBSERVATION REPORT:")
    print(f"   Observer: {observation['observer']}")
    print(f"   Duration: {observation['duration_minutes']} minutes")
    print(f"   Mode: {observation['mode'].upper()}")
    print()
    print("   Findings:")
    for finding in observation["findings"]:
        print(f"     • {finding}")
    print()
    print("   Recommendations:")
    for rec in observation["recommendations"]:
        print(f"     • {rec}")

    # Share wisdom
    print("\n🧠 OWL WISDOM:")
    wisdom = owl.share_wisdom()
    print(f"   Wisdom entries: {wisdom['wisdom_entries']}")
    print(f"   Hidden observations: {wisdom['hidden_observations']}")
    print("   Insights:")
    for insight in wisdom["insights"]:
        print(f"     • {insight}")


def example_7_visualization():
    """Example 7: Visual representations"""
    print_header("Example 7: Visual Representations")

    # Deploy fleet
    sky = create_sky_surveillance()
    forest_data = create_demo_forest_data()

    # Get status
    bird_status = sky.get_fleet_status()

    print("🦅 SKY VIEW:\n")
    sky_view = render_sky_view(forest_data, bird_status)
    print(sky_view)

    print("\n\n🗺️  THREAT MAP:\n")
    threat_map = render_threat_map(forest_data)
    print(threat_map)


def example_8_coordinated_response():
    """Example 8: Coordinated response to threat"""
    print_header("Example 8: Coordinated Threat Response")

    # Deploy fleet
    sky = create_sky_surveillance()
    print("✅ Fleet deployed\n")

    # Threat detected
    threat = {
        "type": "malware",
        "severity": "critical",
        "location": "web-01",
        "confidence": 0.95,
        "details": "Crow detected in tree canopy",
    }

    print("🚨 THREAT DETECTED:")
    print(f"   Type: {threat['type'].upper()}")
    print(f"   Severity: {threat['severity'].upper()}")
    print(f"   Location: {threat['location']}")
    print(f"   Confidence: {threat['confidence']*100:.0f}%\n")

    # Coordinate response
    print("🎯 Coordinating response...\n")
    response = sky.coordinate_response(threat)

    print("📋 COORDINATED RESPONSE PLAN:")
    print(f"   Birds deployed: {', '.join(response['birds_deployed'])}")
    print()

    if "strategic_decision" in response:
        decision = response["strategic_decision"]
        print(f"🦅 Eagle Decision: {decision['decision']}")
        print(f"   Priority: {decision['priority'].upper()}")
        print("   Actions:")
        for action in decision["actions"]:
            print(f"     • {action}")

    print()
    if "falcon_hunt" in response:
        hunt = response["falcon_hunt"]
        print(f"🦅 Falcon Hunt: {hunt['status'].upper()}")
        print(f"   Recommendation: {hunt['recommendation']}")

    print()
    if "actions" in response:
        print("⚡ Immediate Actions:")
        for action in response["actions"][:5]:
            print(f"   • {action}")


def main():
    """Run all examples"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                🦅 EYE IN THE SKY - FALA 8                             ║")
    print("║              Bird Surveillance System Examples                        ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")

    try:
        example_1_basic_deployment()
        time.sleep(1)

        example_2_standard_fleet()
        time.sleep(1)

        example_3_forest_scan()
        time.sleep(1)

        example_4_eagle_executive_report()
        time.sleep(1)

        example_5_falcon_hunting()
        time.sleep(1)

        example_6_owl_observation()
        time.sleep(1)

        example_7_visualization()
        time.sleep(1)

        example_8_coordinated_response()

        print("\n" + "=" * 70)
        print("  ✅ All examples completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
