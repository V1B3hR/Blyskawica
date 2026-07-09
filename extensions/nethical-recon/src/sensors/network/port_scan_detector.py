"""
Port Scan Detector Sensor
🔍 Detects port scanning attempts
Analogia: "Pukanie do drzwi" (Knocking on doors)
"""

import threading
import time
from collections import defaultdict
from typing import Any

from ..base import BaseSensor, SensorStatus


class PortScanDetector(BaseSensor):
    """
    Detects port scanning attempts by monitoring connection patterns
    Identifies SYN scans, connect scans, and other scanning behaviors
    """

    def __init__(self, name: str = "port_scan_detector", config: dict[str, Any] = None):
        """
        Initialize Port Scan Detector

        Config options:
            - port_threshold: Number of ports from same IP to trigger alert (default: 10)
            - time_window: Time window in seconds for detection (default: 60)
            - check_interval: Seconds between checks (default: 5)
        """
        super().__init__(name, config)
        self.port_threshold = self.config.get("port_threshold", 10)
        self.time_window = self.config.get("time_window", 60)
        self.check_interval = self.config.get("check_interval", 5)

        # Track connection attempts: {ip: [(port, timestamp), ...]}
        self._connection_attempts = defaultdict(list)
        self._monitor_thread = None
        self._stop_flag = False
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start port scan detection"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Port scan detector already running")
            return False

        try:
            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_scans, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info("Started port scan detection")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start port scan detector: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop port scan detection"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped port scan detection")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping port scan detector: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single scan detection check"""
        try:
            scanners = self._detect_scanners()

            return {"status": "success", "potential_scanners": len(scanners), "scanners": list(scanners)}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def record_connection_attempt(self, source_ip: str, dest_port: int):
        """
        Record a connection attempt for analysis

        Args:
            source_ip: Source IP address
            dest_port: Destination port
        """
        with self._lock:
            timestamp = time.time()
            self._connection_attempts[source_ip].append((dest_port, timestamp))

    def _monitor_scans(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                # Clean old entries
                self._cleanup_old_entries()

                # Detect scanners
                scanners = self._detect_scanners()

                # Raise alerts for detected scanners
                for scanner_ip in scanners:
                    self._handle_scan_detection(scanner_ip)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in scan monitoring: {e}")
                time.sleep(self.check_interval)

    def _cleanup_old_entries(self):
        """Remove entries outside the time window"""
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - self.time_window

            # Clean up old entries
            for ip in list(self._connection_attempts.keys()):
                # Filter out old attempts
                self._connection_attempts[ip] = [
                    (port, ts) for port, ts in self._connection_attempts[ip] if ts > cutoff_time
                ]

                # Remove IP if no recent attempts
                if not self._connection_attempts[ip]:
                    del self._connection_attempts[ip]

    def _detect_scanners(self) -> set[str]:
        """
        Detect potential port scanners

        Returns:
            Set of IP addresses identified as scanners
        """
        scanners = set()

        with self._lock:
            for ip, attempts in self._connection_attempts.items():
                # Count unique ports
                unique_ports = set(port for port, _ in attempts)

                # If unique port count exceeds threshold, it's a scan
                if len(unique_ports) >= self.port_threshold:
                    scanners.add(ip)

        return scanners

    def _handle_scan_detection(self, scanner_ip: str):
        """
        Handle detection of a port scanner

        Args:
            scanner_ip: IP address of the scanner
        """
        with self._lock:
            attempts = self._connection_attempts.get(scanner_ip, [])
            unique_ports = set(port for port, _ in attempts)

            # Calculate scan characteristics
            scan_info = {
                "scanner_ip": scanner_ip,
                "unique_ports": len(unique_ports),
                "total_attempts": len(attempts),
                "ports": sorted(list(unique_ports))[:20],  # First 20 ports
                "time_window": self.time_window,
            }

        # Determine severity based on scan intensity
        severity = "WARNING"
        if len(unique_ports) > 100:
            severity = "CRITICAL"
        elif len(unique_ports) > 50:
            severity = "WARNING"

        self.raise_alert(
            severity, f"Port scan detected from {scanner_ip}: {len(unique_ports)} ports scanned", scan_info
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get port scan detection statistics"""
        with self._lock:
            active_ips = len(self._connection_attempts)
            total_attempts = sum(len(attempts) for attempts in self._connection_attempts.values())

        return {
            "status": self.status.value,
            "port_threshold": self.port_threshold,
            "time_window": self.time_window,
            "active_ips": active_ips,
            "total_attempts": total_attempts,
            "alerts": len(self.alerts),
        }

    def get_top_scanners(self, limit: int = 10) -> list:
        """
        Get top potential scanners by port count

        Args:
            limit: Maximum number of results to return

        Returns:
            List of (ip, port_count) tuples
        """
        with self._lock:
            scanner_stats = []
            for ip, attempts in self._connection_attempts.items():
                unique_ports = len(set(port for port, _ in attempts))
                scanner_stats.append((ip, unique_ports))

            # Sort by port count descending
            scanner_stats.sort(key=lambda x: x[1], reverse=True)

            return scanner_stats[:limit]
