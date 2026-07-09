# 🌳 Forest Module - Infrastructure as Trees

## Overview

The **Forest Module** is Wave 3 (FALA 3) of the Nethical Recon project. It provides a hierarchical infrastructure mapping system where:

- **🌲 Forest** = Entire infrastructure
- **🌳 Tree** = Individual host/server  
- **🪵 Trunk** = Operating system/kernel
- **👑 Crown** = Monitoring and overview
- **🌿 Branch** = Process/service/connection
- **🍃 Leaf** = Thread/session/packet

## Threat Detection System

The Forest module includes a comprehensive threat detection system with six threat types:

### 🐦‍⬛ Crow (Kruk) - Malware
Patient malware lurking in the canopy, waiting for the perfect moment to strike.

**Characteristics:**
- Hides in shadows (obfuscation)
- Intelligent, learns environment
- Command & control communication
- Data exfiltration capabilities

### 🐦 Magpie (Sroka) - Data Stealer
Quick data thief attracted to "shiny" valuable data.

**Characteristics:**
- Targets credentials, PII, financial data
- Fast grab and escape tactics
- Exfiltrates to external destinations
- Hoards stolen treasures

### 🐿️ Squirrel (Wiewiórka) - Lateral Movement
Jumps between branches, spreading across the infrastructure.

**Characteristics:**
- Host-to-host hopping
- Seeks vulnerable services
- Establishes persistence
- Uses stolen credentials

### 🐍 Snake (Wąż) - Rootkit
Climbs the trunk to gain deep system access.

**Characteristics:**
- Privilege escalation
- Kernel-level hiding
- Hides processes, files, connections
- Silent and deadly

### 🐛 Parasite (Pasożyt) - Cryptominer
Drains system resources for cryptocurrency mining.

**Characteristics:**
- CPU/GPU resource drain
- Slowly weakens host
- Financial impact
- Difficult to detect without monitoring

### 🦇 Bat (Nietoperz) - Night Attack
Active during off-hours when monitoring is reduced.

**Characteristics:**
- Night-time/weekend activity
- Exploits reduced vigilance
- Reconnaissance in darkness
- Off-hours attacks

## Architecture

```
ForestManager
    ├── ForestMap (topology mapping)
    ├── ThreatDetector (threat detection)
    ├── HealthChecker (health monitoring)
    └── Trees
        ├── Tree (host/server)
        │   ├── Trunk (OS/kernel)
        │   ├── Crown (overview)
        │   └── Branches (processes)
        │       └── Leaves (threads)
        └── Threats
            ├── Crow
            ├── Magpie
            ├── Squirrel
            ├── Snake
            ├── Parasite
            └── Bat
```

## Installation

```bash
# The forest module is part of nethical-recon
cd /path/to/nethical-recon

# No additional dependencies required for basic functionality
# Optional: psutil for enhanced system monitoring
pip install psutil
```

## Quick Start

### Basic Forest Creation

```python
from forest import ForestManager, Tree, Trunk, Branch, BranchType

# Create forest manager
manager = ForestManager("Production Infrastructure")

# Create a tree (host)
tree = Tree(
    tree_id="tree-001",
    hostname="web-server-01",
    ip_address="192.168.1.100",
    os_type="Ubuntu 22.04"
)

# Add trunk (OS core)
trunk = Trunk(
    trunk_id="trunk-001",
    os_name="Ubuntu",
    os_version="22.04",
    kernel_version="5.15.0-91"
)
tree.set_trunk(trunk)

# Add branch (process)
branch = Branch(
    branch_id="branch-001",
    name="nginx",
    branch_type=BranchType.SERVICE,
    metadata={'port': 80, 'protocol': 'TCP'}
)
tree.add_branch(branch)

# Add tree to forest
manager.add_tree(tree)

# Get forest status
print(manager.get_visual_overview())
```

### Threat Detection

