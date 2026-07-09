"""
forest/threats/snake.py
Snake threat - represents rootkits.

The snake:
- Climbs up the trunk (privilege escalation)
- Hides in the bark (kernel-level hiding)
- Silent and deadly
"""

from typing import Any

from .base import BaseThreat, ThreatSeverity, ThreatType


class Snake(BaseThreat):
    """
    Snake threat - Rootkit.

    Analogia: 🐍 Wąż - Pnie się po pniu i ukrywa w korze
    """

    def __init__(
        self,
        threat_id: str,
        name: str,
        severity: ThreatSeverity = ThreatSeverity.CRITICAL,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize a Snake threat.

        Args:
            threat_id: Unique identifier
            name: Rootkit name/type
            severity: Severity level (default: CRITICAL)
            metadata: Additional metadata
        """
        super().__init__(threat_id, name, ThreatType.SNAKE, severity, metadata)

        # Snake-specific attributes
        self.rootkit_type = metadata.get("rootkit_type", "unknown") if metadata else "unknown"
        self.privilege_level = metadata.get("privilege_level", "user") if metadata else "user"
        self.kernel_level = metadata.get("kernel_level", False) if metadata else False

        # Hiding capabilities
        self.hidden_processes = []
        self.hidden_files = []
        self.hidden_network = []

        # Escalation path
        self.escalation_method = metadata.get("escalation_method") if metadata else None

    def get_description(self) -> str:
        """Get description of the Snake threat"""
        level = "kernel-level" if self.kernel_level else f"{self.privilege_level}-level"
        return (
            f"Rootkit detected: {self.name} ({self.rootkit_type}). "
            f"This snake operates at {level} and is hiding deep in the system. "
            f"{'Escalation method: ' + self.escalation_method if self.escalation_method else 'Escalation method unknown.'}"
        )

    def get_behavior_pattern(self) -> str:
        """Get characteristic behavior pattern"""
        behaviors = [f"Type: {self.rootkit_type}", f"Level: {self.privilege_level}"]

        if self.kernel_level:
            behaviors.append("⚠️ KERNEL-LEVEL!")
        if self.hidden_processes:
            behaviors.append(f"Hidden processes: {len(self.hidden_processes)}")
        if self.hidden_files:
            behaviors.append(f"Hidden files: {len(self.hidden_files)}")
        if self.hidden_network:
            behaviors.append(f"Hidden connections: {len(self.hidden_network)}")

        return " | ".join(behaviors)

    def add_hidden_process(self, process_name: str, pid: int):
        """
        Record a hidden process.

        Args:
            process_name: Name of the hidden process
            pid: Process ID
        """
        hidden = {"name": process_name, "pid": pid}
        self.hidden_processes.append(hidden)
        self.add_indicator(f"{process_name} (PID: {pid})", "hidden_process")

    def add_hidden_file(self, file_path: str):
        """
        Record a hidden file.

        Args:
            file_path: Path to hidden file
        """
        self.hidden_files.append(file_path)
        self.add_indicator(file_path, "hidden_file")

    def add_hidden_network(self, connection: str):
        """
        Record a hidden network connection.

        Args:
            connection: Description of hidden connection
        """
        self.hidden_network.append(connection)
        self.add_indicator(connection, "hidden_network")

    def escalate_privilege(self, new_level: str):
        """
        Record privilege escalation.

        Args:
            new_level: New privilege level (user, admin, root, kernel)
        """
        old_level = self.privilege_level
        self.privilege_level = new_level

        if new_level == "kernel":
            self.kernel_level = True
            self.severity = ThreatSeverity.CRITICAL

        self.add_indicator(f"{old_level} -> {new_level}", "privilege_escalation")

    def __str__(self):
        base_str = super().__str__()
        if self.kernel_level:
            base_str += " [KERNEL-LEVEL]"
        return base_str
