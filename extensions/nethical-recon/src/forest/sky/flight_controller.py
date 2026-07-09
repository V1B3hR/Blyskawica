"""
🦅 Flight Controller - Coordinate All Birds

> "Air traffic control for the forest - managing all birds in harmony"
"""

from datetime import datetime
from typing import Any

from .base_bird import AlertLevel, BaseBird, BirdAlert, FlightMode
from .eagle import Eagle
from .falcon import Falcon
from .owl import Owl
from .sparrow import Sparrow


class FlightController:
    """
    Flight Controller - Coordinates all surveillance birds

    Manages:
    - Bird deployment and activation
    - Task assignment
    - Alert aggregation
    - Bird communication
    - Territory management
    """

    def __init__(self):
        """Initialize flight controller"""
        self.birds: dict[str, BaseBird] = {}
        self.eagle: Eagle | None = None
        self.falcons: list[Falcon] = []
        self.owls: list[Owl] = []
        self.sparrows: list[Sparrow] = []
        self.all_alerts: list[BirdAlert] = []
        self.is_active = False

    def deploy_eagle(self, name: str = "Eagle-Alpha") -> Eagle:
        """Deploy Eagle for strategic command"""
        eagle = Eagle(name)
        self.eagle = eagle
        self.birds[name] = eagle
        return eagle

    def deploy_falcon(self, name: str = None) -> Falcon:
        """Deploy Falcon for fast response"""
        if name is None:
            name = f"Falcon-{len(self.falcons) + 1}"
        falcon = Falcon(name)
        self.falcons.append(falcon)
        self.birds[name] = falcon
        return falcon

    def deploy_owl(self, name: str = None) -> Owl:
        """Deploy Owl for night watch"""
        if name is None:
            name = f"Owl-{len(self.owls) + 1}"
        owl = Owl(name)
        self.owls.append(owl)
        self.birds[name] = owl
        return owl

    def deploy_sparrow(self, name: str = None) -> Sparrow:
        """Deploy Sparrow for routine checks"""
        if name is None:
            name = f"Sparrow-{len(self.sparrows) + 1}"
        sparrow = Sparrow(name)
        self.sparrows.append(sparrow)
        self.birds[name] = sparrow
        return sparrow

    def deploy_standard_fleet(self):
        """
        Deploy standard bird fleet

        Standard fleet:
        - 1 Eagle (command)
        - 2 Falcons (response)
        - 1 Owl (night watch)
        - 2 Sparrows (routine)
        """
        self.deploy_eagle("Eagle-Alpha")
        self.deploy_falcon("Falcon-Hunter")
        self.deploy_falcon("Falcon-Scout")
        self.deploy_owl("Owl-Watcher")
        self.deploy_sparrow("Sparrow-North")
        self.deploy_sparrow("Sparrow-South")

    def activate_all(self):
        """Activate all deployed birds"""
        if self.eagle:
            self.eagle.take_flight(FlightMode.SOARING)

        for falcon in self.falcons:
            falcon.take_flight(FlightMode.HUNTING)

        for owl in self.owls:
            owl.take_flight(FlightMode.WATCHING)

        for sparrow in self.sparrows:
            sparrow.take_flight(FlightMode.PATROLLING)

        self.is_active = True

    def deactivate_all(self):
        """Land all birds"""
        for bird in self.birds.values():
            bird.land()
        self.is_active = False

    def scan_forest(self, forest_data: dict[str, Any]) -> dict[str, list[BirdAlert]]:
        """
        Coordinate full forest scan with all birds

        Args:
            forest_data: Complete forest state

        Returns:
            Dictionary of alerts by bird type
        """
        results = {"eagle": [], "falcon": [], "owl": [], "sparrow": [], "all": []}

        # Eagle: Strategic overview
        if self.eagle and self.eagle.is_active:
            eagle_alerts = self.eagle.scan(forest_data)
            results["eagle"] = eagle_alerts
            results["all"].extend(eagle_alerts)

        # Falcons: Fast response
        for falcon in self.falcons:
            if falcon.is_active:
                falcon_alerts = falcon.scan(forest_data)
                results["falcon"].extend(falcon_alerts)
                results["all"].extend(falcon_alerts)

        # Owls: Stealth monitoring
        for owl in self.owls:
            if owl.is_active:
                owl_alerts = owl.scan(forest_data)
                results["owl"].extend(owl_alerts)
                results["all"].extend(owl_alerts)

        # Sparrows: Routine checks
        for sparrow in self.sparrows:
            if sparrow.is_active:
                sparrow_alerts = sparrow.scan(forest_data)
                results["sparrow"].extend(sparrow_alerts)
                results["all"].extend(sparrow_alerts)

        # Store all alerts
        self.all_alerts.extend(results["all"])

        return results

    def get_critical_alerts(self) -> list[BirdAlert]:
        """Get all critical and breach level alerts"""
        return [alert for alert in self.all_alerts if alert.level in [AlertLevel.CRITICAL, AlertLevel.BREACH]]

    def get_recent_alerts(self, count: int = 20) -> list[BirdAlert]:
        """Get most recent alerts across all birds"""
        return sorted(self.all_alerts, key=lambda a: a.timestamp, reverse=True)[:count]

    def get_fleet_status(self) -> dict[str, Any]:
        """Get status of entire bird fleet"""
        return {
            "controller_active": self.is_active,
            "total_birds": len(self.birds),
            "active_birds": sum(1 for b in self.birds.values() if b.is_active),
            "fleet_composition": {
                "eagle": 1 if self.eagle else 0,
                "falcons": len(self.falcons),
                "owls": len(self.owls),
                "sparrows": len(self.sparrows),
            },
            "total_alerts": len(self.all_alerts),
            "critical_alerts": len(self.get_critical_alerts()),
            "birds": {name: bird.get_status() for name, bird in self.birds.items()},
        }

    def coordinate_response(self, threat: dict[str, Any]) -> dict[str, Any]:
        """
        Coordinate bird response to a threat

        Args:
            threat: Threat information

        Returns:
            Coordinated response plan
        """
        response = {
            "threat": threat,
            "coordinator": "FlightController",
            "timestamp": datetime.now().isoformat(),
            "birds_deployed": [],
            "actions": [],
        }

        threat_level = threat.get("severity", "medium")
        threat_type = threat.get("type", "unknown")

        # Eagle always gets notified for strategic decision
        if self.eagle:
            response["birds_deployed"].append("Eagle")
            decision = self.eagle.command_decision(f"{threat_type} threat detected - severity: {threat_level}")
            response["strategic_decision"] = decision

        # Deploy Falcon for immediate response
        if threat_level in ["high", "critical"] and self.falcons:
            falcon = self.falcons[0]  # Primary falcon
            response["birds_deployed"].append(falcon.name)
            hunt = falcon.hunt_target(threat)
            response["falcon_hunt"] = hunt
            response["actions"].extend(falcon.quick_response(threat))

        # Deploy Owl for stealth investigation
        if threat_type in ["hidden", "rootkit", "unknown"] and self.owls:
            owl = self.owls[0]  # Primary owl
            response["birds_deployed"].append(owl.name)
            observation = owl.deep_observation(threat, duration_minutes=15)
            response["owl_observation"] = observation

        # Sparrows continue routine monitoring
        if self.sparrows:
            response["routine_monitoring"] = "Sparrows maintaining baseline checks"

        return response

    def generate_sky_report(self, forest_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate comprehensive sky surveillance report

        Args:
            forest_data: Current forest state

        Returns:
            Complete sky report
        """
        report = {
            "report_type": "SKY_SURVEILLANCE",
            "timestamp": datetime.now().isoformat(),
            "controller": "FlightController",
            "fleet_status": self.get_fleet_status(),
        }

        # Eagle's executive report
        if self.eagle:
            report["executive_summary"] = self.eagle.generate_executive_report(forest_data)

        # Falcon activity
        if self.falcons:
            report["falcon_activity"] = {
                "active_hunts": sum(len(f.get_active_hunts()) for f in self.falcons),
                "hunters": [f.name for f in self.falcons if f.is_active],
            }

        # Owl wisdom
        if self.owls:
            report["owl_wisdom"] = [owl.share_wisdom() for owl in self.owls]

        # Sparrow baseline
        if self.sparrows:
            report["baseline_data"] = [sparrow.get_baseline() for sparrow in self.sparrows]

        # Recent alerts summary
        report["recent_alerts"] = {
            "total": len(self.all_alerts),
            "critical": len(self.get_critical_alerts()),
            "last_10": [
                {
                    "bird": alert.bird_type.value,
                    "level": alert.level.level,
                    "message": alert.message,
                    "time": alert.timestamp.strftime("%H:%M:%S"),
                }
                for alert in self.get_recent_alerts(10)
            ],
        }

        return report

    def clear_old_data(self, hours: int = 24):
        """Clear old alerts and data"""
        cutoff_timestamp = datetime.now().timestamp() - (hours * 3600)
        self.all_alerts = [alert for alert in self.all_alerts if alert.timestamp.timestamp() > cutoff_timestamp]

        # Clear bird-specific old data
        for bird in self.birds.values():
            bird.clear_old_alerts(hours)

        # Clear falcon targets
        for falcon in self.falcons:
            falcon.clear_targets(hours * 60)  # Convert to minutes

    def emergency_mode(self):
        """Activate emergency response mode"""
        # All birds to emergency mode
        if self.eagle:
            self.eagle.flight_mode = FlightMode.EMERGENCY

        for falcon in self.falcons:
            falcon.flight_mode = FlightMode.EMERGENCY

        for owl in self.owls:
            owl.flight_mode = FlightMode.EMERGENCY

        # Keep sparrows on patrol to maintain baseline

        return {"status": "EMERGENCY_MODE_ACTIVE", "all_birds_alerted": True, "response_time": "IMMEDIATE"}

    def __str__(self) -> str:
        """String representation"""
        active = sum(1 for b in self.birds.values() if b.is_active)
        return f"FlightController: {active}/{len(self.birds)} birds active"
