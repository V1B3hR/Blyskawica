# 🤖 Nanoboty - Automated Response System

> *"Niewidoczna chmura przy czujnikach - gotowa do natychmiastowej reakcji"*  
> *"Invisible cloud near sensors - ready for immediate response"*

## Overview

The Nanobots system is an automated response framework that acts like an immune system for your infrastructure. Just as antibodies respond to threats in the human body, nanobots autonomously detect and respond to security threats in your network.

### Key Features

- **🛡️ Defensive Mode**: Auto-block IPs, rate limiting, honeypot deployment
- **🔍 Scout Mode**: Auto-enumeration, evidence gathering, lateral movement tracking
- **🧬 Adaptive Mode**: Machine learning-based anomaly detection, baseline learning
- **🌳 Forest Guard Mode**: Tree patrol, threat hunting in forest canopies

### Hybrid Decision System

```
CONFIDENCE LEVEL          ACTION
═══════════════════════════════════════════════════
≥ 90%                     🤖 AUTO-FIRE (autonomous action)
70-89%                    💡 PROPOSE (suggest to hunter)  
< 70%                     👁️  OBSERVE (monitor only)
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  NANOBOT SWARM                          │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Defensive  │  │   Scout    │  │  Adaptive  │       │
│  │  Nanobots  │  │  Nanobots  │  │  Nanobots  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         │                │                │            │
│         └────────────────┴────────────────┘            │
│                          │                             │
│                  ┌───────▼────────┐                    │
│                  │  Rules Engine  │                    │
│                  │  Hybrid Mode   │                    │
│                  └────────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## Installation

Nanobots are included with Nethical Recon:

```bash
cd nethical-recon
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from nanobots import NanobotSwarm, IPBlockerNanobot, AlertNanobot

# Create swarm
swarm = NanobotSwarm("security_swarm")

# Register nanobots
ip_blocker = IPBlockerNanobot(config={'method': 'simulation'})
alerter = AlertNanobot()

swarm.register_nanobot(ip_blocker)
swarm.register_nanobot(alerter)

# Start swarm
swarm.start_swarm()

# Submit security event
event = {
    'source_ip': '192.168.1.105',
    'port_scan_detected': True,
    'ports_scanned': 100,
    'threat_score': 8.5,
    'confidence': 0.85
}

swarm.submit_event(event)

# Get results
status = swarm.get_swarm_status()
print(f"Events processed: {status['events_processed']}")
print(f"Actions taken: {status['actions_taken']}")

# Stop swarm
swarm.stop_swarm()
```

### With Rules Engine

```python
from nanobots import NanobotSwarm, RulesEngine, HybridDecisionMaker
from nanobots import IPBlockerNanobot, RateLimiterNanobot

# Create components
swarm = NanobotSwarm()
rules = RulesEngine()
decision_maker = HybridDecisionMaker()

# Register nanobots
swarm.register_nanobot(IPBlockerNanobot())
swarm.register_nanobot(RateLimiterNanobot())
swarm.start_swarm()

# Process event with rules
event = {
    'source_ip': '10.0.0.50',
    'brute_force_attempt': True,
    'failed_auth_attempts': 10,
    'confidence': 0.75
}

# Get recommended action from rules
recommendation = rules.get_recommended_action(event, event['confidence'])

if recommendation:
    # Make hybrid decision
    decision = decision_maker.make_decision(
        recommendation['confidence'],
        event
    )
    
    print(f"Mode: {decision['mode']}")
    print(f"Confidence: {decision['adjusted_confidence']:.2f}")
    print(f"Reasoning: {decision['reasoning']}")
    
    if decision['should_act']:
        swarm.submit_event(event)
```

## Nanobot Modes

### 🛡️ Defensive Mode

Defensive nanobots act as antibodies, protecting infrastructure from threats.

#### IP Blocker Nanobot

Automatically blocks suspicious IP addresses.

```python
from nanobots import IPBlockerNanobot

blocker = IPBlockerNanobot(config={
    'method': 'simulation',  # or 'iptables', 'pf'
    'whitelist': ['10.0.0.0/8'],
    'max_blocks': 1000
})

# Process event
event = {
    'source_ip': '192.168.1.105',
    'known_malicious': True,
    'threat_score': 9.5,
    'confidence': 0.95
}

result = blocker.process_event(event)
print(f"Action: {result.action_type.value}")
print(f"Status: {result.status.value}")
```

#### Rate Limiter Nanobot

Applies rate limiting to high-traffic sources.

```python
from nanobots import RateLimiterNanobot

limiter = RateLimiterNanobot(config={
    'requests_per_minute': 60,
    'burst_threshold': 100,
    'time_window': 60
})

