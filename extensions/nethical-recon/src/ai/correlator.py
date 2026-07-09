"""
AI Stain Correlator

Links stains together, identifies attack chains, builds threat graphs,
and maps forest connections.
"""

import logging
from datetime import datetime
from typing import Any


class StainCorrelator:
    """
    🔗 AI Stain Correlation Engine

    Provides:
    • Stain linking
    • Attack chain identification
    • Threat graph building
    • Forest mapping
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def link_stains(self, stains: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Link related stains together

        Args:
            stains: List of stain records

        Returns:
            List of stain groups
        """
        if not stains:
            return []

        groups = []
        processed = set()

        for i, stain1 in enumerate(stains):
            if i in processed:
                continue

            group = {
                "primary_stain": stain1.get("tag_id"),
                "linked_stains": [],
                "correlation_strength": 0.0,
                "common_indicators": [],
            }

            for j, stain2 in enumerate(stains[i + 1 :], start=i + 1):
                if j in processed:
                    continue

                correlation = self._calculate_correlation(stain1, stain2)

                if correlation["strength"] >= 0.5:
                    group["linked_stains"].append(
                        {
                            "stain_id": stain2.get("tag_id"),
                            "correlation": correlation["strength"],
                            "indicators": correlation["indicators"],
                        }
                    )
                    processed.add(j)

            if group["linked_stains"]:
                group["correlation_strength"] = sum(s["correlation"] for s in group["linked_stains"]) / len(
                    group["linked_stains"]
                )
                processed.add(i)
                groups.append(group)

        return groups

    def _calculate_correlation(self, stain1: dict, stain2: dict) -> dict[str, Any]:
        """Calculate correlation between two stains"""
        indicators = []
        strength = 0.0

        # Check IP correlation
        ip1 = stain1.get("target", {}).get("ip")
        ip2 = stain2.get("target", {}).get("ip")
        if ip1 and ip2 and ip1 == ip2:
            indicators.append("same_ip")
            strength += 0.4

        # Check time proximity (within 1 hour)
        try:
            time1 = datetime.fromisoformat(stain1.get("timestamp_first_seen", ""))
            time2 = datetime.fromisoformat(stain2.get("timestamp_first_seen", ""))
            if abs((time2 - time1).total_seconds()) < 3600:
                indicators.append("time_proximity")
                strength += 0.3
        except Exception:
            pass

        # Check threat type similarity
        type1 = stain1.get("marker_type")
        type2 = stain2.get("marker_type")
        if type1 and type2 and type1 == type2:
            indicators.append("same_threat_type")
            strength += 0.3

        # Check forest location
        tree1 = stain1.get("forest_location", {}).get("tree")
        tree2 = stain2.get("forest_location", {}).get("tree")
        if tree1 and tree2 and tree1 == tree2:
            indicators.append("same_tree")
            strength += 0.2

        return {"strength": min(strength, 1.0), "indicators": indicators}

    def identify_attack_chain(self, stains: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Identify attack chains from stains

        Args:
            stains: List of stain records

        Returns:
            List of identified attack chains
        """
        # Sort by timestamp
        sorted_stains = sorted(stains, key=lambda s: s.get("timestamp_first_seen", ""))

        chains = []
        current_chain = []
        last_time = None

        for stain in sorted_stains:
            try:
                stain_time = datetime.fromisoformat(stain.get("timestamp_first_seen", ""))

                # If more than 2 hours apart, start new chain
                if last_time and (stain_time - last_time).total_seconds() > 7200:
                    if len(current_chain) >= 2:
                        chains.append(self._analyze_chain(current_chain))
                    current_chain = []

                current_chain.append(stain)
                last_time = stain_time
            except Exception:
                continue

        # Add final chain
        if len(current_chain) >= 2:
            chains.append(self._analyze_chain(current_chain))

        return chains

    def _analyze_chain(self, chain: list[dict]) -> dict[str, Any]:
        """Analyze an attack chain"""
        return {
            "chain_id": f"chain_{datetime.now().timestamp()}",
            "length": len(chain),
            "start_time": chain[0].get("timestamp_first_seen"),
            "end_time": chain[-1].get("timestamp_first_seen"),
            "stains": [s.get("tag_id") for s in chain],
            "attack_pattern": self._identify_pattern(chain),
            "severity": self._assess_chain_severity(chain),
            "recommendations": self._chain_recommendations(chain),
        }

    def _identify_pattern(self, chain: list[dict]) -> str:
        """Identify attack pattern from chain"""
        types = [s.get("marker_type", "").lower() for s in chain]

        if "crow" in types and "magpie" in types:
            return "MALWARE_TO_EXFILTRATION"
        elif "squirrel" in types:
            return "LATERAL_MOVEMENT"
        elif len(set(types)) == 1:
            return "REPEATED_ATTACK"
        else:
            return "MULTI_STAGE_ATTACK"

    def _assess_chain_severity(self, chain: list[dict]) -> str:
        """Assess overall chain severity"""
        max_score = max((s.get("stain", {}).get("threat_score", 0) for s in chain), default=0)

        if max_score >= 8.0 or len(chain) >= 5:
            return "CRITICAL"
        elif max_score >= 6.0 or len(chain) >= 3:
            return "HIGH"
        else:
            return "MEDIUM"

    def _chain_recommendations(self, chain: list[dict]) -> list[str]:
        """Generate recommendations for chain"""
        recommendations = [
            f"Attack chain detected with {len(chain)} stages",
            "Review all affected systems",
            "Check for additional compromised assets",
        ]

        pattern = self._identify_pattern(chain)
        if pattern == "LATERAL_MOVEMENT":
            recommendations.append("Strengthen network segmentation")
        elif pattern == "MALWARE_TO_EXFILTRATION":
            recommendations.append("Review DLP controls and data access")

        return recommendations

    def build_threat_graph(self, stains: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Build threat relationship graph

        Args:
            stains: List of stain records

        Returns:
            Threat graph structure
        """
        nodes = []
        edges = []

        # Create nodes
        for stain in stains:
            nodes.append(
                {
                    "id": stain.get("tag_id"),
                    "type": stain.get("marker_type"),
                    "score": stain.get("stain", {}).get("threat_score", 0),
                    "timestamp": stain.get("timestamp_first_seen"),
                }
            )

        # Create edges based on relationships
        for i, stain1 in enumerate(stains):
            for stain2 in stains[i + 1 :]:
                correlation = self._calculate_correlation(stain1, stain2)

                if correlation["strength"] >= 0.3:
                    edges.append(
                        {
                            "source": stain1.get("tag_id"),
                            "target": stain2.get("tag_id"),
                            "weight": correlation["strength"],
                            "relationship": ", ".join(correlation["indicators"]),
                        }
                    )

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0,
            "clusters": self._identify_clusters(nodes, edges),
        }

    def _identify_clusters(self, nodes: list[dict], edges: list[dict]) -> list[dict[str, Any]]:
        """Identify threat clusters in graph"""
        # Simple clustering based on connected components
        node_ids = {n["id"] for n in nodes}
        visited = set()
        clusters = []

        def dfs(node_id: str, cluster: set[str]):
            if node_id in visited:
                return
            visited.add(node_id)
            cluster.add(node_id)

            # Find connected nodes
            for edge in edges:
                if edge["source"] == node_id and edge["target"] not in visited:
                    dfs(edge["target"], cluster)
                elif edge["target"] == node_id and edge["source"] not in visited:
                    dfs(edge["source"], cluster)

        for node_id in node_ids:
            if node_id not in visited:
                cluster = set()
                dfs(node_id, cluster)
                if len(cluster) > 1:
                    clusters.append({"cluster_id": len(clusters) + 1, "size": len(cluster), "nodes": list(cluster)})

        return clusters

    def map_forest_threats(self, forest_data: dict[str, Any], stains: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Map threats to forest structure

        Args:
            forest_data: Forest topology data
            stains: Stain records

        Returns:
            Threat map
        """
        threat_map = {}

        # Group stains by tree
        for stain in stains:
            tree = stain.get("forest_location", {}).get("tree", "unknown")
            if tree not in threat_map:
                threat_map[tree] = {"tree_name": tree, "threats": [], "threat_count": 0, "max_severity": "LOW"}

            threat_map[tree]["threats"].append(
                {
                    "stain_id": stain.get("tag_id"),
                    "type": stain.get("marker_type"),
                    "branch": stain.get("forest_location", {}).get("branch"),
                    "score": stain.get("stain", {}).get("threat_score", 0),
                }
            )
            threat_map[tree]["threat_count"] += 1

            # Update max severity
            score = stain.get("stain", {}).get("threat_score", 0)
            if score >= 8.0:
                threat_map[tree]["max_severity"] = "CRITICAL"
            elif score >= 6.0 and threat_map[tree]["max_severity"] not in ["CRITICAL"]:
                threat_map[tree]["max_severity"] = "HIGH"
            elif score >= 4.0 and threat_map[tree]["max_severity"] not in ["CRITICAL", "HIGH"]:
                threat_map[tree]["max_severity"] = "MEDIUM"

        # Add threat density and recommendations
        for tree, data in threat_map.items():
            data["threat_density"] = data["threat_count"] / forest_data.get("total_trees", 1)
            data["recommendations"] = self._tree_recommendations(data)

        return {
            "threat_map": threat_map,
            "total_affected_trees": len(threat_map),
            "highest_risk_trees": sorted(threat_map.items(), key=lambda x: x[1]["threat_count"], reverse=True)[:3],
            "forest_summary": self._summarize_forest_threats(threat_map, forest_data),
        }

    def _tree_recommendations(self, tree_data: dict) -> list[str]:
        """Generate recommendations for a tree"""
        recommendations = []

        if tree_data["threat_count"] >= 3:
            recommendations.append("🚨 Multiple threats detected - consider isolation")

        if tree_data["max_severity"] == "CRITICAL":
            recommendations.append("🔴 Critical severity - immediate action required")
            recommendations.append("Deploy nanobots for containment")

        if tree_data["threat_count"] > 0:
            recommendations.append("Increase monitoring on affected branches")

        return recommendations

    def _summarize_forest_threats(self, threat_map: dict, forest_data: dict) -> str:
        """Summarize forest-wide threat situation"""
        total_trees = forest_data.get("total_trees", 0)
        affected_trees = len(threat_map)

        if total_trees == 0:
            return "No forest data available"

        percentage = (affected_trees / total_trees) * 100

        if percentage >= 50:
            return f"CRITICAL: {percentage:.1f}% of forest affected"
        elif percentage >= 25:
            return f"HIGH: {percentage:.1f}% of forest affected"
        elif percentage >= 10:
            return f"MEDIUM: {percentage:.1f}% of forest affected"
        else:
            return f"LOW: {percentage:.1f}% of forest affected"
