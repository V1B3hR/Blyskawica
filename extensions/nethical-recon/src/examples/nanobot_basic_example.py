#!/usr/bin/env python3
"""
Nanobot Basic Example
Demonstrates the nanobot automated response system.

This example shows:
- Creating and configuring nanobots
- Using the swarm manager
- Rules engine and hybrid decisions
- Defensive and scout modes
- Adaptive learning
"""

import sys

# Add parent directory to path
sys.path.insert(0, "..")

from nanobots import (
    AlertNanobot,
    BaselineLearner,
    EnumeratorNanobot,
    ForestPatrolNanobot,
    HybridDecisionMaker,
    IPBlockerNanobot,
    # Core
    NanobotSwarm,
    RateLimiterNanobot,
    Rule,
    RuleCondition,
    RuleOperator,
    # Rules
    RulesEngine,
    SimpleMLAnomalyDetector,
    ThreatHunterNanobot,
)


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def example_1_basic_defensive():
    """Example 1: Basic defensive nanobots"""
    print_section("Example 1: Basic Defensive Nanobots")

    # Create swarm
    swarm = NanobotSwarm("defensive_swarm")

    # Create defensive nanobots
    ip_blocker = IPBlockerNanobot(
        nanobot_id="ip_blocker_1", config={"method": "simulation", "whitelist": ["10.0.0.0/8"], "max_blocks": 100}
    )

    rate_limiter = RateLimiterNanobot(
        nanobot_id="rate_limiter_1", config={"requests_per_minute": 60, "burst_threshold": 100}
    )

    alerter = AlertNanobot(nanobot_id="alerter_1", config={"min_level": "WARNING"})

    # Register nanobots
    swarm.register_nanobot(ip_blocker)
    swarm.register_nanobot(rate_limiter)
    swarm.register_nanobot(alerter)

    # Start swarm
    swarm.start_swarm()
    print("✅ Swarm started with 3 defensive nanobots")

    # Submit security event (port scan detected)
    print("\n📡 Submitting port scan event...")
    event = {
        "source_ip": "192.168.1.105",
        "port_scan_detected": True,
        "ports_scanned": 120,
        "threat_score": 8.5,
        "confidence": 0.92,
        "description": "Rapid port scan detected from external source",
    }

    results = swarm.process_event(event)

    print(f"\n🤖 Nanobot responses: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.action_type.value}: {result.status.value} (confidence: {result.confidence:.2f})")
        if result.details:
            print(f"     Details: {result.details}")

    # Get swarm status
    status = swarm.get_swarm_status()
    print("\n📊 Swarm Status:")
    print(f"  Active nanobots: {status['active_nanobots']}/{status['total_nanobots']}")
    print(f"  Events processed: {status['events_processed']}")
    print(f"  Actions taken: {status['actions_taken']}")

    # Get blocked IPs
    blocked = ip_blocker.get_blocked_ips()
    if blocked:
        print(f"\n🚫 Blocked IPs: {', '.join(blocked)}")

    # Stop swarm
    swarm.stop_swarm()
    print("\n✅ Swarm stopped")