```python
from forest import ForestManager, ThreatSeverity

# Detect a Crow (malware) threat
crow = manager.threat_detector.detect_crow(
    threat_id="crow-001",
    name="Suspicious Process",
    malware_family="Trojan",
    severity=ThreatSeverity.HIGH,
    metadata={'c2_server': '192.168.1.200'}
)

# Attach threat to tree
manager.detect_threat(crow, tree_id="tree-001", branch_id="branch-001")

# Detect lateral movement (Squirrel)
squirrel = manager.threat_detector.detect_squirrel(
    threat_id="sqr-001",
    name="Lateral Movement Attempt",
    technique="Pass-the-Hash"
)

# Track movement path
squirrel.add_movement("tree-001", "tree-002")
squirrel.add_movement("tree-002", "tree-003")

# Get threat summary
print(manager.threat_detector.get_threat_summary())
```

### Health Monitoring

```python
from forest import HealthChecker

# Create health checker
health_checker = HealthChecker()

# Update tree statistics
tree.update_statistics(cpu=75.0, memory=60.0, disk=45.0)

# Perform health check
result = health_checker.check_component(tree)
print(f"Health: {result['health_score']:.1f}%, Grade: {result['health_grade']}")

# Check all trees
all_trees = manager.get_all_trees()
summary = health_checker.get_health_summary(all_trees)
print(f"Average health: {summary['average_health']:.1f}%")
```

## Tree Hierarchy

### Tree Components

#### Tree (Host/Server)
Represents a physical or virtual server in your infrastructure.

```python
tree = Tree(
    tree_id="unique-id",
    hostname="server-name",
    ip_address="192.168.1.100",
    os_type="Linux"
)
```

**Attributes:**
- `hostname`: Server hostname
- `ip_address`: IP address
- `os_type`: Operating system
- `branches`: Dictionary of processes/services
- `health_score`: 0-100 health score
- `threats`: List of detected threats

#### Trunk (OS/Kernel)
Represents the core operating system.

```python
trunk = Trunk(
    trunk_id="trunk-id",
    os_name="Ubuntu",
    os_version="22.04",
    kernel_version="5.15.0-91"
)
tree.set_trunk(trunk)
```

#### Crown (Overview)
Provides monitoring and observational data.

```python
from forest.trees import Crown

crown = Crown(
    crown_id="crown-id",
    tree_hostname="web-server-01"
)
crown.add_observation("High CPU usage detected", severity="WARNING")
tree.set_crown(crown)
```

#### Branch (Process/Service)
Represents a process, service, or network connection.

```python
# Process branch
process = Branch(
    branch_id="proc-001",
    name="nginx",
    branch_type=BranchType.PROCESS,
    metadata={'pid': 1234, 'user': 'www-data'}
)

# Service branch
service = Branch(
    branch_id="svc-001",
    name="postgresql",
    branch_type=BranchType.SERVICE,
    metadata={'port': 5432, 'protocol': 'TCP'}
)

# Connection branch
connection = Branch(
    branch_id="conn-001",
    name="outbound-connection",
    branch_type=BranchType.CONNECTION,
    metadata={'remote_ip': '8.8.8.8', 'remote_port': 443}
)

tree.add_branch(process)
```

#### Leaf (Thread/Session)
Represents the smallest unit - threads, sessions, or packets.

```python
from forest.trees import Leaf, LeafType

# Thread leaf
thread = Leaf(
    leaf_id="leaf-001",
    name="worker-thread",
    leaf_type=LeafType.THREAD,
    metadata={'thread_id': 12345}
)

branch.add_leaf(thread)
```

## Threat Detection Examples

### Detecting a Crow (Malware)

```python
# Detect malware
crow = manager.threat_detector.detect_crow(
    threat_id="crow-malware-001",
    name="Ransomware.Cryptolocker",
    malware_family="Ransomware",
    severity=ThreatSeverity.CRITICAL
)

# Set C&C server
crow.set_c2_server("evil.example.com")

# Mark as dormant
crow.mark_dormant()

# Detect exfiltration
crow.mark_active_exfiltration()

# Attach to tree
manager.detect_threat(crow, "tree-001", "branch-003")
```

### Detecting a Magpie (Data Stealer)

