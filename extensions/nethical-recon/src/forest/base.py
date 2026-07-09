"""
forest/base.py
Base classes for the Forest infrastructure mapping system.

The Forest module maps infrastructure as a hierarchical tree structure:
- Forest: The entire infrastructure
- Trees: Individual hosts/servers
- Branches: Processes, services, connections
- Leaves: Threads, sessions, packets
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any


class ForestComponent(ABC):
    """Abstract base class for all forest components"""

    def __init__(self, component_id: str, name: str, metadata: dict[str, Any] | None = None):
        """
        Initialize a forest component.

        Args:
            component_id: Unique identifier for this component
            name: Human-readable name
            metadata: Additional metadata dictionary
        """
        self.component_id = component_id
        self.name = name
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.status = ComponentStatus.UNKNOWN
        self.health_score = 0.0
        self.threats = []

    @abstractmethod
    def get_type(self) -> str:
        """Return the component type (tree, branch, leaf, etc.)"""
        pass

    def update_status(self, status: "ComponentStatus"):
        """Update component status"""
        self.status = status
        self.last_updated = datetime.now()

    def update_health_score(self, score: float):
        """
        Update health score (0.0 to 100.0).

        Args:
            score: Health score from 0.0 (critical) to 100.0 (perfect health)
        """
        self.health_score = max(0.0, min(100.0, score))
        self.last_updated = datetime.now()

    def add_threat(self, threat):
        """Add a detected threat to this component"""
        self.threats.append(threat)
        self.last_updated = datetime.now()

    def remove_threat(self, threat_id: str):
        """Remove a threat by ID"""
        self.threats = [t for t in self.threats if t.threat_id != threat_id]
        self.last_updated = datetime.now()

    def get_threat_count(self) -> int:
        """Get number of threats on this component"""
        return len(self.threats)

    def has_threats(self) -> bool:
        """Check if component has any threats"""
        return len(self.threats) > 0

    def get_info(self) -> dict[str, Any]:
        """Get component information as dictionary"""
        return {
            "component_id": self.component_id,
            "name": self.name,
            "type": self.get_type(),
            "status": self.status.name,
            "health_score": self.health_score,
            "threat_count": self.get_threat_count(),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata,
        }

    def __str__(self):
        threat_indicator = f" ⚠️{self.get_threat_count()}" if self.has_threats() else ""
        return f"{self.get_type()}: {self.name}{threat_indicator} (Health: {self.health_score:.1f}%)"


class ComponentStatus(Enum):
    """Status of a forest component"""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    COMPROMISED = "compromised"


class ForestBase(ABC):
    """Base class for Forest management"""

    def __init__(self, forest_name: str = "Infrastructure"):
        """
        Initialize the forest.

        Args:
            forest_name: Name of the forest (infrastructure)
        """
        self.forest_name = forest_name
        self.created_at = datetime.now()
        self.components = {}  # component_id -> component
        self.health_checks = []

    def add_component(self, component: ForestComponent):
        """
        Add a component to the forest.

        Args:
            component: ForestComponent to add
        """
        self.components[component.component_id] = component

    def remove_component(self, component_id: str):
        """Remove a component from the forest"""
        if component_id in self.components:
            del self.components[component_id]

    def get_component(self, component_id: str) -> ForestComponent | None:
        """Get a component by ID"""
        return self.components.get(component_id)

    def get_all_components(self) -> list[ForestComponent]:
        """Get all components in the forest"""
        return list(self.components.values())

    def get_components_by_type(self, component_type: str) -> list[ForestComponent]:
        """Get all components of a specific type"""
        return [c for c in self.components.values() if c.get_type() == component_type]

    def get_total_health_score(self) -> float:
        """Calculate average health score across all components"""
        if not self.components:
            return 100.0

        total_score = sum(c.health_score for c in self.components.values())
        return total_score / len(self.components)

    def get_threatened_components(self) -> list[ForestComponent]:
        """Get all components with threats"""
        return [c for c in self.components.values() if c.has_threats()]

    def get_total_threat_count(self) -> int:
        """Get total number of threats in the forest"""
        return sum(c.get_threat_count() for c in self.components.values())

    def get_status_summary(self) -> dict[str, int]:
        """Get count of components by status"""
        summary = {status.name: 0 for status in ComponentStatus}
        for component in self.components.values():
            summary[component.status.name] += 1
        return summary

    def get_forest_info(self) -> dict[str, Any]:
        """Get forest information summary"""
        return {
            "forest_name": self.forest_name,
            "created_at": self.created_at.isoformat(),
            "total_components": len(self.components),
            "average_health": self.get_total_health_score(),
            "total_threats": self.get_total_threat_count(),
            "status_summary": self.get_status_summary(),
            "threatened_components": len(self.get_threatened_components()),
        }

    def __str__(self):
        return (
            f"Forest '{self.forest_name}': {len(self.components)} components, {self.get_total_threat_count()} threats"
        )