def example_2_rules_engine():
    """Example 2: Using rules engine"""
    print_section("Example 2: Rules Engine")

    # Create rules engine
    engine = RulesEngine()
    print("✅ Rules engine created with default rules")

    # Add custom rule
    custom_rule = Rule(
        rule_id="block_aggressive_scanner",
        name="Block Aggressive Port Scanners",
        conditions=[
            RuleCondition("port_scan_detected", RuleOperator.EQUALS, True),
            RuleCondition("ports_scanned", RuleOperator.GREATER_THAN, 100),
        ],
        logic="AND",
        priority=95,
        action_type="block_ip",
        confidence_modifier=0.30,
    )

    engine.add_rule(custom_rule)
    print(f"✅ Added custom rule: {custom_rule.name}")

    # Test events
    events = [
        {"name": "Aggressive Port Scan", "port_scan_detected": True, "ports_scanned": 150, "confidence": 0.70},
        {"name": "Light Port Scan", "port_scan_detected": True, "ports_scanned": 10, "confidence": 0.60},
        {"name": "Brute Force", "brute_force_attempt": True, "failed_auth_attempts": 10, "confidence": 0.75},
    ]

    print("\n🧪 Testing events against rules:\n")
    for event in events:
        print(f"Event: {event['name']}")
        matches = engine.evaluate(event)

        if matches:
            print(f"  ✓ Matched {len(matches)} rule(s):")
            for match in matches[:3]:  # Show top 3
                print(f"    - {match['rule_name']} (priority: {match['priority']})")
                print(f"      Action: {match['action_type']}, Modifier: +{match['confidence_modifier']}")
        else:
            print("  ✗ No rules matched")

        # Get recommended action
        recommendation = engine.get_recommended_action(event, event["confidence"])
        if recommendation:
            print(f"  → Recommended: {recommendation['action_type']}")
            print(f"    Adjusted confidence: {recommendation['confidence']:.2f}")
        print()


def example_3_hybrid_decisions():
    """Example 3: Hybrid decision making"""
    print_section("Example 3: Hybrid Decision Making")

    # Create decision maker
    decision_maker = HybridDecisionMaker(config={"auto_fire_threshold": 0.90, "propose_threshold": 0.70})

    print("✅ Hybrid decision maker created")
    print(f"   Auto-fire: ≥{decision_maker.auto_fire_threshold:.0%}")
    print(f"   Propose: {decision_maker.propose_threshold:.0%}-{decision_maker.auto_fire_threshold:.0%}")
    print(f"   Observe: <{decision_maker.propose_threshold:.0%}")

    # Test scenarios with different confidence levels
    scenarios = [
        {
            "name": "High Confidence Attack",
            "base_confidence": 0.95,
            "event": {"source_ip": "192.168.1.105", "known_malicious": True, "threat_score": 9.5},
            "context": {"historical_threat_level": 0.9, "recent_incidents": 5},
        },
        {
            "name": "Medium Confidence Scan",
            "base_confidence": 0.75,
            "event": {"source_ip": "10.0.0.50", "port_scan_detected": True, "threat_score": 6.5},
            "context": {"historical_threat_level": 0.5, "is_off_hours": True},
        },
        {
            "name": "Low Confidence Activity",
            "base_confidence": 0.60,
            "event": {"source_ip": "10.0.0.100", "suspicious_pattern": True, "threat_score": 4.0},
            "context": {"source_reputation": 0.7},
        },
    ]

    print("\n🧪 Testing decision scenarios:\n")
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        print(f"  Base confidence: {scenario['base_confidence']:.2f}")

        decision = decision_maker.make_decision(scenario["base_confidence"], scenario["event"], scenario["context"])

        mode_emoji = {"auto_fire": "🤖", "propose": "💡", "observe": "👁️"}

        emoji = mode_emoji.get(decision["mode"], "❓")
        print(f"  {emoji} Decision: {decision['mode'].upper()}")
        print(f"  Adjusted confidence: {decision['adjusted_confidence']:.2f}")
        print(f"  Change: {decision['confidence_change']:+.2f}")
        print(f"  Reasoning: {decision['reasoning']}")
        print()