```python
# Detect data stealer
magpie = manager.threat_detector.detect_magpie(
    threat_id="mag-001",
    name="Data Exfiltrator",
    target_data_types=["credentials", "PII", "credit_cards"]
)

# Track stolen data
magpie.add_stolen_item("credentials", size_bytes=1024)
magpie.add_stolen_item("PII", size_bytes=5120)

# Add exfiltration destination
magpie.add_exfiltration_destination("185.220.101.50")

manager.detect_threat(magpie, "tree-002", "branch-005")
```

### Detecting a Snake (Rootkit)

```python
# Detect rootkit
snake = manager.threat_detector.detect_snake(
    threat_id="snake-001",
    name="LD_PRELOAD Rootkit",
    rootkit_type="userland",
    severity=ThreatSeverity.CRITICAL
)

# Track hidden artifacts
snake.add_hidden_process("backdoor", 9999)
snake.add_hidden_file("/tmp/.hidden")
snake.add_hidden_network("0.0.0.0:31337")

# Privilege escalation
snake.escalate_privilege("root")

manager.detect_threat(snake, "tree-001")
```

## Forest Map

The `ForestMap` provides a complete topology view:

```python
from forest.trees import ForestMap

# Create map
forest_map = ForestMap("Production Network")

# Add trees
forest_map.add_tree(tree1)
forest_map.add_tree(tree2)
forest_map.add_tree(tree3)

# Define network segments
forest_map.add_network_segment("DMZ", ["tree-001", "tree-002"])
forest_map.add_network_segment("Internal", ["tree-003", "tree-004"])

# Define relationships
forest_map.add_tree_relationship("tree-001", "tree-003")

# Get summary
summary = forest_map.get_forest_summary()
print(f"Trees: {summary['total_trees']}")
print(f"Threats: {summary['total_threats']}")

# Get threat map
threat_map = forest_map.get_threat_map()
for tree_id, threats in threat_map.items():
    print(f"Tree {tree_id}: {threats['direct_threats']} threats")

# Visual representation
print(forest_map.get_visual_map())
```

## Health Scoring

Health scores are automatically calculated based on:

1. **Resource Usage** (up to -45 points)
   - CPU > 90%: -20 points
   - Memory > 90%: -20 points
   - Disk > 95%: -15 points

2. **Threats** (up to -30 points)
   - 10 points per direct threat (max 30)
   - 5 points per threatened branch

3. **Status Mapping**
   - 80-100: HEALTHY
   - 60-79: WARNING
   - 30-59: CRITICAL
   - 0-29: COMPROMISED

## API Reference

### ForestManager

```python
manager = ForestManager(forest_name="Infrastructure")

# Tree management
manager.add_tree(tree)
manager.remove_tree(tree_id)
manager.get_tree(tree_id)
manager.get_tree_by_hostname(hostname)
manager.get_tree_by_ip(ip_address)
manager.get_all_trees()

# Threat detection
manager.detect_threat(threat, tree_id, branch_id=None, leaf_id=None)
manager.threat_detector.detect_crow(...)
manager.threat_detector.detect_magpie(...)
manager.threat_detector.detect_squirrel(...)
manager.threat_detector.detect_snake(...)
manager.threat_detector.detect_parasite(...)
manager.threat_detector.detect_bat(...)

# Scanning
scan_results = manager.scan_forest()
status = manager.get_forest_status()
overview = manager.get_visual_overview()
```

### ThreatDetector

```python
detector = ThreatDetector()

# Get threats
all_threats = detector.get_all_threats()
active = detector.get_active_threats()
critical = detector.get_critical_threats()
by_type = detector.get_threats_by_type(ThreatType.CROW)

# Threat summary
summary = detector.get_threat_summary()
# Returns: {'total_threats', 'active_threats', 'by_type', 'by_severity', 'critical_count'}
```

### HealthChecker

```python
checker = HealthChecker()

# Check components
result = checker.check_component(component)
results = checker.check_multiple_components(components)

# Get unhealthy
unhealthy = checker.get_unhealthy_components(components, threshold=75.0)
compromised = checker.get_compromised_components(components)

# Summary
summary = checker.get_health_summary(components)
```

## Best Practices

