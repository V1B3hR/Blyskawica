"""
3rd Generation Neuromorphic Computing Implementation.

This module provides advanced neuromorphic computing capabilities including:
- Multi-compartment neurons with dendritic processing
- Advanced synaptic plasticity (STDP, metaplasticity)
- Hierarchical network structures
- Temporal pattern encoding
- Hardware backend abstractions for 3rd generation platforms
"""

from .adaptation import EnvironmentalAdaptationEngine, RealTimeParameterManager
from .advanced_neurons import (
    AdaptiveThresholdNeuron,
    BurstingNeuron,
    MultiCompartmentNeuron,
    StochasticNeuron,
)
from .config import (
    AdaptationMode,
    NeuromorphicConfig,
    NeuromorphicPlatform,
    NeuronType,
    PlasticityRule,
    PlasticityType,
    RealTimeAdaptationConfig,
    SpikeEvent,
)
from .dynamics import BrainWaveOscillator, NeuromodulationSystem
from .hierarchy import NeuromorphicAdaptiveModel
from .lava_compiler import LavaCompiler
from .network_topology import (
    DynamicConnectivity,
    HierarchicalNetwork,
    PopulationLayer,
    RealisticDelays,
)
from .plasticity import (
    HomeostaticScaling,
    MetaplasticitySynapse,
    MultiTimescalePlasticity,
    STDPSynapse,
)
from .temporal_coding import (
    OscillatoryDynamics,
    PhaseEncoder,
    SparseDistributedRepresentation,
    TemporalPatternEncoder,
    VisualSpikeEncoder,
)

__all__ = [
    # Configuration & Enums
    'NeuromorphicPlatform',
    'PlasticityType',
    'AdaptationMode',
    'NeuronType',
    'SpikeEvent',
    'PlasticityRule',
    'RealTimeAdaptationConfig',
    'NeuromorphicConfig',
    'LavaCompiler',

    # Brain Dynamics
    'BrainWaveOscillator',
    'NeuromodulationSystem',

    # Real-time Adaptation
    'EnvironmentalAdaptationEngine',
    'RealTimeParameterManager',

    # Advanced neurons
    'MultiCompartmentNeuron',
    'AdaptiveThresholdNeuron',
    'BurstingNeuron',
    'StochasticNeuron',

    # Plasticity mechanisms
    'STDPSynapse',
    'MetaplasticitySynapse',
    'HomeostaticScaling',
    'MultiTimescalePlasticity',

    # Network topology
    'HierarchicalNetwork',
    'DynamicConnectivity',
    'PopulationLayer',
    'RealisticDelays',
    'TemporalPatternEncoder',
    'VisualSpikeEncoder',
    'SparseDistributedRepresentation',
    'PhaseEncoder',
    'OscillatoryDynamics',
]
