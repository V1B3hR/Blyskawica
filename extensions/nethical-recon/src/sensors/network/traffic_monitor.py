"""
Traffic Monitor Sensor
🚶 Monitors network traffic using tcpdump/tshark
Analogia: "Kamera przy bramie" (Camera at the gate)
"""

import re
import subprocess
import threading
import time
from typing import Any

from ..base import BaseSensor, SensorStatus


class TrafficMonitor(BaseSensor):
    """
    Monitors network traffic and detects who enters/exits
    Uses tcpdump or tshark as backend
    """

    def __init__(self, name: str = "traffic_monitor", config: dict[str, Any] = None):
        """
        Initialize Traffic Monitor

        Config options:
            - interface: Network interface to monitor (default: any)
            - filter: BPF filter expression (default: None)
            - alert_threshold: Packets per second to trigger alert (default: 1000)
            - tool: 'tcpdump' or 'tshark' (default: tcpdump)
        """
        super().__init__(name, config)
        self.interface = self.config.get("interface", "any")
        self.filter = self.config.get("filter", "")
        self.alert_threshold = self.config.get("alert_threshold", 1000)
        self.tool = self.config.get("tool", "tcpdump")

        self._process = None
        self._monitor_thread = None
        self._stop_flag = False
        self._packet_count = 0
        self._last_check_time = None

    def validate_config(self) -> bool:
        """Validate configuration"""
        # Check if tool is available
        try:
            result = subprocess.run(["which", self.tool], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.logger.error(f"{self.tool} not found in PATH")
                return False
        except Exception as e:
            self.logger.error(f"Failed to validate {self.tool}: {e}")
            return False

        return True

    def start(self) -> bool:
        """Start traffic monitoring"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Traffic monitor already running")
            return False

        if not self.validate_config():
            self.status = SensorStatus.ERROR
            return False

        try:
            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_traffic, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info(f"Started traffic monitoring on interface {self.interface}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start traffic monitor: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop traffic monitoring"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Terminate subprocess if running
            if self._process:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                self._process = None

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped traffic monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping traffic monitor: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single traffic check"""
        try:
            # Run tcpdump for a short duration to capture sample
            cmd = [self.tool, "-i", self.interface, "-c", "100", "-n"]

            if self.filter:
                cmd.extend(self.filter.split())

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            packets = result.stdout.split("\n")
            packet_count = len([p for p in packets if p.strip()])

            return {
                "status": "success",
                "packet_count": packet_count,
                "interface": self.interface,
                "sample": packets[:5] if packets else [],
            }

        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": "Check timed out"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_traffic(self):
        """Internal monitoring loop"""
        try:
            # Build command
            cmd = [self.tool, "-i", self.interface, "-n", "-l"]

            if self.filter:
                cmd.extend(self.filter.split())

            # Start capture process
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

            self._last_check_time = time.time()

            # Read output line by line
            for line in self._process.stdout:
                if self._stop_flag:
                    break

                if line.strip():
                    self._packet_count += 1
                    self._analyze_packet(line)

                    # Check packet rate periodically
                    current_time = time.time()
                    if current_time - self._last_check_time >= 1.0:
                        self._check_packet_rate()
                        self._last_check_time = current_time
                        self._packet_count = 0

        except Exception as e:
            self.logger.error(f"Error in traffic monitoring: {e}")
            self.status = SensorStatus.ERROR

    def _analyze_packet(self, packet_line: str):
        """
        Analyze individual packet

        Args:
            packet_line: Raw packet line from tcpdump/tshark
        """
        # Basic analysis - look for suspicious patterns

        # Check for port scanning indicators
        if re.search(r"Flags \[S\]", packet_line):
            # SYN packet - possible scan
            if "RST" in packet_line:
                # SYN-RST pattern - likely closed port scan
                self._increment_scan_counter()

    def _check_packet_rate(self):
        """Check if packet rate exceeds threshold"""
        if self._packet_count > self.alert_threshold:
            self.raise_alert(
                "WARNING",
                f"High packet rate detected: {self._packet_count} packets/sec",
                {"packets_per_sec": self._packet_count, "threshold": self.alert_threshold},
            )

    def _increment_scan_counter(self):
        """Track potential scanning activity"""
        # This could be enhanced to track patterns over time
        pass

    def get_statistics(self) -> dict[str, Any]:
        """Get traffic statistics"""
        return {
            "status": self.status.value,
            "interface": self.interface,
            "filter": self.filter,
            "packet_rate": self._packet_count,
            "alerts": len(self.alerts),
        }
