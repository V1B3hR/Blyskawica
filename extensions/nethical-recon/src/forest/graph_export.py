"""
Graph Export for Forest
Exports forest structure to various graph formats (Graphviz, Neo4j, etc.)
"""

import logging
from typing import Any
import json

from .trees import Tree
from .base import ForestBase


class GraphExporter:
    """
    Exports forest structure to various graph formats
    """

    def __init__(self):
        """Initialize graph exporter"""
        self.logger = logging.getLogger("nethical.graph_exporter")
        self._initialize_logger()

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [GraphExporter] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def export_graphviz(self, forest: ForestBase, output_file: str | None = None) -> str:
        """
        Export forest to Graphviz DOT format

        Args:
            forest: Forest to export
            output_file: Optional file path to write to

        Returns:
            Graphviz DOT format string
        """
        dot = ["digraph Forest {"]
        dot.append("    rankdir=TB;")
        dot.append("    node [shape=box, style=rounded];")
        dot.append("")

        # Add forest root
        dot.append(
            f'    forest [label="{forest.forest_name}\\n🌲", shape=ellipse, style=filled, fillcolor=lightgreen];'
        )

        # Add trees
        for tree in getattr(forest, "trees", {}).values():
            tree_id = tree.component_id.replace("-", "_")
            threat_marker = "⚠️" if tree.has_threats() else "✓"
            label = f"{tree.hostname}\\n{tree.ip_address}\\n{threat_marker}"

            color = "lightcoral" if tree.has_threats() else "lightblue"
            dot.append(f'    {tree_id} [label="{label}", style=filled, fillcolor={color}];')
            dot.append(f"    forest -> {tree_id};")

            # Add branches
            for branch in tree.branches.values():
                branch_id = branch.component_id.replace("-", "_")
                branch_label = f"{branch.service_name}\\nPort {branch.port}"
                branch_color = "yellow" if branch.has_threats() else "lightgray"

                dot.append(f'    {branch_id} [label="{branch_label}", style=filled, fillcolor={branch_color}];')
                dot.append(f"    {tree_id} -> {branch_id};")

                # Add leaves (limited to avoid clutter)
                leaf_count = len(branch.leaves)
                if leaf_count > 0:
                    leaves_id = f"{branch_id}_leaves"
                    dot.append(f'    {leaves_id} [label="{leaf_count} endpoints", shape=plaintext];')
                    dot.append(f"    {branch_id} -> {leaves_id} [style=dotted];")

        dot.append("}")

        dot_content = "\n".join(dot)

        if output_file:
            try:
                with open(output_file, "w") as f:
                    f.write(dot_content)
                self.logger.info(f"Exported Graphviz to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to write Graphviz file: {e}")

        return dot_content

    def export_neo4j_cypher(self, forest: ForestBase, output_file: str | None = None) -> list[str]:
        """
        Export forest to Neo4j Cypher queries

        Args:
            forest: Forest to export
            output_file: Optional file path to write to

        Returns:
            List of Cypher query strings
        """
        queries = []

        # Create forest node
        forest_name = forest.forest_name.replace("'", "\\'")
        queries.append(
            f"CREATE (f:Forest {{name: '{forest_name}', "
            f"health_score: {forest.get_total_health_score()}, "
            f"threat_count: {forest.get_total_threat_count()}}})"
        )

        # Create tree nodes and relationships
        for tree in getattr(forest, "trees", {}).values():
            tree_id = tree.component_id
            hostname = tree.hostname.replace("'", "\\'")
            ip = tree.ip_address.replace("'", "\\'")

            queries.append(
                f"CREATE (t_{tree_id.replace('-', '_')}:Tree {{"
                f"id: '{tree_id}', "
                f"hostname: '{hostname}', "
                f"ip_address: '{ip}', "
                f"health_score: {tree.health_score}, "
                f"status: '{tree.status.name}'"
                f"}})"
            )

            queries.append(
                f"MATCH (f:Forest {{name: '{forest_name}'}}), "
                f"(t:Tree {{id: '{tree_id}'}}) "
                f"CREATE (f)-[:CONTAINS]->(t)"
            )

            # Add branches
            for branch in tree.branches.values():
                branch_id = branch.component_id
                service = branch.service_name.replace("'", "\\'")

                queries.append(
                    f"CREATE (b_{branch_id.replace('-', '_')}:Branch {{"
                    f"id: '{branch_id}', "
                    f"service_name: '{service}', "
                    f"port: {branch.port}, "
                    f"protocol: '{branch.protocol}'"
                    f"}})"
                )

                queries.append(
                    f"MATCH (t:Tree {{id: '{tree_id}'}}), "
                    f"(b:Branch {{id: '{branch_id}'}}) "
                    f"CREATE (t)-[:HAS_SERVICE]->(b)"
                )

        if output_file:
            try:
                with open(output_file, "w") as f:
                    f.write("\n".join(queries))
                self.logger.info(f"Exported Neo4j Cypher to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to write Cypher file: {e}")

        return queries

    def export_json_graph(self, forest: ForestBase, output_file: str | None = None) -> dict[str, Any]:
        """
        Export forest to JSON graph format

        Args:
            forest: Forest to export
            output_file: Optional file path to write to

        Returns:
            JSON graph structure
        """
        graph = {
            "forest": {
                "name": forest.forest_name,
                "health_score": forest.get_total_health_score(),
                "threat_count": forest.get_total_threat_count(),
            },
            "nodes": [],
            "edges": [],
        }

        # Add forest node
        graph["nodes"].append({"id": "forest", "type": "forest", "label": forest.forest_name})

        # Add tree nodes and edges
        for tree in getattr(forest, "trees", {}).values():
            tree_node = {
                "id": tree.component_id,
                "type": "tree",
                "label": tree.hostname,
                "properties": {
                    "ip_address": tree.ip_address,
                    "health_score": tree.health_score,
                    "status": tree.status.name,
                    "threat_count": tree.get_threat_count(),
                },
            }
            graph["nodes"].append(tree_node)
            graph["edges"].append({"source": "forest", "target": tree.component_id, "type": "contains"})

            # Add branches
            for branch in tree.branches.values():
                branch_node = {
                    "id": branch.component_id,
                    "type": "branch",
                    "label": f"{branch.service_name}:{branch.port}",
                    "properties": {
                        "service_name": branch.service_name,
                        "port": branch.port,
                        "protocol": branch.protocol,
                        "threat_count": branch.get_threat_count(),
                    },
                }
                graph["nodes"].append(branch_node)
                graph["edges"].append(
                    {"source": tree.component_id, "target": branch.component_id, "type": "has_service"}
                )

        if output_file:
            try:
                with open(output_file, "w") as f:
                    json.dump(graph, f, indent=2)
                self.logger.info(f"Exported JSON graph to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to write JSON file: {e}")

        return graph

    def export_mermaid(self, forest: ForestBase, output_file: str | None = None) -> str:
        """
        Export forest to Mermaid diagram format

        Args:
            forest: Forest to export
            output_file: Optional file path to write to

        Returns:
            Mermaid diagram string
        """
        mermaid = ["graph TD"]

        # Add forest node
        mermaid.append(f"    Forest[🌲 {forest.forest_name}]")

        # Add trees
        for tree in getattr(forest, "trees", {}).values():
            tree_id = tree.component_id.replace("-", "")
            threat_marker = "⚠️" if tree.has_threats() else "✓"

            mermaid.append(f'    {tree_id}["{threat_marker} {tree.hostname}<br/>{tree.ip_address}"]')
            mermaid.append(f"    Forest --> {tree_id}")

            # Add key branches (limit to avoid clutter)
            branch_count = 0
            for branch in tree.branches.values():
                if branch_count >= 5:  # Limit branches shown
                    remaining = len(tree.branches) - branch_count
                    if remaining > 0:
                        more_id = f"{tree_id}_more"
                        mermaid.append(f'    {more_id}["... +{remaining} more services"]')
                        mermaid.append(f"    {tree_id} -.-> {more_id}")
                    break

                branch_id = branch.component_id.replace("-", "")
                mermaid.append(f'    {branch_id}["{branch.service_name}:{branch.port}"]')
                mermaid.append(f"    {tree_id} --> {branch_id}")
                branch_count += 1

        mermaid_content = "\n".join(mermaid)

        if output_file:
            try:
                with open(output_file, "w") as f:
                    f.write(mermaid_content)
                self.logger.info(f"Exported Mermaid diagram to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to write Mermaid file: {e}")

        return mermaid_content
