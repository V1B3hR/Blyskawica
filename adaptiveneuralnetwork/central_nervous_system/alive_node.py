"""
Adaptive Neural Network - AliveLoopNode Module.

Models a biologically inspired, emotionally and socially adaptive cognitive agent node.
Supports circadian rhythms, dual-rotor cognitive processing, energy and memory management,
attack resilience, proactive interventions, and social/emotional signaling.
"""

from collections import deque
from dataclasses import dataclass, field
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch

from adaptiveneuralnetwork.central_nervous_system.ai_ethics import audit_decision
from adaptiveneuralnetwork.central_nervous_system.time_manager import (
    get_time_manager,
    get_timestamp,
)
from adaptiveneuralnetwork.config import (
    AdaptiveNeuralNetworkConfig,
    get_global_config,
)

logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """Represents a discrete unit of memory in the AliveLoopNode."""

    content: Any
    importance: float = 0.5
    timestamp: int = 0
    memory_type: str = "general"
    emotional_valence: float = 0.0
    source_id: Optional[int] = None
    privacy_level: str = "public"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        return self.metadata.get(item)

    def __setitem__(self, key: str, value: Any) -> None:
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.metadata[key] = value

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        return self.metadata.get(item, default)


@dataclass
class SocialSignal:
    """Represents a communication or social/emotional signal exchanged between nodes."""

    source_id: int
    target_id: Optional[int] = None
    signal_type: str = "general"
    content: Any = None
    urgency: float = 0.5
    timestamp: int = 0
    requires_response: bool = False
    emotional_valence: float = 0.0
    signature: Optional[str] = None


