"""
Heartbeat Monitor Sensor
💓 Monitors service availability and system pulse
Analogia: "Puls systemu" (System pulse)
"""

import socket
import subprocess
import threading
import time
from typing import Any

from ..base import BaseSensor, SensorStatus


class HeartbeatMonitor(BaseSensor):
    """
    Monitors availability of critical services and system health
    Detects when services go down or become unresponsive
    """

    def __init__(self, name: str = "heartbeat_monitor", config: dict[str, Any] = None):
        """
        Initialize Heartbeat Monitor

        Config options:
            - services: List of services to monitor (default: ['sshd', 'http'])
            - ports: List of (host, port) tuples to check (default: [])
            - check_interval: Seconds between heartbeat checks (default: 30)
            - timeout: Timeout for health checks in seconds (default: 5)
        """
        super().__init__(name, config)
        self.services = self.config.get("services", ["sshd"])
        self.ports = self.config.get("ports", [])
        self.check_interval = self.config.get("check_interval", 30)
        self.timeout = self.config.get("timeout", 5)

        self._monitor_thread = None
        self._stop_flag = False
        self._service_status = {}  # Track service status

    def start(self) -> bool:
        """Start heartbeat monitoring"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Heartbeat monitor already running")
            return False

        try:
            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_heartbeat, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info("Started heartbeat monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start heartbeat monitor: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop heartbeat monitoring"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped heartbeat monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping heartbeat monitor: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single heartbeat check"""
        try:
            results = {"services": {}, "ports": {}}

            # Check services
            for service in self.services:
                results["services"][service] = self._check_service(service)

            # Check ports
            for host, port in self.ports:
                results["ports"][f"{host}:{port}"] = self._check_port(host, port)

            return {"status": "success", "results": results}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_heartbeat(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                # Check all services
                for service in self.services:
                    is_running = self._check_service(service)
                    self._handle_service_status(service, is_running)

                # Check all ports
                for host, port in self.ports:
                    is_open = self._check_port(host, port)
                    self._handle_port_status(host, port, is_open)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in heartbeat monitoring: {e}")
                time.sleep(self.check_interval)

    def _check_service(self, service_name: str) -> bool:
        """
        Check if a system service is running

        Args:
            service_name: Name of the service

        Returns:
            bool: True if service is running
        """
        try:
            # Try systemctl first (systemd)
            result = subprocess.run(
                ["systemctl", "is-active", service_name], capture_output=True, text=True, timeout=self.timeout
            )

            return result.returncode == 0 and "active" in result.stdout

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Service check timeout for {service_name}")
            return False
        except FileNotFoundError:
            # Systemctl not available, try service command
            try:
                result = subprocess.run(
                    ["service", service_name, "status"], capture_output=True, text=True, timeout=self.timeout
                )
                return result.returncode == 0
            except Exception:
                return False
        except Exception as e:
            self.logger.error(f"Error checking service {service_name}: {e}")
            return False

    def _check_port(self, host: str, port: int) -> bool:
        """
        Check if a port is open/responsive

        Args:
            host: Hostname or IP address
            port: Port number

        Returns:
            bool: True if port is open
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            self.logger.error(f"Error checking port {host}:{port}: {e}")
            return False

    def _handle_service_status(self, service_name: str, is_running: bool):
        """
        Handle service status change

        Args:
            service_name: Name of the service
            is_running: Current running status
        """
        previous_status = self._service_status.get(service_name)
        self._service_status[service_name] = is_running

        # Alert on status change
        if previous_status is not None and previous_status != is_running:
            if is_running:
                self.raise_alert(
                    "INFO", f"Service {service_name} is back online", {"service": service_name, "status": "running"}
                )
            else:
                self.raise_alert(
                    "CRITICAL", f"Service {service_name} is down!", {"service": service_name, "status": "stopped"}
                )
        elif not is_running:
            # Service is down (first check or still down)
            self.raise_alert(
                "CRITICAL", f"Service {service_name} is not running", {"service": service_name, "status": "stopped"}
            )

    def _handle_port_status(self, host: str, port: int, is_open: bool):
        """
        Handle port status change

        Args:
            host: Hostname or IP
            port: Port number
            is_open: Current open status
        """
        port_key = f"{host}:{port}"
        previous_status = self._service_status.get(port_key)
        self._service_status[port_key] = is_open

        # Alert on status change
        if previous_status is not None and previous_status != is_open:
            if is_open:
                self.raise_alert(
                    "INFO", f"Port {port_key} is now accessible", {"host": host, "port": port, "status": "open"}
                )
            else:
                self.raise_alert(
                    "CRITICAL", f"Port {port_key} is not accessible!", {"host": host, "port": port, "status": "closed"}
                )

    def get_statistics(self) -> dict[str, Any]:
        """Get heartbeat monitoring statistics"""
        return {
            "status": self.status.value,
            "services_monitored": len(self.services),
            "ports_monitored": len(self.ports),
            "check_interval": self.check_interval,
            "current_status": self._service_status.copy(),
            "alerts": len(self.alerts),
        }
