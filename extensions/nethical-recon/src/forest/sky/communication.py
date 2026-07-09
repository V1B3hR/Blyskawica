"""
Bird Communication Protocol
Handles inter-bird communication
"""

import logging
from typing import Any
from datetime import datetime


class BirdCommunicationProtocol:
    """Handles bird-to-bird communication"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.bird_comm")
        self._initialize_logger()
        self.messages: list[dict[str, Any]] = []

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [BirdComm] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def broadcast(self, from_bird: str, message: str):
        """Broadcast message to all birds"""
        msg = {"from": from_bird, "type": "broadcast", "message": message, "timestamp": datetime.now().isoformat()}
        self.messages.append(msg)
        self.logger.info(f"Broadcast from {from_bird}: {message}")

    def direct_message(self, from_bird: str, to_bird: str, message: str):
        """Send direct message"""
        msg = {
            "from": from_bird,
            "to": to_bird,
            "type": "direct",
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(msg)
