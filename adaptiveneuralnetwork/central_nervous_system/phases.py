"""
[Moduł: Cykle Życia (Phases)]
Zarządca chronobiologii Błyskawicy. Definiuje stany świadomości, w jakich może 
znajdować się system, orkiestrując przejścia między aktywnością a spoczynkiem. 

Implementuje zaawansowaną architekturę snu (LIGHT, DEEP, REM), umożliwiając 
konsolidację wspomnień i regenerację metaboliczną. To tutaj czas staje się 
zasobem kognitywnym, a odpoczynek fundamentem inteligencji.
"""

from collections import deque
from enum import Enum

import numpy as np
import torch


class Phase(Enum):
    """
    [Komponent: Stany Świadomości]
    Definiuje główne tryby operacyjne Błyskawicy: 
    - ACTIVE: Pełne skupienie na zadaniu.
    - SLEEP: Regeneracja i porządkowanie pamięci.
    - INTERACTIVE: Otwarcie na sygnały społeczne i empatię.
    - INSPIRED: Stan podwyższonej kreatywności i niskich progów lęku.
    """

    ACTIVE = 0
    SLEEP = 1
    INTERACTIVE = 2
    INSPIRED = 3


class SubPhase(Enum):
    """
    [Komponent: Architektura Snu]
    Głębokie stany fazy SLEEP:
    - LIGHT: Wstępne wyciszenie i czyszczenie buforów.
    - DEEP: Maksymalna regeneracja i "czyszczenie toksyn" (skalowanie synaptyczne).
    - REM: Konsolidacja kognitywna poprzez odtwarzanie doświadczeń (experience replay).
    """
    NONE = 0
    LIGHT = 1
    REM = 2
    DEEP = 3


