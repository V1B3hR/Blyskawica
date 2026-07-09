"""
Rules Engine - Decision-making engine for nanobots.

Evaluates rules to determine when and how nanobots should act.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RuleOperator(Enum):
    """Operators for rule conditions"""

    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class RuleCondition:
    """A single condition in a rule"""

    field: str
    operator: RuleOperator
    value: Any

    def evaluate(self, event: dict[str, Any]) -> bool:
        """Evaluate condition against event"""
        # Get field value from event (support nested fields with dot notation)
        field_value = self._get_field_value(event, self.field)

        if field_value is None:
            return False

        # Evaluate based on operator
        if self.operator == RuleOperator.EQUALS:
            return field_value == self.value
        elif self.operator == RuleOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == RuleOperator.GREATER_THAN:
            return field_value > self.value
        elif self.operator == RuleOperator.LESS_THAN:
            return field_value < self.value
        elif self.operator == RuleOperator.GREATER_EQUAL:
            return field_value >= self.value
        elif self.operator == RuleOperator.LESS_EQUAL:
            return field_value <= self.value
        elif self.operator == RuleOperator.CONTAINS:
            return self.value in field_value
        elif self.operator == RuleOperator.NOT_CONTAINS:
            return self.value not in field_value
        elif self.operator == RuleOperator.IN:
            return field_value in self.value
        elif self.operator == RuleOperator.NOT_IN:
            return field_value not in self.value

        return False

    def _get_field_value(self, event: dict[str, Any], field: str) -> Any:
        """Get field value from event (supports nested fields)"""
        parts = field.split(".")
        value = event

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value


@dataclass
class Rule:
    """
    A rule that determines if an action should be taken.

    Rules consist of:
    - Conditions (AND/OR logic)
    - Priority (higher priority rules evaluated first)
    - Action to take if rule matches
    - Confidence boost/penalty
    """

    rule_id: str
    name: str
    conditions: list[RuleCondition]
    logic: str = "AND"  # AND or OR
    priority: int = 0
    action_type: str | None = None
    confidence_modifier: float = 0.0  # Add/subtract from base confidence
    enabled: bool = True

    def matches(self, event: dict[str, Any]) -> bool:
        """Check if rule matches event"""
        if not self.enabled:
            return False

        if not self.conditions:
            return False

        # Evaluate conditions
        results = [condition.evaluate(event) for condition in self.conditions]

        # Apply logic
        if self.logic == "AND":
            return all(results)
        elif self.logic == "OR":
            return any(results)
        else:
            return False

    def apply_confidence_modifier(self, base_confidence: float) -> float:
        """Apply confidence modifier"""
        return max(0.0, min(1.0, base_confidence + self.confidence_modifier))


class RulesEngine:
    """
    Engine that evaluates rules to guide nanobot decisions.

    The rules engine provides:
    - Rule-based decision making
    - Priority handling
    - Confidence adjustment
    - Custom rule creation
    """

    def __init__(self):
        """Initialize rules engine"""
        self.rules: dict[str, Rule] = {}
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default security rules"""
        # Rule: Auto-block known malicious IPs
        self.add_rule(
            Rule(
                rule_id="block_known_malicious",
                name="Block Known Malicious IPs",
                conditions=[RuleCondition("known_malicious", RuleOperator.EQUALS, True)],
                priority=100,
                action_type="block_ip",
                confidence_modifier=0.3,
            )
        )

        # Rule: Auto-block rapid port scanners
        self.add_rule(
            Rule(
                rule_id="block_port_scanner",
                name="Block Rapid Port Scanners",
                conditions=[
                    RuleCondition("port_scan_detected", RuleOperator.EQUALS, True),
                    RuleCondition("ports_scanned", RuleOperator.GREATER_THAN, 50),
                ],
                logic="AND",
                priority=90,
                action_type="block_ip",
                confidence_modifier=0.25,
            )
        )

        # Rule: Rate limit on brute force
        self.add_rule(
            Rule(
                rule_id="ratelimit_bruteforce",
                name="Rate Limit Brute Force Attempts",
                conditions=[
                    RuleCondition("brute_force_attempt", RuleOperator.EQUALS, True),
                    RuleCondition("failed_auth_attempts", RuleOperator.GREATER_EQUAL, 5),
                ],
                logic="AND",
                priority=85,
                action_type="rate_limit",
                confidence_modifier=0.20,
            )
        )

        # Rule: Deploy honeypot on reconnaissance
        self.add_rule(
            Rule(
                rule_id="honeypot_recon",
                name="Deploy Honeypot on Reconnaissance",
                conditions=[RuleCondition("recon_activity", RuleOperator.EQUALS, True)],
                priority=70,
                action_type="honeypot",
                confidence_modifier=0.15,
            )
        )

        # Rule: Alert on high threat score
        self.add_rule(
            Rule(
                rule_id="alert_high_threat",
                name="Alert on High Threat Score",
                conditions=[RuleCondition("threat_score", RuleOperator.GREATER_EQUAL, 8.0)],
                priority=95,
                action_type="alert",
                confidence_modifier=0.20,
            )
        )

        # Rule: Hunt threats with IOC matches
        self.add_rule(
            Rule(
                rule_id="hunt_ioc_match",
                name="Hunt Threats with IOC Matches",
                conditions=[RuleCondition("iocs", RuleOperator.GREATER_THAN, 0)],
                priority=80,
                action_type="threat_hunt",
                confidence_modifier=0.15,
            )
        )

    def add_rule(self, rule: Rule) -> bool:
        """
        Add a rule to the engine.

        Args:
            rule: Rule to add

        Returns:
            True if added successfully
        """
        if rule.rule_id in self.rules:
            return False

        self.rules[rule.rule_id] = rule
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a rule from the engine.

        Args:
            rule_id: ID of rule to remove

        Returns:
            True if removed
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False

    def evaluate(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Evaluate all rules against an event.

        Args:
            event: Event to evaluate

        Returns:
            List of matching rules with applied modifiers
        """
        matches = []

        # Get all matching rules
        for rule in self.rules.values():
            if rule.matches(event):
                matches.append(
                    {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "priority": rule.priority,
                        "action_type": rule.action_type,
                        "confidence_modifier": rule.confidence_modifier,
                    }
                )

        # Sort by priority (highest first)
        matches.sort(key=lambda x: x["priority"], reverse=True)

        return matches

    def get_recommended_action(self, event: dict[str, Any], base_confidence: float) -> dict[str, Any] | None:
        """
        Get recommended action based on rules.

        Args:
            event: Event to evaluate
            base_confidence: Base confidence level

        Returns:
            Recommended action with adjusted confidence, or None
        """
        matches = self.evaluate(event)

        if not matches:
            return None

        # Use highest priority match
        top_match = matches[0]

        # Adjust confidence
        adjusted_confidence = min(1.0, max(0.0, base_confidence + top_match["confidence_modifier"]))

        return {
            "action_type": top_match["action_type"],
            "confidence": adjusted_confidence,
            "rule_id": top_match["rule_id"],
            "rule_name": top_match["rule_name"],
            "all_matches": matches,
        }

    def get_all_rules(self) -> list[Rule]:
        """Get all rules"""
        return list(self.rules.values())

    def get_rule(self, rule_id: str) -> Rule | None:
        """Get a specific rule"""
        return self.rules.get(rule_id)

    def clear_rules(self):
        """Clear all rules"""
        self.rules.clear()