# Check if source is rate limited
if limiter.is_rate_limited('192.168.1.100'):
    print("Source is rate limited")
```

#### Honeypot Nanobot

Deploys decoy services to trap attackers.

```python
from nanobots import HoneypotNanobot

honeypot = HoneypotNanobot(config={
    'max_honeypots': 10,
    'honeypot_types': ['ssh', 'http', 'ftp']
})

# Deploy honeypot on reconnaissance
event = {
    'recon_activity': True,
    'ports_scanned': [22, 80, 443, 3306],
    'confidence': 0.80
}

result = honeypot.process_event(event)
```

#### Alert Nanobot

Escalates alerts to hunters and monitoring systems.

```python
from nanobots import AlertNanobot, AlertLevel

alerter = AlertNanobot(config={
    'alert_channels': ['log', 'email', 'slack'],
    'min_level': 'WARNING'
})

# Get recent alerts
alerts = alerter.get_active_alerts(level=AlertLevel.CRITICAL)
```

### 🔍 Scout Mode

Scout nanobots perform reconnaissance and intelligence gathering.

#### Enumerator Nanobot

Automatically enumerates discovered hosts and services.

```python
from nanobots import EnumeratorNanobot

enumerator = EnumeratorNanobot(config={
    'max_concurrent': 5,
    'enum_types': ['port_scan', 'service_detection']
})

# Auto-enumerate new host
event = {
    'new_host_discovered': True,
    'target': '192.168.1.200',
    'confidence': 0.85
}

result = enumerator.process_event(event)
```

#### Forest Patrol Nanobot

Patrols forest trees looking for threats.

```python
from nanobots import ForestPatrolNanobot

patrol = ForestPatrolNanobot(config={
    'patrol_interval': 60,
    'max_trees': 100
})

# Patrol tree
event = {
    'tree_id': 'web-server-01',
    'tree_health': 65,
    'threats_in_crown': ['crow'],
    'confidence': 0.75
}

result = patrol.process_event(event)
```

#### Threat Hunter Nanobot

Actively hunts for threats in the forest.

```python
from nanobots import ThreatHunterNanobot

hunter = ThreatHunterNanobot(config={
    'hunt_types': ['crow', 'magpie', 'squirrel'],
    'aggressive': False
})

# Hunt threat
event = {
    'threat_type': 'crow',
    'target': 'web-server-01',
    'iocs': ['malicious.exe', 'suspicious.dll'],
    'confidence': 0.90
}

result = hunter.process_event(event)
```

### 🧬 Adaptive Mode

Adaptive nanobots learn patterns and detect anomalies.

#### Baseline Learner

Learns normal behavior patterns to identify anomalies.

```python
from nanobots import BaselineLearner

learner = BaselineLearner(config={
    'learning_period_days': 7,
    'min_samples': 100
})

# Record observations
for i in range(200):
    learner.record_observation('request_rate', 50 + (i % 20))

# Check for anomaly
anomaly_check = learner.is_anomalous('request_rate', 150)
if anomaly_check['is_anomalous']:
    print(f"Anomaly detected! Confidence: {anomaly_check['confidence']:.2f}")
    print(f"Severity: {anomaly_check['severity']}")
```

#### ML Anomaly Detector

Uses machine learning for anomaly detection.

```python
from nanobots import SimpleMLAnomalyDetector

detector = SimpleMLAnomalyDetector(config={
    'window_size': 100,
    'sensitivity': 0.8,
    'features': ['request_rate', 'error_rate']
})

# Train on normal samples
normal_samples = [
    {'request_rate': 50, 'error_rate': 0.01},
    {'request_rate': 55, 'error_rate': 0.02},
    # ... more samples
]
detector.train(normal_samples)

# Predict on new sample
sample = {'request_rate': 500, 'error_rate': 0.15}
prediction = detector.predict(sample)

if prediction['is_anomalous']:
    print(f"Anomaly! Confidence: {prediction['confidence']:.2f}")
    print(f"Anomalous features: {prediction['anomalous_features']}")
```

## Rules Engine

The rules engine evaluates conditions and recommends actions.

### Creating Rules

```python
from nanobots import RulesEngine, Rule, RuleCondition, RuleOperator

engine = RulesEngine()

# Create custom rule
rule = Rule(
    rule_id="block_scanner",
    name="Block Port Scanners",
    conditions=[
        RuleCondition("port_scan_detected", RuleOperator.EQUALS, True),
        RuleCondition("ports_scanned", RuleOperator.GREATER_THAN, 20)
    ],
    logic="AND",
    priority=90,
    action_type="block_ip",
    confidence_modifier=0.25
)

engine.add_rule(rule)

# Evaluate event
event = {
    'port_scan_detected': True,
    'ports_scanned': 50
}

