"""
Resource Monitor Sensor
📈 Monitors CPU/RAM usage and resource spikes
Analogia: "Nerwowe ruchy" (Nervous movements)
"""

import threading
import time
from typing import Any

import psutil

from ..base import BaseSensor, SensorStatus


class ResourceMonitor(BaseSensor):
    """
    Monitors system resource usage (CPU, RAM, disk, network)
    Detects anomalous spikes that may indicate attacks or issues
    """

    def __init__(self, name: str = "resource_monitor", config: dict[str, Any] = None):
        """
        Initialize Resource Monitor

        Config options:
            - cpu_threshold: CPU usage % to trigger alert (default: 90)
            - memory_threshold: Memory usage % to trigger alert (default: 90)
            - disk_threshold: Disk usage % to trigger alert (default: 90)
            - check_interval: Seconds between checks (default: 10)
        """
        super().__init__(name, config)
        self.cpu_threshold = self.config.get("cpu_threshold", 90)
        self.memory_threshold = self.config.get("memory_threshold", 90)
        self.disk_threshold = self.config.get("disk_threshold", 90)
        self.check_interval = self.config.get("check_interval", 10)

        self._monitor_thread = None
        self._stop_flag = False
        self._baseline = {}  # Store baseline metrics

    def start(self) -> bool:
        """Start resource monitoring"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Resource monitor already running")
            return False

        try:
            # Establish baseline
            self._establish_baseline()

            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info("Started resource monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start resource monitor: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop resource monitoring"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped resource monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping resource monitor: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single resource check"""
        try:
            metrics = self._get_current_metrics()

            return {
                "status": "success",
                "metrics": metrics,
                "thresholds": {"cpu": self.cpu_threshold, "memory": self.memory_threshold, "disk": self.disk_threshold},
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_resources(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                metrics = self._get_current_metrics()

                # Check for threshold violations
                self._check_thresholds(metrics)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in resource monitoring: {e}")
                time.sleep(self.check_interval)

    def _establish_baseline(self):
        """Establish baseline resource usage"""
        try:
            # Take 3 samples over 6 seconds
            samples = []
            for _ in range(3):
                samples.append(self._get_current_metrics())
                time.sleep(2)

            # Calculate average
            self._baseline = {
                "cpu": sum(s["cpu_percent"] for s in samples) / len(samples),
                "memory": sum(s["memory_percent"] for s in samples) / len(samples),
            }

            self.logger.info(
                f"Baseline established: CPU={self._baseline['cpu']:.1f}%, " f"Memory={self._baseline['memory']:.1f}%"
            )
        except Exception as e:
            self.logger.warning(f"Could not establish baseline: {e}")
            self._baseline = {}

    def _get_current_metrics(self) -> dict[str, Any]:
        """
        Get current system resource metrics

        Returns:
            Dictionary with current metrics
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "disk_percent": psutil.disk_usage("/").percent,
            "disk_used_gb": psutil.disk_usage("/").used / (1024**3),
            "disk_total_gb": psutil.disk_usage("/").total / (1024**3),
            "network_sent_mb": psutil.net_io_counters().bytes_sent / (1024**2),
            "network_recv_mb": psutil.net_io_counters().bytes_recv / (1024**2),
        }

    def _check_thresholds(self, metrics: dict[str, Any]):
        """
        Check if metrics exceed thresholds

        Args:
            metrics: Current metrics
        """
        # Check CPU threshold
        if metrics["cpu_percent"] > self.cpu_threshold:
            self.raise_alert(
                "CRITICAL" if metrics["cpu_percent"] > 95 else "WARNING",
                f"High CPU usage: {metrics['cpu_percent']:.1f}%",
                {
                    "cpu_percent": metrics["cpu_percent"],
                    "threshold": self.cpu_threshold,
                    "baseline": self._baseline.get("cpu"),
                },
            )

        # Check memory threshold
        if metrics["memory_percent"] > self.memory_threshold:
            self.raise_alert(
                "CRITICAL" if metrics["memory_percent"] > 95 else "WARNING",
                f"High memory usage: {metrics['memory_percent']:.1f}%",
                {
                    "memory_percent": metrics["memory_percent"],
                    "memory_used_gb": metrics["memory_used_gb"],
                    "threshold": self.memory_threshold,
                    "baseline": self._baseline.get("memory"),
                },
            )

        # Check disk threshold
        if metrics["disk_percent"] > self.disk_threshold:
            self.raise_alert(
                "WARNING",
                f"High disk usage: {metrics['disk_percent']:.1f}%",
                {
                    "disk_percent": metrics["disk_percent"],
                    "disk_used_gb": metrics["disk_used_gb"],
                    "threshold": self.disk_threshold,
                },
            )

        # Check for anomalous spikes (if baseline established)
        if self._baseline:
            cpu_spike = metrics["cpu_percent"] - self._baseline["cpu"]
            if cpu_spike > 50:  # 50% spike from baseline
                self.raise_alert(
                    "WARNING",
                    f"CPU spike detected: +{cpu_spike:.1f}% from baseline",
                    {"current": metrics["cpu_percent"], "baseline": self._baseline["cpu"], "spike": cpu_spike},
                )

            mem_spike = metrics["memory_percent"] - self._baseline["memory"]
            if mem_spike > 30:  # 30% spike from baseline
                self.raise_alert(
                    "WARNING",
                    f"Memory spike detected: +{mem_spike:.1f}% from baseline",
                    {"current": metrics["memory_percent"], "baseline": self._baseline["memory"], "spike": mem_spike},
                )

    def get_statistics(self) -> dict[str, Any]:
        """Get resource monitoring statistics"""
        try:
            current_metrics = self._get_current_metrics()
        except Exception:
            current_metrics = {}

        return {
            "status": self.status.value,
            "thresholds": {"cpu": self.cpu_threshold, "memory": self.memory_threshold, "disk": self.disk_threshold},
            "baseline": self._baseline,
            "current_metrics": current_metrics,
            "alerts": len(self.alerts),
        }

    def get_top_processes(self, limit: int = 10) -> list:
        """
        Get top processes by resource usage

        Args:
            limit: Number of processes to return

        Returns:
            List of process info dictionaries
        """
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort by CPU usage
            processes.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
            return processes[:limit]
        except Exception as e:
            self.logger.error(f"Error getting top processes: {e}")
            return []
