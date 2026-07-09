"""
Bird Coordination Protocol
Coordinates multiple birds for distributed reconnaissance
"""

import logging
from typing import Any
from datetime import datetime
from enum import Enum


class CoordinationMessage(Enum):
    """Message types for bird coordination"""

    DISCOVER = "discover"
    REPORT = "report"
    RECON_REQUEST = "recon_request"
    STATUS_UPDATE = "status_update"


class BirdCoordinationProtocol:
    """Coordinates birds for distributed operations"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.bird_coordination")
        self._initialize_logger()
        self.birds: dict[str, dict[str, Any]] = {}
        self.messages: list[dict[str, Any]] = []

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [BirdCoordination] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_bird(self, bird_id: str, capabilities: list[str]):
        """Register a bird in the coordination system"""
        self.birds[bird_id] = {
            "id": bird_id,
            "capabilities": capabilities,
            "status": "idle",
            "last_seen": datetime.now(),
        }
        self.logger.info(f"Registered bird: {bird_id}")

    def send_message(self, from_bird: str, to_bird: str, message_type: CoordinationMessage, data: dict[str, Any]):
        """Send coordination message"""
        message = {
            "from": from_bird,
            "to": to_bird,
            "type": message_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(message)
        self.logger.debug(f"Message {message_type.value}: {from_bird} -> {to_bird}")

    def coordinate_recon(self, target: str) -> dict[str, Any]:
        """Coordinate reconnaissance of a target"""
        available_birds = [bid for bid, b in self.birds.items() if b["status"] == "idle"]

        if not available_birds:
            return {"success": False, "error": "No birds available"}

        # Assign birds to target
        assigned = available_birds[: min(3, len(available_birds))]
        for bird_id in assigned:
            self.birds[bird_id]["status"] = "busy"
            self.send_message("coordinator", bird_id, CoordinationMessage.RECON_REQUEST, {"target": target})

        return {"success": True, "assigned_birds": assigned, "target": target}
