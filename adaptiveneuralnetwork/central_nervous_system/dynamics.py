"""
[Moduł: Rytm Adaptacji (Dynamics)]
Serce matematycznej choreografii Błyskawicy. Definiuje sposób, w jaki system ewoluuje 
pod wpływem bodźców, balansując między stabilnością a plastycznością. 

Zarządza lękiem kognitywnym, odwagą w działaniu i metabolicznym zużyciem energii, 
dbając o to, by każda zmiana w sieci była celowa i zharmonizowana z aktualną fazą życia.
"""  # noqa: W291
import logging
from typing import Any

import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler
from adaptiveneuralnetwork.central_nervous_system.workspace import GlobalWorkspace

logger = logging.getLogger(__name__)

class AdaptiveDynamics(nn.Module):
    """
    [Rdzeń: Silnik Dynamiki]
    Główny orkiestrator zmian stanów ukrytych. Odpowiada za integrację sygnałów 
    somatycznych, modulację społeczną (zaufanie) oraz mechanizm "Global Workspace", 
    który rozgłasza istotne informacje do całej sieci. 
    Implementuje również mechanizmy predykcyjne (Surprise Logic) i autonoetyczną 
    rozróżnialność między "Ja" a "Światem".
    """  # noqa: W291

    def __init__(self, hidden_dim: int, event_driven: bool = False, device: Any | None = None, **kwargs):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.event_driven = event_driven
        self.state_update = nn.Linear(hidden_dim, hidden_dim)
        self.input_projection = nn.Linear(hidden_dim, hidden_dim)
        self.energy_update = nn.Linear(hidden_dim, 1)
        self.topology_adapter = None # Will be set by core

        # Tier 5: Global Workspace (Spotlight)
        self.workspace: GlobalWorkspace | None = None
        self.num_threads = 4

        # Thread Selection Weights [1, num_threads, hidden_dim]
        # This allows the Dynamics engine to filter the broadcast threads
        self.thread_selector = nn.Parameter(torch.randn(1, self.num_threads, hidden_dim) * 0.1)

        # Predictive Internal Model (Phase 7.1)
        self.surprise_weight = nn.Parameter(torch.ones(hidden_dim))

        # Sensory Grounding (Tier 3)
        self.sensory_gate = nn.Linear(hidden_dim, hidden_dim)
        self.sensory_prediction = nn.Linear(hidden_dim, hidden_dim)

    def forward(self,
                node_state: NodeState,
                external_input: torch.Tensor,
                phase_scheduler: PhaseScheduler,
                micro_phase_scheduler: Any | None = None,
                params: dict[str, torch.Tensor] | None = None,
                deception_factor: float = 0.0) -> NodeState:
        """Main forward pass of the conscious neuromorphic substrate."""

        # If params are provided, use the functional execution path (for MAML)
        if params is not None:
            return self.functional_forward(node_state, external_input, phase_scheduler, params)
        prev_hidden = node_state.hidden_state.clone()  # noqa: F841

        # 1. Somatic/Microbiome signals
        somatic_stats = getattr(phase_scheduler, 'somatic_stats', None)
        somatic_signals = somatic_stats if somatic_stats is not None else None
        glial_manager = getattr(phase_scheduler, 'glial_manager', None)

        # Scepticism/Integrity Filter (Tier 2/3)
        # If deception_factor is high, we reduce the 'Gain' of external input
        scepticism_mask = 1.0 - (deception_factor * 0.8)

        # 2. Anxiety calculation
        node_state.anxiety = self._calculate_anxiety_levels(node_state, somatic_signals)

        # 3. Phase Transition
        phases = phase_scheduler.step(node_state.energy, node_state.activity, node_state.anxiety)
        active_mask = (phases != 1).float() # NOT Phase.SLEEP

        # 4. Social Integration
        social_context = getattr(phase_scheduler, 'social_context', None)
        if social_context is not None:
            # Modulate input based on global average social trust
            # Reduce to scalar for robust broadcasting across batches/nodes
            avg_trust = social_context.trust_matrix.mean().item()
            external_input = external_input * (0.5 + 0.5 * avg_trust)

        # 5. Personality Modulation (Bravery & Stability)
        # Bravery: reduces the inhibition from anxiety
        # [num_nodes]
        bravery = node_state.bravery.squeeze(0).squeeze(-1)
        resilience_factor = 1.0 + bravery * 0.5

        # Adjust active mask: Braver nodes stay active even under stress
        # Structural armor for multi-dimensional anxiety vs active_mask
        target_anxiety = node_state.anxiety.squeeze(-1) # Ensure [batch, nodes]
        target_mask = active_mask
        if target_mask.dim() == 1:
            target_mask = target_mask.unsqueeze(0) # [1, nodes]

        if target_anxiety.dim() > target_mask.dim():
            target_mask = target_mask.expand_as(target_anxiety)
        elif target_mask.dim() > target_anxiety.dim():
            target_anxiety = target_anxiety.expand_as(target_mask)

        brave_active_mask = torch.clamp(target_mask + (target_anxiety < (phase_scheduler.anxiety_threshold * resilience_factor)).float(), 0.0, 1.0)

        # 6. Core Neural Dynamics (Spotlight Augmented & Sensory Grounded)
        # Structural Armor: Ensure hidden_state matches expected features for update/gate
        hid_state = node_state.hidden_state
        if hid_state.size(-1) != self.hidden_dim:
            if hid_state.size(-1) < self.hidden_dim:
                padding = torch.zeros(*hid_state.shape[:-1], self.hidden_dim - hid_state.size(-1), device=hid_state.device)
                hid_state = torch.cat([hid_state, padding], dim=-1)
            else:
                hid_state = hid_state[..., :self.hidden_dim]

        hidden_delta = self.state_update(hid_state)

        # Sensory Fusion with Dimensional Armor (Phase 4.10 Audit Stabilization)
        # Ensure external_input is 3D [batch, 1, features]
        if external_input.dim() == 2:
            external_input = external_input.unsqueeze(1)

        # Armor: Ensure external_input's feature dimension matches our hidden_dim (128)
        if external_input.size(-1) != self.hidden_dim:
            if external_input.size(-1) < self.hidden_dim:
                padding = torch.zeros(*external_input.shape[:-1], self.hidden_dim - external_input.size(-1), device=external_input.device)
                external_input = torch.cat([external_input, padding], dim=-1)
            else:
                external_input = external_input[..., :self.hidden_dim]

        grounded_input = torch.sigmoid(self.sensory_gate(hid_state)) * external_input
        input_proj = self.input_projection(grounded_input)

        # Conscious Broadcast Signal (Tier 5 - Multi-Threaded)
        workspace_bias = 0.0
        if self.workspace is not None:
            # [1, num_nodes, num_threads, hidden_dim]
            broadcast_threads = self.workspace.broadcast(num_nodes=node_state.hidden_state.size(1))

            # Nodes 'tune' into threads using attention-like weighting
            # [1, num_nodes, num_threads, hidden_dim] * [1, 1, num_threads, hidden_dim]
            # Simple version: Sum threads weighted by selector
            # [1, num_nodes, hidden_dim]
            workspace_bias = (broadcast_threads * torch.sigmoid(self.thread_selector).unsqueeze(1)).sum(dim=2)

        # Update hidden state (active nodes only)
        myelination = getattr(glial_manager.glial, 'myelination_levels', 1.0) if glial_manager else 1.0

        # Unified Update: Local + (Suppressed) External + Global Spotlight (Threaded)
        # Scepticism modulates the external input projection ONLY
        update = brave_active_mask.unsqueeze(-1) * (hidden_delta + (0.1 * input_proj * scepticism_mask) + 0.05 * workspace_bias) * myelination.unsqueeze(0).unsqueeze(-1)
        node_state.hidden_state = torch.tanh(node_state.hidden_state + update).contiguous()

        # 7. Autonoetic Discrimination (Self vs World)
        # Correlation between internal update and external input
        # If correlation is high, it's 'World'; if low, it's 'Internal'
        with torch.no_grad():
            self_gen = torch.cosine_similarity(hidden_delta.detach(), input_proj.detach(), dim=-1).mean().item()
            # autonoetic_state = 1.0 (EXTERNAL) -> 0.0 (INTERNAL)
            self.autonoetic_score = torch.clamp(torch.tensor(self_gen), 0.0, 1.0)

        # 6. Energy and Activity
        self._update_energy(node_state, node_state.anxiety, active_mask)
        self._update_activity_levels(node_state, external_input)

        # 7. Glial Support
        if glial_manager is not None:
            current_phase_val = int(phases[0, 0].item()) # Approx
            glial_manager.manage(
                node_state,
                getattr(phase_scheduler, 'somatic_system', None),
                social_context,
                current_phase_val
            )

        # 8. NAS (Structural Plasticity)
        if self.topology_adapter is not None:
            self.topology_adapter.sp.step(node_state.activity, node_state.prediction_error)
            self.topology_adapter.adapt(self)

        return node_state

    def functional_forward(self,
                           node_state: NodeState,
                           external_input: torch.Tensor,
                           phase_scheduler: PhaseScheduler,
                           params: dict[str, torch.Tensor]) -> NodeState:
        """Functional version of the forward pass for meta-learning loops."""
        # Extract params
        w_state = params.get('state_update.weight', self.state_update.weight)
        b_state = params.get('state_update.bias', self.state_update.bias)
        w_input = params.get('input_projection.weight', self.input_projection.weight)
        b_input = params.get('input_projection.bias', self.input_projection.bias)

        # 1. Somatic signals
        somatic_stats = getattr(phase_scheduler, 'somatic_stats', None)

        # 2. Anxiety
        node_state.anxiety = self._calculate_anxiety_levels(node_state, somatic_stats)

        # 3. Phase Transition
        phases = phase_scheduler.step(node_state.energy, node_state.activity, node_state.anxiety)
        active_mask = (phases != 1).float()

        # 4. Neural Dynamics (Functional)
        hidden_delta = torch.nn.functional.linear(node_state.hidden_state, w_state, b_state)
        input_proj = torch.nn.functional.linear(external_input, w_input, b_input)

        update = active_mask * (hidden_delta + 0.1 * input_proj)
        node_state.hidden_state = torch.tanh(node_state.hidden_state + update).contiguous()

        # 5. Metabolic updates
        self._update_energy(node_state, node_state.anxiety, active_mask)
        self._update_activity_levels(node_state, external_input)

        return node_state

    def _calculate_anxiety_levels(self, node_state: NodeState, somatic_signals: dict | None) -> torch.Tensor:
        """Internal 'emotional' state based on surprise and energy. Refined by Stability trait."""
        surge = torch.abs(node_state.prediction_error)

        # Emotional Stability: Dampens the surge (0.0 = volatile, 1.0 = rock solid)
        stability = node_state.emotional_stability
        # Surge Smoothing with Batch-Invariant Dimensional Armor (Task 7.3)
        prev_surge = getattr(node_state, 'prev_surge', surge)

        # Ensure dimensional parity for recurrent state across variable batch sizes
        if prev_surge.size(0) != surge.size(0):
            # Batch size changed: Re-initialize or broadcast
            if prev_surge.dim() == surge.dim():
                 # Expansion/Mean fallback
                 prev_surge = surge.detach()
            else:
                 prev_surge = surge.detach()

        # Ensure stability matches surge for broadcasting
        # stability might be [batch, hidden_dim] or [batch, nodes, 1]
        active_stability = stability
        if active_stability.dim() > surge.dim():
             active_stability = active_stability.mean(dim=list(range(1, active_stability.dim())))

        if active_stability.size(0) != surge.size(0):
             active_stability = active_stability.mean().expand_as(surge)

        smoothed_surge = (1.0 - active_stability) * surge + active_stability * prev_surge
        node_state.prev_surge = smoothed_surge.detach()

        sensitivity = 1.2 if somatic_signals and somatic_signals['hormones']['cortisol'] > 0.5 else 1.0
        anxiety = smoothed_surge * sensitivity
        return anxiety

    def _update_energy(self, node_state: NodeState, anxiety: torch.Tensor, active_mask: torch.Tensor):
        """Metabolic model with basal recovery during sleep."""
        # Consumption
        # Ensure active_mask (which might be nodes-only) broadcasts to anxiety (batch, nodes)
        am = active_mask
        anx = anxiety.squeeze(-1) if anxiety.dim() == 3 else anxiety

        if anx.dim() > am.dim():
            am = am.expand_as(anx)
        elif am.dim() > anx.dim():
            anx = anx.expand_as(am)

        consumption = (am * 0.15) + (anx * 0.05)
        # Restoration (Nodes NOT active/sleeping get a small boost)
        restoration = (1.0 - am) * 0.08

        # Ensure result has original energy shape [batch, nodes, 1]
        energy_delta = (-consumption * 0.1) + (restoration * 0.1)
        if energy_delta.dim() == 2:
            energy_delta = energy_delta.unsqueeze(-1)

        node_state.energy = node_state.energy + energy_delta
        node_state.clamp_energy()

    def _update_activity_levels(self, node_state: NodeState, external_input: torch.Tensor):
        # Surrogate activity calculation
        node_state.activity = torch.sigmoid(node_state.hidden_state.abs().mean(dim=-1, keepdim=True))

        # Predictive Coding (Surprise Logic)
        # Node predicts its own future hidden state based on history
        # (Simplified: prediction is the previous state)
        prediction = node_state.hidden_state.detach()
        current = node_state.hidden_state

        # Surprise = Discordance between self-model and reality
        node_state.prediction_error = torch.abs(current - prediction).mean(dim=-1, keepdim=True)

        # Sensory Prediction (Action-Perception Loop) with Structural Armor
        # Predicting the external world state from internal dynamics
        curr = current
        if curr.size(-1) != self.sensory_prediction.in_features:
            if curr.size(-1) < self.sensory_prediction.in_features:
                padding = torch.zeros(*curr.shape[:-1], self.sensory_prediction.in_features - curr.size(-1), device=curr.device)
                curr = torch.cat([curr, padding], dim=-1)
            else:
                curr = curr[..., :self.sensory_prediction.in_features]
        node_state.sensory_prediction = self.sensory_prediction(curr)
