"""
🦉 Owl - Night Watch & Stealth Monitoring

> "Silent wings in darkness - I see what others cannot"
> "Wisdom, patience, and vision in the shadows"
"""

from datetime import datetime
from typing import Any

from .base_bird import AlertLevel, BaseBird, BirdAlert, BirdType, FlightMode


class Owl(BaseBird):
    """
    🦉 OWL - Night Watch Bird

    Capabilities:
    - Stealth monitoring (cichy lot)
    - Night-time/off-hours surveillance
    - Hidden process detection (widzi w ciemności)
    - Pattern correlation and wisdom
    - Low-noise observation

    Flight Mode: WATCHING (stealth observation)
    Alert Sound: HOOT (soft but concerning)
    """

    def __init__(self, name: str = "Owl-Watcher"):
        """Initialize Owl surveillance bird"""
        super().__init__(name, BirdType.OWL)
        self.stealth_mode = True
        self.night_vision = True
        self.patience_level = "maximum"
        self.wisdom_db: list[dict[str, Any]] = []  # Pattern learning
        self.hidden_observations: list[dict[str, Any]] = []

    def get_capabilities(self) -> dict[str, str]:
        """Get Owl's unique capabilities"""
        return {
            "stealth": "Silent flight - undetectable monitoring",
            "night_vision": "Sees in darkness - hidden processes",
            "wisdom": "Pattern correlation - learns behavior",
            "patience": "Long observation - waits for patterns",
            "timing": "Off-hours specialist - night attacks",
            "specialization": "Stealth and hidden threat detection",
        }

    def scan(self, forest_data: dict[str, Any]) -> list[BirdAlert]:
        """
        Stealth scan for hidden and night-time threats

        Owl focuses on:
        - Hidden/rootkit processes
        - Night-time activity (off-hours)
        - Behavioral anomalies
        - Correlation patterns
        - Long-term trends

        Args:
            forest_data: Current forest state

        Returns:
            List of stealth observation alerts
        """
        alerts = []

        # Ensure we're in stealth watch mode
        if not self.is_active:
            self.take_flight(FlightMode.WATCHING)

        trees = forest_data.get("trees", [])
        current_time = datetime.now()

        # Check if it's night time (off-hours)
        is_night = self._is_night_time(current_time)

        # Hidden process detection
        for tree in trees:
            hidden_procs = tree.get("hidden_processes", [])
            for proc in hidden_procs:
                alert = self.create_alert(
                    AlertLevel.ELEVATED,
                    f"hoot... Hidden process detected on {tree.get('name')}: {proc.get('name')}",
                    location={"tree": tree.get("name"), "type": "hidden_process"},
                    evidence=[
                        f"Process: {proc.get('name')}",
                        f"PID: {proc.get('pid')}",
                        f"Hidden technique: {proc.get('hiding_method', 'unknown')}",
                        f"Detection: {proc.get('detection_method', 'behavioral')}",
                    ],
                )
                alerts.append(alert)
                self.hidden_observations.append(
                    {
                        "type": "hidden_process",
                        "tree": tree.get("name"),
                        "process": proc,
                        "timestamp": current_time.isoformat(),
                    }
                )

        # Rootkit detection
        for tree in trees:
            rootkit_indicators = tree.get("rootkit_indicators", [])
            if rootkit_indicators:
                alert = self.create_alert(
                    AlertLevel.CRITICAL,
                    f"HOOT! Rootkit indicators on {tree.get('name')} - deep system compromise suspected",
                    location={"tree": tree.get("name"), "type": "rootkit"},
                    evidence=[
                        f"Indicators: {', '.join(rootkit_indicators)}",
                        "Severity: Critical - kernel-level threat",
                        "Recommendation: Forensic analysis required",
                    ],
                )
                alerts.append(alert)

        # Night-time activity monitoring
        if is_night:
            for tree in trees:
                night_activity = tree.get("current_activity", {})
                activity_level = night_activity.get("level", 0)

                # High activity during night is suspicious
                if activity_level > 0.7:  # 70% of normal activity
                    alert = self.create_alert(
                        AlertLevel.WARNING,
                        f"hoot... Unusual night activity on {tree.get('name')} - {activity_level*100:.0f}% of normal",
                        location={"tree": tree.get("name"), "time": "night"},
                        evidence=[
                            f"Activity level: {activity_level*100:.0f}%",
                            f"Time: {current_time.strftime('%H:%M')} (night hours)",
                            "Baseline: Low activity expected",
                            "Pattern: Suspicious off-hours behavior",
                        ],
                    )
                    alerts.append(alert)

        # Behavioral anomaly detection (Owl's wisdom)
        behavioral_anomalies = self._detect_behavioral_anomalies(forest_data)
        for anomaly in behavioral_anomalies:
            alert = self.create_alert(
                AlertLevel.WARNING,
                f"hoot... Behavioral anomaly: {anomaly.get('description')}",
                location=anomaly.get("location", {}),
                evidence=anomaly.get("evidence", []),
            )
            alerts.append(alert)

        # Pattern correlation (Owl's wisdom accumulation)
        patterns = self._correlate_patterns(forest_data)
        for pattern in patterns:
            if pattern.get("significance", 0) > 0.7:
                alert = self.create_alert(
                    AlertLevel.ELEVATED,
                    f"HOOT! Pattern detected: {pattern.get('description')}",
                    location=pattern.get("location", {}),
                    evidence=[
                        f"Pattern type: {pattern.get('type')}",
                        f"Significance: {pattern.get('significance', 0)*100:.0f}%",
                        f"Occurrences: {pattern.get('occurrences', 0)}",
                        f"Timespan: {pattern.get('timespan', 'unknown')}",
                    ],
                )
                alerts.append(alert)

        # Persistence mechanisms (long-term threats)
        for tree in trees:
            persistence = tree.get("persistence_mechanisms", [])
            for mech in persistence:
                alert = self.create_alert(
                    AlertLevel.ELEVATED,
                    f"hoot... Persistence mechanism found on {tree.get('name')}: {mech.get('type')}",
                    location={"tree": tree.get("name"), "type": "persistence"},
                    evidence=[
                        f"Mechanism: {mech.get('type')}",
                        f"Location: {mech.get('location')}",
                        f"Method: {mech.get('method')}",
                        "Risk: Long-term compromise",
                    ],
                )
                alerts.append(alert)

        return alerts

    def _is_night_time(self, current_time: datetime) -> bool:
        """
        Check if current time is night/off-hours
        Night defined as: 22:00 - 06:00
        """
        current_hour = current_time.hour
        return current_hour >= 22 or current_hour < 6

    def _detect_behavioral_anomalies(self, forest_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Detect behavioral anomalies using Owl's wisdom

        Owl learns normal patterns and identifies deviations
        """
        anomalies = []
        trees = forest_data.get("trees", [])

        for tree in trees:
            # Check for unusual user behavior
            user_behavior = tree.get("user_behavior", {})
            if user_behavior.get("anomaly_score", 0) > 0.7:
                anomalies.append(
                    {
                        "type": "user_behavior",
                        "description": f"Unusual user behavior on {tree.get('name')}",
                        "location": {"tree": tree.get("name")},
                        "evidence": [
                            f"Anomaly score: {user_behavior.get('anomaly_score', 0)*100:.0f}%",
                            f"Reason: {user_behavior.get('reason', 'deviated from baseline')}",
                            f"Actions: {user_behavior.get('unusual_actions', [])}",
                        ],
                    }
                )

            # Check for process behavior anomalies
            proc_anomalies = tree.get("process_anomalies", [])
            for proc in proc_anomalies:
                anomalies.append(
                    {
                        "type": "process_behavior",
                        "description": f"Process {proc.get('name')} behaving unusually",
                        "location": {"tree": tree.get("name"), "pid": proc.get("pid")},
                        "evidence": [
                            f"Process: {proc.get('name')}",
                            f"Anomaly: {proc.get('anomaly_type')}",
                            f"Expected: {proc.get('expected_behavior')}",
                            f"Observed: {proc.get('observed_behavior')}",
                        ],
                    }
                )

        return anomalies

    def _correlate_patterns(self, forest_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Correlate patterns across time and trees

        Owl's wisdom - connecting the dots
        """
        patterns = []

        # Add current observation to wisdom database
        self.wisdom_db.append(
            {
                "timestamp": datetime.now().isoformat(),
                "forest_state": {
                    "tree_count": len(forest_data.get("trees", [])),
                    "threat_count": sum(forest_data.get("threats", {}).values()),
                    "health": forest_data.get("overall_health", 1.0),
                },
            }
        )

        # Keep only recent wisdom (last 100 observations)
        if len(self.wisdom_db) > 100:
            self.wisdom_db = self.wisdom_db[-100:]

        # Detect repeating threat patterns
        if len(self.wisdom_db) >= 5:
            recent_threats = [obs["forest_state"]["threat_count"] for obs in self.wisdom_db[-10:]]

            # Check if threats are increasing
            if len(recent_threats) >= 5:
                trend = sum(recent_threats[-3:]) / 3 - sum(recent_threats[:3]) / 3
                if trend > 2:  # Significant increase
                    patterns.append(
                        {
                            "type": "increasing_threats",
                            "description": "Threat count increasing over time",
                            "significance": min(trend / 5, 1.0),
                            "occurrences": len(recent_threats),
                            "timespan": "last 10 observations",
                            "location": {"scope": "forest_wide"},
                        }
                    )

        # Detect coordinated attacks (same threat on multiple trees)
        trees = forest_data.get("trees", [])
        threat_types_by_tree = {}
        for tree in trees:
            tree_threats = tree.get("threats", [])
            for threat in tree_threats:
                threat_type = threat.get("type")
                if threat_type not in threat_types_by_tree:
                    threat_types_by_tree[threat_type] = []
                threat_types_by_tree[threat_type].append(tree.get("name"))

        for threat_type, affected_trees in threat_types_by_tree.items():
            if len(affected_trees) >= 2:
                patterns.append(
                    {
                        "type": "coordinated_attack",
                        "description": f'{threat_type} on multiple trees: {", ".join(affected_trees)}',
                        "significance": min(len(affected_trees) / 5, 1.0),
                        "occurrences": len(affected_trees),
                        "timespan": "current",
                        "location": {"scope": "multiple_trees", "trees": affected_trees},
                    }
                )

        return patterns

    def deep_observation(self, target: dict[str, Any], duration_minutes: int = 30) -> dict[str, Any]:
        """
        Perform deep stealth observation of a target

        Args:
            target: Target to observe
            duration_minutes: How long to observe

        Returns:
            Detailed observation report
        """
        observation = {
            "observer": self.name,
            "target": target,
            "duration_minutes": duration_minutes,
            "mode": "stealth",
            "findings": [],
            "patterns": [],
            "recommendations": [],
        }

        target_type = target.get("type", "unknown")

        # Owl's detailed observations based on target type
        if target_type == "suspicious_process":
            observation["findings"].append("Monitoring process behavior silently")
            observation["findings"].append("Tracking system calls and network connections")
            observation["findings"].append("Analyzing memory patterns")
            observation["recommendations"].append("Continue observation before action")
            observation["recommendations"].append("Gather forensic evidence")

        elif target_type == "hidden_threat":
            observation["findings"].append("Using advanced detection techniques")
            observation["findings"].append("Correlating with known malware patterns")
            observation["findings"].append("Checking for rootkit indicators")
            observation["recommendations"].append("Deploy deep system scan")
            observation["recommendations"].append("Consider forensic imaging")

        else:
            observation["findings"].append("General stealth observation in progress")
            observation["recommendations"].append("Gather more intelligence")

        observation["patterns"].append(
            {
                "type": "initial_observation",
                "confidence": 0.6,
                "note": f"Requires {duration_minutes} minutes of observation",
            }
        )

        return observation

    def share_wisdom(self) -> dict[str, Any]:
        """
        Share accumulated wisdom with other birds

        Returns:
            Wisdom summary
        """
        return {
            "bird": self.name,
            "wisdom_entries": len(self.wisdom_db),
            "hidden_observations": len(self.hidden_observations),
            "patterns_learned": self._summarize_patterns(),
            "insights": self._generate_insights(),
        }

    def _summarize_patterns(self) -> list[str]:
        """Summarize learned patterns"""
        if not self.wisdom_db:
            return ["No patterns learned yet"]

        patterns = []

        # Analyze threat trends
        if len(self.wisdom_db) >= 10:
            recent_threats = [obs["forest_state"]["threat_count"] for obs in self.wisdom_db[-10:]]
            avg_threats = sum(recent_threats) / len(recent_threats)
            patterns.append(f"Average threat count: {avg_threats:.1f}")

            if recent_threats[-1] > avg_threats * 1.5:
                patterns.append("Current threats above normal baseline")

        return patterns

    def _generate_insights(self) -> list[str]:
        """Generate insights from observations"""
        insights = []

        if len(self.hidden_observations) > 0:
            insights.append(f"Detected {len(self.hidden_observations)} hidden activities")

        if len(self.wisdom_db) >= 20:
            insights.append("Long-term monitoring established - baseline reliable")
        else:
            insights.append("Still learning baseline patterns")

        insights.append("Stealth monitoring continues silently")

        return insights

    def __str__(self) -> str:
        """String representation"""
        wisdom_count = len(self.wisdom_db)
        return f"🦉 {self.name} [OWL] - Wisdom: {wisdom_count} patterns - {self.flight_mode.value.upper()}"
