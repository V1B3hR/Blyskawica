"""
High-level hierarchy for neuromorphic adaptive models.
Provides a standard API wrapper for hierarchical spike-based networks.
"""

import logging
from typing import Any, Dict, Optional, Tuple, Union

import torch
import torch.nn as nn

from .config import NeuromorphicConfig
from .network_topology import HierarchicalNetwork, TopologyConfig
from .dynamics import BrainWaveOscillator, NeuromodulationSystem

logger = logging.getLogger(__name__)

class NeuromorphicAdaptiveModel(nn.Module):
    """
    High-level adaptive model specifically for neuromorphic backends.
    Wraps a HierarchicalNetwork to provide a standard interface for training and inference.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dim: int = 64,
        config: Optional[NeuromorphicConfig] = None
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
        self.config = config or NeuromorphicConfig()

        # Build topology config based on dimensions
        topology_config = TopologyConfig(
            num_layers=3,
            layer_sizes=[hidden_dim, hidden_dim // 2, output_dim],
            device=self.config.device
        )

        # Initialize the hierarchical substrate
        self.network = HierarchicalNetwork(topology_config)
        
        # Add components for test suite/compatibility
        self.neuromodulation = NeuromodulationSystem(self.config)
        self.oscillator = BrainWaveOscillator(self.config)
        
        logger.info(f"Initialized NeuromorphicAdaptiveModel ({input_dim} -> {hidden_dim} -> {output_dim})")

    def forward(
        self,
        x: torch.Tensor,
        current_time: Union[float, Dict[str, Any]] = 0.0,
        dt: float = 0.001
    ) -> torch.Tensor:
        """
        Standard forward pass for spike-based processing.
        
        Args:
            x: Input tensor [batch_size, input_dim]
            current_time: Current simulation time, or dict of environmental_data
            dt: Time step
            
        Returns:
            Output spikes tensor
        """
        # Check if current_time is actually environmental_data dict
        if isinstance(current_time, dict):
            environmental_data = current_time
            stress_level = environmental_data.get('stress_level', 0.0)
            stressor_type = environmental_data.get('stressor_type', 'general')
            self.neuromodulation.update_stress_level(stress_level, stressor_type)
            current_time = 0.0

        # Ensure input is on correct device
        x = x.to(self.config.device)
        
        # Process through hierarchical network
        output, states = self.network(x, current_time=current_time, dt=dt)
        
        return output

    def get_neuromorphic_state(self) -> Dict[str, Any]:
        """Export current neuromorphic health metrics and activities."""
        return self.network.export_network_statistics()
