"""
Graph Visualizer - D3.js compatible data structures

Prepares asset graph data for D3.js force-directed and hierarchical visualizations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID


class NodeType(str, Enum):
    """Types of nodes in asset graph"""

    TARGET = "target"
    HOST = "host"
    SERVICE = "service"
    TECHNOLOGY = "technology"
    VULNERABILITY = "vulnerability"
    FINDING = "finding"


class EdgeType(str, Enum):
    """Types of relationships between nodes"""

    HAS_HOST = "has_host"
    RUNS_SERVICE = "runs_service"
    USES_TECHNOLOGY = "uses_technology"
    HAS_VULNERABILITY = "has_vulnerability"
    HAS_FINDING = "has_finding"
    RELATES_TO = "relates_to"


@dataclass
class GraphNode:
    """Node in asset graph"""

    id: str
    type: NodeType
    label: str
    size: int = 10
    color: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_d3_format(self) -> Dict[str, Any]:
        """Convert to D3.js node format"""
        return {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "size": self.size,
            "color": self.color or self._default_color(),
            **self.metadata,
        }

    def _default_color(self) -> str:
        """Get default color based on node type"""
        colors = {
            NodeType.TARGET: "#3498db",
            NodeType.HOST: "#2ecc71",
            NodeType.SERVICE: "#f39c12",
            NodeType.TECHNOLOGY: "#9b59b6",
            NodeType.VULNERABILITY: "#e74c3c",
            NodeType.FINDING: "#e67e22",
        }
        return colors.get(self.type, "#95a5a6")


@dataclass
class GraphEdge:
    """Edge in asset graph"""

    source: str
    target: str
    type: EdgeType
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_d3_format(self) -> Dict[str, Any]:
        """Convert to D3.js edge format"""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.value,
            "weight": self.weight,
            **self.metadata,
        }


class GraphVisualizer:
    """
    Graph visualizer for asset relationships.

    Prepares data for D3.js force-directed graph, hierarchical tree,
    and other graph visualization formats.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode):
        """Add node to graph"""
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge):
        """Add edge to graph"""
        # Ensure both nodes exist
        if edge.source in self.nodes and edge.target in self.nodes:
            self.edges.append(edge)

    def add_target(self, target_id: UUID, target_value: str, target_type: str = "domain"):
        """Add target node"""
        node = GraphNode(
            id=f"target-{target_id}",
            type=NodeType.TARGET,
            label=target_value,
            size=20,
            metadata={"target_type": target_type},
        )
        self.add_node(node)
        return node.id

    def add_host(self, host_id: str, host_value: str, target_node_id: str):
        """Add host node and link to target"""
        node = GraphNode(
            id=f"host-{host_id}",
            type=NodeType.HOST,
            label=host_value,
            size=15,
        )
        self.add_node(node)

        edge = GraphEdge(
            source=target_node_id,
            target=node.id,
            type=EdgeType.HAS_HOST,
        )
        self.add_edge(edge)
        return node.id

    def add_service(self, service_id: str, service_name: str, port: int, host_node_id: str):
        """Add service node and link to host"""
        node = GraphNode(
            id=f"service-{service_id}",
            type=NodeType.SERVICE,
            label=f"{service_name}:{port}",
            size=12,
            metadata={"port": port, "service": service_name},
        )
        self.add_node(node)

        edge = GraphEdge(
            source=host_node_id,
            target=node.id,
            type=EdgeType.RUNS_SERVICE,
        )
        self.add_edge(edge)
        return node.id

    def add_finding(self, finding_id: UUID, title: str, severity: str, parent_node_id: str):
        """Add finding node and link to parent"""
        # Size based on severity
        size_map = {"critical": 18, "high": 15, "medium": 12, "low": 10, "info": 8}
        size = size_map.get(severity.lower(), 10)

        node = GraphNode(
            id=f"finding-{finding_id}",
            type=NodeType.FINDING,
            label=title,
            size=size,
            metadata={"severity": severity},
        )
        self.add_node(node)

        edge = GraphEdge(
            source=parent_node_id,
            target=node.id,
            type=EdgeType.HAS_FINDING,
            weight=size / 10.0,  # Weight by severity
        )
        self.add_edge(edge)
        return node.id

    def to_d3_format(self) -> Dict[str, Any]:
        """
        Export graph in D3.js compatible format.

        Returns:
            Dictionary with 'nodes' and 'links' arrays for D3.js
        """
        return {
            "nodes": [node.to_d3_format() for node in self.nodes.values()],
            "links": [edge.to_d3_format() for edge in self.edges],
        }

    def to_hierarchical_format(self, root_id: str) -> Dict[str, Any]:
        """
        Export graph in D3.js hierarchical tree format.

        Args:
            root_id: ID of root node

        Returns:
            Nested dictionary for D3.js tree/cluster layouts
        """
        if root_id not in self.nodes:
            raise ValueError(f"Root node {root_id} not found")

        # Build adjacency list
        children_map: Dict[str, List[str]] = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            children_map[edge.source].append(edge.target)

        def build_tree(node_id: str, visited: Set[str]) -> Dict[str, Any]:
            """Recursively build tree structure"""
            if node_id in visited:
                return None  # Prevent cycles

            visited.add(node_id)
            node = self.nodes[node_id]

            tree_node = {
                "id": node.id,
                "name": node.label,
                "type": node.type.value,
                **node.metadata,
            }

            children = []
            for child_id in children_map.get(node_id, []):
                child_tree = build_tree(child_id, visited.copy())
                if child_tree:
                    children.append(child_tree)

            if children:
                tree_node["children"] = children

            return tree_node

        return build_tree(root_id, set())

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_counts = {}
        for node_type in NodeType:
            count = sum(1 for node in self.nodes.values() if node.type == node_type)
            node_counts[node_type.value] = count

        edge_counts = {}
        for edge_type in EdgeType:
            count = sum(1 for edge in self.edges if edge.type == edge_type)
            edge_counts[edge_type.value] = count

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_counts,
            "edge_types": edge_counts,
        }

    def clear(self):
        """Clear all nodes and edges"""
        self.nodes.clear()
        self.edges.clear()
