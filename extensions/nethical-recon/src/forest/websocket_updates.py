"""
WebSocket Updates for Forest
Provides real-time updates about forest changes via WebSocket
"""

import logging
import json
from datetime import datetime
from typing import Any, Callable
from collections import deque
import asyncio


class ForestEvent:
    """Represents a forest event"""

    def __init__(self, event_type: str, data: dict[str, Any]):
        """
        Initialize forest event

        Args:
            event_type: Type of event (tree_added, threat_detected, etc.)
            data: Event data
        """
        self.event_type = event_type
        self.timestamp = datetime.now()
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary"""
        return {"event_type": self.event_type, "timestamp": self.timestamp.isoformat(), "data": self.data}

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())


class ForestWebSocketManager:
    """
    Manages WebSocket connections and broadcasts forest updates
    """

    def __init__(self, max_event_history: int = 1000):
        """
        Initialize WebSocket manager

        Args:
            max_event_history: Maximum number of events to keep in history
        """
        self.logger = logging.getLogger("nethical.forest_websocket")
        self._initialize_logger()

        # Event queue and history
        self.event_queue: asyncio.Queue | None = None
        self.event_history: deque = deque(maxlen=max_event_history)

        # Subscribers (callback functions)
        self.subscribers: list[Callable[[ForestEvent], None]] = []

        # Statistics
        self.total_events = 0
        self.total_broadcasts = 0
        self.events_by_type: dict[str, int] = {}

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [ForestWebSocket] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def subscribe(self, callback: Callable[[ForestEvent], None]):
        """
        Subscribe to forest events

        Args:
            callback: Function to call when event occurs
        """
        if callback not in self.subscribers:
            self.subscribers.append(callback)
            self.logger.info(f"New subscriber added (total: {len(self.subscribers)})")

    def unsubscribe(self, callback: Callable[[ForestEvent], None]):
        """
        Unsubscribe from forest events

        Args:
            callback: Function to remove
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            self.logger.info(f"Subscriber removed (total: {len(self.subscribers)})")

    def publish_event(self, event_type: str, data: dict[str, Any]):
        """
        Publish an event to all subscribers

        Args:
            event_type: Type of event
            data: Event data
        """
        event = ForestEvent(event_type, data)

        # Add to history
        self.event_history.append(event)

        # Update statistics
        self.total_events += 1
        self.events_by_type[event_type] = self.events_by_type.get(event_type, 0) + 1

        # Broadcast to subscribers
        self._broadcast(event)

        self.logger.debug(f"Published event: {event_type}")

    def _broadcast(self, event: ForestEvent):
        """Broadcast event to all subscribers"""
        for callback in self.subscribers:
            try:
                callback(event)
                self.total_broadcasts += 1
            except Exception as e:
                self.logger.error(f"Error broadcasting to subscriber: {e}")

    def publish_tree_added(self, tree_id: str, hostname: str, ip_address: str):
        """Publish tree added event"""
        self.publish_event("tree_added", {"tree_id": tree_id, "hostname": hostname, "ip_address": ip_address})

    def publish_tree_removed(self, tree_id: str):
        """Publish tree removed event"""
        self.publish_event("tree_removed", {"tree_id": tree_id})

    def publish_threat_detected(self, threat_data: dict[str, Any]):
        """Publish threat detected event"""
        self.publish_event("threat_detected", threat_data)

    def publish_health_changed(self, component_id: str, old_score: float, new_score: float):
        """Publish health score changed event"""
        self.publish_event(
            "health_changed",
            {
                "component_id": component_id,
                "old_score": old_score,
                "new_score": new_score,
                "change": new_score - old_score,
            },
        )

    def publish_scan_completed(self, scan_results: dict[str, Any]):
        """Publish scan completed event"""
        self.publish_event("scan_completed", scan_results)

    def publish_branch_added(self, tree_id: str, branch_id: str, service_name: str, port: int):
        """Publish branch added event"""
        self.publish_event(
            "branch_added", {"tree_id": tree_id, "branch_id": branch_id, "service_name": service_name, "port": port}
        )

    def get_event_history(self, event_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get event history

        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        events = list(self.event_history)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Return most recent first
        events.reverse()

        return [e.to_dict() for e in events[:limit]]

    def get_statistics(self) -> dict[str, Any]:
        """Get WebSocket statistics"""
        return {
            "total_events": self.total_events,
            "total_broadcasts": self.total_broadcasts,
            "active_subscribers": len(self.subscribers),
            "event_history_size": len(self.event_history),
            "events_by_type": self.events_by_type.copy(),
        }

    def clear_history(self):
        """Clear event history"""
        self.event_history.clear()
        self.logger.info("Cleared event history")


class ForestWebSocketBridge:
    """
    Bridge between Forest components and WebSocket manager
    Automatically publishes events when forest changes occur
    """

    def __init__(self, ws_manager: ForestWebSocketManager):
        """
        Initialize WebSocket bridge

        Args:
            ws_manager: WebSocket manager instance
        """
        self.ws_manager = ws_manager
        self.logger = logging.getLogger("nethical.forest_ws_bridge")
        self._initialize_logger()

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [ForestWSBridge] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def wrap_forest_manager(self, forest_manager):
        """
        Wrap forest manager to auto-publish events

        Args:
            forest_manager: ForestManager instance to wrap
        """
        # Store original methods
        original_add_tree = forest_manager.add_tree
        original_remove_tree = forest_manager.remove_tree
        original_detect_threat = forest_manager.detect_threat

        # Wrap add_tree
        def wrapped_add_tree(tree):
            result = original_add_tree(tree)
            self.ws_manager.publish_tree_added(tree.component_id, tree.hostname, tree.ip_address)
            return result

        # Wrap remove_tree
        def wrapped_remove_tree(tree_id):
            result = original_remove_tree(tree_id)
            self.ws_manager.publish_tree_removed(tree_id)
            return result

        # Wrap detect_threat
        def wrapped_detect_threat(threat, tree_id, branch_id=None, leaf_id=None):
            result = original_detect_threat(threat, tree_id, branch_id, leaf_id)
            self.ws_manager.publish_threat_detected(
                {
                    "threat_type": threat.threat_type,
                    "severity": threat.severity,
                    "tree_id": tree_id,
                    "branch_id": branch_id,
                    "leaf_id": leaf_id,
                    "description": threat.description,
                }
            )
            return result

        # Replace methods
        forest_manager.add_tree = wrapped_add_tree
        forest_manager.remove_tree = wrapped_remove_tree
        forest_manager.detect_threat = wrapped_detect_threat

        self.logger.info("Forest manager wrapped for WebSocket events")

    def create_websocket_handler(self):
        """
        Create a WebSocket handler function for web frameworks

        Returns:
            Async handler function
        """

        async def handler(websocket):
            """WebSocket connection handler"""

            # Add this connection as a subscriber
            async def send_event(event: ForestEvent):
                try:
                    await websocket.send(event.to_json())
                except Exception as e:
                    self.logger.error(f"Error sending to WebSocket: {e}")

            self.ws_manager.subscribe(send_event)

            try:
                # Send recent history
                history = self.ws_manager.get_event_history(limit=10)
                for event_dict in history:
                    await websocket.send(json.dumps(event_dict))

                # Keep connection alive
                async for message in websocket:
                    # Handle incoming messages if needed
                    pass
            finally:
                self.ws_manager.unsubscribe(send_event)

        return handler
