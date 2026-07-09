"""
forest/health_check.py
Health checking system for the forest.

Provides:
- Component health monitoring
- Anomaly detection
- Health scoring
- Status updates
"""

from datetime import datetime
from typing import Any

from .base import ComponentStatus, ForestComponent


class HealthChecker:
    """
    Health checking system for forest components.

    Analogia: 🏥 Leśny medyk - Sprawdza zdrowie lasu
    """

    def __init__(self):
        """Initialize the health checker"""
        self.check_history = []
        self.health_thresholds = {"excellent": 90.0, "good": 75.0, "fair": 60.0, "poor": 40.0, "critical": 20.0}

    def check_component(self, component: ForestComponent) -> dict[str, Any]:
        """
        Perform health check on a component.

        Args:
            component: Component to check

        Returns:
            Health check result dictionary
        """
        check_time = datetime.now()

        result = {
            "component_id": component.component_id,
            "component_type": component.get_type(),
            "check_time": check_time.isoformat(),
            "health_score": component.health_score,
            "status": component.status.name,
            "threat_count": component.get_threat_count(),
            "health_grade": self._get_health_grade(component.health_score),
            "issues": [],
        }

        # Check for issues
        if component.has_threats():
            result["issues"].append(f"{component.get_threat_count()} threats detected")

        if component.health_score < self.health_thresholds["poor"]:
            result["issues"].append("Poor health detected")

        if component.status in [ComponentStatus.CRITICAL, ComponentStatus.COMPROMISED]:
            result["issues"].append(f"Critical status: {component.status.name}")

        # Log the check
        self.check_history.append(result)

        return result

    def check_multiple_components(self, components: list[ForestComponent]) -> list[dict[str, Any]]:
        """
        Check multiple components.

        Args:
            components: List of components to check

        Returns:
            List of health check results
        """
        return [self.check_component(comp) for comp in components]

    def get_unhealthy_components(
        self, components: list[ForestComponent], threshold: float = 75.0
    ) -> list[ForestComponent]:
        """
        Get components with health below threshold.

        Args:
            components: Components to check
            threshold: Health score threshold

        Returns:
            List of unhealthy components
        """
        return [c for c in components if c.health_score < threshold]

    def get_compromised_components(self, components: list[ForestComponent]) -> list[ForestComponent]:
        """
        Get components with compromised status.

        Args:
            components: Components to check

        Returns:
            List of compromised components
        """
        return [c for c in components if c.status == ComponentStatus.COMPROMISED]

    def get_health_summary(self, components: list[ForestComponent]) -> dict[str, Any]:
        """
        Get overall health summary for components.

        Args:
            components: Components to analyze

        Returns:
            Health summary dictionary
        """
        if not components:
            return {"total_components": 0, "average_health": 100.0, "by_grade": {}, "by_status": {}}

        # Calculate statistics
        total_health = sum(c.health_score for c in components)
        average_health = total_health / len(components)

        # Group by health grade
        by_grade = {}
        for component in components:
            grade = self._get_health_grade(component.health_score)
            by_grade[grade] = by_grade.get(grade, 0) + 1

        # Group by status
        by_status = {}
        for component in components:
            status = component.status.name
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_components": len(components),
            "average_health": average_health,
            "by_grade": by_grade,
            "by_status": by_status,
            "unhealthy_count": len(self.get_unhealthy_components(components)),
            "compromised_count": len(self.get_compromised_components(components)),
        }

    def _get_health_grade(self, health_score: float) -> str:
        """Get health grade based on score"""
        if health_score >= self.health_thresholds["excellent"]:
            return "excellent"
        elif health_score >= self.health_thresholds["good"]:
            return "good"
        elif health_score >= self.health_thresholds["fair"]:
            return "fair"
        elif health_score >= self.health_thresholds["poor"]:
            return "poor"
        elif health_score >= self.health_thresholds["critical"]:
            return "critical"
        else:
            return "failing"

    def get_check_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent check history"""
        return self.check_history[-limit:]

    def clear_history(self):
        """Clear check history"""
        self.check_history = []

    def __str__(self):
        return f"🏥 HealthChecker: {len(self.check_history)} checks performed"
