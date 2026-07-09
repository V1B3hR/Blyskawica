"""
🦅 Eagle - Strategic Command & Overview

> "From the highest altitude, I see the entire forest - every tree, every threat"
> "King of the skies, master of strategic decision-making"
"""

from typing import Any

from .base_bird import AlertLevel, BaseBird, BirdAlert, BirdType, FlightMode


class Eagle(BaseBird):
    """
    🦅 EAGLE - Strategic Command Bird

    Capabilities:
    - Full infrastructure overview (widok z najwyższego pułapu)
    - Executive dashboards and reports
    - Cross-forest threat correlation
    - Strategic hunting decisions
    - Command & control center

    Flight Mode: SOARING (high altitude overview)
    Alert Sound: ROAR (majestic and powerful)
    """

    def __init__(self, name: str = "Eagle-Alpha"):
        """Initialize Eagle surveillance bird"""
        super().__init__(name, BirdType.EAGLE)
        self.altitude = "highest"
        self.vision_range = "entire_forest"
        self.leadership_role = "command_and_control"

    def get_capabilities(self) -> dict[str, str]:
        """Get Eagle's unique capabilities"""
        return {
            "altitude": "Highest pułap - sees entire infrastructure",
            "vision": "Strategic overview - all trees and threats",
            "correlation": "Cross-forest threat correlation",
            "command": "Executive command & control",
            "reports": "Strategic decision-making",
            "authority": "Highest decision authority",
        }

    def scan(self, forest_data: dict[str, Any]) -> list[BirdAlert]:
        """
        Strategic scan of entire forest

        Eagle focuses on:
        - Overall forest health
        - Cross-tree threat patterns
        - Strategic threat indicators
        - Infrastructure-wide anomalies

        Args:
            forest_data: Complete forest state

        Returns:
            List of strategic alerts
        """
        alerts = []

        # Ensure we're in flight mode
        if not self.is_active:
            self.take_flight(FlightMode.SOARING)

        # Get forest overview
        trees = forest_data.get("trees", [])
        threats = forest_data.get("threats", {})
        overall_health = forest_data.get("overall_health", 1.0)

        # Strategic Assessment: Forest Health
        if overall_health < 0.5:
            alert = self.create_alert(
                AlertLevel.CRITICAL,
                f"Forest health critical: {overall_health*100:.1f}% - Multiple trees compromised",
                location={"scope": "entire_forest"},
                evidence=[f"Health score: {overall_health}", f"Trees affected: {len(trees)}"],
            )
            alerts.append(alert)
        elif overall_health < 0.7:
            alert = self.create_alert(
                AlertLevel.ELEVATED,
                f"Forest health declining: {overall_health*100:.1f}% - Increased monitoring advised",
                location={"scope": "entire_forest"},
                evidence=[f"Health score: {overall_health}"],
            )
            alerts.append(alert)

        # Strategic Assessment: Threat Distribution
        crow_count = threats.get("crows", 0)
        squirrel_count = threats.get("squirrels", 0)
        total_threats = sum(threats.values())

        if total_threats > 10:
            alert = self.create_alert(
                AlertLevel.CRITICAL,
                f"ROAR!! Massive threat presence detected: {total_threats} active threats",
                location={"scope": "entire_forest"},
                evidence=[
                    f"Crows (malware): {crow_count}",
                    f"Squirrels (lateral): {squirrel_count}",
                    f"Total: {total_threats}",
                ],
            )
            alerts.append(alert)
        elif total_threats > 5:
            alert = self.create_alert(
                AlertLevel.ELEVATED,
                f"Elevated threat level: {total_threats} active threats in forest",
                location={"scope": "entire_forest"},
                evidence=["Requires strategic response planning"],
            )
            alerts.append(alert)

        # Strategic Assessment: Cross-Tree Patterns
        if crow_count >= 3:
            alert = self.create_alert(
                AlertLevel.CRITICAL,
                f"ROAR!! Coordinated malware attack: {crow_count} crows across multiple trees",
                location={"scope": "cross_tree_pattern"},
                evidence=["Pattern: Distributed malware campaign", "Recommendation: Full forest lockdown"],
            )
            alerts.append(alert)

        if squirrel_count >= 2:
            alert = self.create_alert(
                AlertLevel.ELEVATED,
                f"Lateral movement detected: {squirrel_count} squirrels jumping between trees",
                location={"scope": "cross_tree_pattern"},
                evidence=["Pattern: Attacker moving laterally", "Recommendation: Isolate affected trees"],
            )
            alerts.append(alert)

        # Strategic Assessment: Individual Tree Analysis
        unhealthy_trees = []
        for tree in trees:
            tree_health = tree.get("health", 1.0)
            if tree_health < 0.6:
                unhealthy_trees.append(tree.get("name", "unknown"))

        if len(unhealthy_trees) >= 3:
            alert = self.create_alert(
                AlertLevel.CRITICAL,
                f"Multiple trees compromised: {', '.join(unhealthy_trees[:3])}",
                location={"scope": "multiple_trees", "trees": unhealthy_trees},
                evidence=[f"Compromised trees: {len(unhealthy_trees)}", "Strategic action required"],
            )
            alerts.append(alert)

        return alerts

    def generate_executive_report(self, forest_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate executive-level strategic report

        Args:
            forest_data: Complete forest state

        Returns:
            Executive summary report
        """
        trees = forest_data.get("trees", [])
        threats = forest_data.get("threats", {})
        overall_health = forest_data.get("overall_health", 1.0)

        # Calculate metrics
        total_trees = len(trees)
        healthy_trees = sum(1 for t in trees if t.get("health", 1.0) >= 0.8)
        compromised_trees = sum(1 for t in trees if t.get("health", 1.0) < 0.5)
        total_threats = sum(threats.values())

        # Determine threat level
        if total_threats > 10 or overall_health < 0.5:
            threat_level = "CRITICAL"
            threat_emoji = "🔴"
        elif total_threats > 5 or overall_health < 0.7:
            threat_level = "ELEVATED"
            threat_emoji = "🟠"
        elif total_threats > 0:
            threat_level = "WARNING"
            threat_emoji = "🟡"
        else:
            threat_level = "NORMAL"
            threat_emoji = "🟢"

        return {
            "report_type": "EXECUTIVE_SUMMARY",
            "generated_by": self.name,
            "bird_type": self.bird_type.value,
            "timestamp": self.last_patrol.isoformat() if self.last_patrol else None,
            "overall_status": {
                "threat_level": threat_level,
                "threat_emoji": threat_emoji,
                "forest_health": f"{overall_health*100:.1f}%",
            },
            "infrastructure": {
                "total_trees": total_trees,
                "healthy_trees": healthy_trees,
                "compromised_trees": compromised_trees,
                "health_percentage": f"{(healthy_trees/total_trees)*100:.1f}%" if total_trees > 0 else "0%",
            },
            "threats": {
                "total": total_threats,
                "crows": threats.get("crows", 0),
                "squirrels": threats.get("squirrels", 0),
                "parasites": threats.get("parasites", 0),
                "bats": threats.get("bats", 0),
            },
            "strategic_recommendations": self._get_strategic_recommendations(
                overall_health, total_threats, compromised_trees
            ),
        }

    def _get_strategic_recommendations(self, health: float, threats: int, compromised: int) -> list[str]:
        """Generate strategic recommendations based on current state"""
        recommendations = []

        if health < 0.5:
            recommendations.append("🚨 IMMEDIATE: Initiate forest-wide incident response")
            recommendations.append("🔒 ISOLATE: Quarantine all compromised trees")

        if threats > 10:
            recommendations.append("⚔️ DEPLOY: All nanobots to defense mode")
            recommendations.append("🎯 MARK: Tag all active threats with marker weapons")

        if compromised >= 3:
            recommendations.append("🔍 INVESTIGATE: Conduct deep forensic analysis")
            recommendations.append("📋 DOCUMENT: Preserve evidence for post-incident review")

        if health < 0.7 or threats > 5:
            recommendations.append("👁️ MONITOR: Increase Falcon and Owl patrol frequency")
            recommendations.append("🛡️ HARDEN: Strengthen defenses on remaining healthy trees")

        if not recommendations:
            recommendations.append("✅ MAINTAIN: Continue normal patrol operations")
            recommendations.append("📊 REVIEW: Regular strategic assessment scheduled")

        return recommendations

    def command_decision(self, situation: str) -> dict[str, Any]:
        """
        Make strategic command decision

        Args:
            situation: Description of current situation

        Returns:
            Command decision with actions
        """
        decision = {
            "commander": self.name,
            "situation": situation,
            "decision": None,
            "actions": [],
            "priority": "normal",
        }

        # Analyze situation keywords for decision making
        situation_lower = situation.lower()

        if "breach" in situation_lower or "compromised" in situation_lower:
            decision["decision"] = "FULL_RESPONSE"
            decision["priority"] = "critical"
            decision["actions"] = [
                "Deploy all nanobots",
                "Mark all threats",
                "Isolate affected systems",
                "Alert all hunters",
                "Initiate incident response",
            ]
        elif "lateral" in situation_lower or "movement" in situation_lower:
            decision["decision"] = "CONTAIN_AND_TRACK"
            decision["priority"] = "high"
            decision["actions"] = [
                "Track squirrel movements",
                "Deploy Falcon for pursuit",
                "Mark squirrel path",
                "Prepare containment",
            ]
        elif "malware" in situation_lower or "crow" in situation_lower:
            decision["decision"] = "IDENTIFY_AND_MARK"
            decision["priority"] = "high"
            decision["actions"] = [
                "Deploy Owl for stealth observation",
                "Mark with black tracer",
                "Gather evidence",
                "Prepare removal",
            ]
        else:
            decision["decision"] = "MONITOR_AND_ASSESS"
            decision["priority"] = "normal"
            decision["actions"] = [
                "Continue Sparrow patrols",
                "Gather more intelligence",
                "Assess threat level",
                "Report findings",
            ]

        return decision

    def __str__(self) -> str:
        """String representation"""
        return f"🦅 {self.name} [EAGLE] - Strategic Command - {self.flight_mode.value.upper()}"
