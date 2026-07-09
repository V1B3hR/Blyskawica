#!/usr/bin/env python3
"""
Example: Basic Sensor Usage
Demonstrates how to use Nethical Recon sensors for network and system monitoring
"""

import os
import sys
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensors import SensorManager
from sensors.network import PortScanDetector
from sensors.system import HeartbeatMonitor, ResourceMonitor


def print_banner():
    """Print example banner"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         Nethical Recon - Sensor Example                 ║
║         Fala 1: Czujniki Ruchu i Wibracji              ║
╚══════════════════════════════════════════════════════════╝
    """)


def main():
    """Main example function"""
    print_banner()

    print("[*] Initializing Sensor Manager...")
    manager = SensorManager()

    # Create sensors with basic configuration
    print("[*] Creating sensors...")

    # Port Scan Detector - monitors for scanning activity
    port_scan = PortScanDetector(
        name="port_scanner_detector", config={"port_threshold": 10, "time_window": 60, "check_interval": 5}
    )

    # Resource Monitor - monitors system resources
    resource_monitor = ResourceMonitor(
        name="system_resources", config={"cpu_threshold": 85, "memory_threshold": 85, "check_interval": 10}
    )

    # Heartbeat Monitor - monitors service availability
    heartbeat = HeartbeatMonitor(
        name="service_heartbeat", config={"services": ["sshd"], "check_interval": 30}  # Monitor SSH service
    )

    # Register sensors
    print("[*] Registering sensors...")
    manager.register_sensor(port_scan)
    manager.register_sensor(resource_monitor)
    manager.register_sensor(heartbeat)

    # Start all sensors
    print("[*] Starting sensors...")
    started = manager.start_all()
    print(f"[+] Started {started} sensors")

    # Display initial status
    print("\n" + "=" * 60)
    print("Initial Sensor Status:")
    print("=" * 60)
    status = manager.get_status_all()
    for name, sensor_status in status.items():
        print(f"  {name}: {sensor_status['status']}")

    # Run for a short time
    print("\n[*] Monitoring for 30 seconds...")
    print("[*] Press Ctrl+C to stop early\n")

    try:
        # Monitor for 30 seconds
        for i in range(6):
            time.sleep(5)

            # Display health check
            health = manager.health_check()
            print(f"[{i*5}s] Health: {health['running']}/{health['total_sensors']} running", end="")

            # Check for alerts
            alerts = manager.get_all_alerts()
            if alerts:
                alert_count = sum(len(sensor_alerts) for sensor_alerts in alerts.values())
                print(f" | Alerts: {alert_count}")

                # Display recent alerts
                for sensor_name, sensor_alerts in alerts.items():
                    for alert in sensor_alerts[-3:]:  # Last 3 alerts
                        severity = alert["severity"]
                        message = alert["message"]
                        print(f"    [{severity}] {sensor_name}: {message}")
            else:
                print(" | No alerts")

        print("\n[*] Monitoring period complete")

        # Display final statistics
        print("\n" + "=" * 60)
        print("Final Statistics:")
        print("=" * 60)

        # Resource Monitor stats
        print("\n📈 Resource Monitor:")
        res_stats = resource_monitor.get_statistics()
        if "current_metrics" in res_stats and res_stats["current_metrics"]:
            metrics = res_stats["current_metrics"]
            print(f"  CPU: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"  Memory: {metrics.get('memory_percent', 0):.1f}%")
            print(f"  Disk: {metrics.get('disk_percent', 0):.1f}%")

        # Port Scan Detector stats
        print("\n🔍 Port Scan Detector:")
        scan_stats = port_scan.get_statistics()
        print(f"  Active IPs tracked: {scan_stats['active_ips']}")
        print(f"  Total attempts: {scan_stats['total_attempts']}")

        # Heartbeat Monitor stats
        print("\n💓 Heartbeat Monitor:")
        hb_stats = heartbeat.get_statistics()
        print(f"  Services monitored: {hb_stats['services_monitored']}")
        for service, is_running in hb_stats["current_status"].items():
            status_str = "✓ running" if is_running else "✗ stopped"
            print(f"  {service}: {status_str}")

        # All alerts summary
        print("\n🚨 Alerts Summary:")
        all_alerts = manager.get_all_alerts()
        total_alerts = sum(len(a) for a in all_alerts.values())
        print(f"  Total alerts: {total_alerts}")

        critical_alerts = manager.get_all_alerts(severity="CRITICAL")
        critical_count = sum(len(a) for a in critical_alerts.values())
        if critical_count > 0:
            print(f"  Critical alerts: {critical_count}")

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")

    # Clean shutdown
    print("\n[*] Stopping sensors...")
    stopped = manager.stop_all()
    print(f"[+] Stopped {stopped} sensors")

    print("\n[✓] Example complete!")
    print("\nFor more examples, see sensors/README.md")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
