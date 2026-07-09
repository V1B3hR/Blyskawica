"""
Nanobot Swarm Manager - orchestrates multiple nanobots.

The swarm manager coordinates nanobots across different modes:
- Defensive mode (antibody behavior)
- Scout mode (reconnaissance)
- Adaptive mode (learning)
- Forest guard mode (patrol)
"""

import threading
import time
from datetime import datetime
from typing import Any

from .base import ActionResult, BaseNanobot, NanobotMode


class NanobotSwarm:
    """
    Manages a swarm of nanobots for automated response.

    The swarm acts like an immune system, with nanobots as antibodies
    that respond to threats automatically.
    """

    def __init__(self, swarm_id: str = "default_swarm"):
        """
        Initialize nanobot swarm.

        Args:
            swarm_id: Unique identifier for this swarm
        """
        self.swarm_id = swarm_id
        self.nanobots: dict[str, BaseNanobot] = {}
        self.event_queue: list[dict[str, Any]] = []
        self.is_active = False
        self.processing_thread: threading.Thread | None = None
        self._lock = threading.Lock()

        # Statistics
        self.total_events_processed = 0
        self.total_actions_taken = 0
        self.swarm_start_time: datetime | None = None

    def register_nanobot(self, nanobot: BaseNanobot) -> bool:
        """
        Register a nanobot with the swarm.

        Args:
            nanobot: Nanobot to register

        Returns:
            True if registration successful
        """
        with self._lock:
            if nanobot.nanobot_id in self.nanobots:
                return False

            self.nanobots[nanobot.nanobot_id] = nanobot
            return True

    def unregister_nanobot(self, nanobot_id: str) -> bool:
        """
        Unregister a nanobot from the swarm.

        Args:
            nanobot_id: ID of nanobot to unregister

        Returns:
            True if unregistration successful
        """
        with self._lock:
            if nanobot_id not in self.nanobots:
                return False

            # Deactivate before removing
            self.nanobots[nanobot_id].deactivate()
            del self.nanobots[nanobot_id]
            return True

    def get_nanobot(self, nanobot_id: str) -> BaseNanobot | None:
        """Get nanobot by ID"""
        return self.nanobots.get(nanobot_id)

    def get_nanobots_by_mode(self, mode: NanobotMode) -> list[BaseNanobot]:
        """Get all nanobots operating in a specific mode"""
        return [nb for nb in self.nanobots.values() if nb.mode == mode]

    def activate_all(self):
        """Activate all nanobots in the swarm"""
        with self._lock:
            for nanobot in self.nanobots.values():
                nanobot.activate()

    def deactivate_all(self):
        """Deactivate all nanobots in the swarm"""
        with self._lock:
            for nanobot in self.nanobots.values():
                nanobot.deactivate()

    def activate_mode(self, mode: NanobotMode):
        """Activate all nanobots in a specific mode"""
        with self._lock:
            for nanobot in self.get_nanobots_by_mode(mode):
                nanobot.activate()

    def deactivate_mode(self, mode: NanobotMode):
        """Deactivate all nanobots in a specific mode"""
        with self._lock:
            for nanobot in self.get_nanobots_by_mode(mode):
                nanobot.deactivate()

    def submit_event(self, event: dict[str, Any]):
        """
        Submit an event to the swarm for processing.

        Args:
            event: Event data containing threat information
        """
        with self._lock:
            self.event_queue.append(event)

    def process_event(self, event: dict[str, Any]) -> list[ActionResult]:
        """
        Process an event through all capable nanobots.

        Args:
            event: Event data containing threat information

        Returns:
            List of action results from nanobots that handled the event
        """
        results = []

        with self._lock:
            for nanobot in self.nanobots.values():
                if nanobot.is_active and nanobot.can_handle(event):
                    result = nanobot.process_event(event)
                    if result:
                        results.append(result)

        self.total_events_processed += 1
        if results:
            self.total_actions_taken += len(results)

        return results

    def _process_queue(self):
        """Background thread to process event queue"""
        while self.is_active:
            events_to_process = []

            with self._lock:
                if self.event_queue:
                    events_to_process = self.event_queue.copy()
                    self.event_queue.clear()

            for event in events_to_process:
                self.process_event(event)

            # Sleep to avoid busy-waiting
            time.sleep(0.1)

    def start_swarm(self):
        """Start the swarm (background processing)"""
        if self.is_active:
            return

        self.is_active = True
        self.swarm_start_time = datetime.now()
        self.activate_all()

        # Start background processing thread
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()

    def stop_swarm(self):
        """Stop the swarm"""
        if not self.is_active:
            return

        self.is_active = False
        self.deactivate_all()

        # Wait for processing thread to finish
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
            self.processing_thread = None

    def get_swarm_status(self) -> dict[str, Any]:
        """Get overall swarm status"""
        with self._lock:
            active_count = sum(1 for nb in self.nanobots.values() if nb.is_active)
            mode_counts = {}

            for mode in NanobotMode:
                mode_bots = self.get_nanobots_by_mode(mode)
                mode_counts[mode.value] = {
                    "total": len(mode_bots),
                    "active": sum(1 for nb in mode_bots if nb.is_active),
                }

            uptime = None
            if self.swarm_start_time:
                uptime = (datetime.now() - self.swarm_start_time).total_seconds()

            return {
                "swarm_id": self.swarm_id,
                "is_active": self.is_active,
                "total_nanobots": len(self.nanobots),
                "active_nanobots": active_count,
                "mode_breakdown": mode_counts,
                "events_processed": self.total_events_processed,
                "actions_taken": self.total_actions_taken,
                "queue_size": len(self.event_queue),
                "uptime_seconds": uptime,
            }

    def get_statistics(self) -> dict[str, Any]:
        """Get detailed statistics for all nanobots"""
        stats = {"swarm_status": self.get_swarm_status(), "nanobots": {}}

        with self._lock:
            for nanobot_id, nanobot in self.nanobots.items():
                stats["nanobots"][nanobot_id] = nanobot.get_statistics()

        return stats

    def get_recent_actions(self, limit: int = 20) -> list[dict[str, Any]]:
        """
        Get recent actions from all nanobots.

        Args:
            limit: Maximum number of recent actions to return

        Returns:
            List of action results with nanobot IDs
        """
        all_actions = []

        with self._lock:
            for nanobot_id, nanobot in self.nanobots.items():
                for action in nanobot.action_history:
                    all_actions.append(
                        {"nanobot_id": nanobot_id, "nanobot_mode": nanobot.mode.value, "action": action.to_dict()}
                    )

        # Sort by timestamp (newest first)
        all_actions.sort(key=lambda x: x["action"]["timestamp"], reverse=True)

        return all_actions[:limit]

    def clear_all_history(self):
        """Clear action history for all nanobots"""
        with self._lock:
            for nanobot in self.nanobots.values():
                nanobot.clear_history()

        self.total_events_processed = 0
        self.total_actions_taken = 0

    def __repr__(self) -> str:
        return f"NanobotSwarm(id={self.swarm_id}, nanobots={len(self.nanobots)}, active={self.is_active})"
