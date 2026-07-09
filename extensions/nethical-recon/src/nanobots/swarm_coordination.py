"""
Enhanced Swarm Coordination for Nanobots
Coordinates multiple nanobots for collaborative threat response
"""

import logging
from typing import Any
from datetime import datetime
from enum import Enum


class SwarmRole(Enum):
    """Roles within the swarm"""

    SCOUT = "scout"  # Reconnaissance
    HUNTER = "hunter"  # Threat hunting
    DEFENDER = "defender"  # Active defense
    ANALYST = "analyst"  # Analysis and learning


class SwarmCoordinator:
    """
    Coordinates swarm of nanobots
    """

    def __init__(self, swarm_id: str = "default"):
        """
        Initialize swarm coordinator

        Args:
            swarm_id: Unique identifier for this swarm
        """
        self.swarm_id = swarm_id
        self.logger = logging.getLogger(f"nethical.swarm.{swarm_id}")
        self._initialize_logger()

        # Swarm members
        self.members: dict[str, dict[str, Any]] = {}

        # Task queue
        self.pending_tasks: list[dict[str, Any]] = []
        self.active_tasks: dict[str, dict[str, Any]] = {}

        # Coordination state
        self.consensus_threshold = 0.7
        self.coordination_mode = "democratic"  # democratic, hierarchical, autonomous

        # Statistics
        self.total_coordinations = 0
        self.successful_coordinations = 0

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f"[%(asctime)s] [SwarmCoord:{self.swarm_id}] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_member(self, nanobot_id: str, role: SwarmRole, capabilities: list[str]):
        """
        Register a nanobot in the swarm

        Args:
            nanobot_id: Unique nanobot identifier
            role: Role in the swarm
            capabilities: List of nanobot capabilities
        """
        self.members[nanobot_id] = {
            "id": nanobot_id,
            "role": role,
            "capabilities": capabilities,
            "status": "idle",
            "tasks_completed": 0,
            "last_seen": datetime.now(),
        }
        self.logger.info(f"Registered nanobot {nanobot_id} as {role.value} " f"with {len(capabilities)} capabilities")

    def unregister_member(self, nanobot_id: str):
        """Unregister a nanobot"""
        if nanobot_id in self.members:
            del self.members[nanobot_id]
            self.logger.info(f"Unregistered nanobot {nanobot_id}")

    def assign_task(self, task: dict[str, Any]) -> str | None:
        """
        Assign a task to the best available nanobot

        Args:
            task: Task specification

        Returns:
            ID of assigned nanobot or None
        """
        required_capability = task.get("requires_capability")
        preferred_role = task.get("preferred_role")

        # Find suitable nanobot
        candidates = []
        for nanobot_id, member in self.members.items():
            if member["status"] != "idle":
                continue

            if required_capability and required_capability not in member["capabilities"]:
                continue

            if preferred_role and member["role"] != preferred_role:
                continue

            candidates.append((nanobot_id, member))

        if not candidates:
            self.pending_tasks.append(task)
            self.logger.warning("No available nanobot for task")
            return None

        # Select best candidate (e.g., least loaded)
        selected_id, selected_member = min(candidates, key=lambda x: x[1]["tasks_completed"])

        # Assign task
        task_id = f"task_{len(self.active_tasks)}_{datetime.now().timestamp()}"
        task["id"] = task_id
        task["assigned_to"] = selected_id
        task["assigned_at"] = datetime.now().isoformat()

        self.active_tasks[task_id] = task
        selected_member["status"] = "busy"

        self.logger.info(f"Assigned task {task_id} to nanobot {selected_id}")
        return selected_id

    def complete_task(self, task_id: str, result: dict[str, Any]):
        """
        Mark a task as completed

        Args:
            task_id: Task identifier
            result: Task result
        """
        if task_id not in self.active_tasks:
            self.logger.warning(f"Unknown task: {task_id}")
            return

        task = self.active_tasks[task_id]
        nanobot_id = task["assigned_to"]

        # Update nanobot status
        if nanobot_id in self.members:
            self.members[nanobot_id]["status"] = "idle"
            self.members[nanobot_id]["tasks_completed"] += 1

        # Remove from active tasks
        del self.active_tasks[task_id]

        # Update statistics
        self.total_coordinations += 1
        if result.get("success"):
            self.successful_coordinations += 1

        self.logger.info(
            f"Task {task_id} completed by {nanobot_id} " f"({'SUCCESS' if result.get('success') else 'FAILURE'})"
        )

        # Process pending tasks
        if self.pending_tasks:
            next_task = self.pending_tasks.pop(0)
            self.assign_task(next_task)

    def coordinate_response(self, threat: dict[str, Any]) -> dict[str, Any]:
        """
        Coordinate swarm response to a threat

        Args:
            threat: Threat information

        Returns:
            Coordination plan
        """
        plan = {"threat_id": threat.get("id"), "coordinated_at": datetime.now().isoformat(), "actions": []}

        # Assign scouts for reconnaissance
        scouts = [nid for nid, m in self.members.items() if m["role"] == SwarmRole.SCOUT and m["status"] == "idle"]
        if scouts:
            plan["actions"].append({"action": "reconnaissance", "assigned_to": scouts[:2]})  # Use 2 scouts

        # Assign hunters for active response
        hunters = [nid for nid, m in self.members.items() if m["role"] == SwarmRole.HUNTER and m["status"] == "idle"]
        if hunters:
            plan["actions"].append({"action": "threat_hunt", "assigned_to": hunters[:1]})

        # Assign defenders for protection
        defenders = [
            nid for nid, m in self.members.items() if m["role"] == SwarmRole.DEFENDER and m["status"] == "idle"
        ]
        if defenders:
            plan["actions"].append({"action": "defend", "assigned_to": defenders[:1]})

        self.logger.info(f"Coordinated response to threat with {len(plan['actions'])} actions")

        return plan

    def get_swarm_status(self) -> dict[str, Any]:
        """Get current swarm status"""
        status_counts = {}
        role_counts = {}

        for member in self.members.values():
            status = member["status"]
            role = member["role"].value

            status_counts[status] = status_counts.get(status, 0) + 1
            role_counts[role] = role_counts.get(role, 0) + 1

        return {
            "swarm_id": self.swarm_id,
            "total_members": len(self.members),
            "by_status": status_counts,
            "by_role": role_counts,
            "pending_tasks": len(self.pending_tasks),
            "active_tasks": len(self.active_tasks),
            "coordination_mode": self.coordination_mode,
            "success_rate": (
                self.successful_coordinations / self.total_coordinations if self.total_coordinations > 0 else 0.0
            ),
        }
