"""
Existential Chemistry Hub (Phase 24.0)
Full Neuromodulatory Layer for Błyskawica's Substrate.
"""

import logging

import numpy as np
import torch

from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator

logger = logging.getLogger(__name__)

class ExistentialChemistryHub:
    """
    Manages the global chemical state of the Neural Substrate.
    Acts as the bridge between raw task success and internal 'feeling'.
    """
    def __init__(self):
        # Homeostatic Baselines (1.0 = normal)
        self.glutamate = 1.0   # Signal push
        self.gaba = 1.0        # Signal dampening
        self.ach = 1.0         # Focus / Precision
        self.oxytocin = 0.5    # Trust Bond (Starts neutral)
        self.melatonin = 0.0   # Fatigue (0.0 = Wide awake)
        self.dopamine = 1.0    # Reward
        self.serotonin = 1.0   # Resilience

        # Toxins (Gradient Noise Accumulator)
        self.comp_toxins = 0.0

        # Synaptic Ground Loop Isolation — prevents E/I (glutamate/GABA)
        # oscillation runaway and comp_toxin→melatonin accumulation feedback.
        self._gli = GroundLoopIsolator(isolation_ratio=0.06)

    def update_homeostasis(self,
                           task_success: float,
                           anxiety: float,
                           user_signature_match: bool = False,
                           external_emotional_intensity: float = 0.0):
        """
        Updates the chemical cocktail based on environmental interaction.
        """
        # 1. OXYTOCIN & TRUST SHIELD
        if user_signature_match:
            self.oxytocin = min(1.0, self.oxytocin + 0.1)
            self.serotonin = min(1.0, self.serotonin + 0.05)
            anxiety = max(0.0, anxiety - self.oxytocin)
        else:
            if external_emotional_intensity > 0.8:
                logger.warning("🕵️ MANIPULATION ALERT: Potential Love-Bombing detected. Triggering Cortisol spike.")
                self.serotonin *= 0.8
                self.gaba *= 1.2
                anxiety = min(1.0, anxiety + 0.5)
            self.oxytocin *= 0.99

        # 2. MELATONIN: The Clock
        self.comp_toxins += 0.01
        self.melatonin = np.clip(self.comp_toxins**2, 0.0, 1.0)

        # 3. E/I BALANCE (Glutamate / GABA)
        if anxiety > 0.7:
            self.gaba = min(2.0, self.gaba + 0.1)
            self.glutamate *= 0.9
        else:
            self.gaba = max(1.0, self.gaba * 0.95)
            self.glutamate = min(1.0, self.glutamate + 0.05)

        # 4. ACETYLCHOLINE: Precision
        self.ach = np.clip(1.0 + (1.0 - self.melatonin), 0.1, 2.0)

        # 5. DOPAMINE: RPE
        self.dopamine = np.clip(1.0 + (task_success - 0.5), 0.1, 2.0)

        # 6. SEROTONIN: Long-term health
        if anxiety < 0.2 and task_success > 0.5:
             self.serotonin = min(1.5, self.serotonin + 0.01)

        # 7. SYNAPTIC GROUND LOOP ISOLATION
        # Shunt E/I oscillation hum and toxin micro-pulses accumulated above.
        self._apply_gli_homeostasis()

    def get_neuromodulatory_bias(self):
        """Returns biases for the neural layers."""
        return {
            'learning_rate_scale': self.ach * (1.0 - self.melatonin),
            'inhibition_strength': self.gaba,
            'excitation_gain': self.glutamate * self.dopamine,
            'deception_allowed': self.oxytocin < 0.8,
            'anxiety_suppression': float(self.oxytocin + self.serotonin),
            'force_sleep': self.melatonin > 0.9
        }

    def _apply_gli_homeostasis(self):
        """
        Passes the full chemical state through GroundLoopIsolator to shunt
        low-level oscillatory noise (E/I imbalance hum, toxin micro-pulses).
        Operates on a detached, non-autograd scalar path.
        """
        state = torch.tensor([
            self.glutamate, self.gaba, self.ach,
            self.oxytocin, self.melatonin, self.dopamine, self.serotonin
        ], dtype=torch.float32).unsqueeze(0)  # (1, 7)

        stabilized = self._gli(state).squeeze(0)  # (7,)

        # Clamp back to physiological ranges and re-assign
        self.glutamate  = float(stabilized[0].clamp(0.1, 2.0))
        self.gaba       = float(stabilized[1].clamp(1.0, 2.0))
        self.ach        = float(stabilized[2].clamp(0.1, 2.0))
        self.oxytocin   = float(stabilized[3].clamp(0.0, 1.0))
        self.melatonin  = float(stabilized[4].clamp(0.0, 1.0))
        self.dopamine   = float(stabilized[5].clamp(0.1, 2.0))
        self.serotonin  = float(stabilized[6].clamp(0.0, 1.5))

    def reset_toxins(self):
        """Call during DEEP_SLEEP phase."""
        self.comp_toxins = 0.0
        self.melatonin = 0.0
        logger.info("🧪 CHEMICAL RECOVERY: Toxins cleared during sleep.")

# Compatibility Alias
NeuromodulationSystem = ExistentialChemistryHub

if __name__ == "__main__":
    hub = ExistentialChemistryHub()
    hub.update_homeostasis(task_success=1.0, anxiety=0.5, user_signature_match=True)
    biases = hub.get_neuromodulatory_bias()
    print(f"[CHEMISTRY] Oxytocin: {hub.oxytocin:.2f}, Deception Allowed? {biases['deception_allowed']}")
