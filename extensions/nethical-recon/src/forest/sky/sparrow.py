"""
🐦 Sparrow - Routine Check & Heartbeat Monitoring

> "Small but essential - I check every tree, every branch, every day"
> "The friendly neighborhood watch"
"""

from datetime import datetime
from typing import Any

from .base_bird import AlertLevel, BaseBird, BirdAlert, BirdType, FlightMode


class Sparrow(BaseBird):
    """
    🐦 SPARROW - Routine Check Bird

    Capabilities:
    - Regular heartbeat monitoring
    - Basic health checks
    - Routine log collection
    - Soft chirp notifications
    - Normal baseline establishment

    Flight Mode: PATROLLING (regular rounds)
    Alert Sound: CHIRP (friendly notification)
    """

    def __init__(self, name: str = "Sparrow-Scout"):
        """Initialize Sparrow surveillance bird"""
        super().__init__(name, BirdType.SPARROW)
        self.patrol_frequency = "regular"
        self.check_type = "routine"
        self.friendly = True
        self.baseline_data: dict[str, Any] = {}
        self.health_history: list[dict[str, Any]] = []

    def get_capabilities(self) -> dict[str, str]:
        """Get Sparrow's unique capabilities"""
        return {
            "frequency": "Regular patrols - consistent monitoring",
            "checks": "Basic health - heartbeat and vitals",
            "baseline": "Normal patterns - establishes baseline",
            "friendly": "Soft alerts - non-alarming notifications",
            "coverage": "Complete - checks every tree",
            "specialization": "Routine monitoring and health checks",
        }

    def scan(self, forest_data: dict[str, Any]) -> list[BirdAlert]:
        """
        Routine scan for basic health and status

        Sparrow focuses on:
        - Service availability (heartbeat)
        - Basic health metrics
        - Routine status checks
        - Establishing baseline
        - Simple anomalies

        Args:
            forest_data: Current forest state

        Returns:
            List of routine status alerts
        """
        alerts = []

        # Ensure we're patrolling
        if not self.is_active:
            self.take_flight(FlightMode.PATROLLING)

        trees = forest_data.get("trees", [])
        overall_health = forest_data.get("overall_health", 1.0)

        # Store current health snapshot
        self.health_history.append(
            {"timestamp": datetime.now().isoformat(), "overall_health": overall_health, "tree_count": len(trees)}
        )

        # Keep only recent history (last 100 checks)
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]

        # Check each tree's basic health
        healthy_count = 0
        unhealthy_count = 0
        offline_count = 0

        for tree in trees:
            tree_name = tree.get("name", "unknown")
            tree_health = tree.get("health", 1.0)
            is_online = tree.get("online", True)

            if not is_online:
                # Tree is offline - more serious
                offline_count += 1
                alert = self.create_alert(
                    AlertLevel.WARNING,
                    f"chirp! Tree offline: {tree_name}",
                    location={"tree": tree_name, "status": "offline"},
                    evidence=[
                        "Status: Offline",
                        f"Last seen: {tree.get('last_seen', 'unknown')}",
                        "Action: Check connectivity",
                    ],
                )
                alerts.append(alert)

            elif tree_health < 0.5:
                # Tree is very unhealthy
                unhealthy_count += 1
                alert = self.create_alert(
                    AlertLevel.WARNING,
                    f"chirp! Tree unhealthy: {tree_name} - {tree_health*100:.0f}% health",
                    location={"tree": tree_name, "status": "unhealthy"},
                    evidence=[f"Health: {tree_health*100:.0f}%", "Action: Investigate issues"],
                )
                alerts.append(alert)

            else:
                healthy_count += 1

        # Overall forest status (routine check)
        if healthy_count == len(trees) and len(trees) > 0:
            # All good - soft chirp
            alert = self.create_alert(
                AlertLevel.INFO,
                f"chirp~ All systems healthy: {healthy_count}/{len(trees)} trees online",
                location={"scope": "entire_forest"},
                evidence=[
                    f"Healthy trees: {healthy_count}",
                    f"Overall health: {overall_health*100:.0f}%",
                    "Status: Normal operations",
                ],
            )
            alerts.append(alert)

        elif unhealthy_count > 0 or offline_count > 0:
            # Some issues found
            alert = self.create_alert(
                AlertLevel.WARNING,
                f"chirp! Forest status: {healthy_count} healthy, {unhealthy_count} unhealthy, {offline_count} offline",
                location={"scope": "entire_forest"},
                evidence=[
                    f"Total trees: {len(trees)}",
                    f"Issues found: {unhealthy_count + offline_count}",
                    "Requires attention",
                ],
            )
            alerts.append(alert)

        # Check for basic resource issues
        for tree in trees:
            resources = tree.get("resources", {})

            # CPU check
            cpu = resources.get("cpu_percent", 0)
            if cpu > 90:
                alert = self.create_alert(
                    AlertLevel.INFO,
                    f"chirp~ High CPU on {tree.get('name')}: {cpu}%",
                    location={"tree": tree.get("name"), "resource": "cpu"},
                    evidence=[f"CPU usage: {cpu}%", "Note: High but not critical"],
                )
                alerts.append(alert)

            # Memory check
            memory = resources.get("memory_percent", 0)
            if memory > 90:
                alert = self.create_alert(
                    AlertLevel.INFO,
                    f"chirp~ High memory on {tree.get('name')}: {memory}%",
                    location={"tree": tree.get("name"), "resource": "memory"},
                    evidence=[f"Memory usage: {memory}%", "Note: High but not critical"],
                )
                alerts.append(alert)

            # Disk check
            disk = resources.get("disk_percent", 0)
            if disk > 85:
                alert = self.create_alert(
                    AlertLevel.WARNING,
                    f"chirp! Low disk space on {tree.get('name')}: {disk}% full",
                    location={"tree": tree.get("name"), "resource": "disk"},
                    evidence=[f"Disk usage: {disk}%", "Action: Clean up or expand"],
                )
                alerts.append(alert)

        # Update baseline with normal behavior
        if overall_health > 0.8 and unhealthy_count == 0:
            self._update_baseline(forest_data)

        return alerts

    def _update_baseline(self, forest_data: dict[str, Any]):
        """Update baseline with normal behavior data"""
        self.baseline_data = {
            "timestamp": datetime.now().isoformat(),
            "tree_count": len(forest_data.get("trees", [])),
            "overall_health": forest_data.get("overall_health", 1.0),
            "threat_count": sum(forest_data.get("threats", {}).values()),
            "status": "normal",
        }

    def heartbeat_check(self, tree: dict[str, Any]) -> dict[str, Any]:
        """
        Perform heartbeat check on a tree

        Args:
            tree: Tree to check

        Returns:
            Heartbeat status
        """
        tree_name = tree.get("name", "unknown")
        is_online = tree.get("online", False)
        last_heartbeat = tree.get("last_heartbeat", None)

        status = {
            "tree": tree_name,
            "checker": self.name,
            "timestamp": datetime.now().isoformat(),
            "online": is_online,
            "status": "healthy" if is_online else "offline",
            "response_time": None,
        }

        if is_online:
            # Simulate response time check
            response_time = tree.get("response_time_ms", 0)
            status["response_time"] = f"{response_time}ms"

            if response_time < 100:
                status["performance"] = "excellent"
            elif response_time < 500:
                status["performance"] = "good"
            elif response_time < 1000:
                status["performance"] = "acceptable"
            else:
                status["performance"] = "slow"
                status["note"] = "Consider investigating performance"
        else:
            status["note"] = "Tree not responding - check connectivity"
            status["last_seen"] = last_heartbeat

        return status

    def routine_report(self) -> dict[str, Any]:
        """
        Generate routine status report

        Returns:
            Summary of routine checks
        """
        if not self.health_history:
            return {"reporter": self.name, "status": "No data yet", "message": "Still collecting baseline data"}

        recent = self.health_history[-10:] if len(self.health_history) >= 10 else self.health_history

        avg_health = sum(h["overall_health"] for h in recent) / len(recent)

        # Determine trend
        if len(recent) >= 3:
            old_avg = sum(h["overall_health"] for h in recent[:3]) / 3
            new_avg = sum(h["overall_health"] for h in recent[-3:]) / 3
            trend = "improving" if new_avg > old_avg else "declining" if new_avg < old_avg else "stable"
        else:
            trend = "insufficient data"

        return {
            "reporter": self.name,
            "report_type": "routine_status",
            "checks_performed": len(self.health_history),
            "average_health": f"{avg_health*100:.1f}%",
            "health_trend": trend,
            "baseline_established": bool(self.baseline_data),
            "last_check": recent[-1]["timestamp"] if recent else None,
            "status": "normal" if avg_health > 0.7 else "attention_needed",
            "recommendations": self._get_routine_recommendations(avg_health, trend),
        }

    def _get_routine_recommendations(self, avg_health: float, trend: str) -> list[str]:
        """Generate routine recommendations"""
        recommendations = []

        if avg_health > 0.9:
            recommendations.append("✅ Excellent - maintain current security posture")
        elif avg_health > 0.7:
            recommendations.append("👍 Good - continue monitoring")
        else:
            recommendations.append("⚠️ Attention needed - investigate issues")

        if trend == "declining":
            recommendations.append("📉 Health declining - increase monitoring frequency")
            recommendations.append("🔍 Deploy Falcon for detailed threat scan")
        elif trend == "improving":
            recommendations.append("📈 Health improving - current measures effective")

        recommendations.append("🔄 Continue routine patrols")

        return recommendations

    def get_baseline(self) -> dict[str, Any]:
        """Get established baseline data"""
        if not self.baseline_data:
            return {"status": "not_established", "note": "Still learning normal behavior"}

        return {
            "status": "established",
            "baseline": self.baseline_data,
            "history_size": len(self.health_history),
            "confidence": min(len(self.health_history) / 100, 1.0),
        }

    def friendly_chirp(self, message: str) -> BirdAlert:
        """
        Send a friendly chirp notification

        Args:
            message: Friendly message

        Returns:
            Info-level alert
        """
        return self.create_alert(
            AlertLevel.INFO, f"chirp~ {message}", evidence=["Routine notification", "No action required"]
        )

    def __str__(self) -> str:
        """String representation"""
        checks = len(self.health_history)
        return f"🐦 {self.name} [SPARROW] - {checks} checks completed - {self.flight_mode.value.upper()}"
