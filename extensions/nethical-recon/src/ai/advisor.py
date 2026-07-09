"""
AI Hunt Advisor

Provides recommendations for next actions, best weapon selection,
hunt strategy, and bird deployment.
"""

import logging
from typing import Any


class HuntAdvisor:
    """
    🎯 AI Hunt Strategy Advisor

    Advises on:
    • Next action recommendations
    • Best weapon selection
    • Hunt strategy
    • Bird deployment
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def recommend_next_action(self, situation: dict[str, Any]) -> dict[str, Any]:
        """
        Recommend next action based on current situation

        Args:
            situation: Current threat and system state

        Returns:
            Action recommendation
        """
        threats = situation.get("threats", [])
        resources = situation.get("resources", {})

        if not threats:
            return {
                "action": "PATROL",
                "priority": "LOW",
                "description": "Continue routine patrols with Sparrow",
                "reasoning": "No active threats detected",
            }

        # Find highest priority threat
        highest_threat = max(threats, key=lambda t: t.get("threat_score", 0))
        score = highest_threat.get("threat_score", 0)

        if score >= 8.0:
            action = "MARK_AND_CONTAIN"
            priority = "CRITICAL"
            description = "Mark threat immediately with marker weapon and deploy nanobots"
        elif score >= 6.0:
            action = "INVESTIGATE"
            priority = "HIGH"
            description = "Deploy Falcon for rapid investigation and prepare markers"
        elif score >= 4.0:
            action = "MONITOR"
            priority = "MEDIUM"
            description = "Deploy Owl for enhanced monitoring"
        else:
            action = "OBSERVE"
            priority = "LOW"
            description = "Continue observation with current sensors"

        return {
            "action": action,
            "priority": priority,
            "description": description,
            "target": highest_threat.get("id", "unknown"),
            "reasoning": f"Threat score: {score}",
            "steps": self._generate_action_steps(action, highest_threat),
        }

    def _generate_action_steps(self, action: str, threat: dict) -> list[str]:
        """Generate detailed action steps"""
        steps = {
            "MARK_AND_CONTAIN": [
                "1. Deploy defensive nanobots to contain threat",
                "2. Select appropriate marker weapon (CO2 Silent recommended)",
                "3. Mark threat with appropriate tracer color",
                "4. Document in stain database",
                "5. Monitor for persistence",
            ],
            "INVESTIGATE": [
                "1. Deploy Falcon for rapid threat assessment",
                "2. Gather additional evidence",
                "3. Analyze threat behavior",
                "4. Prepare marker weapon if needed",
                "5. Report findings",
            ],
            "MONITOR": [
                "1. Deploy Owl for enhanced monitoring",
                "2. Increase sensor sensitivity",
                "3. Track threat behavior",
                "4. Update threat intelligence",
            ],
            "OBSERVE": ["1. Continue routine monitoring", "2. Log threat indicators", "3. Update baseline if needed"],
            "PATROL": ["1. Maintain Sparrow routine patrols", "2. Check forest health", "3. Update system baselines"],
        }
        return steps.get(action, ["Continue monitoring"])

    def select_best_weapon(self, threat: dict[str, Any], environment: dict[str, Any]) -> dict[str, Any]:
        """
        Select best marker weapon for the threat

        Args:
            threat: Threat information
            environment: Environmental constraints

        Returns:
            Weapon recommendation
        """
        threat_type = threat.get("type", "unknown")
        threat_score = threat.get("threat_score", 5.0)
        stealth_required = environment.get("stealth_required", True)

        # Select weapon mode
        if threat_score >= 8.0 and not stealth_required:
            weapon_mode = "ELECTRIC"
            noise_level = 20
            effectiveness = "MAXIMUM"
        elif threat_score >= 5.0 or stealth_required:
            weapon_mode = "CO2_SILENT"
            noise_level = 10
            effectiveness = "HIGH"
        else:
            weapon_mode = "PNEUMATIC"
            noise_level = 0
            effectiveness = "MODERATE"

        # Select tracer color
        tracer_map = {
            "crow": "BLACK",
            "magpie": "PURPLE",
            "squirrel": "BROWN",
            "snake": "RED",
            "parasite": "ORANGE",
            "bat": "BLUE",
        }
        tracer = tracer_map.get(threat_type, "WHITE")

        return {
            "weapon_mode": weapon_mode,
            "tracer_color": tracer,
            "noise_level": noise_level,
            "effectiveness": effectiveness,
            "reasoning": f"Score {threat_score}, type {threat_type}, stealth={stealth_required}",
            "alternative_options": self._suggest_alternatives(weapon_mode),
        }

    def _suggest_alternatives(self, primary_mode: str) -> list[dict[str, str]]:
        """Suggest alternative weapon options"""
        alternatives = {
            "ELECTRIC": [
                {"mode": "CO2_SILENT", "reason": "If stealth becomes important"},
                {"mode": "PNEUMATIC", "reason": "For minimal detection"},
            ],
            "CO2_SILENT": [
                {"mode": "ELECTRIC", "reason": "If maximum impact needed"},
                {"mode": "PNEUMATIC", "reason": "For ultra-stealth operation"},
            ],
            "PNEUMATIC": [
                {"mode": "CO2_SILENT", "reason": "If more impact needed"},
                {"mode": "ELECTRIC", "reason": "For critical threats"},
            ],
        }
        return alternatives.get(primary_mode, [])

    def devise_hunt_strategy(self, situation: dict[str, Any]) -> dict[str, Any]:
        """
        Devise comprehensive hunt strategy

        Args:
            situation: Complete situation assessment

        Returns:
            Hunt strategy
        """
        threats = situation.get("threats", [])
        resources = situation.get("resources", {})
        forest_health = situation.get("forest", {}).get("health_score", 100)

        # Determine strategy type
        threat_count = len(threats)
        critical_count = sum(1 for t in threats if t.get("severity") == "CRITICAL")

        if critical_count > 0:
            strategy_type = "AGGRESSIVE"
            approach = "Immediate threat neutralization"
        elif threat_count > 5:
            strategy_type = "SYSTEMATIC"
            approach = "Methodical threat elimination"
        elif forest_health < 70:
            strategy_type = "DEFENSIVE"
            approach = "Protect and recover"
        else:
            strategy_type = "PROACTIVE"
            approach = "Preventive hunting"

        return {
            "strategy_type": strategy_type,
            "approach": approach,
            "phases": self._plan_hunt_phases(strategy_type, threats),
            "resource_allocation": self._allocate_resources(strategy_type, resources),
            "expected_duration": self._estimate_duration(threat_count, critical_count),
            "success_criteria": self._define_success_criteria(strategy_type),
            "contingency_plans": self._prepare_contingencies(strategy_type),
        }

    def _plan_hunt_phases(self, strategy: str, threats: list[dict]) -> list[dict[str, Any]]:
        """Plan hunt phases"""
        if strategy == "AGGRESSIVE":
            return [
                {
                    "phase": 1,
                    "name": "CONTAIN",
                    "duration": "0-30 min",
                    "actions": ["Deploy nanobots", "Isolate threats"],
                },
                {"phase": 2, "name": "MARK", "duration": "30-60 min", "actions": ["Mark all threats", "Create stains"]},
                {
                    "phase": 3,
                    "name": "ELIMINATE",
                    "duration": "1-2 hours",
                    "actions": ["Neutralize threats", "Verify elimination"],
                },
            ]
        elif strategy == "SYSTEMATIC":
            return [
                {
                    "phase": 1,
                    "name": "PRIORITIZE",
                    "duration": "0-15 min",
                    "actions": ["Rank threats", "Plan sequence"],
                },
                {"phase": 2, "name": "EXECUTE", "duration": "1-4 hours", "actions": ["Process threats one by one"]},
                {
                    "phase": 3,
                    "name": "VERIFY",
                    "duration": "30-60 min",
                    "actions": ["Confirm elimination", "Update database"],
                },
            ]
        else:
            return [
                {"phase": 1, "name": "ASSESS", "duration": "15-30 min", "actions": ["Full situation assessment"]},
                {"phase": 2, "name": "RESPOND", "duration": "Variable", "actions": ["Targeted response"]},
                {"phase": 3, "name": "RECOVER", "duration": "1-2 hours", "actions": ["Restore forest health"]},
            ]

    def _allocate_resources(self, strategy: str, available: dict) -> dict[str, Any]:
        """Allocate resources for strategy"""
        allocations = {
            "AGGRESSIVE": {
                "nanobots": "ALL",
                "birds": ["eagle", "falcon", "owl"],
                "weapons": ["CO2_SILENT", "ELECTRIC"],
                "sensors": "MAXIMUM_SENSITIVITY",
            },
            "SYSTEMATIC": {
                "nanobots": "70%",
                "birds": ["falcon", "owl"],
                "weapons": ["CO2_SILENT"],
                "sensors": "HIGH_SENSITIVITY",
            },
            "DEFENSIVE": {
                "nanobots": "80%",
                "birds": ["eagle", "owl"],
                "weapons": ["PNEUMATIC", "CO2_SILENT"],
                "sensors": "MAXIMUM_SENSITIVITY",
            },
            "PROACTIVE": {
                "nanobots": "40%",
                "birds": ["sparrow", "falcon"],
                "weapons": ["PNEUMATIC"],
                "sensors": "NORMAL_SENSITIVITY",
            },
        }
        return allocations.get(strategy, {})

    def _estimate_duration(self, threat_count: int, critical_count: int) -> str:
        """Estimate hunt duration"""
        base_time = threat_count * 15  # 15 minutes per threat
        critical_time = critical_count * 30  # Extra 30 min for critical
        total_minutes = base_time + critical_time

        hours = total_minutes // 60
        minutes = total_minutes % 60

        return f"{hours}h {minutes}m"

    def _define_success_criteria(self, strategy: str) -> list[str]:
        """Define success criteria"""
        base_criteria = [
            "All threats marked and documented",
            "Forest health restored above 80%",
            "No active threats detected",
        ]

        if strategy == "AGGRESSIVE":
            base_criteria.append("All critical threats eliminated within 1 hour")
        elif strategy == "SYSTEMATIC":
            base_criteria.append("All threats processed in priority order")

        return base_criteria

    def _prepare_contingencies(self, strategy: str) -> list[dict[str, str]]:
        """Prepare contingency plans"""
        return [
            {"scenario": "New threat emerges", "action": "Reassess priorities, deploy Falcon"},
            {"scenario": "Resource exhaustion", "action": "Switch to defensive posture"},
            {"scenario": "Threat escalation", "action": "Activate Eagle mode, request backup"},
        ]

    def recommend_bird_deployment(self, situation: dict[str, Any]) -> dict[str, Any]:
        """
        Recommend bird deployment strategy

        Args:
            situation: Current situation

        Returns:
            Bird deployment recommendations
        """
        threats = situation.get("threats", [])
        time_of_day = situation.get("time_of_day", "day")  # day, night, off_hours
        threat_level = situation.get("threat_level", "MEDIUM")

        deployments = []

        # Eagle - Strategic oversight
        if threat_level in ["HIGH", "CRITICAL"] or len(threats) > 3:
            deployments.append(
                {
                    "bird": "EAGLE",
                    "mode": "STRATEGIC_COMMAND",
                    "priority": "HIGH",
                    "reasoning": "Multiple threats require strategic coordination",
                }
            )

        # Falcon - Rapid response
        if any(t.get("threat_score", 0) >= 7.0 for t in threats):
            deployments.append(
                {
                    "bird": "FALCON",
                    "mode": "RAPID_RESPONSE",
                    "priority": "CRITICAL",
                    "reasoning": "High-score threats detected, immediate response needed",
                }
            )

        # Owl - Night watch
        if time_of_day in ["night", "off_hours"]:
            deployments.append(
                {
                    "bird": "OWL",
                    "mode": "NIGHT_WATCH",
                    "priority": "HIGH",
                    "reasoning": "Off-hours require enhanced stealth monitoring",
                }
            )

        # Sparrow - Routine
        if not threats or threat_level == "LOW":
            deployments.append(
                {
                    "bird": "SPARROW",
                    "mode": "ROUTINE_CHECK",
                    "priority": "NORMAL",
                    "reasoning": "Maintain baseline monitoring",
                }
            )

        return {
            "deployments": deployments,
            "coordination": (
                "Birds should report to Eagle if deployed"
                if any(d["bird"] == "EAGLE" for d in deployments)
                else "Independent operation"
            ),
            "estimated_coverage": "100%" if len(deployments) >= 2 else f"{len(deployments) * 50}%",
        }
