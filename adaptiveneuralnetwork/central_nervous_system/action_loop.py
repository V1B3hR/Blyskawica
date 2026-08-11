"""
Action-Perception Loop with Cognitive Leverage Dynamics.

Implements Tier 3 of the Conscious Roadmap: The "Lever of Intelligence".
Handles the dynamic mapping between external Force (Adversarial/Manipulative) 
and internal Leverage (Cognitive Depth/Reasoning Scale).
"""  # noqa: W291

import logging
from typing import Any

import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.global_workspace import GlobalWorkspaceBus
from adaptiveneuralnetwork.central_nervous_system.metacognitive_monitor import MetacognitiveMonitor
from adaptiveneuralnetwork.central_nervous_system.strategic_offensive import StrategicOffensive
from adaptiveneuralnetwork.peripheral_nervous_system.sensory_hub import SensoryHub

logger = logging.getLogger(__name__)

class ActionPerceptionLoop(nn.Module):
    """
    Orchestrates the continuous flow between Perception and Action.
    Implements the 'Physics of Intelligence' (Cognitive Leverage).
    """
    def __init__(self,
                 hidden_dim: int,
                 sensory_hub: SensoryHub,
                 workspace: GlobalWorkspaceBus,
                 monitor: MetacognitiveMonitor):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.sensory_hub = sensory_hub
        self.workspace = workspace
        self.monitor = monitor

        # Physics of Intelligence components
        self.offensive_layer = StrategicOffensive(hidden_dim)

        # Lever Length: Higher = deeper reasoning, lower = fast/reflexive
        self.lever_length = nn.Parameter(torch.tensor(1.0))
        self.base_threshold = workspace.salience_threshold

        # Leverage state
        self.last_force = 0.0
        self.arm_stiffness = 1.0 # Resistance to bias (Love Bombarding protection)

    def step(self,
             sensory_data: dict[str, torch.Tensor],
             entity_id: str = "unknown") -> dict[str, Any]:
        """
        A single tick of the Action-Perception Loop.
        """
        # 1. Perception (Sensory Grounding)
        # deception_risk is used as a proxy for 'Love Bombarding' or Manipulative Force
        stats = self.monitor.metacognitive_stats
        deception_risk = stats['deception_risk'][-1] if stats['deception_risk'] else 0.0

        grounding_latent = self.sensory_hub.ground(
            sensory_data,
            workspace_state=self.workspace.workspace_state,
            deception_risk=deception_risk
        )

        # 2. Evaluate Force (Physics Metaphor)
        # Force = Intensity of Input + Deception Risk + Metacognitive Dissonance
        force = torch.norm(grounding_latent).item() * (1.0 + deception_risk)
        self.last_force = force

        # 3. Adjust Cognitive Leverage (Ramię Inteligencji)
        # If Force is high (Adversarial/Complex), lengthen the lever (Deeper awareness)
        # If 'Love Bombarding' is detected (Deception risk), stiffen the arm (Bias decoupling)

        # Longer lever = lower workspace threshold (allows more complexity to be broadcasted)
        target_lever = 1.0 + (force * 0.5)
        self.lever_length.data = 0.8 * self.lever_length.data + 0.2 * target_lever

        # Adjust Workspace Sensitivity based on Lever Length
        # Longer lever -> more sensitive to complex patterns (selective attention opens)
        new_threshold = self.base_threshold / (self.lever_length.item() + 1e-6)

        # Handle Love Bombarding: High manipulation risk stiffens the attention gate
        if deception_risk > 0.6:
            # Increase threshold specifically for 'friendly' but manipulative signals
            new_threshold *= 1.5
            self.arm_stiffness = 2.0
            logger.info(f"🛡️ LEVER STIFFENED: Countering suspected Manipulation (Risk: {deception_risk:.2f})")
        else:
            self.arm_stiffness = 1.0

        self.workspace.salience_threshold = torch.clamp(torch.tensor(new_threshold), min=0.1, max=0.9).item()

        # 4. Global Broadcast (Conscious Access)
        conscious_latent = self.workspace.broadcast(grounding_latent)

        # 5. Strategic Offensive (Proactive Counter-Measures)
        anxiety = stats['coherence'][-1] if stats['coherence'] else 0.5 # proxy for stress
        offensive_strategy = self.offensive_layer.evaluate_counter_strategy(
            conscious_latent, force, self.arm_stiffness, 1.0 - anxiety
        )

        # 6. Action Selection (Placeholder for environment interaction)
        # Combine broadcasted consciousness with proactive counter-measures
        action_potentials = torch.tanh(conscious_latent + offensive_strategy['counter_latent'])

        return {
            'action': action_potentials,
            'lever_length': self.lever_length.item(),
            'force': force,
            'stiffness': self.arm_stiffness,
            'workspace_threshold': self.workspace.salience_threshold,
            'offensive_strategy': offensive_strategy
        }

    def get_physics_summary(self) -> dict[str, float]:
        """Returns the current state of the Intelligence Lever."""
        return {
            'lever_length': float(self.lever_length),
            'external_force': self.last_force,
            'mechanical_advantage': float(self.lever_length) * self.last_force,
            'stiffness': self.arm_stiffness
        }
