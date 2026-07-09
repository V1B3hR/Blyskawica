"""
forest/trees/tree.py
Tree class - represents a host or server in the infrastructure.

A tree has:
- Trunk: The core OS/kernel
- Crown: Overview and monitoring
- Branches: Processes, services, connections
"""

from typing import Any

from ..base import ComponentStatus, ForestComponent


class Tree(ForestComponent):
    """
    Represents a host/server in the infrastructure.

    Analogia: 🌳 Drzewo - Each host is a tree in the forest
    """

    def __init__(
        self,
        tree_id: str,
        hostname: str,
        ip_address: str,
        os_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a tree (host).

        Args:
            tree_id: Unique identifier for this tree
            hostname: Hostname of the server
            ip_address: IP address
            os_type: Operating system type
            metadata: Additional metadata
        """
        super().__init__(tree_id, hostname, metadata)
        self.hostname = hostname
        self.ip_address = ip_address
        self.os_type = os_type or "Unknown"

        # Components of the tree
        self.trunk = None  # Trunk (kernel/OS core)
        self.crown = None  # Crown (overview)
        self.branches = {}  # branch_id -> Branch

        # Tree statistics
        self.total_processes = 0
        self.total_connections = 0
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0

    def get_type(self) -> str:
        """Return component type"""
        return "tree"

    def set_trunk(self, trunk):
        """Set the trunk (kernel/OS core) of this tree"""
        self.trunk = trunk

    def set_crown(self, crown):
        """Set the crown (overview) of this tree"""
        self.crown = crown

    def add_branch(self, branch):
        """Add a branch (process/service/connection) to this tree"""
        self.branches[branch.component_id] = branch
        self.total_processes = len(self.branches)

    def remove_branch(self, branch_id: str):
        """Remove a branch from this tree"""
        if branch_id in self.branches:
            del self.branches[branch_id]
            self.total_processes = len(self.branches)

    def get_branch(self, branch_id: str):
        """Get a specific branch by ID"""
        return self.branches.get(branch_id)

    def get_all_branches(self) -> list:
        """Get all branches on this tree"""
        return list(self.branches.values())

    def get_branches_with_threats(self) -> list:
        """Get all branches that have threats"""
        return [b for b in self.branches.values() if b.has_threats()]

    def update_statistics(self, cpu: float = None, memory: float = None, disk: float = None):
        """
        Update tree statistics.

        Args:
            cpu: CPU usage percentage (0-100)
            memory: Memory usage percentage (0-100)
            disk: Disk usage percentage (0-100)
        """
        if cpu is not None:
            self.cpu_usage = max(0.0, min(100.0, cpu))
        if memory is not None:
            self.memory_usage = max(0.0, min(100.0, memory))
        if disk is not None:
            self.disk_usage = max(0.0, min(100.0, disk))

        # Auto-calculate health score based on resource usage
        self._calculate_health_score()

    def _calculate_health_score(self):
        """Calculate health score based on resources and threats"""
        # Start with 100
        score = 100.0

        # Deduct for high resource usage
        if self.cpu_usage > 90:
            score -= 20
        elif self.cpu_usage > 75:
            score -= 10

        if self.memory_usage > 90:
            score -= 20
        elif self.memory_usage > 75:
            score -= 10

        if self.disk_usage > 95:
            score -= 15
        elif self.disk_usage > 85:
            score -= 5

        # Deduct for threats
        threat_count = self.get_threat_count()
        if threat_count > 0:
            score -= min(30, threat_count * 10)  # Max 30 points for threats

        # Check branches for threats
        for branch in self.branches.values():
            if branch.has_threats():
                score -= 5  # Deduct for each threatened branch

        self.update_health_score(max(0.0, score))

        # Update status based on health
        if score >= 80:
            self.status = ComponentStatus.HEALTHY
        elif score >= 60:
            self.status = ComponentStatus.WARNING
        elif score >= 30:
            self.status = ComponentStatus.CRITICAL
        else:
            self.status = ComponentStatus.COMPROMISED

    def get_info(self) -> dict[str, Any]:
        """Get tree information as dictionary"""
        info = super().get_info()
        info.update(
            {
                "hostname": self.hostname,
                "ip_address": self.ip_address,
                "os_type": self.os_type,
                "total_branches": len(self.branches),
                "threatened_branches": len(self.get_branches_with_threats()),
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage,
                "disk_usage": self.disk_usage,
                "has_trunk": self.trunk is not None,
                "has_crown": self.crown is not None,
            }
        )
        return info

    def get_visual_representation(self) -> str:
        """Get ASCII art representation of the tree"""
        threat_marker = ""
        if self.has_threats():
            threat_marker = " ⚠️ THREATS!"

        lines = [f"        👑 Crown{threat_marker}", "         │", f"    🌳 {self.hostname}", "    ╱│╲", "   ╱ │ ╲"]

        # Show up to 5 branches
        branch_list = list(self.branches.values())[:5]
        for i, branch in enumerate(branch_list):
            threat_icon = "⚠️" if branch.has_threats() else "🌿"
            lines.append(f"  {threat_icon}  {threat_icon}  {threat_icon}  Branch: {branch.name[:20]}")

        if len(self.branches) > 5:
            lines.append(f"  ... and {len(self.branches) - 5} more branches")

        lines.append("    ║")
        lines.append(f"  🪵 Trunk ({self.os_type})")

        return "\n".join(lines)

    def __str__(self):
        threat_info = f" ⚠️{self.get_threat_count()} threats" if self.has_threats() else ""
        return f"🌳 Tree '{self.hostname}' ({self.ip_address}): {len(self.branches)} branches, Health: {self.health_score:.1f}%{threat_info}"
