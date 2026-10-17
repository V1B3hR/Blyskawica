"""
Adaptive Neural Network - AliveLoopNode Module.

Models a biologically inspired, emotionally and socially adaptive cognitive agent node.
Supports circadian rhythms, dual-rotor cognitive processing, energy and memory management,
attack resilience, proactive interventions, and social/emotional signaling.
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch

from adaptiveneuralnetwork.central_nervous_system.neurochemistry import (
    NeurochemicalState,
)
from adaptiveneuralnetwork.config import (
    AdaptiveNeuralNetworkConfig,
)
from adaptiveneuralnetwork.immune_system.epistemic_defense import (
    EpistemicQuarantineNode,
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
    source_id: int | None = None
    source_node: int | None = None
    privacy_level: str = "public"
    decay_rate: float = 0.01
    reinforcement_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.source_node is not None and self.source_id is None:
            self.source_id = self.source_node
        elif self.source_id is not None and self.source_node is None:
            self.source_node = self.source_id

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
    target_id: int | None = None
    signal_type: str = "general"
    content: Any = None
    urgency: float = 0.5
    timestamp: int = 0
    requires_response: bool = False
    emotional_valence: float = 0.0
    signature: str | None = None


class AliveLoopNode:
    """
    Core alive loop node managing biological dynamics, neurochemical balance,
    memory consolidation, circadian rhythms, and immune resilience.
    """

    sleep_stages = ["light", "REM", "deep"]

    def __init__(
        self,
        position: list[float] | tuple[float, ...] | np.ndarray = (0.0, 0.0),
        velocity: list[float] | tuple[float, ...] | np.ndarray = (0.0, 0.0),
        initial_energy: float = 10.0,
        field_strength: float = 1.0,
        node_id: int = 0,
        config: AdaptiveNeuralNetworkConfig | None = None,
        spatial_dims: int | None = None,
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
        self.neurochemistry = NeurochemicalState()

        # Dual Rotor / Quantum Engine
        self.dual_rotor_engine = None
        self.inner_state = None
        self.outer_state = None

        # Network and Communication
        self.communication_range = 15.0
        self.trust_network: dict[int, float] = {}
        self.influence_network: dict[int, float] = {}
        self.shared_experience_buffer: list[Any] = []
        self.collective_contribution = 0.0
        self.knowledge_diversity = 0.0
        self.suspicious_events: list[Any] = []
        self.energy_sharing_enabled = True
        self.energy_sharing_history: list[dict[str, Any]] = []
        self.epistemic_quarantine = EpistemicQuarantineNode()
        self.polymath_hub: Any = None

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
        self.emotion_histories: dict[str, deque] = {
            "joy": self.joy_history,
            "anxiety": self.anxiety_history,
            "calm": self.calm_history,
            "energy": self.energy_history,
        }
        self.phase_history: deque = deque(maxlen=24)

        self.memory: deque = deque(maxlen=1000)
        self.working_memory: deque = deque(maxlen=7)
        self.long_term_memory: dict[str, Any] = {}
        self.collaborative_memories: list[Any] = []
        self.communication_queue: deque = deque(maxlen=20)
        self.signal_history: deque = deque(maxlen=50)

        self.help_signals_sent = 0
        self.max_communications_per_step = 5
        self.communications_this_step = 0

    def _determine_phase_transition(self) -> None:
        """Evaluate internal state and neurochemistry to transition phases."""
        if hasattr(self, "neurochemistry") and self.neurochemistry.should_force_sleep():
            self.phase = "sleep"
            self.sleep_stage = "deep"
            return
        if self.anxiety > 15.0 or self.energy <= 2.0:
            self.phase = "sleep"
            self.sleep_stage = "deep" if self.anxiety > 10.0 else "light"
        elif self.energy > 20.0 and self.anxiety < 5.0:
            self.phase = "inspired"
            self.sleep_stage = "light"
        else:
            self.phase = "active"

    def step_phase(self, current_time: int | None = None) -> None:
        """Advance the circadian and cognitive phase cycle."""
        self._time = current_time if current_time is not None else (self._time + 1)

        # Transition Rules
        if hasattr(self, "neurochemistry") and self.neurochemistry.should_force_sleep():
            self.phase = "sleep"
            self.sleep_stage = "deep"
        elif self.anxiety > 15.0 or self.energy <= 2.0:
            self.phase = "sleep"
            self.sleep_stage = "deep" if self.anxiety > 10.0 else "light"
        elif current_time is not None and (current_time >= 22 or current_time < 6):
            self.phase = "sleep"
            self.sleep_stage = "REM"
        else:
            self._determine_phase_transition()

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

        # Temporal pattern prediction
        pattern_energies = [
            (m["content"]["energy"] if isinstance(m, dict) else m.content["energy"])
            for m in self.memory
            if (isinstance(m, dict) and m.get("memory_type") == "pattern" and isinstance(m.get("content"), dict) and "energy" in m["content"])
            or (isinstance(m, Memory) and m.memory_type == "pattern" and isinstance(m.content, dict) and "energy" in m.content)
        ]
        if len(pattern_energies) >= 2 and pattern_energies[-1] < pattern_energies[-2]:
            total_delta = max(total_delta, float(pattern_energies[-2] - pattern_energies[-1] + 1.0))

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
        experiences: list[dict[str, Any]],
        learning_rate: float | None = None,
    ) -> dict[str, Any]:
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
        external_activity: torch.Tensor | None = None,
        internal_stimuli: Any = 0.0,
        emotional_trigger: float = 0.0,
        **kwargs: Any,
    ) -> None:
        """Run cognitive cycle with the Dual Rotor engine if tensor is supplied."""
        if emotional_trigger:
            self.anxiety = min(20.0, self.anxiety + float(emotional_trigger))
        if external_activity is not None and isinstance(external_activity, torch.Tensor):
            hidden_dim = external_activity.shape[-1]
            device = external_activity.device
            dtype = external_activity.dtype
            if self.dual_rotor_engine is None or next(self.dual_rotor_engine.parameters()).device != device:
                from adaptiveneuralnetwork.cognitive_tools.quantum_dual_rotor import (
                    DualRotorEngine,
                )
                self.dual_rotor_engine = DualRotorEngine(hidden_dim).to(device=device)
                self.inner_state = torch.zeros(external_activity.shape[0], hidden_dim, device=device, dtype=dtype)
                self.outer_state = torch.zeros(external_activity.shape[0], hidden_dim, device=device, dtype=dtype)
            elif self.inner_state is None or self.inner_state.shape[0] != external_activity.shape[0] or self.inner_state.device != device:
                self.inner_state = torch.zeros(external_activity.shape[0], hidden_dim, device=device, dtype=dtype)
                self.outer_state = torch.zeros(external_activity.shape[0], hidden_dim, device=device, dtype=dtype)

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
            stim = float(internal_stimuli) if isinstance(internal_stimuli, (int, float)) else 0.0
            self.activity = float(max(0.0, min(1.0, self.activity + stim)))

    def check_anxiety_overwhelm(self) -> bool:
        """Determine whether anxiety levels exceed the intervention threshold."""
        return self.anxiety > self.anxiety_threshold

    def can_send_help_signal(self) -> bool:
        """Check if rate limits permit dispatching another help signal."""
        return self.help_signals_sent < self.max_help_signals_per_period

    def send_help_signal(self, nearby_nodes: list["AliveLoopNode"]) -> list["AliveLoopNode"]:
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

    def handle_attack_detection(self) -> str:
        """Evaluate accumulated suspicious events and trigger Wolf Teeth defense response."""
        from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine

        threat_level = min(1.0, len(self.suspicious_events) / 6.0)
        wolf = WolfTeethDefenseEngine()
        return wolf.process_adversarial_interaction(threat_level)

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

    def share_valuable_memory(self, nodes: list["AliveLoopNode"]) -> list[SocialSignal]:
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
        target_nodes: list["AliveLoopNode"],
        signal_type: str,
        content: Any,
        urgency: float = 0.5,
        requires_response: bool = False,
    ) -> list[SocialSignal]:
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
            self.signal_history.append(sig)
        return dispatched

    def _process_query_signal(self, signal: SocialSignal) -> SocialSignal:
        """Process incoming query signals via PolymathicHub."""
        from adaptiveneuralnetwork.cognitive_tools.polymathic_hub import PolymathicHub

        if self.polymath_hub is None:
            self.polymath_hub = PolymathicHub()
        cost, response = self.polymath_hub.process_polymathic_signal(
            str(signal.content), current_energy=self.energy
        )
        self.energy = max(0.0, self.energy - cost)
        return SocialSignal(
            source_id=self.node_id,
            target_id=signal.source_id,
            signal_type="memory",
            content=response,
            urgency=signal.urgency,
        )

    def receive_signal(self, signal: SocialSignal) -> SocialSignal | None:
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
        elif signal.signal_type == "query":
            return self._process_query_signal(signal)
        elif signal.signal_type == "memory":
            raw_content = signal.content.content if isinstance(signal.content, Memory) else signal.content
            pkg = {
                "source": getattr(signal, "source_id", ""),
                "content": raw_content,
                "urgency": getattr(signal, "urgency", 0.5),
            }
            cortisol = (
                getattr(self.neurochemistry, "cortisol", 0.0)
                if hasattr(self, "neurochemistry")
                else 0.0
            )
            if cortisol > 1.0:
                self.epistemic_quarantine._quarantine(
                    pkg, f"High cortisol ({cortisol:.2f}) elevated skepticism quarantine."
                )
            else:
                accepted, _reason = self.epistemic_quarantine.vet_knowledge(pkg)
                if accepted:
                    mem = (
                        signal.content
                        if isinstance(signal.content, Memory)
                        else Memory(
                            content=signal.content,
                            source_id=signal.source_id,
                            timestamp=self._time,
                        )
                    )
                    self.memory.append(mem)
        return None

    def process_social_interactions(self) -> None:
        """Process pending items in the communication queue."""
        while self.communication_queue and self.communications_this_step < self.max_communications_per_step:
            sig = self.communication_queue.popleft()
            self.receive_signal(sig)
            self.communications_this_step += 1


def run_social_simulation(nodes: list[AliveLoopNode], steps: int = 10) -> dict[str, Any]:
    """Helper to run a multi-node social simulation."""
    for step in range(steps):
        for node in nodes:
            node.step_phase(step % 24)
            node.move()
            node.process_social_interactions()
    return {"status": "completed", "steps": steps, "nodes_count": len(nodes)}
