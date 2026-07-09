"""
forest/trees/branch.py
Branch class - represents a process, service, or connection.

A branch can represent:
- A system process
- A network service
- A network connection
"""

from enum import Enum
from typing import Any

from ..base import ForestComponent


class BranchType(Enum):
    """Type of branch"""

    PROCESS = "process"
    SERVICE = "service"
    CONNECTION = "connection"
    UNKNOWN = "unknown"


class Branch(ForestComponent):
    """
    Represents a process, service, or connection on a host.

    Analogia: 🌿 Gałąź - Processes and services growing from the tree
    """

    def __init__(self, branch_id: str, name: str, branch_type: BranchType, metadata: dict[str, Any] | None = None):
        """
        Initialize a branch.

        Args:
            branch_id: Unique identifier
            name: Name of process/service/connection
            branch_type: Type of branch (PROCESS, SERVICE, CONNECTION)
            metadata: Additional metadata
        """
        super().__init__(branch_id, name, metadata)
        self.branch_type = branch_type
        self.leaves = {}  # leaf_id -> Leaf (threads, sessions, packets)

        # Process-specific attributes
        self.pid = metadata.get("pid") if metadata else None
        self.user = metadata.get("user", "Unknown") if metadata else "Unknown"
        self.command = metadata.get("command", "") if metadata else ""

        # Service-specific attributes
        self.port = metadata.get("port") if metadata else None
        self.protocol = metadata.get("protocol", "TCP") if metadata else "TCP"

        # Connection-specific attributes
        self.remote_ip = metadata.get("remote_ip") if metadata else None
        self.remote_port = metadata.get("remote_port") if metadata else None
        self.local_port = metadata.get("local_port") if metadata else None

        # Resource usage
        self.cpu_percent = 0.0
        self.memory_mb = 0.0

    def get_type(self) -> str:
        """Return component type"""
        return "branch"

    def add_leaf(self, leaf):
        """Add a leaf (thread/session/packet) to this branch"""
        self.leaves[leaf.component_id] = leaf

    def remove_leaf(self, leaf_id: str):
        """Remove a leaf from this branch"""
        if leaf_id in self.leaves:
            del self.leaves[leaf_id]

    def get_leaf(self, leaf_id: str):
        """Get a specific leaf by ID"""
        return self.leaves.get(leaf_id)

    def get_all_leaves(self) -> list:
        """Get all leaves on this branch"""
        return list(self.leaves.values())

    def update_resources(self, cpu_percent: float = None, memory_mb: float = None):
        """Update resource usage"""
        if cpu_percent is not None:
            self.cpu_percent = cpu_percent
        if memory_mb is not None:
            self.memory_mb = memory_mb

    def get_info(self) -> dict[str, Any]:
        """Get branch information as dictionary"""
        info = super().get_info()
        info.update(
            {
                "branch_type": self.branch_type.value,
                "leaf_count": len(self.leaves),
                "cpu_percent": self.cpu_percent,
                "memory_mb": self.memory_mb,
            }
        )

        # Add type-specific info
        if self.branch_type == BranchType.PROCESS:
            info.update({"pid": self.pid, "user": self.user, "command": self.command})
        elif self.branch_type == BranchType.SERVICE:
            info.update({"port": self.port, "protocol": self.protocol})
        elif self.branch_type == BranchType.CONNECTION:
            info.update({"remote_ip": self.remote_ip, "remote_port": self.remote_port, "local_port": self.local_port})

        return info

    def __str__(self):
        threat_marker = f" ⚠️{self.get_threat_count()}" if self.has_threats() else ""

        if self.branch_type == BranchType.PROCESS:
            return f"🌿 Branch (Process): {self.name} [PID: {self.pid}]{threat_marker}"
        elif self.branch_type == BranchType.SERVICE:
            return f"🌿 Branch (Service): {self.name} [Port: {self.port}]{threat_marker}"
        elif self.branch_type == BranchType.CONNECTION:
            return f"🌿 Branch (Connection): {self.remote_ip}:{self.remote_port}{threat_marker}"
        else:
            return f"🌿 Branch: {self.name}{threat_marker}"
