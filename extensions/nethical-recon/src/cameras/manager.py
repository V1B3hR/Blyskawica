"""
Camera Manager
Orchestrates multiple cameras (IR scanners) and manages their lifecycle
"""

import logging
import threading
from typing import Any

from .base import BaseCamera, CameraStatus


class CameraManager:
    """
    Manages multiple cameras, coordinates their scanning operations,
    and aggregates their discoveries.

    Think of this as the "Control Room" where all IR cameras feed their
    night vision data back to the hunter.
    """

    def __init__(self):
        """Initialize the Camera Manager"""
        self.cameras: dict[str, BaseCamera] = {}
        self.logger = logging.getLogger("nethical.camera_manager")
        self._initialize_logger()
        self._scan_threads: dict[str, threading.Thread] = {}

    def _initialize_logger(self):
        """Initialize logging for the manager"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [📷 CameraManager] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_camera(self, camera: BaseCamera) -> bool:
        """
        Register a new camera

        Args:
            camera: Camera instance to register

        Returns:
            bool: True if registered successfully
        """
        if camera.name in self.cameras:
            self.logger.warning(f"Camera {camera.name} already registered")
            return False

        self.cameras[camera.name] = camera
        self.logger.info(f"Registered camera: {camera.name} (mode: {camera.mode.value})")
        return True

    def unregister_camera(self, name: str) -> bool:
        """
        Unregister a camera

        Args:
            name: Name of the camera to unregister

        Returns:
            bool: True if unregistered successfully
        """
        if name not in self.cameras:
            self.logger.warning(f"Camera {name} not found")
            return False

        # Stop camera if scanning
        camera = self.cameras[name]
        if camera.status == CameraStatus.SCANNING:
            camera.stop()

        del self.cameras[name]
        self.logger.info(f"Unregistered camera: {name}")
        return True

    def scan_with_camera(self, name: str, target: str, async_mode: bool = False) -> dict[str, Any] | None:
        """
        Perform a scan with a specific camera

        Args:
            name: Name of the camera to use
            target: Target to scan
            async_mode: If True, scan in background thread

        Returns:
            Dict with scan results (None if async mode or error)
        """
        if name not in self.cameras:
            self.logger.error(f"Camera {name} not found")
            return None

        camera = self.cameras[name]

        if async_mode:
            # Run scan in background thread
            thread = threading.Thread(target=self._scan_worker, args=(camera, target), daemon=True)
            thread.start()
            self._scan_threads[name] = thread
            self.logger.info(f"Started async scan with {name} on {target}")
            return None
        else:
            # Run scan synchronously
            try:
                camera.start(target)
                results = camera.scan(target)
                camera.stop()
                self.logger.info(f"Completed scan with {name} on {target}")
                return results
            except Exception as e:
                self.logger.error(f"Scan failed with {name}: {e}")
                camera.stop()
                return None

    def _scan_worker(self, camera: BaseCamera, target: str):
        """Worker function for async scanning"""
        try:
            camera.start(target)
            camera.scan(target)
            camera.stop()
        except Exception as e:
            self.logger.error(f"Async scan failed with {camera.name}: {e}")
            camera.stop()

    def scan_all(self, target: str, async_mode: bool = False) -> dict[str, Any]:
        """
        Scan with all registered cameras

        Args:
            target: Target to scan
            async_mode: If True, run all scans in parallel

        Returns:
            Dict mapping camera names to their results
        """
        results = {}

        if async_mode:
            # Start all scans in parallel
            threads = []
            for name, camera in self.cameras.items():
                thread = threading.Thread(target=self._scan_worker, args=(camera, target), daemon=True)
                thread.start()
                threads.append((name, thread))

            # Wait for all to complete
            for name, thread in threads:
                thread.join(timeout=300)  # 5 minute timeout per camera
                if thread.is_alive():
                    self.logger.warning(f"Camera {name} scan timed out")

            # Collect results from discoveries
            for name, camera in self.cameras.items():
                results[name] = {
                    "discoveries": [d.to_dict() for d in camera.discoveries],
                    "statistics": camera.get_statistics(),
                }
        else:
            # Run scans sequentially
            for name, camera in self.cameras.items():
                result = self.scan_with_camera(name, target, async_mode=False)
                results[name] = result

        return results

    def stop_camera(self, name: str) -> bool:
        """
        Stop a specific camera

        Args:
            name: Name of the camera to stop

        Returns:
            bool: True if stopped successfully
        """
        if name not in self.cameras:
            self.logger.error(f"Camera {name} not found")
            return False

        camera = self.cameras[name]
        if camera.stop():
            self.logger.info(f"Stopped camera: {name}")
            return True
        else:
            self.logger.error(f"Failed to stop camera: {name}")
            return False

    def stop_all(self) -> bool:
        """
        Stop all cameras

        Returns:
            bool: True if all stopped successfully
        """
        success = True
        for name in self.cameras:
            if not self.stop_camera(name):
                success = False

        return success

    def get_camera_status(self, name: str) -> dict[str, Any] | None:
        """
        Get status of a specific camera

        Args:
            name: Name of the camera

        Returns:
            Dict with camera status
        """
        if name not in self.cameras:
            return None

        return self.cameras[name].get_status()

    def get_status_all(self) -> dict[str, dict[str, Any]]:
        """
        Get status of all cameras

        Returns:
            Dict mapping camera names to their status
        """
        return {name: camera.get_status() for name, camera in self.cameras.items()}

    def get_all_discoveries(self, severity: str | None = None) -> list[dict[str, Any]]:
        """
        Get all discoveries from all cameras

        Args:
            severity: Optional filter by severity

        Returns:
            List of all discoveries
        """
        all_discoveries = []

        for camera_name, camera in self.cameras.items():
            discoveries = camera.get_discoveries(severity=severity)
            for discovery in discoveries:
                disc_dict = discovery.to_dict()
                disc_dict["camera"] = camera_name
                disc_dict["mode"] = camera.mode.value
                all_discoveries.append(disc_dict)

        return all_discoveries

    def get_discoveries_by_camera(self, name: str, **filters) -> list[dict[str, Any]]:
        """
        Get discoveries from a specific camera

        Args:
            name: Camera name
            **filters: Additional filters (discovery_type, severity)

        Returns:
            List of discoveries
        """
        if name not in self.cameras:
            return []

        camera = self.cameras[name]
        discoveries = camera.get_discoveries(**filters)
        return [d.to_dict() for d in discoveries]

    def clear_all_discoveries(self):
        """Clear discoveries from all cameras"""
        for camera in self.cameras.values():
            camera.clear_discoveries()
        self.logger.info("Cleared all discoveries from all cameras")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get aggregated statistics from all cameras

        Returns:
            Dict with aggregated statistics
        """
        total_discoveries = 0
        by_camera = {}
        by_mode = {}
        by_severity = {"INFO": 0, "WARNING": 0, "CRITICAL": 0}

        for name, camera in self.cameras.items():
            stats = camera.get_statistics()
            by_camera[name] = stats["total_discoveries"]
            total_discoveries += stats["total_discoveries"]

            mode = camera.mode.value
            by_mode[mode] = by_mode.get(mode, 0) + stats["total_discoveries"]

            for sev, count in stats["by_severity"].items():
                by_severity[sev] += count

        return {
            "total_cameras": len(self.cameras),
            "total_discoveries": total_discoveries,
            "by_camera": by_camera,
            "by_mode": by_mode,
            "by_severity": by_severity,
        }

    def get_camera_by_mode(self, mode: str) -> list[BaseCamera]:
        """
        Get all cameras with a specific mode

        Args:
            mode: Camera mode (night, thermal, ghost, etc.)

        Returns:
            List of cameras with that mode
        """
        return [camera for camera in self.cameras.values() if camera.mode.value == mode]
