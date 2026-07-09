# 🎯 Nethical Hunter Command Center UI

**FALA 7: TABLET MYŚLIWEGO** - The Hunter's Tablet Dashboard

---

## Overview

The Command Center UI is the central hub for all Nethical Hunter operations. It provides a fast, readable, and beautifully organized interface for monitoring threats, controlling weapons, managing nanobots, and overseeing the entire forest infrastructure.

## Features

### 📱 Main Dashboard
- **Real-time status monitoring** across all systems
- **Multi-panel layout** with categorized information
- **Live alerts feed** (Bird Songs) with severity levels
- **Quick navigation** to specialized screens

### 🎨 Visual Components

#### Panels
- **Threat Level**: Real-time threat assessment with color-coded indicators
- **Sensors Status**: Network and system sensor monitoring
- **Nanobots Status**: Swarm control and mode display
- **Birds Status**: Sky surveillance patrol status
- **Alerts Feed**: Recent bird song alerts with timestamps
- **Forest Status**: Infrastructure health and threat summary
- **Weapon Status**: Weapon mode, ammo counts, and stealth level

#### Screens
- **Targeting**: Precision weapon targeting interface
- **Stain Report**: Hunting session statistics and reports
- **Forest View**: Detailed infrastructure tree visualization
- **Settings**: Configuration and preferences management

#### Widgets
- **Progress Bars**: Visual indicators for various metrics
- **Threat Indicator**: Dynamic threat level display
- **Tree Widget**: Forest structure visualization

## Quick Start

### Installation

```bash
pip install rich textual
```

### Basic Usage

```python
from ui.dashboard import Dashboard, create_demo_status, create_demo_alerts

# Create and configure dashboard
dashboard = Dashboard()
dashboard.update_status(create_demo_status())

# Add alerts
for alert in create_demo_alerts():
    dashboard.add_alert(alert)

# Display dashboard
dashboard.show()
```

### Run Demo

```bash
# Static demo - shows all screens
python examples/dashboard_example.py

# Interactive demo - navigate between screens
python examples/dashboard_example.py --interactive
```

## Architecture

```
ui/
├── __init__.py              # Package initialization
├── base.py                  # Base classes and enums
├── dashboard.py             # Main dashboard controller
│
├── panels/                  # Dashboard panel components
│   ├── threat_level.py      # Threat assessment panel
│   ├── sensors_status.py    # Sensors monitoring panel
│   ├── nanobots_status.py   # Nanobot control panel
│   ├── alerts_feed.py       # Bird songs alert feed
│   ├── weapon_status.py     # Weapon system panel
│   ├── forest_status.py     # Forest overview panel
│   └── birds_status.py      # Birds patrol panel
│
├── screens/                 # Full-screen views
│   ├── targeting.py         # Weapon targeting screen
│   ├── stain_report.py      # Statistics and reports
│   ├── forest_view.py       # Forest visualization
│   └── settings.py          # Configuration screen
│
└── widgets/                 # Reusable UI widgets
    ├── progress_bars.py     # Progress bar components
    ├── threat_indicator.py  # Threat level indicators
    └── tree_widget.py       # Tree visualization widget
```

## Integration

### With Sensors (FALA 1)

```python
from ui.dashboard import Dashboard
from ui.base import SystemStatus

dashboard = Dashboard()
status = SystemStatus()
status.sensors_online = 16
status.sensors_total = 16
dashboard.update_status(status)
```

### With Cameras (FALA 2)

```python
status.cameras_online = 4
dashboard.update_status(status)
```

### With Forest (FALA 3)

```python
from ui.widgets.tree_widget import TreeWidget
from ui.base import ThreatType

tree = TreeWidget("web-server-01")
tree.add_branch("nginx-master", 4)
tree.add_threat(ThreatType.CROW, "nginx-master")
```

### With Nanobots (FALA 4)

```python
status.nanobots_active = 847
status.nanobots_mode = "DEFENSE"
dashboard.update_status(status)
```

### With Weapons (FALA 5)

```python
from ui.screens.targeting import Target, TargetingScreen

targeting = TargetingScreen()
target = Target(
    ip="192.168.1.105",
    port=4444,
    target_type="MALWARE C2",
    confidence=0.87
)
targeting.set_target(target)
```

### With Database (FALA 6)