def example_4_scout_mode():
    """Example 4: Scout mode nanobots"""
    print_section("Example 4: Scout Mode Nanobots")

    # Create swarm
    swarm = NanobotSwarm("scout_swarm")

    # Create scout nanobots
    enumerator = EnumeratorNanobot(config={"max_concurrent": 3})

    forest_patrol = ForestPatrolNanobot(config={"patrol_interval": 60})

    threat_hunter = ThreatHunterNanobot(config={"hunt_types": ["crow", "magpie", "squirrel"]})

    # Register and start
    swarm.register_nanobot(enumerator)
    swarm.register_nanobot(forest_patrol)
    swarm.register_nanobot(threat_hunter)
    swarm.start_swarm()

    print("✅ Scout swarm started with 3 nanobots")

    # Event 1: New host discovered
    print("\n📡 Event 1: New host discovered")
    event1 = {"new_host_discovered": True, "target": "192.168.1.200", "confidence": 0.85}
    results1 = swarm.process_event(event1)
    print(f"  Actions: {len(results1)}")
    for result in results1:
        print(f"  - {result.action_type.value}: {result.details.get('target', 'N/A')}")

    # Event 2: Forest patrol request
    print("\n🌳 Event 2: Forest patrol")
    event2 = {"tree_id": "web-server-01", "tree_health": 65, "threats_in_crown": ["crow", "magpie"], "confidence": 0.80}
    results2 = swarm.process_event(event2)
    print(f"  Actions: {len(results2)}")
    for result in results2:
        if result.details.get("findings_count", 0) > 0:
            print(f"  - Found {result.details['findings_count']} issue(s) in tree")

    # Event 3: Threat hunt
    print("\n🎯 Event 3: Threat hunt")
    event3 = {
        "threat_type": "crow",
        "target": "web-server-01",
        "iocs": ["malware.exe", "backdoor.dll"],
        "suspicious_pattern": True,
        "confidence": 0.92,
    }
    results3 = swarm.process_event(event3)
    print(f"  Actions: {len(results3)}")
    for result in results3:
        if result.details.get("threats_found", 0) > 0:
            print(f"  - Caught {result.details['threats_found']} threat(s)")

    swarm.stop_swarm()
    print("\n✅ Scout swarm stopped")


def example_5_adaptive_learning():
    """Example 5: Adaptive learning"""
    print_section("Example 5: Adaptive Learning")

    # Example 5a: Baseline Learning
    print("📚 Baseline Learning\n")

    learner = BaselineLearner(config={"learning_period_days": 7, "min_samples": 50})

    # Record normal observations
    print("Recording normal request rate observations...")
    for i in range(100):
        # Simulate normal traffic: 40-60 requests/min
        value = 50 + (i % 10) - 5
        learner.record_observation("request_rate", value)

    baseline = learner.get_baseline("request_rate")
    if baseline:
        print("✅ Baseline established:")
        print(f"  Mean: {baseline['mean']:.1f}")
        print(f"  Std Dev: {baseline['stdev']:.1f}")
        print(f"  Range: {baseline['min']:.1f} - {baseline['max']:.1f}")

    # Test for anomalies
    print("\n🧪 Testing for anomalies:")
    test_values = [52, 75, 150, 45]

    for value in test_values:
        check = learner.is_anomalous("request_rate", value)
        status = "🔴 ANOMALY" if check["is_anomalous"] else "🟢 NORMAL"
        print(f"  {status} - Value: {value:.0f}, Z-score: {check['z_score']:.2f}")
        if check["is_anomalous"]:
            print(f"    Severity: {check['severity']}, Confidence: {check['confidence']:.2f}")

    # Example 5b: ML Anomaly Detection
    print("\n\n🤖 ML Anomaly Detection\n")

    detector = SimpleMLAnomalyDetector(
        config={"window_size": 50, "sensitivity": 0.75, "features": ["request_rate", "error_rate"]}
    )

    # Train on normal samples
    print("Training on normal samples...")
    normal_samples = []
    for i in range(100):
        normal_samples.append({"request_rate": 50 + (i % 10) - 5, "error_rate": 0.01 + (i % 5) * 0.001})

    detector.train(normal_samples)
    print(f"✅ Trained on {len(normal_samples)} samples")

    # Test predictions
    print("\n🧪 Testing predictions:")
    test_samples = [
        {"name": "Normal", "request_rate": 52, "error_rate": 0.012},
        {"name": "High Traffic", "request_rate": 150, "error_rate": 0.015},
        {"name": "High Errors", "request_rate": 55, "error_rate": 0.15},
        {"name": "Both High", "request_rate": 200, "error_rate": 0.20},
    ]

    for sample in test_samples:
        name = sample.pop("name")
        prediction = detector.predict(sample)

        status = "🔴 ANOMALY" if prediction["is_anomalous"] else "🟢 NORMAL"
        print(f"  {status} - {name}")
        print(f"    Confidence: {prediction['confidence']:.2f}")
        print(f"    Severity: {prediction['severity']}")
        if prediction["anomalous_features"]:
            print(f"    Anomalous features: {', '.join(prediction['anomalous_features'])}")


