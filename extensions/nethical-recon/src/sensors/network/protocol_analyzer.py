"""
Protocol Analyzer Sensor
🔬 Deep protocol analysis (Suricata-like functionality)
Analogia: "Analityk tropów" (Tracker analyst)
"""

import re
import subprocess
import threading
import time
from typing import Any

from ..base import BaseSensor, SensorStatus


class ProtocolAnalyzer(BaseSensor):
    """
    Performs deep packet inspection and protocol analysis
    Detects protocol violations and suspicious patterns
    """

    def __init__(self, name: str = "protocol_analyzer", config: dict[str, Any] = None):
        """
        Initialize Protocol Analyzer

        Config options:
            - interface: Network interface to monitor (default: any)
            - protocols: List of protocols to analyze (default: ['http', 'dns', 'tls'])
            - check_interval: Seconds between analysis cycles (default: 30)
        """
        super().__init__(name, config)
        self.interface = self.config.get("interface", "any")
        self.protocols = self.config.get("protocols", ["http", "dns", "tls"])
        self.check_interval = self.config.get("check_interval", 30)

        self._monitor_thread = None
        self._stop_flag = False

        # Protocol-specific analyzers
        self._analyzers = {"http": self._analyze_http, "dns": self._analyze_dns, "tls": self._analyze_tls}

    def start(self) -> bool:
        """Start protocol analysis"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Protocol analyzer already running")
            return False

        try:
            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_protocols, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info(f"Started protocol analysis on interface {self.interface}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start protocol analyzer: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop protocol analysis"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped protocol analysis")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping protocol analyzer: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single protocol analysis check"""
        try:
            results = {}

            for protocol in self.protocols:
                if protocol in self._analyzers:
                    results[protocol] = self._analyzers[protocol]()

            return {"status": "success", "protocols_analyzed": len(results), "results": results}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_protocols(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                # Analyze each configured protocol
                for protocol in self.protocols:
                    if protocol in self._analyzers:
                        findings = self._analyzers[protocol]()

                        # Handle any findings
                        for finding in findings.get("anomalies", []):
                            self._handle_protocol_anomaly(protocol, finding)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in protocol monitoring: {e}")
                time.sleep(self.check_interval)

    def _analyze_http(self) -> dict[str, Any]:
        """
        Analyze HTTP traffic

        Returns:
            Analysis results
        """
        anomalies = []

        try:
            # Capture HTTP traffic sample
            result = subprocess.run(
                [
                    "timeout",
                    "5",
                    "tcpdump",
                    "-i",
                    self.interface,
                    "-n",
                    "tcp",
                    "port",
                    "80",
                    "or",
                    "port",
                    "8080",
                    "-c",
                    "20",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            packets = result.stdout.split("\n")

            # Analyze for common HTTP anomalies
            for packet in packets:
                # Look for unusual HTTP methods
                if re.search(r"(TRACE|TRACK|DELETE|PUT)", packet):
                    anomalies.append({"type": "unusual_http_method", "data": packet})

                # Look for SQL injection attempts in URLs
                if re.search(r"(union|select|insert|drop|update)\s+(from|into|table)", packet, re.IGNORECASE):
                    anomalies.append({"type": "potential_sql_injection", "data": packet})

        except Exception as e:
            self.logger.debug(f"HTTP analysis error: {e}")

        return {
            "protocol": "http",
            "anomalies": anomalies,
            "packets_analyzed": len(packets) if "packets" in locals() else 0,
        }

    def _analyze_dns(self) -> dict[str, Any]:
        """
        Analyze DNS traffic

        Returns:
            Analysis results
        """
        anomalies = []

        try:
            # Capture DNS traffic sample
            result = subprocess.run(
                ["timeout", "5", "tcpdump", "-i", self.interface, "-n", "udp", "port", "53", "-c", "20"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            packets = result.stdout.split("\n")

            # Analyze for DNS anomalies
            for packet in packets:
                # Look for suspiciously long domain names (possible DGA or tunneling)
                if len(packet) > 200:
                    anomalies.append({"type": "suspicious_long_query", "data": packet[:100]})  # Truncate for logging

                # Look for unusual TLDs
                if re.search(r"\.(tk|ml|ga|cf|gq)\s", packet):
                    anomalies.append({"type": "suspicious_tld", "data": packet})

        except Exception as e:
            self.logger.debug(f"DNS analysis error: {e}")

        return {
            "protocol": "dns",
            "anomalies": anomalies,
            "packets_analyzed": len(packets) if "packets" in locals() else 0,
        }

    def _analyze_tls(self) -> dict[str, Any]:
        """
        Analyze TLS/SSL traffic

        Returns:
            Analysis results
        """
        anomalies = []

        try:
            # Capture TLS traffic sample
            result = subprocess.run(
                ["timeout", "5", "tcpdump", "-i", self.interface, "-n", "tcp", "port", "443", "-c", "20"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            packets = result.stdout.split("\n")

            # Basic TLS anomaly detection
            # In a real implementation, this would do deep TLS inspection
            # looking for weak ciphers, cert issues, etc.

        except Exception as e:
            self.logger.debug(f"TLS analysis error: {e}")

        return {
            "protocol": "tls",
            "anomalies": anomalies,
            "packets_analyzed": len(packets) if "packets" in locals() else 0,
        }

    def _handle_protocol_anomaly(self, protocol: str, finding: dict[str, Any]):
        """
        Handle detected protocol anomaly

        Args:
            protocol: Protocol name
            finding: Anomaly details
        """
        anomaly_type = finding.get("type", "unknown")

        # Determine severity
        severity = "INFO"
        if "injection" in anomaly_type or "attack" in anomaly_type:
            severity = "CRITICAL"
        elif "suspicious" in anomaly_type:
            severity = "WARNING"

        self.raise_alert(
            severity, f"Protocol anomaly in {protocol}: {anomaly_type}", {"protocol": protocol, "finding": finding}
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get protocol analysis statistics"""
        return {
            "status": self.status.value,
            "interface": self.interface,
            "protocols": self.protocols,
            "check_interval": self.check_interval,
            "alerts": len(self.alerts),
        }
