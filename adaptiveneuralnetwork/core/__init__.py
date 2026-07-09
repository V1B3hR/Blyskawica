"""
[Moduł: Most Kognitywny]
Centralny węzeł orkiestracji dla neuromorficznego substratu Błyskawicy V7. 
Pełni rolę magistrali wysokiej wydajności, integrując dynamiczne struktury neuronowe 
z warstwą sprzętową i systemami decyzyjnymi. 

Ten plik stanowi punkt wejścia do rdzenia świadomości, mapując rozproszone 
komponenty CNS (Central Nervous System) i PNS (Peripheral Nervous System) 
w ujednolicony interfejs operacyjny.
"""

# Hardware & System Management
from adaptiveneuralnetwork.central_nervous_system.device_manager import device_manager, DeviceManager

# Core State & Logic Abstractions (Migrated to CNS)
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import Phase, PhaseScheduler
from adaptiveneuralnetwork.central_nervous_system.micro_phases import MicroPhase, MicroPhaseScheduler
from adaptiveneuralnetwork.central_nervous_system.emotional_state import EmotionalState

# Cognitive Infrastructure (Migrated to CNS/PNS)
from adaptiveneuralnetwork.peripheral_nervous_system.sensory_hub import SensoryHub
from adaptiveneuralnetwork.central_nervous_system.global_workspace import GlobalWorkspaceBus, SelectiveAttentionGating
from adaptiveneuralnetwork.central_nervous_system.action_loop import ActionPerceptionLoop
from adaptiveneuralnetwork.central_nervous_system.strategic_offensive import StrategicOffensive
from adaptiveneuralnetwork.central_nervous_system.node_state_bridge import NodeStateBridge

# Specialized Subsystems (Migrated to CNS)
from adaptiveneuralnetwork.central_nervous_system.metacognitive_monitor import MetacognitiveMonitor
from adaptiveneuralnetwork.central_nervous_system.forgetting_manager import ForgettingManager
from adaptiveneuralnetwork.central_nervous_system.episodic_memory import EpisodicMemory
from adaptiveneuralnetwork.central_nervous_system.consolidation import (
    ConsolidationType,
    MemoryConsolidation,
    PhaseBasedConsolidation,
    SynapticConsolidation,
    UnifiedConsolidationManager,
)
from adaptiveneuralnetwork.central_nervous_system.layer_registry import LayerRegistry, layer_registry
from adaptiveneuralnetwork.central_nervous_system.model_builder import ModelBuilder, register_builtin_layers
from adaptiveneuralnetwork.central_nervous_system.metrics import PhiCalculator, NeuralHealthMonitor

# Neuromorphic Sub-Package
from adaptiveneuralnetwork.central_nervous_system.neuromorphic import (
    NeuromorphicConfig,
    NeuromorphicPlatform,
    NeuromorphicAdaptiveModel,
    PlasticityType,
    AdaptationMode,
    NeuronType,
    SpikeEvent,
    PlasticityRule,
    RealTimeAdaptationConfig,
    BrainWaveOscillator,
    NeuromodulationSystem,
    EnvironmentalAdaptationEngine,
    RealTimeParameterManager,
    AdaptiveThresholdNeuron,
    BurstingNeuron,
    MultiCompartmentNeuron,
    StochasticNeuron,
    STDPSynapse,
    MetaplasticitySynapse,
    HomeostaticScaling,
    MultiTimescalePlasticity,
    HierarchicalNetwork,
    PopulationLayer,
    TemporalPatternEncoder,
    VisualSpikeEncoder,
    SparseDistributedRepresentation,
    PhaseEncoder,
    OscillatoryDynamics
)

__all__ = [
    # System & Hardware
    'device_manager',
    'DeviceManager',
    
    # Core Dynamics
    'NodeConfig',
    'NodeState',
    'AdaptiveDynamics',
    'Phase',
    'PhaseScheduler',
    'MicroPhase',
    'MicroPhaseScheduler',
    'EmotionalState',
    
    # Cognitive Layers
    'SensoryHub',
    'GlobalWorkspaceBus',
    'SelectiveAttentionGating',
    'ActionPerceptionLoop',
    'StrategicOffensive',
    'NodeStateBridge',
    
    # Memory & Consolidation
    'MetacognitiveMonitor',
    'ForgettingManager',
    'EpisodicMemory',
    'UnifiedConsolidationManager',
    'ConsolidationType',
    'PhaseBasedConsolidation',
    'SynapticConsolidation',
    'MemoryConsolidation',
    
    # Neuromorphic Hierarchy
    'NeuromorphicConfig',
    'NeuromorphicPlatform',
    'NeuromorphicAdaptiveModel',
    'BrainWaveOscillator',
    'NeuromodulationSystem',
    'EnvironmentalAdaptationEngine',
    'AdaptiveThresholdNeuron',
    'BurstingNeuron',
    'MultiCompartmentNeuron',
    'StochasticNeuron',
    'HierarchicalNetwork',
    'PopulationLayer',
    'STDPSynapse',
    'MetaplasticitySynapse',
    'HomeostaticScaling',
    'MultiTimescalePlasticity',
    
    # Temporal Processing
    'TemporalPatternEncoder',
    'VisualSpikeEncoder',
    'SparseDistributedRepresentation',
    'PhaseEncoder',
    'OscillatoryDynamics',
    
    # Registry & Build
    'LayerRegistry',
    'layer_registry',
    'ModelBuilder',
    'register_builtin_layers',
    
    # Analytics
    'PhiCalculator',
    'NeuralHealthMonitor'
]