```python
from ui.screens.stain_report import StainReportScreen

report = StainReportScreen()
report.set_statistics({
    "MALWARE": 3,
    "CROW": 5,
    "SQUIRREL": 2
})
```

## Bird Songs Alert System

The dashboard uses "bird songs" as alert notifications:

| Bird | Sound | Level | Description |
|------|-------|-------|-------------|
| 🐦 Sparrow | chirp | INFO | Routine operations |
| 🦉 Owl | hoot... | WARNING | Unusual activity |
| 🦅 Falcon | SCREECH! | ELEVATED | Suspicious activity |
| 🦅 Eagle | ROAR!! | CRITICAL | Active threat |
| 🐦‍⬛ Crow | CAW! | BREACH | Confirmed compromise |

### Adding Alerts

```python
from ui.base import Alert, BirdType, ThreatLevel

alert = Alert(
    bird=BirdType.FALCON,
    message="Port scan detected from 192.168.1.105",
    level=ThreatLevel.ELEVATED
)
dashboard.add_alert(alert)
```

## Customization

### Threat Levels

```python
from ui.base import ThreatLevel, calculate_threat_level

# Automatic calculation from score
level = calculate_threat_level(7.5)  # Returns ThreatLevel.ELEVATED

# Manual setting
status.threat_level = ThreatLevel.CRITICAL
status.threat_score = 8.2
```

### Color Scheme

Modify `ui/base.py` to customize colors:

```python
class UIColors:
    SAFE = "green"
    WARNING = "yellow"
    CRITICAL = "red"
    # ... customize as needed
```

## Live Updates

For real-time dashboard updates:

```python
dashboard.run_live(refresh_rate=1.0)  # Update every second
```

## API Reference

### Dashboard Class

- `update_status(status: SystemStatus)` - Update system status
- `add_alert(alert: Alert)` - Add new alert
- `show()` - Display dashboard once
- `run_live(refresh_rate: float)` - Run with live updates
- `switch_screen(screen: str)` - Switch to different screen

### SystemStatus Class

Properties:
- `threat_level: ThreatLevel`
- `threat_score: float`
- `sensors_online: int`
- `sensors_total: int`
- `cameras_online: int`
- `nanobots_active: int`
- `nanobots_mode: str`
- `forest_trees: int`
- `forest_branches: int`
- `forest_leaves: int`
- `forest_threats: Dict[str, int]`
- `weapon_status: str`
- `weapon_mode: str`
- `weapon_stealth: int`
- `ammo_counts: Dict[str, int]`

## Best Practices

1. **Update frequency**: Update status at reasonable intervals (1-5 seconds)
2. **Alert management**: Keep recent alerts list to 4-6 items for readability
3. **Forest monitoring**: Update tree counts when infrastructure changes
4. **Weapon status**: Keep ammo counts accurate for targeting decisions
5. **Color coding**: Use consistent color schemes for threat levels

## Testing

Run the comprehensive demo:

```bash
python examples/dashboard_example.py
```

Test individual components:

```python
# Test panel rendering
from ui.panels.threat_level import ThreatLevelPanel
panel = ThreatLevelPanel(score=7.5)
print(panel.render_compact())

# Test widget
from ui.widgets.tree_widget import TreeWidget
tree = TreeWidget("test-server")
print(tree.render_simple())
```

## Performance

- **Rendering**: ~10ms per frame (depends on terminal size)
- **Memory**: ~5MB for full dashboard
- **Update rate**: Supports up to 60 FPS (though 1-5 Hz is recommended)

## Troubleshooting

### Colors not displaying correctly
- Ensure terminal supports 256 colors
- Try different color schemes in `UIColors`

### Layout issues
- Verify terminal width is at least 80 characters
- Check Rich version: `pip show rich`

### Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version >= 3.8

## Contributing

When adding new panels or screens:

1. Follow existing naming conventions
2. Implement `render()` method
3. Add to respective `__init__.py`
4. Update dashboard layout if needed
5. Add example usage to `dashboard_example.py`

## License

Part of Nethical Hunter project - see main LICENSE file.

---

**Status**: ✅ Production Ready  
**Version**: 3.0.0  
**FALA**: 7 Complete

*"Główne centrum dowodzenia - szybko, czytelnie, podzielone na kategorie"*
