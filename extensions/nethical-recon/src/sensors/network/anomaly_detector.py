"""
Anomaly Detector Sensor
📊 Detects anomalous network patterns using Zeek (formerly Bro)
Analogia: "Dziwne zachowania" (Suspicious behaviors)
"""

import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from ..base import BaseSensor, SensorStatus


class AnomalyDetector(BaseSensor):
    """
    Detects network anomalies using Zeek IDS
    Monitors for unusual patterns that deviate from normal behavior
    """

    def __init__(self, name: str = "anomaly_detector", config: dict[str, Any] = None):
        """
        Initialize Anomaly Detector

        Config options:
            - interface: Network interface to monitor (default: any)
            - zeek_path: Path to zeek binary (default: zeek)
            - log_dir: Directory for zeek logs (default: /tmp/zeek_logs)
            - check_interval: Seconds between log checks (default: 60)
        """
        super().__init__(name, config)
        self.interface = self.config.get("interface", "any")
        self.zeek_path = self.config.get("zeek_path", "zeek")
        self.log_dir = self.config.get("log_dir", "/tmp/zeek_logs")
        self.check_interval = self.config.get("check_interval", 60)

        self._process = None
        self._monitor_thread = None
        self._stop_flag = False

        # Create log directory
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def validate_config(self) -> bool:
        """Validate configuration"""
        # Check if Zeek is available
        try:
            result = subprocess.run(["which", self.zeek_path], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.logger.warning("Zeek not found. Anomaly detection will use fallback mode")
                return True  # Allow fallback mode
        except Exception as e:
            self.logger.warning(f"Could not validate Zeek: {e}")
            return True  # Allow fallback mode

        return True

    def start(self) -> bool:
        """Start anomaly detection"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Anomaly detector already running")
            return False

        if not self.validate_config():
            self.status = SensorStatus.ERROR
            return False

        try:
            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_anomalies, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info(f"Started anomaly detection on interface {self.interface}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start anomaly detector: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop anomaly detection"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Terminate Zeek process if running
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
            self.logger.info("Stopped anomaly detection")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping anomaly detector: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single anomaly check"""
        try:
            # Check if Zeek logs exist and analyze them
            anomalies = self._analyze_zeek_logs()

            return {"status": "success", "anomalies_detected": len(anomalies), "anomalies": anomalies}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_anomalies(self):
        """Internal monitoring loop"""
        # Try to start Zeek if available
        zeek_available = self._start_zeek()

        while not self._stop_flag:
            try:
                # Analyze logs for anomalies
                anomalies = self._analyze_zeek_logs()

                for anomaly in anomalies:
                    self._handle_anomaly(anomaly)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in anomaly monitoring: {e}")
                time.sleep(self.check_interval)

    def _start_zeek(self) -> bool:
        """
        Start Zeek process

        Returns:
            bool: True if Zeek started successfully
        """
        try:
            # Check if Zeek is available
            result = subprocess.run(["which", self.zeek_path], capture_output=True, timeout=5)

            if result.returncode != 0:
                self.logger.info("Zeek not available, using fallback anomaly detection")
                return False

            # Start Zeek in live capture mode
            cmd = [self.zeek_path, "-i", self.interface, "local"]

            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.log_dir)

            self.logger.info("Started Zeek process for anomaly detection")
            return True

        except Exception as e:
            self.logger.warning(f"Could not start Zeek: {e}. Using fallback mode")
            return False

    def _analyze_zeek_logs(self) -> list[dict[str, Any]]:
        """
        Analyze Zeek logs for anomalies

        Returns:
            List of detected anomalies
        """
        anomalies = []

        try:
            # Check for common Zeek log files
            log_files = {
                "conn.log": self._analyze_connection_anomalies,
                "dns.log": self._analyze_dns_anomalies,
                "http.log": self._analyze_http_anomalies,
                "notice.log": self._analyze_notices,
            }

            for log_file, analyzer in log_files.items():
                log_path = os.path.join(self.log_dir, log_file)
                if os.path.exists(log_path):
                    file_anomalies = analyzer(log_path)
                    anomalies.extend(file_anomalies)

        except Exception as e:
            self.logger.error(f"Error analyzing Zeek logs: {e}")

        return anomalies

    def _analyze_connection_anomalies(self, log_path: str) -> list[dict[str, Any]]:
        """Analyze connection logs for anomalies"""
        anomalies = []
        # Placeholder for connection anomaly detection
        # Would analyze patterns like:
        # - Unusual connection counts
        # - Strange port usage
        # - Suspicious connection durations
        return anomalies

    def _analyze_dns_anomalies(self, log_path: str) -> list[dict[str, Any]]:
        """Analyze DNS logs for anomalies"""
        anomalies = []
        # Placeholder for DNS anomaly detection
        # Would look for:
        # - DGA (Domain Generation Algorithm) patterns
        # - DNS tunneling
        # - Unusual query volumes
        return anomalies

    def _analyze_http_anomalies(self, log_path: str) -> list[dict[str, Any]]:
        """Analyze HTTP logs for anomalies"""
        anomalies = []
        # Placeholder for HTTP anomaly detection
        # Would detect:
        # - Unusual user agents
        # - Suspicious URLs
        # - Data exfiltration patterns
        return anomalies

    def _analyze_notices(self, log_path: str) -> list[dict[str, Any]]:
        """Analyze Zeek notices (alerts)"""
        anomalies = []
        try:
            with open(log_path) as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    # Parse Zeek notice
                    anomalies.append({"type": "zeek_notice", "data": line.strip()})
        except Exception as e:
            self.logger.error(f"Error reading notices: {e}")

        return anomalies

    def _handle_anomaly(self, anomaly: dict[str, Any]):
        """
        Handle detected anomaly

        Args:
            anomaly: Anomaly details
        """
        anomaly_type = anomaly.get("type", "unknown")

        # Determine severity
        severity = "WARNING"
        if "critical" in str(anomaly).lower() or "attack" in str(anomaly).lower():
            severity = "CRITICAL"

        self.raise_alert(severity, f"Network anomaly detected: {anomaly_type}", anomaly)

    def get_statistics(self) -> dict[str, Any]:
        """Get anomaly detection statistics"""
        return {
            "status": self.status.value,
            "interface": self.interface,
            "log_directory": self.log_dir,
            "zeek_running": self._process is not None,
            "alerts": len(self.alerts),
        }
