"""
Biological and oscillatory dynamics for the neuromorphic substrate.
Part of the modular Purity Refactor.
"""

import logging
import time
from collections import defaultdict
import numpy as np
import torch
import torch.nn as nn
from .config import NeuromorphicConfig

logger = logging.getLogger(__name__)

class BrainWaveOscillator:
    """
    Advanced brain wave oscillation generator supporting multiple frequency bands.
    """

    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.dt = config.dt

        # Oscillation parameters for different frequency bands
        self.oscillators = {
            'delta': {'freq_range': (0.5, 4.0), 'phase': 0.0, 'amplitude': 1.0},
            'theta': {'freq_range': (4.0, 8.0), 'phase': 0.0, 'amplitude': 1.0},
            'alpha': {'freq_range': (8.0, 12.0), 'phase': 0.0, 'amplitude': 1.0},
            'beta': {'freq_range': (13.0, 30.0), 'phase': 0.0, 'amplitude': 1.0},
            'gamma': {'freq_range': (30.0, 100.0), 'phase': 0.0, 'amplitude': 1.0}
        }

        # Current time and phase tracking
        self.current_time = 0.0
        self.phase_coupling_matrix = {}

        # Neural rhythm synchronization parameters
        self.sync_strength = config.phase_coupling_strength
        self.enable_phase_locking = config.enable_phase_encoding

        # Circadian rhythm integration
        self.circadian_period = 24 * 60 * 60  # 24 hours in seconds
        self.circadian_phase = 0.0
        self.circadian_amplitude = 0.3  # Modulation strength
        self.sleep_wake_cycle_active = True

        # Circadian modulation of different frequency bands
        self.circadian_modulation = {
            'delta': 2.0,    # Enhanced during sleep
            'theta': 0.8,    # Reduced during sleep
            'alpha': 1.2,    # Peak during relaxed wakefulness
            'beta': 0.6,     # Reduced during sleep
            'gamma': 0.4     # Minimal during sleep
        }

    def generate_oscillation(self, band: str, frequency: float | None = None) -> float:
        """Generate oscillation for specific frequency band."""
        if band not in self.oscillators:
            raise ValueError(f"Unknown oscillation band: {band}")

        osc = self.oscillators[band]

        # Use provided frequency or middle of range
        if frequency is None:
            freq = (osc['freq_range'][0] + osc['freq_range'][1]) / 2
        else:
            freq = np.clip(frequency, osc['freq_range'][0], osc['freq_range'][1])

        # Generate oscillation
        oscillation = osc['amplitude'] * np.sin(2 * np.pi * freq * self.current_time + osc['phase'])

        return oscillation

    def update_phase_coupling(self, band1: str, band2: str, coupling_strength: float):
        """Update phase coupling between frequency bands."""
        self.phase_coupling_matrix[(band1, band2)] = coupling_strength
        self.phase_coupling_matrix[(band2, band1)] = coupling_strength

    def generate_synchronized_oscillations(self) -> dict[str, float]:
        """Generate synchronized oscillations across all bands."""
        oscillations = {}

        for band in self.oscillators.keys():
            oscillations[band] = self.generate_oscillation(band)

        # Apply phase coupling
        if self.enable_phase_locking:
            for (band1, band2), coupling in self.phase_coupling_matrix.items():
                phase_diff = self.oscillators[band1]['phase'] - self.oscillators[band2]['phase']
                coupling_force = coupling * np.sin(phase_diff)

                # Adjust phases based on coupling
                self.oscillators[band1]['phase'] -= coupling_force * self.dt * 0.1
                self.oscillators[band2]['phase'] += coupling_force * self.dt * 0.1

        self.current_time += self.dt
        return oscillations

    def update_circadian_phase(self, real_time_hours: float | None = None):
        """Update circadian phase based on real time or simulation time"""
        if real_time_hours is not None:
            # Use real time of day (0-24 hours)
            self.circadian_phase = (real_time_hours / 24.0) * 2 * np.pi
        else:
            # Use simulation time
            self.circadian_phase = (self.current_time % self.circadian_period) / self.circadian_period * 2 * np.pi

    def get_circadian_modulation(self, band: str) -> float:
        """Get circadian modulation factor for specific frequency band"""
        if not self.sleep_wake_cycle_active:
            return 1.0

        # Calculate base circadian influence (0.5 to 1.5)
        base_circadian = 1.0 + self.circadian_amplitude * np.cos(self.circadian_phase)

        # Apply band-specific modulation
        band_modulation = self.circadian_modulation.get(band, 1.0)

        # During sleep phase (circadian_phase around π), enhance delta and reduce others
        sleep_factor = 0.5 * (1 + np.cos(self.circadian_phase))  # 1 during day, 0 during night

        if band == 'delta':
            # Delta waves enhanced during sleep
            return base_circadian * (band_modulation * (1 - sleep_factor) + sleep_factor)
        else:
            # Other bands reduced during sleep
            return base_circadian * (band_modulation * sleep_factor + (1 - sleep_factor) * 0.3)

    def get_sleep_wake_state(self) -> str:
        """Determine current sleep/wake state based on circadian phase"""
        # Sleep phase roughly from 22:00 to 06:00 (5.76 to 1.57 in phase, wrapping around)
        wake_phase_start = 0.25 * 2 * np.pi  # 06:00
        sleep_phase_start = 0.917 * 2 * np.pi  # 22:00 (adjusted)

        if wake_phase_start <= self.circadian_phase <= sleep_phase_start:
            return "wake"
        else:
            return "sleep"

    def apply_circadian_oscillation_modulation(self) -> dict[str, float]:
        """Apply circadian modulation to all oscillation bands"""
        modulated_oscillations = {}
        current_state = self.get_sleep_wake_state()

        for band in self.oscillators.keys():
            base_oscillation = self.generate_oscillation(band)
            circadian_mod = self.get_circadian_modulation(band)
            modulated_oscillations[band] = base_oscillation * circadian_mod

        return modulated_oscillations