class AliveLoopNode:
    """
    Core alive loop node managing biological dynamics, neurochemical balance,
    memory consolidation, circadian rhythms, and immune resilience.
    """

    sleep_stages = ["light", "REM", "deep"]

    def __init__(
        self,
        position: Union[List[float], Tuple[float, ...], np.ndarray] = (0.0, 0.0),
        velocity: Union[List[float], Tuple[float, ...], np.ndarray] = (0.0, 0.0),
        initial_energy: float = 10.0,
        field_strength: float = 1.0,
        node_id: int = 0,
        config: Optional[AdaptiveNeuralNetworkConfig] = None,
        spatial_dims: Optional[int] = None,
    ):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.energy = float(max(0.0, initial_energy))
        self.energy_capacity = float(max(100.0, initial_energy))
        self.field_strength = float(field_strength)
        self.node_id = int(node_id)
        self.spatial_dims = spatial_dims or len(self.position)
        self.config = config if config is not None else AdaptiveNeuralNetworkConfig()

        # Phase and Circadian Dynamics
        self.phase = "active"
        self.sleep_stage = "light"
        self.circadian_cycle = 0
        self._time = 0

        # Emotional & Cognitive States
        self.anxiety = 0.0
        self.joy = 0.0
        self.calm = 1.0
        self.activity = 0.0
        self.confusion_level = 0.0
        self.predicted_energy = float(self.energy)
        self.emotional_state = {"valence": 0.0, "arousal": 0.5}
        self.communication_style = {
            "directness": 0.7,
            "formality": 0.3,
            "expressiveness": 0.6,
        }

        # Dual Rotor / Quantum Engine
        self.dual_rotor_engine = None
        self.inner_state = None
        self.outer_state = None

        # Network and Communication
        self.communication_range = 15.0
        self.trust_network: Dict[int, float] = {}
        self.influence_network: Dict[int, float] = {}
        self.shared_experience_buffer: List[Any] = []
        self.collective_contribution = 0.0
        self.knowledge_diversity = 0.0
        self.suspicious_events: List[Any] = []
        self.energy_sharing_enabled = True
        self.energy_sharing_history: List[Dict[str, Any]] = []

        # Proactive Intervention & Attack Resilience Parameters from Config
        proactive = getattr(self.config, "proactive_interventions", None)
        self.anxiety_threshold = float(getattr(proactive, "anxiety_threshold", 8.0))
        self.max_help_signals_per_period = int(getattr(proactive, "max_help_signals_per_period", 3))
        self.help_signal_cooldown = int(getattr(proactive, "help_signal_cooldown", 10))
        self.anxiety_unload_capacity = float(getattr(proactive, "anxiety_unload_capacity", 2.0))

        attack = getattr(self.config, "attack_resilience", None)
        self.energy_drain_resistance = float(getattr(attack, "energy_drain_resistance", 0.7))
        self.signal_redundancy_level = int(getattr(attack, "signal_redundancy_level", 2))
        self.jamming_detection_sensitivity = float(getattr(attack, "jamming_detection_sensitivity", 0.3))
        self.attack_detection_threshold = int(getattr(attack, "attack_detection_threshold", 3))

        # Rolling History & Memory Buffers
        rolling = getattr(self.config, "rolling_history", None)
        max_history_len = int(getattr(rolling, "max_len", 20))


        self.anxiety_history: deque = deque(maxlen=max_history_len)
        self.joy_history: deque = deque(maxlen=max_history_len)
        self.energy_history: deque = deque(maxlen=max_history_len)
        self.calm_history: deque = deque(maxlen=max_history_len)
        self.emotion_histories: Dict[str, deque] = {
            "joy": self.joy_history,
            "anxiety": self.anxiety_history,
            "calm": self.calm_history,
            "energy": self.energy_history,
        }
        self.phase_history: deque = deque(maxlen=24)

        self.memory: deque = deque(maxlen=1000)
        self.working_memory: deque = deque(maxlen=7)
        self.long_term_memory: Dict[str, Any] = {}
        self.collaborative_memories: List[Any] = []
        self.communication_queue: deque = deque(maxlen=20)
        self.signal_history: deque = deque(maxlen=50)

        self.help_signals_sent = 0
        self.max_communications_per_step = 5
        self.communications_this_step = 0

    def step_phase(self, current_time: Optional[int] = None) -> None:
        """Advance the circadian and cognitive phase cycle."""
        tm = get_time_manager()
        self._time = current_time if current_time is not None else (self._time + 1)

        # Transition Rules
        if self.anxiety > 15.0 or self.energy < 2.0:
            self.phase = "sleep"
            self.sleep_stage = "deep" if self.anxiety > 10.0 else "light"
        elif self.energy > 20.0 and self.anxiety < 5.0:
            self.phase = "inspired"
            self.sleep_stage = "light"
        elif current_time is not None and (current_time >= 22 or current_time < 6):
            self.phase = "sleep"
            self.sleep_stage = "REM"
        else:
            self.phase = "active"

        self.phase_history.append(self.phase)
        self.anxiety_history.append(self.anxiety)
        self.communications_this_step = 0

    def move(self) -> None:
        """Update node position based on velocity and update energy."""
        self.position = self.position + self.velocity
        cost = 0.05 * (float(np.linalg.norm(self.velocity)) + 1.0)
        self.energy = max(0.0, self.energy - cost)

    def interact_with_capacitor(self, capacitor: Any, threshold: float = 2.0) -> None:
        """Exchange energy with an external capacitor in space."""
        if hasattr(capacitor, "capacity") and hasattr(capacitor, "energy"):
            transfer = min(self.energy * 0.1, max(0.0, capacitor.capacity - capacitor.energy))
            if transfer > 0:
                capacitor.energy += transfer
                self.energy -= transfer

    def predict_energy(self) -> float:
        """Estimate future energy based on recent experiences and signals."""
        total_delta = 0.0
        for item in self.memory:
            if isinstance(item, dict):
                mtype = item.get("memory_type")
                content = item.get("content", {})
                if mtype == "reward" and isinstance(content, dict):
                    total_delta += content.get("transfer", 0.0)
                elif mtype == "signal" and isinstance(content, dict):
                    total_delta += content.get("energy", 0.0)
            elif isinstance(item, Memory):
                if item.memory_type == "reward" and isinstance(item.content, dict):
                    total_delta += item.content.get("transfer", 0.0)
                elif item.memory_type == "signal" and isinstance(item.content, dict):
                    total_delta += item.content.get("energy", 0.0)
        self.predicted_energy = self.energy + total_delta
        return self.predicted_energy

    def clear_anxiety(self) -> None:
        """Soothe anxiety, especially effective during sleep phases."""
        if self.phase == "sleep":
            damping = 0.4 if self.sleep_stage == "deep" else 0.7
            self.anxiety = max(0.0, self.anxiety * damping)
        else:
            self.anxiety = max(0.0, self.anxiety * 0.9)

    def train(
        self,
        experiences: List[Dict[str, Any]],
        learning_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Learn and consolidate memories from batches of experiences."""
        lr = learning_rate or 0.01
        total_reward = 0.0
        memories_created = 0

        for exp in experiences:
            rew = exp.get("reward", 0.0)
            total_reward += rew
            mem = Memory(
                content=exp,
                importance=min(1.0, abs(rew) / 10.0 + 0.1),
                timestamp=self._time,
                memory_type="experience",
                emotional_valence=np.clip(rew / 10.0, -1.0, 1.0),
            )
            self.memory.append(mem)
            memories_created += 1

        avg_reward = total_reward / len(experiences) if experiences else 0.0
        if total_reward > 0:
            self.joy += total_reward * 0.1
            self.calm = min(10.0, self.calm + 0.2)
        else:
            self.anxiety = min(20.0, self.anxiety + abs(total_reward) * 0.05)

        self.predict_energy()
        return {
            "total_reward": float(total_reward),
            "avg_reward": float(avg_reward),
            "memories_created": memories_created,
            "learning_rate": lr,
            "current_energy": float(self.energy),
            "predicted_energy": float(self.predicted_energy),
        }


    def update(
        self,
        external_activity: Optional[torch.Tensor] = None,
        internal_stimuli: float = 0.0,
    ) -> None:
        """Run cognitive cycle with the Dual Rotor engine if tensor is supplied."""
        if external_activity is not None and isinstance(external_activity, torch.Tensor):
            hidden_dim = external_activity.shape[-1]
            if self.dual_rotor_engine is None:
                from adaptiveneuralnetwork.cognitive_tools.quantum_dual_rotor import (
                    DualRotorEngine,
                )
                self.dual_rotor_engine = DualRotorEngine(hidden_dim)
                self.inner_state = torch.zeros(external_activity.shape[0], hidden_dim)
                self.outer_state = torch.zeros(external_activity.shape[0], hidden_dim)

            res = self.dual_rotor_engine(
                external_activity, self.inner_state, self.outer_state
            )
            if len(res) == 3:
                out_inner, out_outer, _freq = res
            else:
                out_inner, out_outer = res[0], res[1]
            self.inner_state = out_inner
            self.outer_state = out_outer
            self.activity = float(torch.mean(torch.abs(out_inner)).item())

        else:
            self.activity = float(max(0.0, min(1.0, self.activity + internal_stimuli)))

    def check_anxiety_overwhelm(self) -> bool:
        """Determine whether anxiety levels exceed the intervention threshold."""
        return self.anxiety > self.anxiety_threshold

    def can_send_help_signal(self) -> bool:
        """Check if rate limits permit dispatching another help signal."""
        return self.help_signals_sent < self.max_help_signals_per_period

    def send_help_signal(self, nearby_nodes: List["AliveLoopNode"]) -> List["AliveLoopNode"]:
        """Send urgent help requests to peers within range."""
        if not self.can_send_help_signal():
            return []
        helpers = []
        for node in nearby_nodes:
            if node.node_id != self.node_id:
                dist = np.linalg.norm(self.position - node.position)
                if dist <= self.communication_range:
                    helpers.append(node)
                    node.receive_signal(
                        SocialSignal(
                            source_id=self.node_id,
                            target_id=node.node_id,
                            signal_type="anxiety_help",
                            content={"anxiety": self.anxiety},
                            urgency=0.9,
                            requires_response=True,
                        )
                    )
        self.help_signals_sent += 1
        return helpers

    def record_suspicious_event(self, event: Any) -> None:
        """Log suspicious or adversarial activity."""
        self.suspicious_events.append({"event": event, "timestamp": self._time})
        if len(self.suspicious_events) > 3:
            self.signal_redundancy_level = min(5, self.signal_redundancy_level + 1)

    def apply_calm_effect(self) -> None:
        """Reinforce serenity and dampen acute anxiety."""
        self.calm = min(10.0, self.calm + 1.0)
        self.anxiety = max(0.0, self.anxiety - 1.5)

    def _apply_emotional_contagion(self, emotional_valence: float, source_id: int) -> None:
        """Absorb peer emotional contagion modulated by trust."""
        trust = self.trust_network.get(source_id, 0.5)
        current = self.emotional_state.get("valence", 0.0)
        updated = current + (emotional_valence - current) * 0.2 * trust
        self.emotional_state["valence"] = float(np.clip(updated, -1.0, 1.0))

    def share_valuable_memory(self, nodes: List["AliveLoopNode"]) -> List[SocialSignal]:
        """Broadcast top memory to trustworthy neighbors."""
        if not self.memory:
            return []
        best_mem = max(
            self.memory,
            key=lambda m: m.get("importance", 0.5) if isinstance(m, (dict, Memory)) else 0.5,
        )
        signals = []
        for peer in nodes:
            if peer.node_id != self.node_id:
                dist = np.linalg.norm(self.position - peer.position)
                if dist <= self.communication_range:
                    sig = SocialSignal(
                        source_id=self.node_id,
                        target_id=peer.node_id,
                        signal_type="memory_share",
                        content=best_mem,
                        urgency=0.6,
                    )
                    peer.receive_signal(sig)
                    signals.append(sig)
        return signals

    def send_signal(
        self,
        target_nodes: List["AliveLoopNode"],
        signal_type: str,
        content: Any,
        urgency: float = 0.5,
        requires_response: bool = False,
    ) -> List[SocialSignal]:
        """Dispatch a general signal to specified peers."""
        dispatched = []
        for target in target_nodes:
            sig = SocialSignal(
                source_id=self.node_id,
                target_id=target.node_id,
                signal_type=signal_type,
                content=content,
                urgency=urgency,
                requires_response=requires_response,
            )
            target.receive_signal(sig)
            dispatched.append(sig)
        return dispatched

    def receive_signal(self, signal: SocialSignal) -> Optional[SocialSignal]:
        """Process received incoming social signal."""
        self.signal_history.append(signal)
        if signal.signal_type == "anxiety_help":
            if self.calm > 2.0:
                self.apply_calm_effect()
                return SocialSignal(
                    source_id=self.node_id,
                    target_id=signal.source_id,
                    signal_type="anxiety_help_response",
                    content={"comfort": True, "calm_share": 0.5},
                    urgency=signal.urgency,
                )
        elif signal.signal_type == "memory_share":
            self.collaborative_memories.append(signal.content)
            self._apply_emotional_contagion(signal.emotional_valence, signal.source_id)
        return None

    def process_social_interactions(self) -> None:
        """Process pending items in the communication queue."""
        while self.communication_queue and self.communications_this_step < self.max_communications_per_step:
            sig = self.communication_queue.popleft()
            self.receive_signal(sig)
            self.communications_this_step += 1


def run_social_simulation(nodes: List[AliveLoopNode], steps: int = 10) -> Dict[str, Any]:
    """Helper to run a multi-node social simulation."""
    for step in range(steps):
        for node in nodes:
            node.step_phase(step % 24)
            node.move()
            node.process_social_interactions()
    return {"status": "completed", "steps": steps, "nodes_count": len(nodes)}
