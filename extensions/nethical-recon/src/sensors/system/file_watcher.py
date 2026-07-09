"""
File Watcher Sensor
📁 Monitors file integrity and changes (AIDE/Tripwire-like)
Analogia: "Ślady na ziemi" (Footprints on the ground)
"""

import hashlib
import os
import threading
import time
from typing import Any

from ..base import BaseSensor, SensorStatus


class FileWatcher(BaseSensor):
    """
    Monitors files and directories for unauthorized changes
    Detects modifications, creations, and deletions
    """

    def __init__(self, name: str = "file_watcher", config: dict[str, Any] = None):
        """
        Initialize File Watcher

        Config options:
            - watch_paths: List of paths to monitor (default: ['/etc', '/usr/bin'])
            - check_interval: Seconds between checks (default: 300)
            - hash_algorithm: Hash algorithm to use (default: 'sha256')
            - recursive: Watch directories recursively (default: True)
        """
        super().__init__(name, config)
        self.watch_paths = self.config.get("watch_paths", ["/etc"])
        self.check_interval = self.config.get("check_interval", 300)
        self.hash_algorithm = self.config.get("hash_algorithm", "sha256")
        self.recursive = self.config.get("recursive", True)

        self._monitor_thread = None
        self._stop_flag = False
        self._file_hashes = {}  # Store file hashes
        self._baseline_established = False

    def start(self) -> bool:
        """Start file watching"""
        if self.status == SensorStatus.RUNNING:
            self.logger.warning("File watcher already running")
            return False

        try:
            # Establish baseline if not already done
            if not self._baseline_established:
                self.logger.info("Establishing file integrity baseline...")
                self._establish_baseline()

            self._stop_flag = False
            self._monitor_thread = threading.Thread(target=self._monitor_files, daemon=True)
            self._monitor_thread.start()

            self.status = SensorStatus.RUNNING
            self.logger.info(f"Started file watching on {len(self.watch_paths)} paths")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start file watcher: {e}")
            self.status = SensorStatus.ERROR
            return False

    def stop(self) -> bool:
        """Stop file watching"""
        if self.status != SensorStatus.RUNNING:
            return False

        try:
            self._stop_flag = True

            # Wait for monitor thread
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)

            self.status = SensorStatus.STOPPED
            self.logger.info("Stopped file watching")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping file watcher: {e}")
            return False

    def check(self) -> dict[str, Any]:
        """Perform a single file integrity check"""
        try:
            changes = self._detect_changes()

            return {"status": "success", "files_monitored": len(self._file_hashes), "changes": changes}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _monitor_files(self):
        """Internal monitoring loop"""
        while not self._stop_flag:
            try:
                # Detect changes
                changes = self._detect_changes()

                # Handle detected changes
                for change in changes:
                    self._handle_file_change(change)

                # Sleep for check interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in file monitoring: {e}")
                time.sleep(self.check_interval)

    def _establish_baseline(self):
        """Establish baseline file hashes"""
        try:
            self._file_hashes.clear()

            for watch_path in self.watch_paths:
                if not os.path.exists(watch_path):
                    self.logger.warning(f"Watch path does not exist: {watch_path}")
                    continue

                if os.path.isfile(watch_path):
                    # Single file
                    file_hash = self._calculate_hash(watch_path)
                    if file_hash:
                        self._file_hashes[watch_path] = file_hash

                elif os.path.isdir(watch_path):
                    # Directory
                    files = self._get_files_in_directory(watch_path)
                    for file_path in files:
                        file_hash = self._calculate_hash(file_path)
                        if file_hash:
                            self._file_hashes[file_path] = file_hash

            self._baseline_established = True
            self.logger.info(f"Baseline established for {len(self._file_hashes)} files")

        except Exception as e:
            self.logger.error(f"Error establishing baseline: {e}")

    def _get_files_in_directory(self, directory: str) -> set[str]:
        """
        Get all files in a directory

        Args:
            directory: Directory path

        Returns:
            Set of file paths
        """
        files = set()

        try:
            if self.recursive:
                for root, _, filenames in os.walk(directory):
                    for filename in filenames:
                        files.add(os.path.join(root, filename))
            else:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        files.add(item_path)
        except PermissionError:
            self.logger.debug(f"Permission denied: {directory}")
        except Exception as e:
            self.logger.error(f"Error listing directory {directory}: {e}")

        return files

    def _calculate_hash(self, file_path: str) -> str:
        """
        Calculate hash of a file

        Args:
            file_path: Path to file

        Returns:
            Hash string or None if error
        """
        try:
            hasher = hashlib.new(self.hash_algorithm)

            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                while chunk := f.read(8192):
                    hasher.update(chunk)

            return hasher.hexdigest()

        except PermissionError:
            return None
        except Exception as e:
            self.logger.debug(f"Error hashing {file_path}: {e}")
            return None

    def _detect_changes(self) -> list:
        """
        Detect changes to monitored files

        Returns:
            List of changes detected
        """
        changes = []
        current_files = set()

        try:
            # Scan all watch paths
            for watch_path in self.watch_paths:
                if not os.path.exists(watch_path):
                    continue

                if os.path.isfile(watch_path):
                    current_files.add(watch_path)
                    # Check if modified
                    current_hash = self._calculate_hash(watch_path)
                    if current_hash and watch_path in self._file_hashes:
                        if current_hash != self._file_hashes[watch_path]:
                            changes.append(
                                {
                                    "type": "modified",
                                    "path": watch_path,
                                    "old_hash": self._file_hashes[watch_path],
                                    "new_hash": current_hash,
                                }
                            )
                            # Update hash
                            self._file_hashes[watch_path] = current_hash
                    elif current_hash and watch_path not in self._file_hashes:
                        changes.append({"type": "created", "path": watch_path, "hash": current_hash})
                        self._file_hashes[watch_path] = current_hash

                elif os.path.isdir(watch_path):
                    dir_files = self._get_files_in_directory(watch_path)
                    current_files.update(dir_files)

                    # Check each file
                    for file_path in dir_files:
                        current_hash = self._calculate_hash(file_path)
                        if not current_hash:
                            continue

                        if file_path in self._file_hashes:
                            # Check if modified
                            if current_hash != self._file_hashes[file_path]:
                                changes.append(
                                    {
                                        "type": "modified",
                                        "path": file_path,
                                        "old_hash": self._file_hashes[file_path],
                                        "new_hash": current_hash,
                                    }
                                )
                                self._file_hashes[file_path] = current_hash
                        else:
                            # New file
                            changes.append({"type": "created", "path": file_path, "hash": current_hash})
                            self._file_hashes[file_path] = current_hash

            # Check for deleted files
            baseline_files = set(self._file_hashes.keys())
            deleted_files = baseline_files - current_files

            for file_path in deleted_files:
                changes.append({"type": "deleted", "path": file_path, "old_hash": self._file_hashes[file_path]})
                del self._file_hashes[file_path]

        except Exception as e:
            self.logger.error(f"Error detecting changes: {e}")

        return changes

    def _handle_file_change(self, change: dict[str, Any]):
        """
        Handle detected file change

        Args:
            change: Change details
        """
        change_type = change.get("type")
        file_path = change.get("path")

        # Determine severity
        severity = "WARNING"

        # Critical paths
        critical_paths = ["/etc/passwd", "/etc/shadow", "/etc/sudoers", "/usr/bin/sudo"]
        if any(file_path.startswith(cp) for cp in critical_paths):
            severity = "CRITICAL"

        # Alert message
        if change_type == "modified":
            message = f"File modified: {file_path}"
        elif change_type == "created":
            message = f"File created: {file_path}"
        elif change_type == "deleted":
            message = f"File deleted: {file_path}"
        else:
            message = f"File change detected: {file_path}"

        self.raise_alert(severity, message, change)

    def get_statistics(self) -> dict[str, Any]:
        """Get file watching statistics"""
        return {
            "status": self.status.value,
            "watch_paths": self.watch_paths,
            "files_monitored": len(self._file_hashes),
            "check_interval": self.check_interval,
            "hash_algorithm": self.hash_algorithm,
            "baseline_established": self._baseline_established,
            "alerts": len(self.alerts),
        }