def example_6_full_integration():
    """Example 6: Full system integration"""
    print_section("Example 6: Full System Integration")

    # Create all components
    swarm = NanobotSwarm("integrated_swarm")
    rules = RulesEngine()
    decision_maker = HybridDecisionMaker()
    learner = BaselineLearner()

    # Register all types of nanobots
    swarm.register_nanobot(IPBlockerNanobot())
    swarm.register_nanobot(RateLimiterNanobot())
    swarm.register_nanobot(AlertNanobot())
    swarm.register_nanobot(EnumeratorNanobot())
    swarm.register_nanobot(ThreatHunterNanobot())

    swarm.start_swarm()

    print("✅ Integrated system started")
    print(f"  Nanobots: {swarm.get_swarm_status()['total_nanobots']}")
    print(f"  Rules: {len(rules.get_all_rules())}")

    # Simulate security event pipeline
    print("\n📡 Simulating security event pipeline...\n")

    event = {
        "source_ip": "192.168.1.105",
        "port_scan_detected": True,
        "ports_scanned": 150,
        "threat_score": 8.5,
        "confidence": 0.82,
    }

    # Step 1: Rules evaluation
    print("1️⃣ Rules Engine Evaluation")
    recommendation = rules.get_recommended_action(event, event["confidence"])
    if recommendation:
        print(f"  Recommended: {recommendation['action_type']}")
        print(f"  Adjusted confidence: {recommendation['confidence']:.2f}")
        event["confidence"] = recommendation["confidence"]

    # Step 2: Hybrid decision
    print("\n2️⃣ Hybrid Decision Making")
    decision = decision_maker.make_decision(event["confidence"], event, context={"is_off_hours": True})
    print(f"  Mode: {decision['mode']}")
    print(f"  Confidence: {decision['adjusted_confidence']:.2f}")
    print(f"  Should act: {decision['should_act']}")

    # Step 3: Nanobot action
    if decision["should_act"]:
        print("\n3️⃣ Nanobot Response")
        results = swarm.process_event(event)
        print(f"  Actions taken: {len(results)}")
        for result in results:
            print(f"  - {result.action_type.value}: {result.status.value}")

    # Step 4: Learning
    print("\n4️⃣ Adaptive Learning")
    learner.record_observation("threat_score", event["threat_score"])
    print(f"  Recorded observation: threat_score={event['threat_score']}")

    # Final statistics
    print("\n📊 Final Statistics:")
    status = swarm.get_swarm_status()
    print(f"  Events processed: {status['events_processed']}")
    print(f"  Actions taken: {status['actions_taken']}")
    print(f"  Success rate: {status['actions_taken']/max(status['events_processed'], 1)*100:.1f}%")

    swarm.stop_swarm()
    print("\n✅ System stopped")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("  🤖 NANOBOTS - AUTOMATED RESPONSE SYSTEM")
    print("  Examples Demonstration")
    print("=" * 60)

    examples = [
        ("Basic Defensive Nanobots", example_1_basic_defensive),
        ("Rules Engine", example_2_rules_engine),
        ("Hybrid Decision Making", example_3_hybrid_decisions),
        ("Scout Mode", example_4_scout_mode),
        ("Adaptive Learning", example_5_adaptive_learning),
        ("Full Integration", example_6_full_integration),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback

            traceback.print_exc()

        if i < len(examples):
            print("\n" + "-" * 60)
            input("Press Enter to continue to next example...")

    print("\n" + "=" * 60)
    print("  ✅ All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
