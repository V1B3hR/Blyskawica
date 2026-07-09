# 🔫 Weapons Module - Silent Marker System

**FALA 5: Broń Markerowa (Silent Marker)**

> *"Cichy, z tłumikiem, naboje tracer - raz trafiony, zawsze widoczny"*  
> *"Silent, with suppressor, tracer rounds - once hit, always visible"*

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Arsenal Components](#arsenal-components)
3. [Weapon Modes](#weapon-modes)
4. [Tracer Ammunition](#tracer-ammunition)
5. [Quick Start](#quick-start)
6. [Usage Examples](#usage-examples)
7. [API Reference](#api-reference)
8. [Integration](#integration)
9. [Best Practices](#best-practices)

---

## 🎯 Overview

The Silent Marker System is a sophisticated threat-tagging weapon that marks detected threats with permanent, colored "stains" for tracking and analysis. Like a hunter's marker gun, it tags targets for identification and tracking throughout their lifecycle.

### Key Features

- **Three Weapon Modes**: Pneumatic (0 dB), CO2 Silent (10 dB), Electric (20 dB)
- **Eight Tracer Colors**: Each color marks a different threat type
- **Targeting System**: Intelligent target acquisition and validation
- **Fire Control**: Automated and manual engagement protocols
- **Permanent Stains**: Immutable tags with threat metadata
- **Forest Integration**: Works seamlessly with Forest module (canopy threats)

---

## 🔫 Arsenal Components

### 1. MarkerGun
Main weapon class that fires tracer rounds at targets.

```python
from weapons import MarkerGun

gun = MarkerGun(name="Silent Marker Alpha")
gun.arm()
gun.safety_off()
```

### 2. Weapon Modes
Three firing modes with different noise/power profiles:

| Mode | Noise (dB) | Power | Range (m) | Use Case |
|------|-----------|-------|-----------|----------|
| 💨 Pneumatic | 0 | 3/10 | 50 | Stealth recon |
| 🧊 CO2 Silent | 10 | 6/10 | 100 | Standard ops |
| ⚡ Electric | 20 | 9/10 | 150 | High-priority |

### 3. Tracer Ammunition
Eight colored tracers for different threat types:

| Color | Type | Use Case |
|-------|------|----------|
| 🔴 Red | Malware | Confirmed malicious files |
| 🟣 Purple | Evil AI | Malicious bots/AI |
| 🟠 Orange | Suspicious IP | Anomalous sources |
| 🟡 Yellow | Backdoor | Unauthorized access |
| 🔵 Blue | Hidden Service | Shadow IT |
| ⚪ White | Unknown | Requires investigation |
| 🖤 Black | Crow | Canopy threats |
| 🤎 Brown | Squirrel | Lateral movement |

### 4. Targeting System
Intelligent target acquisition and validation.

### 5. Fire Control System
Automated engagement and safety protocols.

---

## 💨 Weapon Modes

### Pneumatic Mode (0 dB)

**Characteristics:**
- Completely silent
- Lower power (3/10)
- 50-meter effective range
- 85% hit probability

**Best For:**
- Stealth reconnaissance
- Low-priority threats
- When detection must be avoided

```python
from weapons import PneumaticMode, WeaponMode

gun.register_mode(WeaponMode.PNEUMATIC, PneumaticMode())
gun.set_mode(WeaponMode.PNEUMATIC)
```

### CO2 Silent Mode (10 dB)

**Characteristics:**
- Very quiet (whisper level)
- Balanced power (6/10)
- 100-meter effective range
- 92% hit probability

**Best For:**
- Standard operations
- Most threat types
- Balanced stealth/effectiveness

```python
from weapons import CO2SilentMode, WeaponMode

gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
gun.set_mode(WeaponMode.CO2_SILENT)
```

### Electric Mode (20 dB)

**Characteristics:**
- Quiet conversation level
- High power (9/10)
- 150-meter effective range
- 96% hit probability

**Best For:**
- High-priority threats
- Critical targets
- When certainty is needed

```python
from weapons import ElectricMode, WeaponMode

gun.register_mode(WeaponMode.ELECTRIC, ElectricMode())
gun.set_mode(WeaponMode.ELECTRIC)
```

---

## 🎨 Tracer Ammunition

### Red Tracer (🔴 Malware)

**Tag Format:** `MAL-[HASH]-[DATE]`

**Use For:**
- Confirmed malware
- Trojans, viruses, ransomware
- Malicious processes

**Required Fields:**
```python
target = {
    'file_hash': 'a1b2c3d4...',
    'process_name': 'evil.exe',
    'threat_score': 9.5,
    'confidence': 0.95
}
```

### Purple Tracer (🟣 Evil AI)

**Tag Format:** `EAI-[PATTERN]-[DATE]`

**Use For:**
- Malicious bots
- Automated attacks
- AI-powered threats

**Required Fields:**
```python
target = {
    'user_agent': 'EvilBot/1.0',
    'bot_signature': 'pattern123',
    'threat_score': 8.0,
    'confidence': 0.88
}
```

### Orange Tracer (🟠 Suspicious IP)

**Tag Format:** `SIP-[IP]-[SCORE]-[DATE]`

**Use For:**
- Suspicious IP addresses
- Known bad actors
- Anomalous sources

**Required Fields:**
```python
target = {
    'ip': '192.168.1.105',
    'threat_score': 7.5,
    'confidence': 0.82,
    'country': 'XX',
    'asn': 'AS12345'
}
```

### Yellow Tracer (🟡 Backdoor)

**Tag Format:** `BKD-[PORT]-[CVE]-[DATE]`

**Use For:**
- Backdoors
- Reverse shells
- Unauthorized access points

**Required Fields:**
```python
target = {
    'port': 4444,
    'service': 'netcat',
    'cve': 'CVE-2024-1234',
    'threat_score': 9.0,
    'confidence': 0.90
}
```

### Blue Tracer (🔵 Hidden Service)

**Tag Format:** `HID-[SERVICE]-[RISK]-[DATE]`

**Use For:**
- Undocumented services
- Shadow IT
- Hidden endpoints

**Required Fields:**
```python
target = {
    'service': 'rogue-api',
    'port': 8080,
    'risk_score': 6.5,
    'confidence': 0.75
}
```

### White Tracer (⚪ Unknown)

**Tag Format:** `UNK-[ID]-[DATE]`

**Use For:**
- Unknown threats
- Anomalies requiring investigation
- First-time observations

**Required Fields:**
```python
target = {
    'anomaly_id': 'anom-001',
    'anomaly_type': 'unusual_traffic',
    'threat_score': 5.0,
    'confidence': 0.60
}
```

### Black Tracer (🖤 Crow)

**Tag Format:** `CRW-[TYPE]-[TREE]-[DATE]`

**Use For:**
- Malware in forest canopy
- Patient, waiting threats
- APT-style persistence

**Required Fields:**
```python
target = {
    'crow_type': 'trojan',
    'forest_location': {
        'tree': 'web-server-01',
        'branch': 'nginx-worker',
        'crown': 'process-tree'
    },
    'threat_score': 8.5,
    'confidence': 0.87
}
```

### Brown Tracer (🤎 Squirrel)

**Tag Format:** `SQR-[PATH]-[DATE]`

**Use For:**
- Lateral movement
- Host hopping
- Privilege escalation paths

**Required Fields:**
```python
target = {
    'source_host': 'workstation-05',
    'dest_host': 'server-prod',
    'method': 'psexec',
    'threat_score': 8.0,
    'confidence': 0.85
}
```

---

## 🚀 Quick Start

### Basic Usage

```python
from weapons import MarkerGun, WeaponMode
from weapons import CO2SilentMode, RedTracer

# Create and setup weapon
gun = MarkerGun("Silent Marker")

# Register weapon mode
gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
gun.set_mode(WeaponMode.CO2_SILENT)

# Load ammunition
gun.load_ammo(RedTracer())

# Prepare weapon
gun.arm()
gun.safety_off()

# Define target
target = {
    'ip': '192.168.1.105',
    'file_hash': 'a1b2c3d4e5f6...',
    'threat_score': 9.0,
    'confidence': 0.92
}

# Fire!
result = gun.fire(target)

if result['hit']:
    print(f"Target marked! Stain ID: {result['stain']['tag_id']}")
    print(f"Marker type: {result['stain']['marker_type']}")
```

### Advanced Usage with Fire Control

```python
from weapons import MarkerGun, TargetingSystem, FireControlSystem
from weapons import CO2SilentMode, ElectricMode, WeaponMode
from weapons import RedTracer, OrangeTracer

# Initialize components
gun = MarkerGun("Hunter's Marker")
targeting = TargetingSystem()
fire_control = FireControlSystem(gun, targeting)

# Setup weapon
gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
gun.register_mode(WeaponMode.ELECTRIC, ElectricMode())
gun.load_ammo(RedTracer())
gun.load_ammo(OrangeTracer())

# Prepare for engagement
fire_control.prepare_weapon(mode='CO2_SILENT', ammo='RED')

# Acquire target
target_data = {
    'ip': '10.0.0.50',
    'file_hash': 'abc123...',
    'threat_score': 8.5,
    'confidence': 0.90,
    'threat_type': 'MALWARE'
}

target = targeting.acquire_target(target_data)

# Engage!
result = fire_control.engage_target(target)

print(f"Engagement {'successful' if result.success else 'failed'}")
print(f"Hit: {result.hit}")
print(f"Stain ID: {result.stain_id}")
```

---

## 📚 Usage Examples

### Example 1: Marking Malware

```python
from weapons import MarkerGun, CO2SilentMode, RedTracer, WeaponMode

gun = MarkerGun()
gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
gun.load_ammo(RedTracer())
gun.arm()
gun.safety_off()

# Malware detected
malware_target = {
    'file_hash': 'd41d8cd98f00b204e9800998ecf8427e',
    'process_name': 'ransomware.exe',
    'file_path': '/tmp/suspicious/ransomware.exe',
    'malware_family': 'WannaCry',
    'threat_score': 10.0,
    'confidence': 0.98
}

result = gun.fire(malware_target)
stain = result['stain']

print(f"🔴 Red tracer fired!")
print(f"Tag ID: {stain['tag_id']}")
print(f"Target: {stain['target']}")
```

### Example 2: Tracking Lateral Movement

```python
from weapons import MarkerGun, ElectricMode, BrownTracer, WeaponMode

gun = MarkerGun()
gun.register_mode(WeaponMode.ELECTRIC, ElectricMode())
gun.load_ammo(BrownTracer())
gun.arm()
gun.safety_off()

# Lateral movement detected
lateral_movement = {
    'source_host': 'workstation-42',
    'dest_host': 'dc-01',
    'method': 'pass-the-hash',
    'protocol': 'SMB',
    'credentials_used': 'admin',
    'threat_score': 9.5,
    'confidence': 0.95,
    'detected_by': 'falcon'
}

result = gun.fire(lateral_movement)

print(f"🤎 Brown tracer (Squirrel marker) fired!")
print(f"Movement path: {lateral_movement['source_host']} → {lateral_movement['dest_host']}")
```

### Example 3: Forest Integration

```python
from weapons import MarkerGun, CO2SilentMode, BlackTracer, WeaponMode

gun = MarkerGun()
gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
gun.load_ammo(BlackTracer())
gun.arm()
gun.safety_off()

# Crow detected in forest canopy
crow_in_canopy = {
    'crow_type': 'trojan',
    'forest_location': {
        'tree': 'web-server-01',
        'branch': 'nginx-process',
        'crown': 'suspicious-thread'
    },
    'behavior': 'patient_waiting',
    'hiding_method': 'obfuscation',
    'threat_score': 8.7,
    'confidence': 0.89,
    'detected_by': 'owl'
}

result = gun.fire(crow_in_canopy)

print(f"🖤 Black tracer (Crow marker) fired!")
print(f"Location: Tree '{crow_in_canopy['forest_location']['tree']}'")
```

### Example 4: Auto-Fire Mode

```python
from weapons import *

# Setup
gun = MarkerGun()
targeting = TargetingSystem()
fire_control = FireControlSystem(gun, targeting)

# Configure weapon
gun.register_mode(WeaponMode.CO2_SILENT, CO2SilentMode())
gun.load_ammo(RedTracer())
gun.load_ammo(OrangeTracer())

fire_control.prepare_weapon('CO2_SILENT', 'RED')

# Enable auto-fire for high-confidence targets
fire_control.enable_auto_fire(threshold=0.90)

# Acquire multiple targets
targets_data = [
    {'ip': '10.0.0.1', 'threat_score': 9.0, 'confidence': 0.95, 'threat_type': 'MALWARE'},
    {'ip': '10.0.0.2', 'threat_score': 7.0, 'confidence': 0.85, 'threat_type': 'SUSPICIOUS_IP'},
    {'ip': '10.0.0.3', 'threat_score': 8.5, 'confidence': 0.92, 'threat_type': 'BACKDOOR'},
]

for data in targets_data:
    targeting.acquire_target(data)

# Auto-engage high-confidence targets
results = fire_control.auto_engage()

print(f"Auto-fire engaged {len(results)} targets")
for r in results:
    if r.hit:
        print(f"  ✓ Hit: {r.target_id} with {r.ammo_used}")
```

---

## 🔧 API Reference

### MarkerGun

**Methods:**
- `register_mode(mode_type, mode)` - Register weapon mode
- `set_mode(mode_type)` - Change firing mode
- `load_ammo(tracer)` - Load tracer ammunition
- `select_ammo(color)` - Select ammo by color
- `arm()` - Arm the weapon
- `disarm()` - Disarm the weapon
- `safety_on()` / `safety_off()` - Safety control
- `fire(target)` - Fire at target
- `get_stain(tag_id)` - Retrieve stain by ID
- `get_statistics()` - Get weapon stats

### TargetingSystem

**Methods:**
- `acquire_target(target_data)` - Acquire new target
- `validate_target(target)` - Validate engagement criteria
- `lock_target(target)` - Lock onto target
- `unlock_target()` - Release target lock
- `prioritize_targets()` - Sort by priority
- `recommend_ammo(target)` - Suggest tracer color
- `recommend_weapon_mode(target)` - Suggest firing mode

### FireControlSystem

**Methods:**
- `engage_target(target, mode, ammo)` - Engage target
- `auto_engage()` - Automatically engage targets
- `enable_auto_fire(threshold)` - Enable auto mode
- `disable_auto_fire()` - Disable auto mode
- `prepare_weapon(mode, ammo)` - Prepare for firing
- `safe_weapon()` - Make weapon safe
- `get_engagement_statistics()` - Get stats

---

## 🔗 Integration

### With Sensors (FALA 1)

```python
from sensors import PortScanDetector
from weapons import MarkerGun, OrangeTracer

sensor = PortScanDetector()
gun = MarkerGun()
gun.load_ammo(OrangeTracer())

def on_port_scan(alert):
    target = {
        'ip': alert['source_ip'],
        'threat_score': alert['severity'] * 2,
        'confidence': 0.80,
        'threat_type': 'SUSPICIOUS_IP'
    }
    gun.fire(target)

sensor.register_callback(on_port_scan)
```

### With Nanobots (FALA 4)

```python
from nanobots import ThreatHunterNanobot
from weapons import MarkerGun, BlackTracer

nanobot = ThreatHunterNanobot()
gun = MarkerGun()
gun.load_ammo(BlackTracer())

# When nanobot detects threat, mark it
def mark_threat(threat_event):
    gun.fire(threat_event)

nanobot.register_action_callback(mark_threat)
```

### With Forest (FALA 3)

```python
from forest import ForestManager
from weapons import MarkerGun, BlackTracer, BrownTracer

forest = ForestManager()
gun = MarkerGun()
gun.load_ammo(BlackTracer())
gun.load_ammo(BrownTracer())

# Mark crows in canopy
for tree in forest.get_all_trees():
    for threat in tree.get_canopy_threats():
        if threat.type == 'crow':
            gun.select_ammo('BLACK')
        elif threat.type == 'squirrel':
            gun.select_ammo('BROWN')
        gun.fire(threat.to_dict())
```

---

## 🎯 Best Practices

### 1. Mode Selection

- **Use Pneumatic** for reconnaissance and low-priority targets
- **Use CO2 Silent** for standard operations (80% of cases)
- **Use Electric** for critical, confirmed threats

### 2. Ammo Selection

- **Validate** threat type before selecting tracer
- **Use White tracer** when uncertain, reclassify later
- **Forest threats** should use Black (crow) or Brown (squirrel)

### 3. Safety

```python
# Always safe weapon when not in use
gun.safety_on()
gun.disarm()

# Only disable safety when ready to fire
gun.arm()
gun.safety_off()
gun.fire(target)
gun.safety_on()  # Re-engage safety
```

### 4. Target Validation

```python
# Always validate before firing
validation = targeting.validate_target(target)
if validation['valid']:
    fire_control.engage_target(target)
else:
    print(f"Invalid target: {validation['reasons']}")
```

### 5. Stain Management

```python
# Track all stains
all_stains = gun.get_all_stains()

# Query by type
malware_stains = gun.get_stains_by_type('MALWARE')

# Update stains with evidence
stain = gun.get_stain(tag_id)
stain.add_evidence("Sample analyzed by AV engine")
stain.link_tag(related_tag_id)
```

---

## 📊 Statistics and Monitoring

```python
# Weapon statistics
stats = gun.get_statistics()
print(f"Accuracy: {stats['accuracy_percent']}%")
print(f"Shots fired: {stats['shots_fired']}")
print(f"Stains created: {stats['stains_created']}")

# Fire control statistics
fc_stats = fire_control.get_engagement_statistics()
print(f"Total engagements: {fc_stats['total_engagements']}")
print(f"By mode: {fc_stats['engagements_by_mode']}")
print(f"By ammo: {fc_stats['engagements_by_ammo']}")
```

---

## ⚠️ Security Considerations

1. **Validate targets** before marking to avoid false positives
2. **Use appropriate confidence thresholds** for auto-fire
3. **Log all engagements** for audit trails
4. **Protect stain database** - it contains threat intelligence
5. **Use proper tracer colors** for accurate threat classification

---

## 🎓 Tactical Guidelines

### Stealth Operations
- Use Pneumatic mode
- Mark with Blue/White tracers
- Avoid detection

### Active Threat Response
- Use Electric mode
- Mark with Red/Purple/Yellow tracers
- Maximum impact

### Forest Patrol
- Use CO2 Silent mode
- Mark with Black (crow) or Brown (squirrel) tracers
- Track canopy threats

---

## 📝 License

Part of Nethical Recon project by V1B3hR

---

**Status:** ✅ FALA 5 COMPLETE

*"Raz trafiony, zawsze widoczny" - Once hit, always visible*
