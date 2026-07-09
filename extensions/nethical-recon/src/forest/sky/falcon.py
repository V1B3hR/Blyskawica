"""
🦅 Falcon - Fast Response & Real-Time Alerts

> "Fastest in the sky - I see threats instantly and screech the alarm"
> "Sharp vision, lightning speed, piercing cry"
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from .base_bird import AlertLevel, BaseBird, BirdAlert, BirdType, FlightMode


class Falcon(BaseBird):
    """
    🦅 FALCON - Fast Response Bird

    Capabilities:
    - Real-time threat detection (ostry wzrok)
    - Instant alert system (przenikliwy krzyk)
    - Quick targeting and marking
    - Active hunting patrols
    - Fast evidence gathering

    Flight Mode: HUNTING (active pursuit)
    Alert Sound: SCREECH (piercing and immediate)
    """

    def __init__(self, name: str = "Falcon-Hunter"):
        """Initialize Falcon surveillance bird"""
        super().__init__(name, BirdType.FALCON)
        self.reaction_time = "instant"  # Fastest response
        self.vision_sharpness = "maximum"
        self.alert_priority = "immediate"
        self.hunting_mode = True
        self.targets: list[dict[str, Any]] = []

    def get_capabilities(self) -> dict[str, str]:
        """Get Falcon's unique capabilities"""
        return {
            "speed": "Fastest bird - instant response",
            "vision": "Sharpest eyes - detail detection",
            "alerts": "Piercing screech - immediate notification",
            "hunting": "Active pursuit - tracks targets",
            "reaction": "Real-time - no delay",
            "specialization": "Threat detection and rapid response",
        }

    def scan(self, forest_data: dict[str, Any]) -> list[BirdAlert]:
        """
        Fast real-time scan for immediate threats

        Falcon focuses on:
        - Real-time anomalies
        - Suspicious processes
        - Port scans and attacks
        - Unexpected network activity
        - Immediate threat indicators

        Args:
            forest_data: Current forest state

        Returns:
            List of immediate alerts
        """
        alerts = []

        # Ensure we're hunting
        if not self.is_active:
            self.take_flight(FlightMode.HUNTING)

        trees = forest_data.get("trees", [])
        recent_events = forest_data.get("recent_events", [])
        network_activity = forest_data.get("network_activity", {})

        # Real-time: New threats just appeared
        new_threats = forest_data.get("new_threats", [])
        for threat in new_threats:
            alert = self.create_alert(
                AlertLevel.ELEVATED,
                f"SCREECH! New threat detected: {threat.get('type', 'unknown')} on {threat.get('location', 'unknown')}",
                location=threat.get("location_detail", {}),
                evidence=[
                    f"Threat type: {threat.get('type')}",
                    "First seen: just now",
                    f"Confidence: {threat.get('confidence', 0)*100:.0f}%",
                ],
            )
            alerts.append(alert)
            self.targets.append(threat)

        # Real-time: Port scans
        port_scans = network_activity.get("port_scans", [])
        for scan in port_scans:
            if self._is_recent(scan.get("timestamp")):
                alert = self.create_alert(
                    AlertLevel.ELEVATED,
                    f"SCREECH! Port scan from {scan.get('source_ip', 'unknown')}",
                    location={"tree": scan.get("target_tree"), "type": "network"},
                    evidence=[
                        f"Source: {scan.get('source_ip')}",
                        f"Ports: {scan.get('port_count', 0)} scanned",
                        f"Pattern: {scan.get('scan_type', 'unknown')}",
                    ],
                )
                alerts.append(alert)

        # Real-time: Suspicious processes
        for tree in trees:
            suspicious_procs = tree.get("suspicious_processes", [])
            for proc in suspicious_procs:
                if self._is_recent(proc.get("start_time")):
                    alert = self.create_alert(
                        AlertLevel.ELEVATED,
                        f"SCREECH! Suspicious process on {tree.get('name')}: {proc.get('name')}",
                        location={"tree": tree.get("name"), "branch": proc.get("pid")},
                        evidence=[
                            f"Process: {proc.get('name')}",
                            f"PID: {proc.get('pid')}",
                            f"Started: {proc.get('start_time')}",
                            f"Reason: {proc.get('reason', 'unknown behavior')}",
                        ],
                    )
                    alerts.append(alert)

        # Real-time: Authentication failures
        auth_failures = forest_data.get("auth_failures", [])
        for failure in auth_failures:
            if self._is_recent(failure.get("timestamp")):
                # Multiple failures = elevated alert
                count = failure.get("attempt_count", 1)
                level = AlertLevel.CRITICAL if count > 5 else AlertLevel.ELEVATED

                alert = self.create_alert(
                    level,
                    f"SCREECH! Authentication attack: {count} failed attempts on {failure.get('target')}",
                    location={"tree": failure.get("tree"), "type": "authentication"},
                    evidence=[
                        f"Username attempted: {failure.get('username')}",
                        f"Source: {failure.get('source_ip')}",
                        f"Attempts: {count}",
                        f"Service: {failure.get('service')}",
                    ],
                )
                alerts.append(alert)

        # Real-time: Unusual network connections
        unusual_connections = network_activity.get("unusual_connections", [])
        for conn in unusual_connections:
            if self._is_recent(conn.get("timestamp")):
                alert = self.create_alert(
                    AlertLevel.WARNING,
                    f"Unusual connection: {conn.get('source')} → {conn.get('destination')}",
                    location={"type": "network", "tree": conn.get("tree")},
                    evidence=[
                        f"Protocol: {conn.get('protocol')}",
                        f"Port: {conn.get('port')}",
                        f"Reason: {conn.get('reason', 'anomalous pattern')}",
                    ],
                )
                alerts.append(alert)

        # Real-time: Resource spikes
        for tree in trees:
            resource_alerts = tree.get("resource_spikes", [])
            for spike in resource_alerts:
                if self._is_recent(spike.get("timestamp")):
                    alert = self.create_alert(
                        AlertLevel.WARNING,
                        f"Resource spike on {tree.get('name')}: {spike.get('resource')} at {spike.get('value')}%",
                        location={"tree": tree.get("name"), "type": "resource"},
                        evidence=[
                            f"Resource: {spike.get('resource')}",
                            f"Value: {spike.get('value')}%",
                            f"Normal baseline: {spike.get('baseline')}%",
                        ],
                    )
                    alerts.append(alert)

        return alerts

    def _is_recent(self, timestamp: str | None, minutes: int = 5) -> bool:
        """Check if timestamp is recent (within specified minutes)"""
        if not timestamp:
            return True  # Treat missing timestamp as recent

        try:
            if isinstance(timestamp, str):
                event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            elif isinstance(timestamp, datetime):
                event_time = timestamp
            else:
                return True

            # Handle timezone-aware and naive datetime comparison
            cutoff = datetime.now()
            if event_time.tzinfo is not None:
                # If event_time is timezone-aware, make cutoff timezone-aware too

                cutoff = datetime.now(UTC)

            cutoff = cutoff - timedelta(minutes=minutes)
            return event_time > cutoff
        except Exception:
            return True  # On parse error, assume recent

    def hunt_target(self, target: dict[str, Any]) -> dict[str, Any]:
        """
        Actively hunt a specific target

        Args:
            target: Target information

        Returns:
            Hunt result with findings
        """
        hunt_result = {
            "hunter": self.name,
            "target": target,
            "status": "hunting",
            "findings": [],
            "recommendation": None,
        }

        threat_type = target.get("type", "unknown")
        confidence = target.get("confidence", 0)

        # High confidence threats get immediate marking
        if confidence > 0.8:
            hunt_result["status"] = "target_acquired"
            hunt_result["recommendation"] = "MARK_IMMEDIATELY"
            hunt_result["findings"].append(f"High confidence threat: {confidence*100:.0f}%")
            hunt_result["findings"].append("Recommend: Fire marker weapon")
            hunt_result["weapon_type"] = self._recommend_weapon(threat_type)

        elif confidence > 0.6:
            hunt_result["status"] = "tracking"
            hunt_result["recommendation"] = "CONTINUE_OBSERVATION"
            hunt_result["findings"].append(f"Medium confidence: {confidence*100:.0f}%")
            hunt_result["findings"].append("Recommend: Gather more evidence")

        else:
            hunt_result["status"] = "monitoring"
            hunt_result["recommendation"] = "OBSERVE_ONLY"
            hunt_result["findings"].append(f"Low confidence: {confidence*100:.0f}%")
            hunt_result["findings"].append("Recommend: Continue monitoring")

        return hunt_result

    def _recommend_weapon(self, threat_type: str) -> str:
        """Recommend weapon based on threat type"""
        weapon_map = {
            "malware": "RED_TRACER",
            "crow": "BLACK_TRACER",
            "squirrel": "BROWN_TRACER",
            "backdoor": "YELLOW_TRACER",
            "data_stealer": "RED_TRACER",
            "suspicious_ip": "ORANGE_TRACER",
        }
        return weapon_map.get(threat_type.lower(), "ORANGE_TRACER")

    def quick_response(self, alert_data: dict[str, Any]) -> list[str]:
        """
        Generate quick response actions for an alert

        Args:
            alert_data: Alert information

        Returns:
            List of immediate action items
        """
        actions = []

        alert_type = alert_data.get("type", "unknown")
        severity = alert_data.get("severity", "medium")

        # Always: Alert the command center
        actions.append("🚨 ALERT: Notify Eagle command immediately")

        if severity == "critical":
            actions.append("🛡️ DEFEND: Activate nanobots in affected area")
            actions.append("🎯 MARK: Fire marker weapon at threat")
            actions.append("🔒 ISOLATE: Quarantine affected branch/tree")

        if alert_type in ["port_scan", "network_attack"]:
            actions.append("📡 BLOCK: Add source IP to firewall rules")
            actions.append("🔍 TRACE: Track back to source")

        if alert_type in ["malware", "suspicious_process"]:
            actions.append("⏸️ SUSPEND: Stop suspicious process")
            actions.append("📸 CAPTURE: Take memory snapshot")
            actions.append("🦉 DEPLOY: Send Owl for deep analysis")

        if alert_type == "auth_failure":
            actions.append("🔐 LOCK: Temporarily lock target account")
            actions.append("📝 LOG: Preserve authentication logs")

        actions.append("📊 DOCUMENT: Save all evidence to database")

        return actions

    def get_active_hunts(self) -> list[dict[str, Any]]:
        """Get list of active hunting targets"""
        return [
            {
                "target": target,
                "tracked_since": target.get("first_seen"),
                "confidence": target.get("confidence"),
                "status": "active",
            }
            for target in self.targets
        ]

    def clear_targets(self, max_age_minutes: int = 60):
        """Clear old hunting targets"""
        # Keep targets from last hour by default
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
        self.targets = [t for t in self.targets if self._is_recent(t.get("first_seen"), max_age_minutes)]

    def __str__(self) -> str:
        """String representation"""
        target_count = len(self.targets)
        return f"🦅 {self.name} [FALCON] - Hunting {target_count} targets - {self.flight_mode.value.upper()}"
