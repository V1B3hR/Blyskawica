# Sensors Module - Fala 1: Czujniki Ruchu i Wibracji

## Overview

The Sensors module implements "Fala 1" (Wave 1) of the Nethical Recon roadmap - Network and System monitoring sensors. These sensors act as the "eyes and ears" of the security monitoring system.

## Architecture

```
sensors/
├── base.py                 # Base sensor class and infrastructure
├── manager.py             # Sensor orchestration and management
├── network/               # Network sensors (Czujniki Sieciowe)
│   ├── traffic_monitor.py       # 🚶 Traffic monitoring (tcpdump)
│   ├── anomaly_detector.py      # 📊 Anomaly detection (Zeek)
│   ├── port_scan_detector.py    # 🔍 Port scan detection
│   └── protocol_analyzer.py     # 🔬 Deep protocol analysis
└── system/                # System sensors (Czujniki Systemowe)
    ├── heartbeat_monitor.py     # 💓 Service availability
    ├── resource_monitor.py      # 📈 CPU/RAM monitoring
    ├── file_watcher.py          # 📁 File integrity
    ├── auth_monitor.py          # 🔐 Authentication monitoring
    └── dns_watcher.py           # 🌐 DNS query monitoring
```

## Quick Start

### Basic Usage

```python
from sensors import SensorManager
from sensors.network import TrafficMonitor, PortScanDetector
from sensors.system import ResourceMonitor, HeartbeatMonitor

# Create sensor manager
manager = SensorManager()

# Create and register sensors
traffic = TrafficMonitor(config={'interface': 'eth0'})
port_scan = PortScanDetector(config={'port_threshold': 10})
resources = ResourceMonitor(config={'cpu_threshold': 85})
heartbeat = HeartbeatMonitor(config={'services': ['sshd', 'nginx']})

manager.register_sensor(traffic)
manager.register_sensor(port_scan)
manager.register_sensor(resources)
manager.register_sensor(heartbeat)

# Start all sensors
manager.start_all()

# Monitor in background
manager.start_monitoring(interval=60)

# Get status of all sensors
status = manager.get_status_all()
print(status)

# Get all alerts
alerts = manager.get_all_alerts()
print(alerts)

# Stop when done
manager.stop_all()
```

### Individual Sensor Usage

#### Traffic Monitor (Network)

```python
from sensors.network import TrafficMonitor

# Create traffic monitor
traffic = TrafficMonitor(
    name="main_traffic",
    config={
        'interface': 'eth0',
        'filter': 'tcp port 80',  # BPF filter
        'alert_threshold': 1000    # packets/sec
    }
)

# Start monitoring
traffic.start()

# Get statistics
stats = traffic.get_statistics()
print(f"Packet rate: {stats['packet_rate']}")

# Get alerts
alerts = traffic.get_alerts(severity='CRITICAL')
for alert in alerts:
    print(alert.to_dict())

# Stop monitoring
traffic.stop()
```

#### Port Scan Detector (Network)

```python
from sensors.network import PortScanDetector

# Create port scan detector
scanner = PortScanDetector(
    config={
        'port_threshold': 15,      # ports to trigger alert
        'time_window': 60,         # seconds
        'check_interval': 5        # check frequency
    }
)

scanner.start()

# Record connection attempts (if integrating with firewall/IDS)
scanner.record_connection_attempt('192.168.1.100', 22)
scanner.record_connection_attempt('192.168.1.100', 80)
scanner.record_connection_attempt('192.168.1.100', 443)

# Get top scanners
top_scanners = scanner.get_top_scanners(limit=5)
for ip, port_count in top_scanners:
    print(f"{ip}: {port_count} ports")
```

#### Resource Monitor (System)

```python
from sensors.system import ResourceMonitor

# Create resource monitor
monitor = ResourceMonitor(
    config={
        'cpu_threshold': 90,
        'memory_threshold': 90,
        'disk_threshold': 85,
        'check_interval': 10
    }
)

monitor.start()

# Get current metrics
metrics = monitor.check()
print(f"CPU: {metrics['metrics']['cpu_percent']}%")
print(f"Memory: {metrics['metrics']['memory_percent']}%")

# Get top processes
top_procs = monitor.get_top_processes(limit=10)
for proc in top_procs:
    print(f"{proc['name']}: CPU={proc['cpu_percent']}%")
```

#### File Watcher (System)

```python
from sensors.system import FileWatcher

# Create file watcher
watcher = FileWatcher(
    config={
        'watch_paths': ['/etc/passwd', '/etc/ssh', '/usr/bin'],
        'check_interval': 300,
        'hash_algorithm': 'sha256',
        'recursive': True
    }
)

watcher.start()

# Get statistics
stats = watcher.get_statistics()
print(f"Monitoring {stats['files_monitored']} files")
```

