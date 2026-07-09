"""
Weapons Module - Basic Examples
FALA 5: Broń Markerowa (Silent Marker)

This example demonstrates the complete Silent Marker weapon system including:
- Weapon modes (Pneumatic, CO2 Silent, Electric)
- Tracer ammunition (all 8 colors)
- Targeting system
- Fire control system
- Integration patterns
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from weapons import (
    BlackTracer,
    BlueTracer,
    BrownTracer,
    CO2SilentMode,
    ElectricMode,
    FireControlSystem,
    MarkerGun,
    OrangeTracer,
    PneumaticMode,
    PurpleTracer,
    RedTracer,
    TargetingSystem,
    WeaponMode,
    WhiteTracer,
    YellowTracer,
)


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_basic_weapon():
    """Example 1: Basic weapon usage"""
    print_section("Example 1: Basic Weapon Setup and Firing")

    # Create weapon
    gun = MarkerGun(name="Silent Marker Alpha")
    print(f"✅ Created: {gun.name} (S/N: {gun.serial_number})")

    # Register weapon modes
    gun.register_mode(WeaponMode.PNEUMATIC, PneumaticMode())
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
    gun.register_mode(WeaponMode.ELECTRIC, ElectricMode())
    print("✅ Registered 3 weapon modes")

    # Load ammunition
    gun.load_ammo(RedTracer())
    gun.load_ammo(OrangeTracer())
    gun.load_ammo(BlackTracer())
    print("✅ Loaded 3 tracer types")

    # Set mode and ammo
    gun.set_mode(WeaponMode.CO2_SILENT)
    gun.select_ammo("RED")
    print("✅ Mode: CO2_SILENT, Ammo: RED")

    # Prepare to fire
    gun.arm()
    gun.safety_off()
    print("✅ Weapon armed, safety off")

    # Define target
    target = {
        "ip": "192.168.1.105",
        "file_hash": "a1b2c3d4e5f6789012345678901234567890",
        "process_name": "malware.exe",
        "threat_score": 9.0,
        "confidence": 0.92,
    }

    print(f"\n🎯 Target acquired: {target['ip']}")
    print(f"   File: {target['process_name']}")
    print(f"   Threat Score: {target['threat_score']}")
    print(f"   Confidence: {target['confidence']}")

    # Fire!
    print("\n🔫 FIRING...")
    result = gun.fire(target)

    if result["hit"]:
        print("✅ HIT! Target marked successfully")
        print(f"   Mode: {result['mode_used']}")
        print(f"   Noise: {result['noise_level_db']} dB")
        print(f"   Stain ID: {result['stain']['tag_id']}")
        print(f"   Marker Type: {result['stain']['marker_type']}")
    else:
        print(f"❌ MISS: {result['message']}")

    # Get statistics
    stats = gun.get_statistics()
    print("\n📊 Weapon Statistics:")
    print(f"   Shots Fired: {stats['shots_fired']}")
    print(f"   Hits: {stats['hits_successful']}")
    print(f"   Accuracy: {stats['accuracy_percent']}%")
    print(f"   Stains Created: {stats['stains_created']}")


def example_2_all_tracers():
    """Example 2: Demonstrate all tracer types"""
    print_section("Example 2: All Tracer Types")

    gun = MarkerGun(name="Rainbow Marker")
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())

    # Load all ammo types
    tracers = {
        "RED": RedTracer(),
        "PURPLE": PurpleTracer(),
        "ORANGE": OrangeTracer(),
        "YELLOW": YellowTracer(),
        "BLUE": BlueTracer(),
        "WHITE": WhiteTracer(),
        "BLACK": BlackTracer(),
        "BROWN": BrownTracer(),
    }

    for color, tracer in tracers.items():
        gun.load_ammo(tracer)

    print("✅ Loaded all 8 tracer types\n")

    gun.arm()
    gun.safety_off()

    # Fire different colored tracers
    test_targets = [
        {"color": "RED", "target": {"file_hash": "abc123", "threat_score": 9.5, "confidence": 0.95}, "type": "Malware"},
        {
            "color": "PURPLE",
            "target": {"user_agent": "EvilBot", "threat_score": 8.0, "confidence": 0.88},
            "type": "Evil AI",
        },
        {
            "color": "ORANGE",
            "target": {"ip": "10.0.0.50", "threat_score": 7.5, "confidence": 0.82},
            "type": "Suspicious IP",
        },
        {
            "color": "YELLOW",
            "target": {"port": 4444, "cve": "CVE-2024-001", "threat_score": 9.0, "confidence": 0.90},
            "type": "Backdoor",
        },
        {
            "color": "BLUE",
            "target": {"service": "rogue-api", "risk_score": 6.5, "confidence": 0.75},
            "type": "Hidden Service",
        },
        {
            "color": "WHITE",
            "target": {"anomaly_id": "anom-001", "threat_score": 5.0, "confidence": 0.60},
            "type": "Unknown",
        },
        {
            "color": "BLACK",
            "target": {
                "crow_type": "trojan",
                "forest_location": {"tree": "web-01"},
                "threat_score": 8.7,
                "confidence": 0.89,
            },
            "type": "Crow",
        },
        {
            "color": "BROWN",
            "target": {"source_host": "ws-05", "dest_host": "srv-01", "threat_score": 8.5, "confidence": 0.85},
            "type": "Squirrel",
        },
    ]

    stain_count = {}

    for test in test_targets:
        gun.select_ammo(test["color"])
        result = gun.fire(test["target"])

        icon = "🔴🟣🟠🟡🔵⚪🖤🤎"[list(tracers.keys()).index(test["color"])]

        if result["hit"]:
            print(f"{icon} {test['color']:8} → {test['type']:20} [HIT] {result['stain']['tag_id']}")
            stain_count[test["color"]] = stain_count.get(test["color"], 0) + 1
        else:
            print(f"{icon} {test['color']:8} → {test['type']:20} [MISS]")

    print("\n📊 Stains by Color:")
    for color, count in stain_count.items():
        print(f"   {color}: {count}")


def example_3_weapon_modes():
    """Example 3: Compare weapon modes"""
    print_section("Example 3: Weapon Modes Comparison")

    gun = MarkerGun(name="Mode Tester")

    # Register all modes
    modes = {"PNEUMATIC": PneumaticMode(), "CO2_SILENT": CO2SilentMode(), "ELECTRIC": ElectricMode()}

    for mode_name, mode_obj in modes.items():
        gun.register_mode(WeaponMode[mode_name], mode_obj)

    gun.load_ammo(RedTracer())
    gun.arm()
    gun.safety_off()

    target = {"ip": "192.168.1.100", "threat_score": 8.0, "confidence": 0.85}

    print("Testing all weapon modes on same target:\n")

    for mode_name in modes.keys():
        gun.set_mode(WeaponMode[mode_name])
        result = gun.fire(target)

        if result["hit"]:
            mode_info = modes[mode_name].get_info()
            print(
                f"{'💨🧊⚡'[list(modes.keys()).index(mode_name)]} {mode_name:12} | "
                f"Noise: {mode_info['noise_level_db']:2} dB | "
                f"Power: {mode_info['power_level']}/10 | "
                f"Range: {mode_info['effective_range_m']:3}m | "
                f"Result: HIT"
            )
        else:
            print(f"  {mode_name:12} | Result: MISS")


def example_4_targeting_system():
    """Example 4: Targeting system usage"""
    print_section("Example 4: Targeting System")

    targeting = TargetingSystem()

    # Acquire multiple targets
    targets_data = [
        {"ip": "10.0.0.1", "threat_score": 9.5, "confidence": 0.95, "threat_type": "MALWARE"},
        {"ip": "10.0.0.2", "threat_score": 7.0, "confidence": 0.85, "threat_type": "SUSPICIOUS_IP"},
        {"ip": "10.0.0.3", "threat_score": 8.5, "confidence": 0.92, "threat_type": "BACKDOOR"},
        {"ip": "10.0.0.4", "threat_score": 5.0, "confidence": 0.60, "threat_type": "UNKNOWN"},
        {"ip": "10.0.0.5", "threat_score": 8.0, "confidence": 0.88, "threat_type": "CROW"},
    ]

    print("Acquiring targets...\n")

    targets = []
    for data in targets_data:
        target = targeting.acquire_target(data)
        targets.append(target)
        print(
            f"🎯 Target {target.target_id[:8]}: {target.ip} "
            f"(Score: {target.threat_score}, Conf: {target.confidence})"
        )

    # Validate targets
    print("\nValidating targets...\n")

    for target in targets:
        validation = targeting.validate_target(target)
        status = "✅ VALID" if validation["valid"] else "❌ INVALID"
        print(f"{status} {target.ip}")

        if not validation["valid"]:
            for reason in validation["reasons"]:
                print(f"   ⚠️ {reason}")

        if validation["warnings"]:
            for warning in validation["warnings"]:
                print(f"   ⚠️ {warning}")

    # Prioritize targets
    print("\nPrioritized targets:\n")

    prioritized = targeting.prioritize_targets()
    for i, target in enumerate(prioritized, 1):
        priority_score = target.threat_score * target.confidence
        print(
            f"{i}. {target.ip:15} | Score: {target.threat_score} | "
            f"Conf: {target.confidence} | Priority: {priority_score:.2f}"
        )

    # Get top target
    top_target = targeting.get_top_target()
    print(f"\n🎯 Top Priority: {top_target.ip}")

    # Recommendations
    print(f"\n💡 Recommendations for {top_target.ip}:")
    print(f"   Ammo: {targeting.recommend_ammo(top_target)}")
    print(f"   Mode: {targeting.recommend_weapon_mode(top_target)}")


def example_5_fire_control():
    """Example 5: Fire control system"""
    print_section("Example 5: Fire Control System")

    # Setup components
    gun = MarkerGun(name="Fire Control Demo")
    targeting = TargetingSystem()
    fire_control = FireControlSystem(gun, targeting)

    # Configure weapon
    gun.register_mode(WeaponMode.PNEUMATIC, PneumaticMode())
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
    gun.register_mode(WeaponMode.ELECTRIC, ElectricMode())

    gun.load_ammo(RedTracer())
    gun.load_ammo(OrangeTracer())
    gun.load_ammo(BlackTracer())

    print("✅ Fire control system initialized\n")

    # Prepare weapon
    fire_control.prepare_weapon(mode="CO2_SILENT", ammo="RED")
    print("✅ Weapon prepared: CO2_SILENT + RED tracer\n")

    # Acquire and engage targets
    targets_data = [
        {"ip": "10.0.0.10", "file_hash": "abc123", "threat_score": 9.0, "confidence": 0.92, "threat_type": "MALWARE"},
        {"ip": "10.0.0.20", "threat_score": 7.5, "confidence": 0.80, "threat_type": "SUSPICIOUS_IP"},
    ]

    for data in targets_data:
        target = targeting.acquire_target(data)
        print(f"🎯 Engaging: {target.ip}")

        result = fire_control.engage_target(target)

        if result.success and result.hit:
            print(f"   ✅ HIT - Stain ID: {result.stain_id}")
            print(f"   Mode: {result.mode_used}, Ammo: {result.ammo_used}")
        else:
            print(f"   ❌ {result.message}")
        print()

    # Statistics
    stats = fire_control.get_engagement_statistics()
    print("📊 Fire Control Statistics:")
    print(f"   Total Engagements: {stats['total_engagements']}")
    print(f"   Successful Hits: {stats['successful_hits']}")
    print(f"   Accuracy: {stats['accuracy_percent']}%")
    print(f"   By Mode: {stats['engagements_by_mode']}")
    print(f"   By Ammo: {stats['engagements_by_ammo']}")


def example_6_auto_fire():
    """Example 6: Auto-fire mode"""
    print_section("Example 6: Auto-Fire Mode")

    gun = MarkerGun(name="Auto Marker")
    targeting = TargetingSystem()
    fire_control = FireControlSystem(gun, targeting)

    # Setup
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
    gun.load_ammo(RedTracer())
    gun.load_ammo(OrangeTracer())

    fire_control.prepare_weapon("CO2_SILENT", "RED")

    # Enable auto-fire (90% confidence threshold)
    fire_control.enable_auto_fire(threshold=0.90)
    print("✅ Auto-fire ENABLED (threshold: 0.90)\n")

    # Acquire multiple targets
    targets_data = [
        {"ip": "10.0.0.1", "threat_score": 9.5, "confidence": 0.95, "threat_type": "MALWARE"},  # Will auto-fire
        {"ip": "10.0.0.2", "threat_score": 7.0, "confidence": 0.85, "threat_type": "SUSPICIOUS_IP"},  # Will NOT
        {"ip": "10.0.0.3", "threat_score": 9.0, "confidence": 0.92, "threat_type": "BACKDOOR"},  # Will auto-fire
        {"ip": "10.0.0.4", "threat_score": 6.0, "confidence": 0.75, "threat_type": "UNKNOWN"},  # Will NOT
    ]

    print("Acquiring targets:\n")
    for data in targets_data:
        target = targeting.acquire_target(data)
        auto = "🤖 AUTO" if data["confidence"] >= 0.90 else "👁️ OBSERVE"
        print(f"{auto} {target.ip} (Conf: {target.confidence})")

    # Auto-engage high-confidence targets
    print("\n🤖 Auto-firing at high-confidence targets...\n")

    results = fire_control.auto_engage()

    for result in results:
        if result.hit:
            print(f"✅ AUTO-HIT: {result.target_id[:8]} with {result.ammo_used}")
        else:
            print(f"❌ AUTO-MISS: {result.target_id[:8]}")

    print(f"\n📊 Auto-fire engaged {len(results)} targets")


def example_7_forest_integration():
    """Example 7: Forest integration (marking crows and squirrels)"""
    print_section("Example 7: Forest Integration")

    gun = MarkerGun(name="Forest Hunter")
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
    gun.load_ammo(BlackTracer())  # Crow marker
    gun.load_ammo(BrownTracer())  # Squirrel marker
    gun.arm()
    gun.safety_off()

    print("🌳 Patrolling forest for threats...\n")

    # Crow in canopy
    crow_target = {
        "crow_type": "trojan",
        "forest_location": {"tree": "web-server-01", "branch": "nginx-worker-3", "crown": "process-tree-suspicious"},
        "behavior": "patient_waiting",
        "hiding_method": "obfuscation",
        "threat_score": 8.7,
        "confidence": 0.89,
        "detected_by": "owl",
    }

    gun.select_ammo("BLACK")
    result = gun.fire(crow_target)

    if result["hit"]:
        print(f"🖤 CROW MARKED in {crow_target['forest_location']['tree']}")
        print(f"   Tag: {result['stain']['tag_id']}")
        print(f"   Location: {crow_target['forest_location']['branch']}")
        print(f"   Detected by: {crow_target['detected_by']}")

    print()

    # Squirrel (lateral movement)
    squirrel_target = {
        "source_host": "workstation-42",
        "dest_host": "domain-controller-01",
        "method": "pass-the-hash",
        "protocol": "SMB",
        "forest_location": {"source_tree": "workstation-42", "dest_tree": "dc-01"},
        "jump_count": 3,
        "threat_score": 8.5,
        "confidence": 0.87,
        "detected_by": "falcon",
    }

    gun.select_ammo("BROWN")
    result = gun.fire(squirrel_target)

    if result["hit"]:
        print("🤎 SQUIRREL MARKED jumping between trees")
        print(f"   Tag: {result['stain']['tag_id']}")
        print(f"   Path: {squirrel_target['source_host']} → {squirrel_target['dest_host']}")
        print(f"   Method: {squirrel_target['method']}")
        print(f"   Detected by: {squirrel_target['detected_by']}")


def example_8_stain_management():
    """Example 8: Stain management"""
    print_section("Example 8: Stain Management")

    gun = MarkerGun(name="Stain Tracker")
    gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
    gun.load_ammo(RedTracer())
    gun.load_ammo(OrangeTracer())
    gun.arm()
    gun.safety_off()

    # Create some stains
    targets = [
        {"ip": "10.0.0.1", "file_hash": "hash1", "threat_score": 9.0, "confidence": 0.90},
        {"ip": "10.0.0.2", "threat_score": 7.5, "confidence": 0.85},
        {"ip": "10.0.0.3", "file_hash": "hash3", "threat_score": 8.5, "confidence": 0.88},
    ]

    print("Creating stains...\n")

    stain_ids = []
    for i, target in enumerate(targets):
        ammo = "RED" if "file_hash" in target else "ORANGE"
        gun.select_ammo(ammo)
        result = gun.fire(target)

        if result["hit"]:
            stain_id = result["stain"]["tag_id"]
            stain_ids.append(stain_id)
            print(f"{i+1}. Created stain: {stain_id} ({ammo})")

    # Retrieve and analyze stains
    print(f"\n📋 All Stains ({len(stain_ids)}):\n")

    all_stains = gun.get_all_stains()
    for stain in all_stains:
        print(f"ID: {stain['tag_id']}")
        print(f"   Type: {stain['marker_type']}")
        print(f"   Target: {stain['target'].get('ip', 'N/A')}")
        print(f"   Score: {stain['stain']['threat_score']}")
        print()

    # Get stains by type
    malware_stains = gun.get_stains_by_type("MALWARE")
    ip_stains = gun.get_stains_by_type("SUSPICIOUS_IP")

    print("📊 Stains by Type:")
    print(f"   MALWARE: {len(malware_stains)}")
    print(f"   SUSPICIOUS_IP: {len(ip_stains)}")

    # Get specific stain
    if stain_ids:
        stain = gun.get_stain(stain_ids[0])
        print(f"\n🔍 Stain Details: {stain_ids[0]}")
        print(f"   Hit Count: {stain.hit_count}")
        print(f"   First Seen: {stain.timestamp_first_seen}")
        print(f"   Status: {stain.status}")


def main():
    """Run all examples"""
    print("\n" + "🔫" * 35)
    print("  WEAPONS MODULE - SILENT MARKER SYSTEM")
    print("  FALA 5 Examples")
    print("🔫" * 35)

    try:
        example_1_basic_weapon()
        example_2_all_tracers()
        example_3_weapon_modes()
        example_4_targeting_system()
        example_5_fire_control()
        example_6_auto_fire()
        example_7_forest_integration()
        example_8_stain_management()

        print_section("🎯 All Examples Complete!")
        print("Silent Marker System fully operational.")
        print("\n'Raz trafiony, zawsze widoczny' - Once hit, always visible\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
