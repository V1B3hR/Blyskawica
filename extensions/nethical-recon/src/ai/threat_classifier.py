"""
AI Threat Classifier

Classifies threats into specific animal types (Crow, Magpie, Squirrel, Snake, Parasite, Bat)
based on behavior patterns and indicators.
"""

import logging
from datetime import datetime
from typing import Any


class ThreatClassifier:
    """
    🎭 AI Threat Classification Engine

    Classifies threats as:
    • 🐦‍⬛ Crow (Malware)
    • 🐦 Magpie (Data Stealer)
    • 🐿️ Squirrel (Lateral Movement)
    • 🐍 Snake (Rootkit)
    • 🐛 Parasite (Cryptominer)
    • 🦇 Bat (Night Attacks)
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.classification_rules = self._load_classification_rules()

    def _load_classification_rules(self) -> dict[str, dict[str, Any]]:
        """Load classification rules for each threat type"""
        return {
            "crow": {
                "indicators": ["persistent", "hidden_process", "waiting", "obfuscated", "c2_communication", "patience"],
                "behaviors": ["execution", "persistence", "command_and_control", "stealth"],
                "weight_indicators": 0.6,
                "weight_behaviors": 0.4,
            },
            "magpie": {
                "indicators": [
                    "data_access",
                    "credential_theft",
                    "exfiltration",
                    "file_access",
                    "database_query",
                    "clipboard_access",
                ],
                "behaviors": ["collection", "exfiltration", "credential_access", "discovery"],
                "weight_indicators": 0.7,
                "weight_behaviors": 0.3,
            },
            "squirrel": {
                "indicators": [
                    "lateral_movement",
                    "network_scanning",
                    "smb_activity",
                    "rdp_connection",
                    "ssh_connection",
                    "host_hopping",
                ],
                "behaviors": ["lateral_movement", "discovery", "remote_services", "valid_accounts"],
                "weight_indicators": 0.5,
                "weight_behaviors": 0.5,
            },
            "snake": {
                "indicators": [
                    "rootkit",
                    "kernel_modification",
                    "driver_loading",
                    "process_hiding",
                    "privilege_escalation",
                    "deep_system_access",
                ],
                "behaviors": ["privilege_escalation", "defense_evasion", "persistence", "rootkit_behavior"],
                "weight_indicators": 0.8,
                "weight_behaviors": 0.2,
            },
            "parasite": {
                "indicators": [
                    "high_cpu",
                    "cryptomining",
                    "resource_abuse",
                    "gpu_usage",
                    "mining_pool_connection",
                    "cryptocurrency",
                ],
                "behaviors": ["impact", "resource_hijacking", "persistence"],
                "weight_indicators": 0.7,
                "weight_behaviors": 0.3,
            },
            "bat": {
                "indicators": [
                    "night_activity",
                    "off_hours",
                    "scheduled_task",
                    "cron_job",
                    "time_based",
                    "after_hours",
                ],
                "behaviors": ["execution", "scheduled_task", "time_based_evasion"],
                "weight_indicators": 0.6,
                "weight_behaviors": 0.4,
            },
        }

    def classify_threat(self, threat_data: dict[str, Any]) -> dict[str, Any]:
        """
        Classify a threat into one of the animal types

        Args:
            threat_data: Threat information including indicators and behaviors

        Returns:
            Classification result with confidence
        """
        indicators = set(threat_data.get("indicators", []))
        behaviors = set(threat_data.get("behaviors", []))

        # Calculate scores for each threat type
        scores = {}
        for threat_type, rules in self.classification_rules.items():
            score = self._calculate_classification_score(indicators, behaviors, rules)
            scores[threat_type] = score

        # Find best match
        best_match = max(scores.items(), key=lambda x: x[1])
        classification = best_match[0]
        confidence = best_match[1]

        # Get emoji and name
        emoji_map = {"crow": "🐦‍⬛", "magpie": "🐦", "squirrel": "🐿️", "snake": "🐍", "parasite": "🐛", "bat": "🦇"}

        name_map = {
            "crow": "Crow (Malware)",
            "magpie": "Magpie (Data Stealer)",
            "squirrel": "Squirrel (Lateral Movement)",
            "snake": "Snake (Rootkit)",
            "parasite": "Parasite (Cryptominer)",
            "bat": "Bat (Night Attack)",
        }

        return {
            "threat_id": threat_data.get("id", "unknown"),
            "classification": classification,
            "emoji": emoji_map.get(classification, "❓"),
            "name": name_map.get(classification, "Unknown"),
            "confidence": round(confidence, 2),
            "all_scores": {k: round(v, 2) for k, v in scores.items()},
            "matched_indicators": list(indicators & set(self.classification_rules[classification]["indicators"])),
            "matched_behaviors": list(behaviors & set(self.classification_rules[classification]["behaviors"])),
            "recommendations": self._get_classification_recommendations(classification),
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_classification_score(self, indicators: set, behaviors: set, rules: dict) -> float:
        """Calculate classification score for a threat type"""
        rule_indicators = set(rules["indicators"])
        rule_behaviors = set(rules["behaviors"])

        # Calculate indicator match score
        indicator_score = 0.0
        if rule_indicators:
            indicator_matches = len(indicators & rule_indicators)
            indicator_score = indicator_matches / len(rule_indicators)

        # Calculate behavior match score
        behavior_score = 0.0
        if rule_behaviors:
            behavior_matches = len(behaviors & rule_behaviors)
            behavior_score = behavior_matches / len(rule_behaviors)

        # Weighted combination
        total_score = indicator_score * rules["weight_indicators"] + behavior_score * rules["weight_behaviors"]

        return total_score

    def _get_classification_recommendations(self, threat_type: str) -> list[str]:
        """Get specific recommendations for classified threat"""
        recommendations = {
            "crow": [
                "🔫 Mark with BLACK tracer immediately",
                "🤖 Deploy defensive nanobots",
                "🦉 Deploy Owl for continuous monitoring",
                "🔍 Check for C2 communication",
                "🛡️ Isolate affected system",
            ],
            "magpie": [
                "🔫 Mark with PURPLE tracer",
                "🔒 Lock down sensitive data access",
                "📊 Audit data access logs",
                "🚫 Block exfiltration paths",
                "🔐 Reset credentials",
            ],
            "squirrel": [
                "🔫 Mark with BROWN tracer",
                "🌐 Review network segmentation",
                "🔍 Map lateral movement path",
                "🛡️ Strengthen access controls",
                "📡 Monitor inter-host connections",
            ],
            "snake": [
                "🔫 Mark with RED tracer - CRITICAL",
                "⚠️ System may be deeply compromised",
                "🔧 Kernel-level inspection required",
                "💿 Consider full system rebuild",
                "🦅 Alert Eagle for strategic assessment",
            ],
            "parasite": [
                "🔫 Mark with ORANGE tracer",
                "⚡ Terminate resource-draining process",
                "🔍 Check for mining pool connections",
                "📊 Monitor resource usage",
                "🛡️ Deploy resource monitoring nanobots",
            ],
            "bat": [
                "🔫 Mark with BLUE tracer",
                "🦉 Deploy Owl for night watch",
                "⏰ Review scheduled tasks",
                "🔍 Monitor off-hours activity",
                "📅 Check cron jobs and timers",
            ],
        }

        return recommendations.get(threat_type, ["Mark threat and monitor"])

    def classify_multiple_threats(self, threats: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Classify multiple threats at once

        Args:
            threats: List of threat data

        Returns:
            Classification results for all threats
        """
        results = []
        counts = {"crow": 0, "magpie": 0, "squirrel": 0, "snake": 0, "parasite": 0, "bat": 0, "unknown": 0}

        for threat in threats:
            classification = self.classify_threat(threat)
            results.append(classification)

            threat_type = classification["classification"]
            if classification["confidence"] >= 0.5:
                counts[threat_type] = counts.get(threat_type, 0) + 1
            else:
                counts["unknown"] += 1

        return {
            "total_threats": len(threats),
            "classifications": results,
            "counts": counts,
            "dominant_threat": max(counts.items(), key=lambda x: x[1])[0] if threats else "none",
            "summary": self._generate_classification_summary(counts),
        }

    def _generate_classification_summary(self, counts: dict[str, int]) -> str:
        """Generate human-readable classification summary"""
        total = sum(counts.values())
        if total == 0:
            return "No threats classified"

        # Build summary string
        parts = []
        for threat_type, count in counts.items():
            if count > 0 and threat_type != "unknown":
                emoji_map = {
                    "crow": "🐦‍⬛",
                    "magpie": "🐦",
                    "squirrel": "🐿️",
                    "snake": "🐍",
                    "parasite": "🐛",
                    "bat": "🦇",
                }
                emoji = emoji_map.get(threat_type, "❓")
                parts.append(f"{emoji} {count} {threat_type}(s)")

        if counts["unknown"] > 0:
            parts.append(f"❓ {counts['unknown']} unknown")

        return ", ".join(parts) if parts else "No threats classified"

    def suggest_bird_for_threat(self, threat_classification: dict[str, Any]) -> dict[str, Any]:
        """
        Suggest which bird should handle this threat type

        Args:
            threat_classification: Result from classify_threat

        Returns:
            Bird deployment suggestion
        """
        threat_type = threat_classification["classification"]
        confidence = threat_classification["confidence"]

        # Bird suggestions based on threat type
        bird_map = {
            "crow": {
                "primary": "OWL",
                "reason": "Crows are stealthy and patient; Owl excels at detecting hidden threats",
                "secondary": "FALCON",
                "backup_reason": "Falcon provides rapid response if Crow becomes active",
            },
            "magpie": {
                "primary": "FALCON",
                "reason": "Magpies move quickly; Falcon matches their speed",
                "secondary": "EAGLE",
                "backup_reason": "Eagle coordinates data protection strategy",
            },
            "squirrel": {
                "primary": "EAGLE",
                "reason": "Squirrels hop between trees; Eagle tracks movement patterns",
                "secondary": "FALCON",
                "backup_reason": "Falcon provides rapid response at each hop",
            },
            "snake": {
                "primary": "EAGLE",
                "reason": "Snakes are deeply embedded; requires strategic Eagle oversight",
                "secondary": "OWL",
                "backup_reason": "Owl detects deep system modifications",
            },
            "parasite": {
                "primary": "SPARROW",
                "reason": "Parasites drain resources slowly; Sparrow monitors baseline",
                "secondary": "FALCON",
                "backup_reason": "Falcon terminates resource-draining processes",
            },
            "bat": {
                "primary": "OWL",
                "reason": "Bats are active at night; Owl is the night watcher",
                "secondary": "EAGLE",
                "backup_reason": "Eagle plans strategic night defense",
            },
        }

        suggestion = bird_map.get(
            threat_type,
            {
                "primary": "FALCON",
                "reason": "Unknown threat type; Falcon provides general rapid response",
                "secondary": "EAGLE",
                "backup_reason": "Eagle provides strategic assessment",
            },
        )

        return {
            "threat_type": threat_type,
            "confidence": confidence,
            "primary_bird": suggestion["primary"],
            "primary_reason": suggestion["reason"],
            "secondary_bird": suggestion.get("secondary"),
            "secondary_reason": suggestion.get("backup_reason"),
            "deployment_priority": "CRITICAL" if confidence >= 0.8 else "HIGH" if confidence >= 0.6 else "MEDIUM",
        }

    def get_threat_statistics(self) -> dict[str, Any]:
        """Get statistics about threat classifications"""
        return {
            "supported_types": list(self.classification_rules.keys()),
            "total_indicators": sum(len(r["indicators"]) for r in self.classification_rules.values()),
            "total_behaviors": sum(len(r["behaviors"]) for r in self.classification_rules.values()),
            "classification_confidence_threshold": 0.5,
            "emojis": {"crow": "🐦‍⬛", "magpie": "🐦", "squirrel": "🐿️", "snake": "🐍", "parasite": "🐛", "bat": "🦇"},
        }