class PhaseScheduler:
    """
    [Rdzeń: Chronobiologiczny Planista]
    Orkiestrator przejść fazowych. Monitoruje poziom energii, lęku oraz rytm 
    dobowy (circadian period), by wyznaczyć optymalny stan dla każdego węzła. 
    Integruje dane z układu somatycznego (Gut-Brain Axis) i kontekstu społecznego.
    """


    def __init__(
        self,
        num_nodes: int,
        device: str = "cpu",
        circadian_period: int = 100,
        phase_weights: dict[Phase, float] | None = None,
        anxiety_threshold: float = 5.0,
        restorative_strength: float = 0.1,
        stochastic_policy: bool = True,
        policy_temperature: float = 1.0,
        exploration_rate: float = 0.1,
    ):
        self.num_nodes = num_nodes
        self.device = torch.device(device)
        self.circadian_period = circadian_period
        self.current_step = 0
        self.anxiety_threshold = anxiety_threshold
        self.restorative_strength = restorative_strength

        # Enhanced stochastic policy parameters
        self.stochastic_policy = stochastic_policy
        self.policy_temperature = policy_temperature
        self.exploration_rate = exploration_rate
        self.policy_entropy_history = []
        self.phase_diversity_score = 0.0

        # Somatic System (Gut-Brain Axis) - Phase 7.4
        from adaptiveneuralnetwork.central_nervous_system.somatic import SomaticSystem
        self.somatic_system = SomaticSystem()
        self.somatic_stats = {}

        # Social System (Trust & ToM) - Phase 7.4
        from adaptiveneuralnetwork.central_nervous_system.social import InternalSocialDynamics
        self.social_context = InternalSocialDynamics(num_nodes)

        # Glial System (Maintenance) - Phase 7.5
        from adaptiveneuralnetwork.central_nervous_system.glial import GlialManager
        self.glial_manager = GlialManager(num_nodes)

        # Default phase weights (probability of being in each phase)
        self.phase_weights = phase_weights or {
            Phase.ACTIVE: 0.6,
            Phase.INTERACTIVE: 0.25,
            Phase.SLEEP: 0.1,
            Phase.INSPIRED: 0.05,
        }

        # Current phase for each node [num_nodes]
        self.node_phases = torch.zeros(num_nodes, dtype=torch.long, device=self.device)

        # Anxiety tracking for enhanced phase control
        self.node_anxiety = torch.zeros(num_nodes, device=self.device)
        self.anxiety_history = torch.zeros(num_nodes, 10, device=self.device)  # Track last 10 steps

        # Restorative needs and sleep quality
        self.restorative_needs = torch.zeros(num_nodes, device=self.device)
        self.sleep_quality = torch.ones(num_nodes, device=self.device)
        
        # Sub-phase tracking (for Staged Sleep)
        self.node_sub_phases = torch.full((num_nodes,), SubPhase.NONE.value, dtype=torch.long, device=self.device)
        self.sleep_timer = torch.zeros(num_nodes, device=self.device)

        # ── REM Experience Replay Buffer ──────────────────────────────────────
        # Stores (loss_value, experience_tensor) tuples pushed by the training
        # loop.  During REM the K highest-loss experiences are surfaced so the
        # caller can perform priority replay (like hippocampal replay in humans).
        self.replay_buffer: deque = deque(maxlen=512)
        self.rem_replay_k: int = 16          # How many samples to surface per REM cycle
        self.rem_consolidation_pending: bool = False  # Set True when REM fires
        self.rem_experiences: list = []      # Populated during REM; read by trainer

        # ── Polyphasic micro-nap tracking ─────────────────────────────────────
        self.nap_interval: int = 50          # Steps between automatic micro-naps
        self.nap_duration: int = 5           # Steps a micro-nap lasts
        self.nap_timer: int = 0             # Counts steps since last nap
        self.nap_active: bool = False
        self.nap_steps_remaining: int = 0

        # Phase transition probabilities based on energy/activity
        self.transition_matrix = self._build_transition_matrix()

    def _build_transition_matrix(self) -> torch.Tensor:
        """Build phase transition probability matrix."""
        # Simplified transition logic - can be made more sophisticated
        num_phases = len(Phase)
        matrix = torch.zeros(num_phases, num_phases, device=self.device)

        # Stay in same phase (diagonal)
        for phase in Phase:
            matrix[phase.value, phase.value] = 0.8

        # Specific transitions
        matrix[Phase.ACTIVE.value, Phase.INTERACTIVE.value] = 0.15
        matrix[Phase.ACTIVE.value, Phase.SLEEP.value] = 0.04
        matrix[Phase.ACTIVE.value, Phase.INSPIRED.value] = 0.01

        matrix[Phase.SLEEP.value, Phase.ACTIVE.value] = 0.15
        matrix[Phase.SLEEP.value, Phase.INTERACTIVE.value] = 0.04
        matrix[Phase.SLEEP.value, Phase.INSPIRED.value] = 0.01

        matrix[Phase.INTERACTIVE.value, Phase.ACTIVE.value] = 0.15
        matrix[Phase.INTERACTIVE.value, Phase.SLEEP.value] = 0.04
        matrix[Phase.INTERACTIVE.value, Phase.INSPIRED.value] = 0.01

        matrix[Phase.INSPIRED.value, Phase.ACTIVE.value] = 0.1
        matrix[Phase.INSPIRED.value, Phase.INTERACTIVE.value] = 0.05
        matrix[Phase.INSPIRED.value, Phase.SLEEP.value] = 0.05

        return matrix

    def step(self, energy_levels: torch.Tensor, activity_levels: torch.Tensor, anxiety_levels: torch.Tensor | None = None) -> torch.Tensor:
        """
        Update phases for all nodes based on current state.

        Args:
            energy_levels: Current energy for each node [batch_size, num_nodes, 1]
            activity_levels: Current activity for each node [batch_size, num_nodes, 1]
            anxiety_levels: Optional anxiety levels for each node [batch_size, num_nodes, 1]

        Returns:
            Phase IDs for each node [batch_size, num_nodes]
        """
        self.current_step += 1
        batch_size = energy_levels.shape[0]
        device = energy_levels.device
        
        # Ensure all state tensors are on the active device
        self.node_phases = self.node_phases.to(device)
        self.node_anxiety = self.node_anxiety.to(device)
        self.anxiety_history = self.anxiety_history.to(device)
        self.restorative_needs = self.restorative_needs.to(device)
        self.sleep_quality = self.sleep_quality.to(device)
        self.node_sub_phases = self.node_sub_phases.to(device)
        self.sleep_timer = self.sleep_timer.to(device)
        
        if self.social_context is not None:
            self.social_context = self.social_context.to(device)

        # Detach persistent state from previous batches
        self.node_anxiety = self.node_anxiety.detach()
        self.anxiety_history = self.anxiety_history.detach()
        self.restorative_needs = self.restorative_needs.detach()
        self.sleep_quality = self.sleep_quality.detach()
        self.sleep_timer = self.sleep_timer.detach()

        # Update anxiety tracking if provided
        if anxiety_levels is not None:
            # Use last batch for anxiety tracking
            last_batch_anxiety = anxiety_levels[-1].squeeze(-1)  # [num_nodes]
            self._update_anxiety_tracking(last_batch_anxiety)

        # Circadian rhythm influence
        circadian_phase = (self.current_step % self.circadian_period) / self.circadian_period
        circadian_factor = np.sin(2 * np.pi * circadian_phase)

        # Update somatic states (Gut-Brain interactions)
        # We use mean energy consumption as a proxy for somatic stress
        mean_energy_drain = (10.0 - energy_levels.mean()).item() / 10.0
        # Use average phase for global microbiome update
        avg_phase = self.node_phases.float().mean().item()
        self.somatic_stats = self.somatic_system.step(mean_energy_drain, int(avg_phase))
        
        # Update anxiety threshold from gut feedback
        self.anxiety_threshold = self.somatic_stats['anxiety_threshold']
        
        # Update Social Context (Phase 7.4)
        if self.social_context is not None:
            # Use last batch for activity/anxiety signals
            self.social_context.update_trust(
                activity_levels[-1].squeeze(-1), 
                self.node_anxiety.unsqueeze(0)
            )
        
        # Expand node_phases for batch processing
        batch_phases = self.node_phases.unsqueeze(0).expand(batch_size, -1).clone()

        for b in range(batch_size):
            for node in range(self.num_nodes):
                current_phase = batch_phases[b, node].item()
                energy = energy_levels[b, node, 0].item()
                activity = activity_levels[b, node, 0].item()

                # Get anxiety and restorative factors for this node
                node_anxiety = self.node_anxiety[node].item()
                restorative_need = self.restorative_needs[node].item()
                
                # Somatic Sleep Drive (from toxins/waste)
                restorative_need = max(restorative_need, self.somatic_stats.get('sleep_drive', 0.0))
                
                # Social Pressure (Theory of Mind - Phase 7.4)
                social_anxiety = self.social_context.get_social_influence(node) if self.social_context is not None else 0.0
                # Social stress contagion: neighbor anxiety increases local perceived need for interaction
                anxiety_with_social = node_anxiety + (social_anxiety * 0.3)
                
                sleep_qual = self.sleep_quality[node].item()

                # Enhanced phase transition logic with anxiety/restorative/somatic/social mechanics
                new_phase = self._determine_phase_transition(
                    current_phase, energy, activity, anxiety_with_social,
                    restorative_need, sleep_qual, circadian_factor, node
                )

                batch_phases[b, node] = new_phase

        # Update stored phases with last batch (for stateful behavior)
        self.node_phases = batch_phases[-1].clone()

        # Update restorative needs and sub-phases based on current state
        self._update_restorative_state()
        self._cycle_sleep_sub_phases()

        return batch_phases

    def _cycle_sleep_sub_phases(self):
        """
        Cycle through staged sleep sub-phases: LIGHT -> DEEP -> REM.

        Sleep architecture (steps are relative to circadian_period):
            0  – 30 %  → LIGHT  (N1/N2): shallow, noisy gradients settle.
            30 – 70 %  → DEEP   (N3):    maximum physical restoration.
            70 – 100 % → REM:            cognitive replay & consolidation.

        When the majority of nodes enter REM for the first time in a cycle,
        rem_consolidation_pending is set to True so the training loop knows
        to call get_rem_replay_batch().
        """
        rem_entry_count = 0

        for i in range(self.num_nodes):
            if self.node_phases[i] == Phase.SLEEP.value:
                self.sleep_timer[i] += 1
                timer = self.sleep_timer[i].item()

                # Sleep Architecture timing (steps)
                if timer < 30:
                    self.node_sub_phases[i] = SubPhase.LIGHT.value
                elif timer < 70:
                    self.node_sub_phases[i] = SubPhase.DEEP.value
                elif timer < 100:
                    prev = self.node_sub_phases[i].item()
                    self.node_sub_phases[i] = SubPhase.REM.value
                    # Count first-entry into REM this cycle
                    if prev != SubPhase.REM.value:
                        rem_entry_count += 1
                else:
                    # Stay in REM for the remainder of the sleep session
                    self.sleep_timer[i] = 70.0
            else:
                self.sleep_timer[i] = 0
                self.node_sub_phases[i] = SubPhase.NONE.value

        # Trigger REM consolidation when ≥50% of sleeping nodes just entered REM
        sleeping_nodes = (self.node_phases == Phase.SLEEP.value).sum().item()
        if sleeping_nodes > 0 and rem_entry_count >= max(1, sleeping_nodes // 2):
            self._rem_consolidation()

    # ── REM Consolidation ────────────────────────────────────────────────────

    def register_experience(self, loss: float, experience: torch.Tensor) -> None:
        """
        Push a training experience into the replay buffer.

        Call this from the training loop after every backward pass::

            scheduler.register_experience(loss.item(), inputs.detach().cpu())

        Args:
            loss:       Scalar loss value for this experience (higher = harder).
            experience: Input tensor for this batch (detached, on CPU to save VRAM).
        """
        self.replay_buffer.append((float(loss), experience))

    def _rem_consolidation(self) -> None:
        """
        Internal: select the K hardest experiences from the replay buffer.
        Results are stored in self.rem_experiences and the
        rem_consolidation_pending flag is set so the training loop can
        pick them up via get_rem_replay_batch().
        """
        if not self.replay_buffer:
            return

        # Sort by loss descending — hardest examples first (priority replay)
        sorted_experiences = sorted(self.replay_buffer, key=lambda x: x[0], reverse=True)
        top_k = sorted_experiences[: self.rem_replay_k]

        self.rem_experiences = [exp for _, exp in top_k]
        self.rem_consolidation_pending = True

    def get_rem_replay_batch(self) -> list[torch.Tensor] | None:
        """
        Return the list of high-priority replay tensors if REM consolidation
        is pending, then clear the flag.

        Usage in the training loop::

            if (batch := scheduler.get_rem_replay_batch()) is not None:
                for replay_input in batch:
                    # Forward + backward at low LR on replay_input
                    ...

        Returns:
            List of tensors to replay, or None if no consolidation is pending.
        """
        if not self.rem_consolidation_pending:
            return None
        batch = self.rem_experiences
        self.rem_consolidation_pending = False
        self.rem_experiences = []
        return batch

    # ── Polyphasic micro-nap ─────────────────────────────────────────────────

    def polyphasic_nap(self, energy_levels: torch.Tensor) -> bool:
        """
        Trigger a short polyphasic micro-nap for all nodes with low energy.

        A micro-nap is a brief mandatory SLEEP override that lasts
        ``nap_duration`` steps.  It fires automatically every ``nap_interval``
        steps when average energy is below 30 % of expected maximum.

        This addresses the *low_energy_environment* benchmark failure (79 %
        performance degradation) by adding scheduled energy micro-recovery.

        Args:
            energy_levels: [batch_size, num_nodes, 1] energy tensor.

        Returns:
            True if a nap is currently active (caller may reduce LR or skip
            heavy computation), False otherwise.
        """
        self.nap_timer += 1

        if self.nap_active:
            self.nap_steps_remaining -= 1
            if self.nap_steps_remaining <= 0:
                self.nap_active = False
                self.nap_timer = 0
            return True

        # Auto-trigger: low energy + interval elapsed
        if isinstance(energy_levels, (float, int)):
            mean_energy = float(energy_levels)
        else:
            mean_energy = energy_levels.mean().item()
            
        energy_low = mean_energy < 3.0  # Below ~30 % of default capacity (10.0)
        if self.nap_timer >= self.nap_interval and energy_low:
            self.nap_active = True
            self.nap_steps_remaining = self.nap_duration
            # Force all nodes into SLEEP for the nap duration
            self.node_phases.fill_(Phase.SLEEP.value)
            self.sleep_timer.zero_()
            return True

        return False

    def _update_anxiety_tracking(self, anxiety_levels: torch.Tensor) -> None:
        """Update anxiety history and current levels."""
        # Shift anxiety history
        self.anxiety_history[:, 1:] = self.anxiety_history[:, :-1].clone()
        self.anxiety_history[:, 0] = anxiety_levels.to(self.anxiety_history.device)

        # Update current anxiety (exponential moving average)
        alpha = 0.3
        self.node_anxiety = self.node_anxiety.to(anxiety_levels.device)
        self.node_anxiety = alpha * anxiety_levels + (1 - alpha) * self.node_anxiety

    def _handle_exploration_phase(self) -> int:
        """Handle stochastic exploration when enabled."""
        if not (self.stochastic_policy and np.random.random() < self.exploration_rate):
            return None  # No exploration

        phase_probs = torch.tensor([
            self.phase_weights[Phase.ACTIVE],
            self.phase_weights[Phase.SLEEP],
            self.phase_weights[Phase.INTERACTIVE],
            self.phase_weights[Phase.INSPIRED]
        ], device=self.device)

        # Apply temperature scaling for exploration
        phase_probs = torch.softmax(phase_probs / self.policy_temperature, dim=0)
        return torch.multinomial(phase_probs, 1).item()

    def _handle_high_anxiety_phase(self, anxiety: float) -> int:
        """Handle phase transitions for high anxiety states."""
        if anxiety <= self.anxiety_threshold:
            return None  # No anxiety override needed

        anxiety_severity = min(1.0, anxiety / (self.anxiety_threshold * 2))

        if self.stochastic_policy:
            anxiety_probs = torch.zeros(4, device=self.device)
            anxiety_probs[Phase.SLEEP.value] = anxiety_severity * 0.6
            anxiety_probs[Phase.INTERACTIVE.value] = anxiety_severity * 0.3
            anxiety_probs[Phase.ACTIVE.value] = (1 - anxiety_severity) * 0.1
            anxiety_probs = torch.softmax(anxiety_probs / self.policy_temperature, dim=0)
            return torch.multinomial(anxiety_probs, 1).item()
        else:
            # Deterministic anxiety response
            if anxiety_severity > 0.7:
                return Phase.SLEEP.value  # Deep restoration needed
            elif anxiety_severity > 0.4:
                return Phase.INTERACTIVE.value  # Social support seeking
            else:
                # Reduce to lower activity phase
                return Phase.INTERACTIVE.value  # Default for moderate anxiety

        return None

    def _handle_restorative_need_phase(self, restorative_need: float, node_idx: int) -> int:
        """Handle phase transitions for high restorative needs."""
        if restorative_need <= 0.6:
            return None

        # Check if we haven't had enough sleep recently
        recent_sleep = (self.node_phases[node_idx] == Phase.SLEEP.value).float()
        if recent_sleep >= 0.1:  # Had enough sleep recently
            return None

        if self.stochastic_policy:
            rest_probs = torch.zeros(4, device=self.device)
            rest_probs[Phase.SLEEP.value] = 0.8
            rest_probs[Phase.INTERACTIVE.value] = 0.2
            rest_probs = torch.softmax(rest_probs / self.policy_temperature, dim=0)
            return torch.multinomial(rest_probs, 1).item()
        else:
            return Phase.SLEEP.value

    def _handle_low_energy_phase(self, energy: float, anxiety: float) -> int:
        """Handle phase transitions for low energy states."""
        if energy >= 2.0:
            return None

        if self.stochastic_policy:
            low_energy_probs = torch.zeros(4, device=self.device)
            base_sleep_prob = 0.7
            if anxiety > self.anxiety_threshold * 0.5:
                base_sleep_prob = 0.9  # Higher probability when anxious
            low_energy_probs[Phase.SLEEP.value] = base_sleep_prob
            low_energy_probs[Phase.INTERACTIVE.value] = 1 - base_sleep_prob
            low_energy_probs = torch.softmax(low_energy_probs / self.policy_temperature, dim=0)
            return torch.multinomial(low_energy_probs, 1).item()
        else:
            return Phase.SLEEP.value

    def _handle_high_energy_low_activity_phase(self, energy: float, activity: float, anxiety: float, circadian_factor: float) -> int:
        """Handle phase transitions for high energy with low activity."""
        if not (energy > 20.0 and activity < 0.3):
            return None

        if self.stochastic_policy:
            high_energy_probs = torch.zeros(4, device=self.device)
            if anxiety < self.anxiety_threshold * 0.3 and circadian_factor > 0.5:
                # Low anxiety + good circadian timing = inspiration possible
                high_energy_probs[Phase.INSPIRED.value] = 0.6
                high_energy_probs[Phase.INTERACTIVE.value] = 0.3
                high_energy_probs[Phase.ACTIVE.value] = 0.1
            else:
                # High energy but anxious = social interaction preferred
                high_energy_probs[Phase.INTERACTIVE.value] = 0.7
                high_energy_probs[Phase.ACTIVE.value] = 0.3
            high_energy_probs = torch.softmax(high_energy_probs / self.policy_temperature, dim=0)
            return torch.multinomial(high_energy_probs, 1).item()
        else:
            if anxiety < self.anxiety_threshold * 0.3 and circadian_factor > 0.5:
                return Phase.INSPIRED.value
            else:
                return Phase.INTERACTIVE.value

    def _handle_high_activity_phase(self, activity: float, anxiety: float) -> int:
        """Handle phase transitions for high activity states."""
        if activity <= 0.7:
            return None

        if self.stochastic_policy:
            high_activity_probs = torch.zeros(4, device=self.device)
            if anxiety > self.anxiety_threshold * 0.4:
                # Anxious nodes seek interaction over pure activity
                high_activity_probs[Phase.INTERACTIVE.value] = 0.8
                high_activity_probs[Phase.ACTIVE.value] = 0.2
            else:
                # Normal high activity distribution
                high_activity_probs[Phase.ACTIVE.value] = 0.7
                high_activity_probs[Phase.INTERACTIVE.value] = 0.3
            high_activity_probs = torch.softmax(high_activity_probs / self.policy_temperature, dim=0)
            return torch.multinomial(high_activity_probs, 1).item()
        else:
            if anxiety > self.anxiety_threshold * 0.4:
                return Phase.INTERACTIVE.value
            else:
                # Normal high activity transition
                return Phase.ACTIVE.value if np.random.random() > 0.3 else Phase.INTERACTIVE.value

    def _handle_default_transition(self, current_phase: int, anxiety: float, restorative_need: float, node_idx: int) -> int:
        """Handle default phase transitions using transition probabilities."""
        probs = self.transition_matrix[current_phase].clone()

        # Modify probabilities based on anxiety and restorative needs
        if anxiety > self.anxiety_threshold * 0.5:
            probs[Phase.SLEEP.value] *= 1.5  # Increase sleep probability
            probs[Phase.INTERACTIVE.value] *= 1.3  # Increase social interaction
            probs[Phase.ACTIVE.value] *= 0.7  # Decrease pure activity

        if restorative_need > 0.4:
            probs[Phase.SLEEP.value] *= 1.4
            probs[Phase.INSPIRED.value] *= 0.6  # Less likely to be inspired when tired

        # Social Synchronization (Phase 7.4)
        # If we trust neighbors, we tend to sync phases with them
        if getattr(self, 'social_context', None) is not None:
            trust = self.social_context.trust_matrix[node_idx]
            neighbor_phases = self.node_phases # current phases of all nodes
            
            # Find nodes we trust above a threshold (e.g. 0.8)
            trusted_mask = trust > 0.8
            if trusted_mask.any():
                # Count phases in trusted neighborhood
                trusted_phases = neighbor_phases[trusted_mask]
                for p_val in range(len(Phase)):
                    p_count = (trusted_phases == p_val).float().sum()
                    if p_count > 0:
                        # Bias towards neighbor phases: 20% influence per trusted node count
                        probs[p_val] *= (1.0 + 0.2 * p_count)

        # Apply stochastic policy temperature scaling
        if self.stochastic_policy:
            probs = torch.softmax(probs / self.policy_temperature, dim=0)
        else:
            # Normalize probabilities
            probs = probs / probs.sum()

        return torch.multinomial(probs, 1).item()

    def _determine_phase_transition(
        self, current_phase: int, energy: float, activity: float,
        anxiety: float, restorative_need: float, sleep_quality: float,
        circadian_factor: float, node_idx: int
    ) -> int:
        """Determine phase transition with enhanced anxiety/restorative mechanics and stochastic policy."""

        # Check transition handlers in priority order
        transition_handlers = [
            lambda: self._handle_exploration_phase(),
            lambda: self._handle_high_anxiety_phase(anxiety),
            lambda: self._handle_restorative_need_phase(restorative_need, node_idx),
            lambda: self._handle_low_energy_phase(energy, anxiety),
            lambda: self._handle_high_energy_low_activity_phase(energy, activity, anxiety, circadian_factor),
            lambda: self._handle_high_activity_phase(activity, anxiety),
        ]

        # Execute handlers until one returns a phase
        for handler in transition_handlers:
            result = handler()
            if result is not None:
                return result

        # Default transition if no specific handler applies
        return self._handle_default_transition(current_phase, anxiety, restorative_need, node_idx)

    def _update_restorative_state(self) -> None:
        """
        Update restorative needs and sleep quality based on current phases
        and *sub*-phases.

        Sub-phase differentiation (biologically inspired):
            LIGHT  → modest restoration (0.5× base rate).
            DEEP   → maximum physical restoration (1.5× base rate).
                     Mirrors N3 slow-wave sleep / glial waste clearance.
            REM    → standard restoration (1.0×) plus a small inspiration
                     bonus: nodes in REM have a higher chance of entering
                     the INSPIRED phase when they wake, reflecting the
                     creativity boost linked to REM sleep in humans.
        """
        active_mask = (self.node_phases == Phase.ACTIVE.value)
        interactive_mask = (self.node_phases == Phase.INTERACTIVE.value)
        sleep_mask = (self.node_phases == Phase.SLEEP.value)

        # Active phases accumulate fatigue
        self.restorative_needs[active_mask] += 0.05
        self.restorative_needs[interactive_mask] += 0.03

        if sleep_mask.any():
            # Anxiety reduces restoration quality
            sleep_effectiveness = torch.where(
                self.node_anxiety[sleep_mask] > self.anxiety_threshold,
                torch.tensor(0.7, device=self.device),
                torch.tensor(1.0, device=self.device),
            )

            # Sub-phase restoration multipliers
            sub_phases_sleeping = self.node_sub_phases[sleep_mask]
            restoration_multiplier = torch.ones_like(sleep_effectiveness)

            light_mask = (sub_phases_sleeping == SubPhase.LIGHT.value)
            deep_mask  = (sub_phases_sleeping == SubPhase.DEEP.value)
            rem_mask   = (sub_phases_sleeping == SubPhase.REM.value)

            restoration_multiplier[light_mask] = 0.5   # LIGHT: partial rest
            restoration_multiplier[deep_mask]  = 1.5   # DEEP:  maximum recovery
            restoration_multiplier[rem_mask]   = 1.0   # REM:   normal + cognitive

            effective_rate = self.restorative_strength * sleep_effectiveness * restoration_multiplier

            self.restorative_needs[sleep_mask] -= effective_rate
            self.sleep_quality[sleep_mask] = torch.clamp(
                self.sleep_quality[sleep_mask] + 0.02 * sleep_effectiveness * restoration_multiplier,
                0.0, 1.0,
            )

            # REM inspiration bonus: lower the INSPIRED phase threshold slightly
            # for nodes finishing REM so they are more likely to wake inspired.
            rem_nodes_global = sleep_mask.clone()
            rem_nodes_global[sleep_mask] = rem_mask
            if rem_nodes_global.any():
                # Temporarily boost the phase weight for INSPIRED during REM
                # (read by _handle_high_energy_low_activity_phase)
                self._rem_inspiration_boost = True
            else:
                self._rem_inspiration_boost = False

        # Clamp restorative needs
        self.restorative_needs = torch.clamp(self.restorative_needs, 0.0, 1.0)

        # Gradual sleep quality decay when not sleeping
        non_sleep_mask = ~sleep_mask
        self.sleep_quality[non_sleep_mask] *= 0.995

    def get_phase_mask(self, phases: torch.Tensor, target_phase: Phase) -> torch.Tensor:
        """Get boolean mask for nodes in specific phase."""
        return phases == target_phase.value

    def get_active_mask(self, phases: torch.Tensor) -> torch.Tensor:
        """Get mask for nodes that should be actively processing."""
        active_phases = {Phase.ACTIVE.value, Phase.INTERACTIVE.value, Phase.INSPIRED.value}
        mask = torch.zeros_like(phases, dtype=torch.bool)
        for phase_val in active_phases:
            mask |= phases == phase_val
        return mask

    def get_phase_stats(self, phases: torch.Tensor) -> dict[str, float]:
        """Get statistics about current phase distribution."""
        batch_size, num_nodes = phases.shape
        total_nodes = batch_size * num_nodes

        stats = {}
        for phase in Phase:
            count = (phases == phase.value).sum().item()
            stats[f"{phase.name.lower()}_ratio"] = count / total_nodes

        return stats

    def get_anxiety_stats(self) -> dict[str, float]:
        """Get anxiety-related statistics."""
        return {
            'mean_anxiety': self.node_anxiety.mean().item(),
            'max_anxiety': self.node_anxiety.max().item(),
            'anxious_nodes_ratio': (self.node_anxiety > self.anxiety_threshold).float().mean().item(),
            'mean_restorative_need': self.restorative_needs.mean().item(),
            'mean_sleep_quality': self.sleep_quality.mean().item()
        }

    def get_sparsity_metrics(self, energy_levels: torch.Tensor, activity_levels: torch.Tensor) -> dict[str, float]:
        """
        Calculate energy and activity sparsity metrics.
        
        Args:
            energy_levels: [batch_size, num_nodes, 1]
            activity_levels: [batch_size, num_nodes, 1]
            
        Returns:
            Dictionary with sparsity metrics
        """
        # Flatten to [batch_size * num_nodes]
        energy_flat = energy_levels.flatten()
        activity_flat = activity_levels.flatten()

        # Energy sparsity metrics
        energy_sparsity = (energy_flat < 0.1).float().mean().item()  # Fraction with very low energy
        energy_l0_norm = (energy_flat > 0.01).float().sum().item()  # Count of non-zero energies
        energy_l1_norm = energy_flat.abs().sum().item()
        energy_l2_norm = torch.sqrt((energy_flat ** 2).sum()).item()

        # Activity sparsity metrics
        activity_sparsity = (activity_flat < 0.1).float().mean().item()  # Fraction with very low activity
        activity_l0_norm = (activity_flat > 0.01).float().sum().item()  # Count of active nodes
        activity_l1_norm = activity_flat.abs().sum().item()
        activity_l2_norm = torch.sqrt((activity_flat ** 2).sum()).item()

        # Combined sparsity (nodes with both low energy and activity)
        combined_sparse = ((energy_flat < 0.1) & (activity_flat < 0.1)).float().mean().item()

        # Phase-based sparsity
        active_nodes = self.get_active_mask(self.node_phases.unsqueeze(0)).flatten()
        active_ratio = active_nodes.float().mean().item()

        return {
            'energy_sparsity': energy_sparsity,
            'energy_l0_ratio': energy_l0_norm / len(energy_flat),
            'energy_l1_norm': energy_l1_norm,
            'energy_l2_norm': energy_l2_norm,
            'activity_sparsity': activity_sparsity,
            'activity_l0_ratio': activity_l0_norm / len(activity_flat),
            'activity_l1_norm': activity_l1_norm,
            'activity_l2_norm': activity_l2_norm,
            'combined_sparsity': combined_sparse,
            'active_phase_ratio': active_ratio,
            'mean_energy': energy_flat.mean().item(),
            'mean_activity': activity_flat.mean().item()
        }

    def get_stochastic_policy_metrics(self, phases: torch.Tensor) -> dict[str, float]:
        """Get metrics about stochastic policy performance."""
        if not self.stochastic_policy:
            return {'stochastic_policy_enabled': False}

        # Calculate phase distribution entropy
        phase_counts = torch.zeros(4, device=self.device)
        for phase in Phase:
            phase_counts[phase.value] = (phases == phase.value).float().sum()
        phase_probs = phase_counts / phase_counts.sum()

        # Shannon entropy of phase distribution
        phase_entropy = -torch.sum(phase_probs * torch.log(phase_probs + 1e-8)).item()

        # Calculate diversity score (normalized entropy)
        max_entropy = np.log(len(Phase))
        diversity_score = phase_entropy / max_entropy

        # Track entropy history
        self.policy_entropy_history.append(phase_entropy)
        if len(self.policy_entropy_history) > 100:  # Keep last 100 steps
            self.policy_entropy_history.pop(0)

        # Calculate entropy stability (lower variance = more stable)
        entropy_variance = np.var(self.policy_entropy_history) if len(self.policy_entropy_history) > 1 else 0.0

        return {
            'stochastic_policy_enabled': True,
            'phase_entropy': phase_entropy,
            'phase_diversity_score': diversity_score,
            'entropy_variance': entropy_variance,
            'policy_temperature': self.policy_temperature,
            'exploration_rate': self.exploration_rate,
            'entropy_history_length': len(self.policy_entropy_history)
        }

    def adjust_policy_parameters(self, performance_feedback: float):
        """Dynamically adjust stochastic policy parameters based on performance."""
        if not self.stochastic_policy:
            return

        # Adjust temperature based on performance
        # Good performance -> reduce temperature (less exploration)
        # Poor performance -> increase temperature (more exploration)
        if performance_feedback > 0.8:
            self.policy_temperature = max(0.1, self.policy_temperature * 0.95)
            self.exploration_rate = max(0.01, self.exploration_rate * 0.98)
        elif performance_feedback < 0.5:
            self.policy_temperature = min(2.0, self.policy_temperature * 1.05)
            self.exploration_rate = min(0.3, self.exploration_rate * 1.02)

    def reset(self) -> None:
        """Reset scheduler to initial state."""
        self.current_step = 0
        self.node_phases.zero_()
        self.node_anxiety.zero_()
        self.anxiety_history.zero_()
        self.restorative_needs.zero_()
        self.sleep_quality.fill_(1.0)
        # REM replay state
        self.replay_buffer.clear()
        self.rem_consolidation_pending = False
        self.rem_experiences = []
        # Polyphasic nap state
        self.nap_timer = 0
        self.nap_active = False
        self.nap_steps_remaining = 0
        # REM inspiration boost flag
        self._rem_inspiration_boost = False

