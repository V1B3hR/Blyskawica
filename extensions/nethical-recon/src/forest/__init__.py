"""
forest/__init__.py
Forest module initialization - Infrastructure mapping as trees.

The Forest module maps infrastructure hierarchically:
- Forest: Entire infrastructure
- Trees: Hosts/servers
- Trunks: OS/kernel
- Crowns: Overview/monitoring
- Branches: Processes/services/connections
- Leaves: Threads/sessions/packets

Threats in the canopy:
- Crows: Malware
- Magpies: Data stealers
- Squirrels: Lateral movement
- Snakes: Rootkits
- Parasites: Cryptominers
- Bats: Night attacks
"""

from .base import ComponentStatus, ForestBase, ForestComponent

# Import new features
from .graph_export import GraphExporter
from .health_check import HealthChecker
from .manager import ForestManager
from .snapshot import ForestDiff, ForestSnapshot, ForestSnapshotManager

# Import threat components
from .threats import (
    BaseThreat,
    Bat,
    Crow,
    Magpie,
    Parasite,
    Snake,
    Squirrel,
    ThreatDetector,
    ThreatSeverity,
    ThreatType,
)

# Import tree components
from .trees import Branch, BranchType, Crown, ForestMap, Leaf, LeafType, Tree, Trunk
from .websocket_updates import ForestEvent, ForestWebSocketBridge, ForestWebSocketManager

__all__ = [
    # Base classes
    "ForestBase",
    "ForestComponent",
    "ComponentStatus",
    # Management
    "ForestManager",
    "HealthChecker",
    # Tree components
    "Tree",
    "Trunk",
    "Branch",
    "BranchType",
    "Leaf",
    "LeafType",
    "Crown",
    "ForestMap",
    # Threat components
    "BaseThreat",
    "ThreatType",
    "ThreatSeverity",
    "Crow",
    "Magpie",
    "Squirrel",
    "Snake",
    "Parasite",
    "Bat",
    "ThreatDetector",
    # New features
    "GraphExporter",
    "ForestWebSocketManager",
    "ForestWebSocketBridge",
    "ForestEvent",
    "ForestSnapshot",
    "ForestDiff",
    "ForestSnapshotManager",
]
