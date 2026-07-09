"""Graph builder for attack surface visualization."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class NodeType(Enum):
    """Types of nodes in the attack surface graph."""

    HOST = "host"
    SERVICE = "service"
    TECHNOLOGY = "technology"
    VULNERABILITY = "vulnerability"
    PORT = "port"


@dataclass
class GraphNode:
    """Node in the attack surface graph."""

    id: str
    type: NodeType
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Edge connecting nodes in the graph."""

    source: str
    target: str
    relationship: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackSurfaceGraph:
    """Attack surface dependency graph."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        # Check if both source and target exist
        source_exists = any(n.id == edge.source for n in self.nodes)
        target_exists = any(n.id == edge.target for n in self.nodes)

        if source_exists and target_exists:
            self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return next((n for n in self.nodes if n.id == node_id), None)

    def get_neighbors(self, node_id: str) -> list[GraphNode]:
        """Get neighboring nodes."""
        neighbor_ids = set()

        for edge in self.edges:
            if edge.source == node_id:
                neighbor_ids.add(edge.target)
            elif edge.target == node_id:
                neighbor_ids.add(edge.source)

        return [n for n in self.nodes if n.id in neighbor_ids]

    def to_dict(self) -> dict[str, Any]:
        """Convert graph to dictionary format."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "label": n.label,
                    "properties": n.properties,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "relationship": e.relationship,
                    "properties": e.properties,
                }
                for e in self.edges
            ],
            "metadata": self.metadata,
        }

    def to_graphviz(self) -> str:
        """Export to Graphviz DOT format.

        Returns:
            DOT format string
        """
        lines = ["digraph AttackSurface {", "  rankdir=LR;", "  node [shape=box, style=rounded];", ""]

        # Add nodes with styling based on type
        node_styles = {
            NodeType.HOST: 'fillcolor=lightblue, style="rounded,filled"',
            NodeType.SERVICE: 'fillcolor=lightgreen, style="rounded,filled"',
            NodeType.TECHNOLOGY: 'fillcolor=lightyellow, style="rounded,filled"',
            NodeType.VULNERABILITY: 'fillcolor=lightcoral, style="rounded,filled"',
            NodeType.PORT: 'fillcolor=lightgray, style="rounded,filled"',
        }

        for node in self.nodes:
            style = node_styles.get(node.type, "")
            label = node.label.replace('"', '\\"')
            lines.append(f'  "{node.id}" [label="{label}", {style}];')

        lines.append("")

        # Add edges
        for edge in self.edges:
            label = edge.relationship.replace('"', '\\"')
            lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)


class GraphBuilder:
    """Builder for attack surface graphs."""

    def __init__(self):
        """Initialize graph builder."""
        self.graph = AttackSurfaceGraph()

    def build_from_snapshot(self, snapshot: Any) -> AttackSurfaceGraph:
        """Build graph from attack surface snapshot.

        Args:
            snapshot: AttackSurfaceSnapshot object

        Returns:
            AttackSurfaceGraph
        """
        self.graph = AttackSurfaceGraph()
        self.graph.metadata = {
            "snapshot_id": snapshot.snapshot_id,
            "target": snapshot.target,
            "timestamp": snapshot.timestamp.isoformat() if snapshot.timestamp else None,
        }

        # Add assets as nodes
        for asset in snapshot.assets:
            # Add host node
            host_node = GraphNode(
                id=asset.asset_id,
                type=NodeType.HOST,
                label=asset.host,
                properties={
                    "asset_type": asset.asset_type,
                    "ip": asset.ip,
                },
            )
            self.graph.add_node(host_node)

            # Add port nodes if present
            if asset.port:
                port_node = GraphNode(
                    id=f"{asset.asset_id}_port_{asset.port}",
                    type=NodeType.PORT,
                    label=f"Port {asset.port}",
                    properties={"port": asset.port, "protocol": asset.protocol},
                )
                self.graph.add_node(port_node)

                # Connect host to port
                self.graph.add_edge(
                    GraphEdge(
                        source=asset.asset_id,
                        target=port_node.id,
                        relationship="exposes",
                    )
                )

                # Add service node if present
                if asset.service:
                    service_node = GraphNode(
                        id=f"{asset.asset_id}_service_{asset.service}",
                        type=NodeType.SERVICE,
                        label=asset.service,
                        properties={"version": asset.service_version},
                    )
                    self.graph.add_node(service_node)

                    # Connect port to service
                    self.graph.add_edge(
                        GraphEdge(
                            source=port_node.id,
                            target=service_node.id,
                            relationship="runs",
                        )
                    )

            # Add technology nodes
            for tech in asset.technologies:
                tech_id = f"tech_{tech['name']}_{tech.get('version', 'unknown')}"
                tech_node = GraphNode(
                    id=tech_id,
                    type=NodeType.TECHNOLOGY,
                    label=f"{tech['name']} {tech.get('version', '')}",
                    properties=tech,
                )
                self.graph.add_node(tech_node)

                # Connect host to technology
                self.graph.add_edge(
                    GraphEdge(
                        source=asset.asset_id,
                        target=tech_id,
                        relationship="uses",
                    )
                )

        return self.graph

    def add_vulnerabilities(self, findings: list[Any]) -> None:
        """Add vulnerability nodes to the graph.

        Args:
            findings: List of Finding objects
        """
        for finding in findings:
            vuln_node = GraphNode(
                id=f"vuln_{finding.id}",
                type=NodeType.VULNERABILITY,
                label=finding.title,
                properties={
                    "severity": finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity),
                    "description": finding.description,
                },
            )
            self.graph.add_node(vuln_node)

            # Try to connect vulnerability to affected asset
            if finding.affected_asset:
                # Find matching host node
                host_node = self.graph.get_node(finding.affected_asset)
                if host_node:
                    self.graph.add_edge(
                        GraphEdge(
                            source=host_node.id,
                            target=vuln_node.id,
                            relationship="has_vulnerability",
                        )
                    )

    def get_graph(self) -> AttackSurfaceGraph:
        """Get the built graph."""
        return self.graph
