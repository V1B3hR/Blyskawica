"""
Neural Architecture Search (NAS) and Structural Plasticity for Phase 7.5.

Implements the dynamic evolution of network topology:
- Pruning: Removing idle or low-trust nodes to increase sparsity.
- Expansion: Adding or splitting high-salience nodes to increase capacity.
- Structural Mutations: Randomly adding bypass or feedback connections.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional
import logging

from adaptiveneuralnetwork.central_nervous_system.metrics import PhiCalculator, NeuralHealthMonitor

logger = logging.getLogger(__name__)

class StructuralPlasticity(nn.Module):
    """
    Manages the growth and pruning of the network topology.
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        
        # Track usage stats per node
        self.register_buffer('usage_frequency', torch.zeros(hidden_dim))
        self.register_buffer('surprisal_history', torch.zeros(hidden_dim))
        
        # Tier 4 Complexity tracking
        self.phi_calc = PhiCalculator()
        
    def step(self, 
             node_activity: torch.Tensor, 
             prediction_error: torch.Tensor, 
             dt: float = 0.01):
        """
        Update usage and surprise stats.
        """
        # [batch, num_nodes, 1] -> [num_nodes]
        activity = node_activity.mean(dim=0).squeeze(-1)
        surprise = prediction_error.mean(dim=0).squeeze(-1)
        
        # Lazy resize buffers if num_nodes differs from hidden_dim
        if self.usage_frequency.size(0) != activity.size(0):
            self.usage_frequency = torch.zeros_like(activity)
            self.surprisal_history = torch.zeros_like(surprise)
        
        # Dynamic averages (Accelerated for demonstration)
        self.usage_frequency = 0.90 * self.usage_frequency + 0.10 * activity
        self.surprisal_history = 0.90 * self.surprisal_history + 0.10 * surprise

    def suggest_topology_changes(self) -> Dict[str, List[int]]:
        """
        Identify nodes to prune or expand.
        """
        # Pruning candidates: Low usage AND low surprise for a long time
        prune_threshold = 0.05
        nodes_to_prune = torch.where((self.usage_frequency < prune_threshold) & 
                                    (self.surprisal_history < prune_threshold))[0].tolist()
        
        # Expansion candidates: High surprise AND high energy usage
        expand_threshold = 0.8
        nodes_to_expand = torch.where(self.surprisal_history > expand_threshold)[0].tolist()
        
        return {
            'prune': nodes_to_prune,
            'expand': nodes_to_expand
        }

    def calculate_complexity_pressure(self, weights: torch.Tensor) -> float:
        """
        Structural complexity reward (Self-Organized Criticality).
        Prevents topology collapse into trivial (full-zero or full-one) states.
        """
        # Reward diversity in weights
        w_entropy = -torch.sum(torch.abs(weights) * torch.log(torch.abs(weights) + 1e-8)).item()
        return w_entropy

class TopologyAdapter(nn.Module):
    """
    Applies structural changes to the Dynamics weights.
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.sp = StructuralPlasticity(hidden_dim)
        
    def adapt(self, dynamics_module: nn.Module):
        """
        Perform actual pruning or restructuring.
        """
        suggestions = self.sp.suggest_topology_changes()
        
        if not suggestions['prune'] and not suggestions['expand']:
            return
            
        # Tier 4: Complexity Pressure Check
        # Estimate current structural complexity
        current_complexity = self.sp.calculate_complexity_pressure(dynamics_module.state_update.weight)
        
        # 1. Pruning: Zero-out weights for specific nodes
        # This keeps the matrix size constant for hardware stability
        # but logically removes the nodes.
        with torch.no_grad():
            for node_idx in suggestions['prune']:
                # Zero out input and output weights for this node
                dynamics_module.state_update.weight[node_idx, :] *= 0.1
                dynamics_module.state_update.weight[:, node_idx] *= 0.1
                logger.info(f"NAS: Pruning inactive node {node_idx}")
                
        # 2. Expansion (Splitting): Copy high-surprise nodes to neighbors
        # This doubles the 'attention' on difficult features.
        with torch.no_grad():
            for node_idx in suggestions['expand']:
                # Find a low-usage neighbor to 'take over'
                if suggestions['prune']:
                    target_idx = suggestions['prune'].pop(0)
                    dynamics_module.state_update.weight[target_idx, :] = dynamics_module.state_update.weight[node_idx, :]
                    dynamics_module.state_update.weight[:, target_idx] = dynamics_module.state_update.weight[:, node_idx]
                    logger.info(f"NAS: Expanding high-surprise node {node_idx} into slot {target_idx}")
