"""
Auth Monitor Sensor
🔐 Monitors authentication attempts and failures
Analogia: "Trzask gałęzi" (Crack of a branch)
"""

import re
import threading
import time
from collections import defaultdict
from typing import Any

from ..base import BaseSensor, SensorStatus


class AuthMonitor(BaseSensor):
    """
    Monitors authentication logs for failed login attempts,
    brute force attacks, and suspicious authentication patterns
    """

    def __init__(self, name: str = "auth_monitor", config: dict[str, Any] = None):
        """
        Initialize Auth Monitor

        Config options:
            - log_files: List of auth log files to monitor (default: ['/var/log/auth.log'])
            - failure_threshold: Failed attempts to trigger alert (default: 5)
            - time_window: Time window in seconds for counting failures (default: 300)
            - check_interval: Seconds between checks (default: 60)
        """
        super().__init__(name, config)
        self.log_files = self.config.get("log_files", ["/var/log/auth.log", "/var/log/secure"])
        self.failure_threshold = self.config.get("failure_threshold", 5)
        self.time_window = self.config.get("time_window", 300)
        self.check_interval = self.config.get("check_interval", 60)

        self._monitor_thread = None
        self._stop_flag = False
        self._last_position = {}  # Track position in each log file
        self._failure_counts = defaultdict(int)  # Track failures by IP/user

    def start(self) -> bool:
        """Start auth monitoring"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("Auth monitor already running")
            return False

        try:
            # Initialize log positions
            self._initialize_log_positions()

            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_auth, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info("Started auth monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start auth monitor: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop auth monitoring"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped auth monitoring")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping auth monitor: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single auth log check"""
        try:
            events = self._parse_new_log_entries()

            return {"status": "success", "events_found": len(events), "events": events[:10]}  # Return first 10

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_auth(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                # Parse new log entries
                events = self._parse_new_log_entries()

                # Analyze events
                for event in events:
                    self._analyze_auth_event(event)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in auth monitoring: {e}")
                time.sleep(self.check_interval)

    def _initialize_log_positions(self):
        """Initialize position tracking for log files"""
        for log_file in self.log_files:
            try:
                with open(log_file) as f:
                    # Seek to end of file
                    f.seek(0, 2)
                    self._last_position[log_file] = f.tell()
            except FileNotFoundError:
                self.logger.debug(f"Log file not found: {log_file}")
            except PermissionError:
                self.logger.warning(f"Permission denied for log file: {log_file}")
            except Exception as e:
                self.logger.error(f"Error initializing log position for {log_file}: {e}")

    def _parse_new_log_entries(self) -> list:
        """
        Parse new entries from auth logs

        Returns:
            List of auth events
        """
        events = []

        for log_file in self.log_files:
            try:
                with open(log_file) as f:
                    # Seek to last position
                    start_position = self._last_position.get(log_file, 0)
                    f.seek(start_position)

                    # Read new lines
                    for line in f:
                        event = self._parse_auth_line(line)
                        if event:
                            events.append(event)

                    # Update position
                    self._last_position[log_file] = f.tell()

            except FileNotFoundError:
                pass
            except PermissionError:
                pass
            except Exception as e:
                self.logger.error(f"Error parsing log file {log_file}: {e}")

        return events

    def _parse_auth_line(self, line: str) -> dict[str, Any]:
        """
        Parse a single auth log line

        Args:
            line: Log line

        Returns:
            Parsed event dict or None
        """
        event = None

        # Failed password patterns
        failed_patterns = [
            r"Failed password for (?:invalid user )?(\S+) from (\S+)",
            r"authentication failure.*user=(\S+).*rhost=(\S+)",
            r"FAILED LOGIN.*FROM (\S+).*user (\S+)",
        ]

        for pattern in failed_patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    event = {"type": "failed_login", "user": groups[0], "source": groups[1], "raw": line.strip()}
                    break

        # Successful login patterns
        if not event:
            success_patterns = [
                r"Accepted (?:password|publickey) for (\S+) from (\S+)",
                r"session opened for user (\S+)",
            ]

            for pattern in success_patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    event = {
                        "type": "successful_login",
                        "user": groups[0],
                        "source": groups[1] if len(groups) > 1 else "local",
                        "raw": line.strip(),
                    }
                    break

        # Root login attempts
        if "root" in line.lower() and "login" in line.lower():
            if not event:
                event = {}
            event["root_login_attempt"] = True

        return event

    def _analyze_auth_event(self, event: dict[str, Any]):
        """
        Analyze authentication event

        Args:
            event: Event details
        """
        event_type = event.get("type")
        user = event.get("user", "unknown")
        source = event.get("source", "unknown")

        if event_type == "failed_login":
            # Track failed attempts
            key = f"{source}:{user}"
            self._failure_counts[key] += 1

            # Check if threshold exceeded
            if self._failure_counts[key] >= self.failure_threshold:
                severity = "CRITICAL" if event.get("root_login_attempt") else "WARNING"

                self.raise_alert(
                    severity,
                    f"Multiple failed login attempts: {user} from {source} " f"({self._failure_counts[key]} attempts)",
                    {
                        "user": user,
                        "source": source,
                        "failure_count": self._failure_counts[key],
                        "threshold": self.failure_threshold,
                    },
                )

                # Reset counter after alert
                self._failure_counts[key] = 0

        elif event_type == "successful_login":
            # Alert on root login
            if event.get("root_login_attempt") or user == "root":
                self.raise_alert("WARNING", f"Root login: {user} from {source}", event)

    def get_statistics(self) -> dict[str, Any]:
        """Get auth monitoring statistics"""
        return {
            "status": self.status.value,
            "log_files": self.log_files,
            "failure_threshold": self.failure_threshold,
            "time_window": self.time_window,
            "active_trackers": len(self._failure_counts),
            "alerts": len(self.alerts),
        }
