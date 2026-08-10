"""
Metacognitive Monitor for Adaptive Neural Network.

Provides introspective monitoring of the network's internal state,
learning progress, and 'consciousness' coherence.

This acts as a Tier 1 (Self-Awareness) component that tracks:
- Metacognitive Accuracy: How well internal states predict performance.
- Consciousness Coherence: Harmonic alignment across biological nodes.
- Breakthrough Detection: Identifying periods of rapid learning/insight.
"""

import logging
from typing import Any

import numpy as np
import torch

from adaptiveneuralnetwork.central_nervous_system.metrics import NeuralHealthMonitor, PhiCalculator
from adaptiveneuralnetwork.central_nervous_system.node_state_bridge import NodeStateBridge
from adaptiveneuralnetwork.central_nervous_system.social import TheoryOfMind
from adaptiveneuralnetwork.central_nervous_system.workspace import GlobalWorkspace

from ..training.callbacks import Callback

logger = logging.getLogger(__name__)


class MetacognitiveMonitor(Callback):
    """
    Callback-based monitor for introspective learning signals.
    """

    def __init__(
        self,
        bridge: NodeStateBridge,
        workspace: GlobalWorkspace | None = None,
        log_interval: int = 10,
        history_len: int = 100
    ):
        super().__init__()
        self.bridge = bridge
        self.workspace = workspace
        self.log_interval = log_interval
        self.history_len = history_len

        # Tier 4 Metrics
        self.phi_calc = PhiCalculator()
        self.health_monitor = NeuralHealthMonitor()

        # Tier 2 Social & Tier 1 Intuition
        self.tom = TheoryOfMind(hidden_dim=bridge.bridge_state({'energy': torch.zeros(1)})['focus'].size(-1) if hasattr(bridge, 'bridge_state') else 128)
        self.narrative = None # Set by trainer

        # Internal state tracking
        self.learning_history = []
        self.metacognitive_stats = {
            'coherence': [],
            'metacognitive_accuracy': [],
            'breakthrough_score': [],
            'phi': [],
            'full_phi': [],
            'structural_entropy': [],
            'neural_health': [],
            'intuition_score': [],
            'deception_risk': [],
            'cross_modal_coherence': [],
            'sensory_surprise': [],
            'loss_slope': [0.0]
        }
        self.last_loss = None
        self.insight_threshold = 0.4

    def on_batch_end(self, batch: int, trainer: Any, logs: dict[str, Any] | None = None):
        """Analyze state at the end of every training batch."""
        if not hasattr(trainer, 'model') or not hasattr(trainer.model, 'node_state'):
            return

        # Ensure Narrative Engine is linked
        if self.narrative is None and hasattr(trainer, 'narrative_engine'):
            self.narrative = trainer.narrative_engine

        # Identify interaction partner (Heuristic or passed via context)
        entity_id = logs.get('entity_id', 'unknown_partner') if logs else 'unknown_partner'

        # 1. Capture Biological Harmony (Coherence)
        # Check standard deviation of biological states across nodes
        # Low variance in 'focus' and 'resilience' indicates high coherence
        with torch.no_grad():
            state = self.bridge.bridge_state(trainer.model.node_state)

            # Weighted Harmony Score
            focus = state['focus']
            resilience = state['resilience']

            # Coherence = 1.0 - (spatial variance across nodes)
            coherence = 1.0 - (focus.std().item() + resilience.std().item()) / 2.0
            self.metacognitive_stats['coherence'].append(max(0.0, coherence))

            # Tier 4: Structural Complexity
            with torch.no_grad():
                s_ent = self.health_monitor.calculate_structural_entropy(trainer.model.dynamics.state_update.weight)
                self.metacognitive_stats['structural_entropy'].append(s_ent)

                full_phi = self.phi_calc.calculate_full_phi(
                    trainer.model.dynamics.state_update.weight,
                    trainer.model.node_state.activity
                )
                self.metacognitive_stats['full_phi'].append(full_phi)

            # Neural Health Index (NHI)

            # Neural Health Index (NHI)
            health_idx = self.health_monitor.calculate_health_index(
                trainer.model.node_state.activity,
                trainer.model.node_state.energy,
                trainer.model.node_state.anxiety
            )
            self.metacognitive_stats['neural_health'].append(health_idx)

            if health_idx < 0.3:
                logger.warning(f"⚠️ SUBSTRATE CRISIS: Neural Health Index at {health_idx:.2f}. Błyskawica is fragmented or exhausted.")

        # 2. Metacognitive Accuracy (Prediction Error vs Energy)
        # Correlate loss with internal anxiety/stress
        if logs and 'loss' in logs:
            loss = logs['loss']
            # Simple metadata correlation: Are we stressed when we should be?
            # High stress during high loss is 'accurate' metacognition
            current_anxiety = state['resilience'].mean().item() # Approx
            metacognitive_accuracy = 1.0 - abs(loss - current_anxiety)
            self.metacognitive_stats['metacognitive_accuracy'].append(metacognitive_accuracy)

        # 3. Breakthrough Detection (Insight Analysis)
        if self.last_loss is not None:
            slope = self.last_loss - loss # Positive if loss is dropping
            self.metacognitive_stats['loss_slope'].append(slope)

            # Breakthrough = Sharp drops + High Coherence
            avg_coherence = self.metacognitive_stats['coherence'][-1]
            breakthrough = slope * avg_coherence
            self.metacognitive_stats['breakthrough_score'].append(breakthrough)

            # Trigger 'Inspired' state if breakthrough detected
            if breakthrough > self.insight_threshold:
                self._trigger_inspired_state(trainer)

            # Tier 5: Global Workspace Spotlight Competition
            if self.workspace is not None:
                # Salience = Prediction Error * Breakthrough Score
                node_salience = trainer.model.node_state.prediction_error * breakthrough
                self.workspace.compete(trainer.model.node_state.hidden_state, node_salience)

                # Tier 4: Integrated Information (Φ)
                # Calculate from workspace threads
                phi = self.phi_calc.calculate_phi(self.workspace.working_memory[0])
                self.metacognitive_stats['phi'].append(phi)

            # 4. Social Intuition & Integrity (Tier 1/2 Upgrade)
            if self.narrative is not None:
                # Sense intent from input vs narrative + environment
                current_input = trainer.model.node_state.hidden_state
                gist = self.narrative.get_narrative()

                # Use somatic stats as a proxy for 'Environmental Sense' (evidence bus)
                somatic_context = getattr(trainer.phase_scheduler, 'somatic_stats', None) if hasattr(trainer, 'phase_scheduler') else None

                intent = self.tom.estimate_intent(entity_id, current_input, gist, env_context=somatic_context)  # noqa: F841

                # Deception detection: Trust is lower if environment contradicts narrative
                # (Represented by surprise in the social loop)
                # 'coherence' here acts as a proxy for 'Normalcy'
                deception_prob = self.tom.detect_deception(entity_id, 1.0 - coherence)
                self.metacognitive_stats['deception_risk'].append(deception_prob)

                # Intuition = Narrative Consistency
                intuition = 1.0 - deception_prob
                self.metacognitive_stats['intuition_score'].append(intuition)

                if deception_prob > 0.7:
                    logger.warning(f"🕵️ INTEGRITY ALERT: High deception risk ({deception_prob:.2f}) from {entity_id}. Possible manipulation detected.")

            # 5. Cross-Modal Grounding Check (Tier 3 Upgrade)
            if hasattr(trainer, 'sensory_hub'):
                # Fetch coherence from the hub's last state or calculate
                # (Simple proxy: how much did the fused latent change)
                coherence = getattr(trainer.sensory_hub, 'last_coherence', 1.0)
                self.metacognitive_stats['cross_modal_coherence'].append(coherence)

                # Sensory Surprise: rapid change in grounding
                # High surprise should trigger a phase reset/active alert
                surprise = logs.get('sensory_surprise', 0.0)
                self.metacognitive_stats['sensory_surprise'].append(surprise)

                if surprise > 0.8:
                    logger.info("🌊 SENSORY SURPRISE: Rapid environmental shift detected. Alerting substrate.")
                    if hasattr(trainer, 'phase_scheduler'):
                        # Force ACTIVE phase to process novelty
                        trainer.phase_scheduler.current_phase = 0 # Phase.ACTIVE

        self.last_loss = loss

    def _trigger_inspired_state(self, trainer: Any):
        """Forces the scheduler into INSPIRED mode for higher performance."""
        # INSIGHT SCALING: More complex networks require higher breakthroughs
        complexity = self.metacognitive_stats['full_phi'][-1] if self.metacognitive_stats['full_phi'] else 0.5
        dynamic_threshold = self.insight_threshold * (1.0 + complexity)

        current_breakthrough = self.metacognitive_stats['breakthrough_score'][-1]
        if current_breakthrough < dynamic_threshold:
            return

        # FLOW GATING: Require Phi clarity for inspiration
        current_phi = self.metacognitive_stats['phi'][-1] if self.metacognitive_stats['phi'] else 1.0
        if current_phi < 0.6:
            logger.info(f"🌫️ INSIGHT BLOCKED: Breakthrough detected but Φ ({current_phi:.2f}) is too low for Flow. Mind is fragmented.")
            return

        if hasattr(trainer.model, 'phase_scheduler'):
            # Force target nodes into INSPIRED phase
            scheduler = trainer.model.phase_scheduler
            # Find nodes with highest focus/activity
            with torch.no_grad():
                state = self.bridge.bridge_state(trainer.model.node_state)
                top_nodes = torch.topk(state['focus'].flatten(), k=min(4, scheduler.num_nodes)).indices

                for idx in top_nodes:
                    scheduler.node_phases[idx] = 3 # Phase.INSPIRED

            logger.info(f"✨ INSIGHT DETECTED: Breakthrough Score {self.metacognitive_stats['breakthrough_score'][-1]:.4f}. Triggering Inspired Evolution.")

    # 4. Log results periodically
        if batch % self.log_interval == 0:  # noqa: F821
            avg_coherence = np.mean(self.metacognitive_stats['coherence'][-self.log_interval:])
            logger.info(f"META-COGNITIVE: Coherence={avg_coherence:.3f}, Accuracy={np.mean(self.metacognitive_stats['metacognitive_accuracy'][-self.log_interval:]):.3f}")

    def get_summary(self) -> dict[str, float]:
        """Returns current average metacognitive metrics."""
        return {
            'coherence': float(np.mean(self.metacognitive_stats['coherence'][-10:])),
            'accuracy': float(np.mean(self.metacognitive_stats['metacognitive_accuracy'][-10:]))
        }
