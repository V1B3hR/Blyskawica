"""
forest/trees/leaf.py
Leaf class - represents threads, sessions, or packets.

A leaf is the smallest unit in the forest hierarchy:
- Thread of a process
- Session of a connection
- Individual packet
"""

from enum import Enum
from typing import Any

from ..base import ForestComponent


class LeafType(Enum):
    """Type of leaf"""

    THREAD = "thread"
    SESSION = "session"
    PACKET = "packet"
    UNKNOWN = "unknown"


class Leaf(ForestComponent):
    """
    Represents a thread, session, or packet.

    Analogia: 🍃 Liść - The smallest unit, growing from branches
    """

    def __init__(self, leaf_id: str, name: str, leaf_type: LeafType, metadata: dict[str, Any] | None = None):
        """
        Initialize a leaf.

        Args:
            leaf_id: Unique identifier
            name: Name/description of the leaf
            leaf_type: Type of leaf (THREAD, SESSION, PACKET)
            metadata: Additional metadata
        """
        super().__init__(leaf_id, name, metadata)
        self.leaf_type = leaf_type

        # Thread-specific
        self.thread_id = metadata.get("thread_id") if metadata else None

        # Session-specific
        self.session_id = metadata.get("session_id") if metadata else None
        self.session_start = metadata.get("session_start") if metadata else None

        # Packet-specific
        self.packet_size = metadata.get("packet_size", 0) if metadata else 0
        self.source_ip = metadata.get("source_ip") if metadata else None
        self.dest_ip = metadata.get("dest_ip") if metadata else None

    def get_type(self) -> str:
        """Return component type"""
        return "leaf"

    def get_info(self) -> dict[str, Any]:
        """Get leaf information as dictionary"""
        info = super().get_info()
        info.update({"leaf_type": self.leaf_type.value})

        # Add type-specific info
        if self.leaf_type == LeafType.THREAD:
            info["thread_id"] = self.thread_id
        elif self.leaf_type == LeafType.SESSION:
            info.update({"session_id": self.session_id, "session_start": self.session_start})
        elif self.leaf_type == LeafType.PACKET:
            info.update({"packet_size": self.packet_size, "source_ip": self.source_ip, "dest_ip": self.dest_ip})

        return info

    def __str__(self):
        threat_marker = " ⚠️" if self.has_threats() else ""

        if self.leaf_type == LeafType.THREAD:
            return f"🍃 Leaf (Thread): {self.name} [TID: {self.thread_id}]{threat_marker}"
        elif self.leaf_type == LeafType.SESSION:
            return f"🍃 Leaf (Session): {self.session_id}{threat_marker}"
        elif self.leaf_type == LeafType.PACKET:
            return f"🍃 Leaf (Packet): {self.source_ip} → {self.dest_ip} ({self.packet_size}B){threat_marker}"
        else:
            return f"🍃 Leaf: {self.name}{threat_marker}"