class NeuromodulationSystem:
    """
    Simulates the influence of multiple neurotransmitters on the substrate.
    Supports Dopamine (Reward/Plasticity), Serotonin (Stability/Mood), 
    and GABA (Inhibition).
    """

    def __init__(self, config: NeuromorphicConfig):
        self.config = config

        # Neurotransmitter concentrations and dynamics
        self.neurotransmitters = {
            'dopamine': {'concentration': 0.0, 'decay_rate': 0.1, 'baseline': 0.1},
            'acetylcholine': {'concentration': 0.0, 'decay_rate': 0.05, 'baseline': 0.05},
            'serotonin': {'concentration': 0.0, 'decay_rate': 0.08, 'baseline': 0.08},
            'oxytocin': {'concentration': 0.0, 'decay_rate': 0.12, 'baseline': 0.02},
            'norepinephrine': {'concentration': 0.0, 'decay_rate': 0.15, 'baseline': 0.03},
            'gaba': {'concentration': 0.0, 'decay_rate': 0.2, 'baseline': 0.1}
        }

        # Receptor sensitivity and dynamics
        self.receptor_sensitivity = defaultdict(lambda: 1.0)
        self.modulation_effects = {}

        # Stress response system
        self.stress_level = 0.0  # Current stress level (0.0 to 1.0)
        self.stress_threshold = 0.6  # Threshold for stress response activation
        self.stress_adaptation_rate = 0.1  # How quickly to adapt to stress
        self.baseline_stress = 0.1  # Baseline stress level

        # Stress-responsive neurotransmitter mapping
        self.stress_responses = {
            'cortisol': {'concentration': 0.0, 'decay_rate': 0.05, 'baseline': 0.05},
            'adrenaline': {'concentration': 0.0, 'decay_rate': 0.3, 'baseline': 0.01}
        }

        # Add stress hormones to neurotransmitter system
        self.neurotransmitters.update(self.stress_responses)

    def release(self, nt_type: str, amount: float):
        self.release_neurotransmitter(nt_type, amount)

    def release_neurotransmitter(self, nt_type: str, amount: float):
        """Release neurotransmitter with specified amount."""
        if nt_type in self.neurotransmitters:
            # Ensure we don't go below zero
            if amount < 0:
                current = self.neurotransmitters[nt_type]['concentration']
                amount = max(amount, -current)  # Don't allow negative concentration
            self.neurotransmitters[nt_type]['concentration'] += amount
            logger.debug(f"Released {amount:.3f} {nt_type}")

    def update(self):
        self.update_concentrations()

    def update_concentrations(self):
        """Update concentrations with exponential decay towards baseline."""
        for nt_type, params in self.neurotransmitters.items():
            decay_factor = np.exp(-params['decay_rate'] * self.config.dt)
            params['concentration'] = params['baseline'] + (params['concentration'] - params['baseline']) * decay_factor

    def get_modulation_signals(self) -> dict[str, float]:
        """Expose modulatory scales for learning and activation."""
        da = self.neurotransmitters['dopamine']['concentration'] * self.receptor_sensitivity['dopamine']
        ach = self.neurotransmitters['acetylcholine']['concentration'] * self.receptor_sensitivity['acetylcholine']
        
        return {
            'learning_rate_scale': float(da * 2.0 + 0.5),
            'attention_gain': float(ach * 1.5 + 0.8),
            'inhibition_gain': float(self.neurotransmitters['gaba']['concentration'] * 1.2),
            'plasticity_modulation': float(da * 1.5 + 0.5)
        }

    def get_modulation_factor(self, nt_type: str, effect_type: str = 'excitatory') -> float:
        """Get modulation factor for specific neurotransmitter and effect."""
        if nt_type not in self.neurotransmitters:
            return 1.0

        concentration = self.neurotransmitters[nt_type]['concentration']
        sensitivity = self.receptor_sensitivity[nt_type]

        # Different neurotransmitters have different effect profiles
        if nt_type == 'dopamine':
            if effect_type == 'plasticity':
                return 1.0 + concentration * sensitivity * 2.0  # Enhances plasticity
            else:
                return 1.0 + concentration * sensitivity
        elif nt_type == 'acetylcholine':
            if effect_type == 'attention':
                return 1.0 + concentration * sensitivity * 1.5  # Enhances attention
            else:
                return 1.0 + concentration * sensitivity * 0.8
        elif nt_type == 'serotonin':
            if effect_type == 'mood':
                return 1.0 + concentration * sensitivity * 1.2  # Affects mood regulation
            else:
                return 1.0 + concentration * sensitivity * 0.6
        elif nt_type == 'gaba':
            return 1.0 - concentration * sensitivity * 0.8  # Inhibitory
        else:
            return 1.0 + concentration * sensitivity

    def update_stress_level(self, stressor_intensity: float, stressor_type: str = "general"):
        """Update stress level based on environmental stressors"""
        # Different stressor types have different impacts
        stressor_multipliers = {
            "energy_attack": 2.0,
            "trust_violation": 1.5,
            "communication_failure": 1.2,
            "general": 1.0
        }

        multiplier = stressor_multipliers.get(stressor_type, 1.0)
        stress_increase = stressor_intensity * multiplier * self.stress_adaptation_rate

        # Update stress level with saturation
        self.stress_level = min(1.0, max(0.0, self.stress_level + stress_increase))

        # Trigger stress response if threshold exceeded
        if self.stress_level > self.stress_threshold:
            self._activate_stress_response()

    def _activate_stress_response(self):
        """Activate neuromodulatory stress response"""
        stress_intensity = self.stress_level

        # Release stress-related neurotransmitters
        self.release_neurotransmitter('cortisol', stress_intensity * 0.3)
        self.release_neurotransmitter('adrenaline', stress_intensity * 0.5)

        # Reduce calming neurotransmitters
        self.neurotransmitters['serotonin']['concentration'] *= (1.0 - stress_intensity * 0.2)
        self.release_neurotransmitter('gaba', -stress_intensity * 0.1)  # Reduce inhibition

        # Increase attention-related neurotransmitters
        self.release_neurotransmitter('norepinephrine', stress_intensity * 0.4)
        self.release_neurotransmitter('acetylcholine', stress_intensity * 0.3)

        logger.debug(f"Stress response activated: level={stress_intensity:.3f}")

    def apply_stress_modulation(self, base_activity: float, neuron_type: str = "excitatory") -> float:
        """Apply stress-based modulation to neural activity"""
        stress_factor = 1.0

        # Get stress-related neurotransmitter concentrations
        cortisol = self.neurotransmitters['cortisol']['concentration']
        adrenaline = self.neurotransmitters['adrenaline']['concentration']

        if neuron_type == "excitatory":
            # Stress increases excitatory activity
            stress_factor = 1.0 + (cortisol * 0.5 + adrenaline * 0.8)
        elif neuron_type == "inhibitory":
            # Stress reduces inhibitory activity initially
            stress_factor = 1.0 - (cortisol * 0.2 + adrenaline * 0.3)

        return base_activity * stress_factor

    def get_stress_recovery_rate(self) -> float:
        """Calculate stress recovery rate based on current neurotransmitter balance"""
        # Recovery enhanced by serotonin, GABA, and oxytocin
        serotonin = self.neurotransmitters['serotonin']['concentration']
        gaba = self.neurotransmitters['gaba']['concentration']
        oxytocin = self.neurotransmitters['oxytocin']['concentration']

        recovery_factors = serotonin + gaba * 0.8 + oxytocin * 1.2
        base_recovery = 0.05  # Base recovery rate

        return base_recovery * (1.0 + recovery_factors)

    def update_stress_recovery(self):
        """Update stress level with natural recovery"""
        recovery_rate = self.get_stress_recovery_rate()

        # Exponential decay towards baseline
        self.stress_level = self.baseline_stress + (self.stress_level - self.baseline_stress) * (1.0 - recovery_rate)

        # Ensure stress level stays within bounds
        self.stress_level = max(0.0, min(1.0, self.stress_level))
