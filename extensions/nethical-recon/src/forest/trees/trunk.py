"""
forest/trees/trunk.py
Trunk class - represents the core OS/kernel of a host.

The trunk is the foundation of the tree, representing:
- Operating system
- Kernel
- Core system processes
"""

from typing import Any

from ..base import ForestComponent


class Trunk(ForestComponent):
    """
    Represents the OS/kernel core of a host.

    Analogia: 🪵 Pień - The foundation of the tree
    """

    def __init__(
        self,
        trunk_id: str,
        os_name: str,
        os_version: str,
        kernel_version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a trunk.

        Args:
            trunk_id: Unique identifier
            os_name: Operating system name (e.g., "Ubuntu", "Windows Server")
            os_version: OS version
            kernel_version: Kernel version
            metadata: Additional metadata
        """
        super().__init__(trunk_id, os_name, metadata)
        self.os_name = os_name
        self.os_version = os_version
        self.kernel_version = kernel_version or "Unknown"
        self.architecture = metadata.get("architecture", "Unknown") if metadata else "Unknown"
        self.boot_time = None
        self.uptime_seconds = 0

    def get_type(self) -> str:
        """Return component type"""
        return "trunk"

    def update_uptime(self, uptime_seconds: int):
        """Update system uptime"""
        self.uptime_seconds = uptime_seconds

    def get_uptime_display(self) -> str:
        """Get human-readable uptime"""
        days = self.uptime_seconds // 86400
        hours = (self.uptime_seconds % 86400) // 3600
        minutes = (self.uptime_seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def get_info(self) -> dict[str, Any]:
        """Get trunk information as dictionary"""
        info = super().get_info()
        info.update(
            {
                "os_name": self.os_name,
                "os_version": self.os_version,
                "kernel_version": self.kernel_version,
                "architecture": self.architecture,
                "uptime": self.get_uptime_display(),
            }
        )
        return info

    def __str__(self):
        return f"🪵 Trunk: {self.os_name} {self.os_version} (Kernel: {self.kernel_version})"