matches = engine.evaluate(event)
for match in matches:
    print(f"Rule matched: {match['rule_name']}")
```

### Rule Operators

- `EQUALS`: Field equals value
- `NOT_EQUALS`: Field does not equal value
- `GREATER_THAN`: Field greater than value
- `LESS_THAN`: Field less than value
- `GREATER_EQUAL`: Field greater than or equal to value
- `LESS_EQUAL`: Field less than or equal to value
- `CONTAINS`: Value in field (for strings/lists)
- `NOT_CONTAINS`: Value not in field
- `IN`: Field in value (for checking membership)
- `NOT_IN`: Field not in value

## Hybrid Decision Mode

The hybrid decision maker combines rules, confidence, and context.

```python
from nanobots import HybridDecisionMaker

decision_maker = HybridDecisionMaker(config={
    'auto_fire_threshold': 0.90,
    'propose_threshold': 0.70
})

# Make decision with context
decision = decision_maker.make_decision(
    base_confidence=0.80,
    event={
        'source_ip': '192.168.1.105',
        'threat_score': 7.5
    },
    context={
        'historical_threat_level': 0.8,
        'recent_incidents': 3,
        'is_off_hours': True
    }
)

print(f"Mode: {decision['mode']}")
print(f"Adjusted confidence: {decision['adjusted_confidence']:.2f}")
print(f"Reasoning: {decision['reasoning']}")
```

## Swarm Management

### Activating/Deactivating Modes

```python
from nanobots import NanobotSwarm, NanobotMode

swarm = NanobotSwarm()

# Activate only defensive nanobots
swarm.activate_mode(NanobotMode.DEFENSIVE)

# Deactivate scout mode
swarm.deactivate_mode(NanobotMode.SCOUT)
```

### Getting Statistics

```python
# Swarm status
status = swarm.get_swarm_status()
print(f"Active nanobots: {status['active_nanobots']}")
print(f"Events processed: {status['events_processed']}")

# Detailed statistics
stats = swarm.get_statistics()
for nanobot_id, nanobot_stats in stats['nanobots'].items():
    print(f"{nanobot_id}: {nanobot_stats['success_rate']:.2%}")

# Recent actions
recent = swarm.get_recent_actions(limit=10)
```

## Configuration

### Nanobot Configuration

Each nanobot accepts a configuration dictionary:

```python
config = {
    # Common options
    'auto_fire_threshold': 0.90,
    'propose_threshold': 0.70,
    
    # IP Blocker specific
    'method': 'simulation',  # or 'iptables', 'pf'
    'whitelist': ['10.0.0.0/8'],
    'max_blocks': 1000,
    
    # Rate Limiter specific
    'requests_per_minute': 60,
    'burst_threshold': 100,
    
    # Honeypot specific
    'max_honeypots': 10,
    'honeypot_types': ['ssh', 'http'],
    
    # Enumerator specific
    'max_concurrent': 5,
    'enum_types': ['port_scan', 'service_detection']
}
```

## Event Schema

Events submitted to nanobots should follow this schema:

```python
event = {
    # Source information
    'source_ip': '192.168.1.105',
    'source': 'external_scanner',
    
    # Threat indicators
    'threat_score': 8.5,  # 0-10 scale
    'confidence': 0.85,   # 0-1 scale
    'known_malicious': True,
    
    # Attack types
    'port_scan_detected': True,
    'brute_force_attempt': False,
    'recon_activity': True,
    
    # Details
    'ports_scanned': [22, 80, 443],
    'failed_auth_attempts': 5,
    'iocs': ['malware.exe'],
    
    # Forest-specific
    'tree_id': 'web-server-01',
    'branch_id': 'nginx-worker',
    'threat_type': 'crow',
    
    # Context
    'timestamp': '2025-12-15T20:00:00Z',
    'description': 'Port scan detected'
}
```

## Integration with Other Modules

### With Sensors (Fala 1)

```python
from sensors import PortScanDetector
from nanobots import NanobotSwarm, IPBlockerNanobot

# Create components
sensor = PortScanDetector()
swarm = NanobotSwarm()
swarm.register_nanobot(IPBlockerNanobot())
swarm.start_swarm()

# Sensor detects port scan → Submit to swarm
def on_sensor_alert(alert):
    event = {
        'source_ip': alert['source'],
        'port_scan_detected': True,
        'threat_score': alert['severity_score'],
        'confidence': 0.85
    }
    swarm.submit_event(event)

# Connect sensor to swarm
sensor.register_callback(on_sensor_alert)
sensor.start()
```

### With Forest (Fala 3)

```python
from forest import ForestManager, ThreatDetector
from nanobots import NanobotSwarm, ThreatHunterNanobot