### 1. Regular Health Checks
```python
# Check forest health regularly
health_checker = HealthChecker()
all_components = manager.get_all_components()
summary = health_checker.get_health_summary(all_components)

if summary['average_health'] < 70:
    print("⚠️ Forest health below threshold!")
```

### 2. Threat Correlation
```python
# Track threats across multiple trees
squirrel = detector.detect_squirrel(...)
squirrel.add_movement("tree-001", "tree-002")
squirrel.add_movement("tree-002", "tree-003")

# This indicates lateral movement across infrastructure
if len(squirrel.visited_trees) > 3:
    # Escalate to incident response
    pass
```

### 3. Resource Monitoring
```python
# Update tree statistics regularly
for tree in manager.get_all_trees():
    # Collect from monitoring system
    cpu, memory, disk = get_system_metrics(tree.ip_address)
    tree.update_statistics(cpu=cpu, memory=memory, disk=disk)
```

### 4. Persistent Threat Tracking
```python
# Save threat state
threat_data = {
    'threats': [t.get_info() for t in detector.get_all_threats()],
    'timestamp': datetime.now().isoformat()
}
with open('threat_state.json', 'w') as f:
    json.dump(threat_data, f)
```

## Integration Examples

### Integration with Sensors

```python
from sensors import SensorManager, PortScanDetector
from forest import ForestManager, ThreatSeverity

# Create forest
manager = ForestManager()

# Sensor detects port scan
sensor = PortScanDetector()
alerts = sensor.get_alerts()

for alert in alerts:
    if alert['severity'] == 'critical':
        # Create bat threat (reconnaissance)
        bat = manager.threat_detector.detect_bat(
            threat_id=f"bat-{alert['source_ip']}",
            name="Port Scan Detected",
            attack_type="reconnaissance"
        )
        bat.add_recon_method("port_scanning")
        
        # Find target tree
        tree = manager.get_tree_by_ip(alert['target_ip'])
        if tree:
            manager.detect_threat(bat, tree.component_id)
```

### Integration with Cameras

```python
from cameras import ShodanEye
from forest import ForestManager

# Scan with camera
shodan = ShodanEye(api_key="your_key")
discoveries = shodan.scan("example.com")

# Map to forest
for disc in discoveries:
    if disc['type'] == 'service':
        # Create tree if not exists
        tree = manager.get_tree_by_ip(disc['target']['ip'])
        if not tree:
            tree = Tree(
                tree_id=f"tree-{disc['target']['ip']}",
                hostname=disc['target'].get('hostname', disc['target']['ip']),
                ip_address=disc['target']['ip']
            )
            manager.add_tree(tree)
        
        # Add service as branch
        branch = Branch(
            branch_id=f"svc-{disc['target']['port']}",
            name=disc['data'].get('service', 'unknown'),
            branch_type=BranchType.SERVICE,
            metadata={'port': disc['target']['port']}
        )
        tree.add_branch(branch)
```

## Troubleshooting

### Issue: Low Health Scores

**Solution:** Check resource usage and threats:
```python
tree = manager.get_tree(tree_id)
print(f"CPU: {tree.cpu_usage}%")
print(f"Memory: {tree.memory_usage}%")
print(f"Threats: {tree.get_threat_count()}")
```

### Issue: Threats Not Detected

**Solution:** Ensure threats are properly attached:
```python
threat = detector.detect_crow(...)
manager.detect_threat(threat, tree_id="tree-001")  # Must use manager
```

### Issue: Visual Output Not Displaying

**Solution:** Use print() explicitly:
```python
output = manager.get_visual_overview()
print(output)
```

## Future Enhancements

- **Fala 4**: Nanobots - Automated threat response
- **Fala 5**: Marker Gun - Threat tagging system
- **Fala 6**: Stain Database - Persistent threat storage
- **Fala 7**: Tablet Dashboard - Real-time visualization
- **Fala 8**: Eye in the Sky - Bird-based monitoring
- **Fala 9**: AI Engine - Intelligent analysis

## Contributing

Contributions are welcome! Please follow the existing code structure and patterns.

## License

See main project LICENSE file.

---

**Status**: ✅ COMPLETE  
**Version**: 1.0  
**Date**: December 15, 2025