#### Authentication Monitor (System)

```python
from sensors.system import AuthMonitor

# Create auth monitor
auth = AuthMonitor(
    config={
        'log_files': ['/var/log/auth.log'],
        'failure_threshold': 5,
        'time_window': 300
    }
)

auth.start()

# Get alerts for failed logins
alerts = auth.get_alerts(severity='CRITICAL')
```

## Configuration Options

### Network Sensors

#### TrafficMonitor
- `interface`: Network interface (default: 'any')
- `filter`: BPF filter expression
- `alert_threshold`: Packets/sec to alert (default: 1000)
- `tool`: 'tcpdump' or 'tshark'

#### AnomalyDetector
- `interface`: Network interface
- `zeek_path`: Path to Zeek binary
- `log_dir`: Zeek log directory
- `check_interval`: Check frequency in seconds

#### PortScanDetector
- `port_threshold`: Ports to trigger alert (default: 10)
- `time_window`: Time window in seconds (default: 60)
- `check_interval`: Check frequency

#### ProtocolAnalyzer
- `interface`: Network interface
- `protocols`: List of protocols to analyze
- `check_interval`: Analysis frequency

### System Sensors

#### HeartbeatMonitor
- `services`: List of services to monitor
- `ports`: List of (host, port) tuples
- `check_interval`: Check frequency
- `timeout`: Health check timeout

#### ResourceMonitor
- `cpu_threshold`: CPU % to alert (default: 90)
- `memory_threshold`: Memory % to alert (default: 90)
- `disk_threshold`: Disk % to alert (default: 90)
- `check_interval`: Check frequency

#### FileWatcher
- `watch_paths`: List of paths to monitor
- `check_interval`: Check frequency (default: 300)
- `hash_algorithm`: Hash algorithm (default: 'sha256')
- `recursive`: Watch directories recursively

#### AuthMonitor
- `log_files`: List of auth log files
- `failure_threshold`: Failed attempts to alert (default: 5)
- `time_window`: Time window for counting failures
- `check_interval`: Check frequency

#### DNSWatcher
- `interface`: Network interface
- `query_threshold`: Queries/min to alert (default: 100)
- `suspicious_tlds`: List of suspicious TLDs
- `check_interval`: Check frequency

## Alert Severities

Sensors raise alerts with three severity levels:

- **INFO**: Informational events
- **WARNING**: Potentially suspicious activity
- **CRITICAL**: Serious security concerns

## Requirements

### System Requirements
- Python 3.7+
- Linux/Unix-based system

### Python Dependencies
- `psutil` - For system resource monitoring

### Optional System Tools
- `tcpdump` or `tshark` - For network traffic monitoring
- `zeek` (formerly Bro) - For anomaly detection
- Root/sudo access - For some network monitoring features

### Installation

```bash
pip install psutil

# Optional tools (Ubuntu/Debian)
sudo apt-get install tcpdump tshark zeek

# Optional tools (RHEL/CentOS)
sudo yum install tcpdump wireshark zeek
```

## Best Practices

1. **Start with Essential Sensors**: Begin with ResourceMonitor and HeartbeatMonitor
2. **Tune Thresholds**: Adjust alert thresholds based on your environment
3. **Use SensorManager**: Manage multiple sensors through the manager for consistency
4. **Monitor Alerts**: Regularly check and clear alerts to avoid memory buildup
5. **Permissions**: Some sensors require elevated privileges (especially network sensors)

## Security Considerations

⚠️ **Important**: 
- Network sensors may require root/sudo privileges
- Be mindful of privacy when monitoring traffic
- File monitoring can be resource-intensive
- Only use on systems you own or have permission to monitor

## Troubleshooting

### "tcpdump not found"
```bash
sudo apt-get install tcpdump
# or
sudo yum install tcpdump
```

### "Permission denied" for network monitoring
Run with sudo or grant CAP_NET_RAW capability:
```bash
sudo setcap cap_net_raw+ep $(which python3)
```

### High CPU usage
- Reduce check intervals
- Limit watch paths for FileWatcher
- Use BPF filters to reduce traffic capture

## Next Steps

After implementing Fala 1, the roadmap continues with:
- **Fala 2**: Kamery IR (Deep/Dark Discovery)
- **Fala 3**: Forest (Infrastructure Mapping)
- **Fala 4**: Nanoboty (Automated Response)

## License

Part of Nethical Recon project. See main LICENSE file.
