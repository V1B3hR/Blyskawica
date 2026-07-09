"""
Configuration schemas and enums for the neuromorphic substrate.
Part of the modular Purity Refactor.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import torch

logger = logging.getLogger(__name__)

class NeuromorphicPlatform(Enum):
    """Supported neuromorphic hardware platforms."""
    LOIHI = "loihi"
    SPINNAKER = "spinnaker"
    TRUENORTH = "truenorth"
    AKIDA = "akida"
    GENERIC_SNN = "generic_snn"
    LOIHI2 = "loihi2"
    SPINNAKER2 = "spinnaker2"
    GENERIC_V3 = "generic_v3"
    MEMRISTIVE_CROSSBAR = "memristive_crossbar"
    PHOTONIC_SNN = "photonic_snn"
    QUANTUM_NEUROMORPHIC = "quantum_neuromorphic"
    SIMULATION = "simulation"

class PlasticityType(Enum):
    """Types of synaptic plasticity mechanisms."""
    STDP = "spike_timing_dependent_plasticity"
    BCM = "bienenstock_cooper_munro"
    HOMEOSTATIC = "homeostatic_scaling"
    METAPLASTICITY = "metaplasticity"
    TRIPLET_STDP = "triplet_stdp"
    CALCIUM_DEPENDENT = "calcium_dependent"
    DOPAMINE_MODULATED = "dopamine_modulated"
    VOLTAGE_DEPENDENT = "voltage_dependent"
    STRUCTURAL_PLASTICITY = "structural_plasticity"

class AdaptationMode(Enum):
    """Real-time adaptation modes."""
    CONTINUOUS = "continuous"
    EPISODIC = "episodic"
    TRIGGERED = "triggered"
    LEARNING_BASED = "learning_based"
    HYBRID = "hybrid"

class NeuronType(Enum):
    """Advanced neuron model types."""
    LIF = "leaky_integrate_fire"
    ADAPTIVE_LIF = "adaptive_lif"
    IZHIKEVICH = "izhikevich"
    HODGKIN_HUXLEY = "hodgkin_huxley"
    MULTI_COMPARTMENT = "multi_compartment"
    STOCHASTIC_LIF = "stochastic_lif"
    FRACTIONAL_LIF = "fractional_lif"
    RESONATOR = "resonator_neuron"

@dataclass
class SpikeEvent:
    """Represents a spike event in neuromorphic processing."""
    neuron_id: int
    timestamp: float
    amplitude: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    phase: float | None = None
    burst_index: int | None = None
    dendrite_id: int | None = None
    axon_delay: float = 0.0

@dataclass
class PlasticityRule:
    """Configuration for plasticity rules."""
    rule_type: PlasticityType
    learning_rate: float = 0.01
    time_window: float = 0.02  # ms
    tau_plus: float = 0.02
    tau_minus: float = 0.02
    a_plus: float = 1.0
    a_minus: float = 1.0
    tau_bcm: float = 1.0
    theta_0: float = 1.0
    target_rate: float = 10.0
    tau_homeostatic: float = 10.0
    meta_learning_rate: float = 0.001
    sliding_threshold: bool = True
    modulation_factor: float = 1.0
    modulator_type: str | None = None
    adaptive_learning_rate: bool = False
    adaptation_window: float = 1.0
    min_learning_rate: float = 1e-6
    max_learning_rate: float = 0.1

@dataclass
class RealTimeAdaptationConfig:
    """Configuration for real-time adaptation mechanisms."""
    mode: AdaptationMode = AdaptationMode.CONTINUOUS
    update_frequency: float = 0.1
    performance_window: float = 1.0
    performance_threshold: float = 0.8
    adaptation_sensitivity: float = 0.1
    monitor_energy: bool = True
    monitor_latency: bool = True
    monitor_accuracy: bool = True
    energy_budget: float | None = None
    latency_budget: float | None = None
    parameter_scaling: bool = True
    topology_adaptation: bool = False
    plasticity_modulation: bool = True
    lr_schedule_type: str = "exponential"
    lr_decay_rate: float = 0.95
    lr_min: float = 1e-6
    lr_max: float = 0.1
    pruning_threshold: float = 0.01
    growth_threshold: float = 0.8
    max_connections_per_neuron: int = 100
    temperature_compensation: bool = False
    noise_adaptation: bool = False
    power_scaling: bool = False

@dataclass
class NeuromorphicConfig:
    """Enhanced configuration for neuromorphic hardware compatibility."""
    platform: NeuromorphicPlatform = NeuromorphicPlatform.SIMULATION
    dt: float = 0.001
    v_threshold: float = 1.0
    v_reset: float = 0.0
    v_rest: float = 0.0
    tau_mem: float = 0.01
    tau_syn: float = 0.005
    refractory_period: float = 0.002
    neuron_type: NeuronType = NeuronType.LIF
    v_spike: float = 1.0
    tau_adaptation: float = 0.1
    adaptation_strength: float = 0.1
    noise_amplitude: float = 0.0
    izhikevich_a: float = 0.02
    izhikevich_b: float = 0.2
    izhikevich_c: float = -65.0
    izhikevich_d: float = 2.0
    num_compartments: int = 1
    compartment_coupling: float = 0.1
    dendritic_delay: float = 0.001
    encoding_window: float = 0.1
    max_spike_rate: float = 1000.0
    temporal_resolution: float = 0.0001
    generation: int = 3
    enable_multi_compartment: bool = False
    enable_adaptive_threshold: bool = True
    enable_burst_firing: bool = False
    enable_stochastic_dynamics: bool = False
    enable_calcium_dynamics: bool = False
    enable_ion_channels: bool = False
    plasticity_rules: list[PlasticityRule] = field(default_factory=list)
    enable_stdp: bool = True
    enable_metaplasticity: bool = False
    enable_homeostatic_scaling: bool = True
    enable_structural_plasticity: bool = False
    real_time_adaptation: RealTimeAdaptationConfig = field(default_factory=RealTimeAdaptationConfig)
    enable_hierarchical_structure: bool = False
    enable_dynamic_connectivity: bool = True
    num_hierarchy_levels: int = 3
    connectivity_density: float = 0.1
    enable_temporal_patterns: bool = True
    enable_phase_encoding: bool = False
    enable_oscillatory_dynamics: bool = False
    enable_sparse_coding: bool = True
    enable_population_coding: bool = False
    enable_gamma_oscillations: bool = False
    enable_theta_rhythms: bool = False
    enable_delta_waves: bool = False
    enable_alpha_oscillations: bool = False
    enable_beta_oscillations: bool = False
    oscillation_frequency: float = 40.0
    phase_coupling_strength: float = 0.1
    delta_frequency: float = 2.0
    theta_frequency: float = 6.0
    alpha_frequency: float = 10.0
    beta_frequency: float = 20.0
    gamma_frequency: float = 40.0
    bit_precision: int = 16
    device: str = "cpu"
    quantization_levels: int = 256
    enable_analog_compute: bool = False
    enable_in_memory_compute: bool = False
    energy_per_spike: float = 1e-12
    synaptic_delay_mean: float = 0.001
    synaptic_delay_std: float = 0.0005
    axonal_delay_mean: float = 0.002
    axonal_delay_std: float = 0.001
    memristor_conductance_min: float = 1e-6
    memristor_conductance_max: float = 1e-3
    memristor_retention_time: float = 100.0
    memristor_switching_energy: float = 1e-15
    input_data_type: str | None = None
    expected_input_rate: float | None = None
    input_sparsity: float | None = None
    enable_performance_monitoring: bool = True
    enable_energy_monitoring: bool = False
    enable_spike_monitoring: bool = False
    monitoring_resolution: float = 0.01
    max_processing_latency: float | None = None
    real_time_factor: float = 1.0
    enable_fault_tolerance: bool = False
    redundancy_factor: int = 1
    error_correction: bool = False
    _auto_configure_phase_encoding: bool = True
    _parameter_history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.plasticity_rules and self.enable_stdp:
            self.plasticity_rules.append(
                PlasticityRule(rule_type=PlasticityType.STDP, learning_rate=0.01, adaptive_learning_rate=True)
            )
        if self.enable_homeostatic_scaling:
            self.plasticity_rules.append(
                PlasticityRule(rule_type=PlasticityType.HOMEOSTATIC, learning_rate=0.001, target_rate=10.0)
            )
        self._configure_platform_specifics()
        if self._auto_configure_phase_encoding:
            self._configure_phase_encoding()
        self._log_parameter_state("initialization")

    def _configure_platform_specifics(self):
        platform_configs = {
            NeuromorphicPlatform.LOIHI2: {'bit_precision': 8, 'enable_in_memory_compute': True, 'max_spike_rate': 1000.0, 'energy_per_spike': 23e-12},
            NeuromorphicPlatform.SPINNAKER2: {'bit_precision': 16, 'enable_analog_compute': False, 'max_spike_rate': 10000.0, 'energy_per_spike': 45e-12},
            NeuromorphicPlatform.MEMRISTIVE_CROSSBAR: {'bit_precision': 4, 'enable_analog_compute': True, 'enable_in_memory_compute': True, 'energy_per_spike': 0.1e-12},
            NeuromorphicPlatform.PHOTONIC_SNN: {'bit_precision': 32, 'enable_analog_compute': True, 'max_spike_rate': 100000.0, 'energy_per_spike': 0.01e-12, 'temporal_resolution': 1e-6}
        }
        if self.platform in platform_configs:
            config = platform_configs[self.platform]
            for param, value in config.items():
                if hasattr(self, param):
                    setattr(self, param, value)
            logger.info(f"Applied {self.platform.value} specific configuration")

    def _configure_phase_encoding(self):
        if self.platform in [NeuromorphicPlatform.PHOTONIC_SNN, NeuromorphicPlatform.LOIHI2]:
            self.enable_phase_encoding = True
            self.enable_oscillatory_dynamics = True
            self.enable_gamma_oscillations = True
            self.enable_alpha_oscillations = True
            self.enable_beta_oscillations = True
            if self.generation >= 4:
                self.enable_theta_rhythms = True
                self.enable_delta_waves = True
        if self.generation >= 3:
            self.enable_alpha_oscillations = True
            self.enable_beta_oscillations = True
            self.enable_gamma_oscillations = True
            if self.generation >= 4:
                self.enable_theta_rhythms = True
                self.enable_delta_waves = True

    def _log_parameter_state(self, event: str):
        state = {
            'timestamp': time.time(),
            'event': event,
            'dt': self.dt,
            'v_threshold': self.v_threshold,
            'tau_mem': self.tau_mem,
            'learning_rates': [rule.learning_rate for rule in self.plasticity_rules],
            'platform': self.platform.value
        }
        self._parameter_history.append(state)
        if len(self._parameter_history) > 1000:
            self._parameter_history = self._parameter_history[-1000:]