forest = ForestManager()
swarm = NanobotSwarm()
swarm.register_nanobot(ThreatHunterNanobot())
swarm.start_swarm()

# Threat detected in forest → Hunt with nanobots
threat = forest.threat_detector.detect_crow(
    threat_id="crow-001",
    name="Suspicious Process",
    malware_family="Trojan"
)

event = {
    'threat_type': 'crow',
    'tree_id': 'web-server-01',
    'threat_indicator': threat.threat_id,
    'confidence': 0.90
}

swarm.submit_event(event)
```

## Best Practices

### 1. Start with Simulation Mode

Always test in simulation mode before production:

```python
config = {'method': 'simulation'}
blocker = IPBlockerNanobot(config=config)
```

### 2. Use Appropriate Thresholds

Adjust confidence thresholds based on your risk tolerance:

```python
# Conservative (fewer false positives)
config = {
    'auto_fire_threshold': 0.95,
    'propose_threshold': 0.80
}

# Aggressive (faster response)
config = {
    'auto_fire_threshold': 0.85,
    'propose_threshold': 0.65
}
```

### 3. Monitor Nanobot Performance

Regularly check nanobot statistics:

```python
stats = swarm.get_statistics()
for nanobot_id, nanobot_stats in stats['nanobots'].items():
    success_rate = nanobot_stats['success_rate']
    if success_rate < 0.8:
        print(f"Warning: {nanobot_id} has low success rate")
```

### 4. Use Rules for Consistency

Define rules for common scenarios:

```python
# Always block known malicious IPs
rule = Rule(
    rule_id="block_known_malicious",
    conditions=[
        RuleCondition("known_malicious", RuleOperator.EQUALS, True)
    ],
    action_type="block_ip",
    confidence_modifier=0.3
)
```

### 5. Learn from Feedback

Use adaptive learning to improve over time:

```python
detector = SimpleMLAnomalyDetector()
# Train on normal behavior
detector.train(normal_samples)

# Learn from feedback
prediction = detector.predict(sample)
actual_anomaly = verify_with_hunter(sample)
detector.learn_from_feedback(sample, actual_anomaly)
```

## Security Considerations

⚠️ **Important Security Notes**:

1. **Whitelist Critical IPs**: Always whitelist management IPs
2. **Test in Simulation**: Test thoroughly before production use
3. **Monitor Actions**: Review nanobot actions regularly
4. **Rate Limiting**: Be cautious with aggressive blocking
5. **Access Control**: Restrict nanobot management access
6. **Logging**: Enable comprehensive logging
7. **Backup Rules**: Keep backup of firewall rules

## Troubleshooting

### Nanobots Not Acting

```python
# Check if nanobot is active
if not nanobot.is_active:
    nanobot.activate()

# Check confidence threshold
decision = decision_maker.make_decision(...)
if decision['should_observe']:
    print("Confidence too low for action")
```

### Too Many False Positives

```python
# Increase thresholds
decision_maker.update_thresholds(
    auto_fire=0.95,
    propose=0.80
)

# Adjust rule sensitivity
rule.confidence_modifier = 0.1  # Lower boost
```

### Performance Issues

```python
# Limit concurrent operations
config = {
    'max_concurrent': 3,  # Reduce from 5
    'max_blocks': 500     # Reduce from 1000
}

# Clear old data
swarm.clear_all_history()
```

## API Reference

See individual nanobot classes for detailed API documentation:

- `BaseNanobot`: Base class for all nanobots
- `NanobotSwarm`: Swarm manager
- `IPBlockerNanobot`: IP blocking
- `RateLimiterNanobot`: Rate limiting
- `HoneypotNanobot`: Honeypot deployment
- `AlertNanobot`: Alert escalation
- `EnumeratorNanobot`: Auto-enumeration
- `ForestPatrolNanobot`: Forest patrol
- `ThreatHunterNanobot`: Threat hunting
- `RulesEngine`: Rules evaluation
- `HybridDecisionMaker`: Hybrid decisions
- `BaselineLearner`: Baseline learning
- `SimpleMLAnomalyDetector`: ML anomaly detection

## Examples

See `examples/nanobot_basic_example.py` for complete working examples.

## Contributing

When adding new nanobots:

1. Extend `BaseNanobot`
2. Implement `can_handle()`, `assess_threat()`, `execute_action()`
3. Add to appropriate mode (defensive, scout, adaptive, forest_guard)
4. Document configuration options
5. Add tests
6. Update this README

## License

Part of Nethical Recon - See main project LICENSE.

## Version

Nanobots Module v1.0.0

---

**Status**: ✅ FALA 4 COMPLETE

*"Like antibodies in the immune system, nanobots protect your infrastructure autonomously."*
