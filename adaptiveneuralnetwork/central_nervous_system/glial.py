"""
Glial Cell Simulation for Phase 7.5.

Implements non-neuronal support cells that optimize the network substrate:
- Astrocytes: Nutrient/Energy redistribution and homeostatic regulation.
- Microglia: Metabolic waste clearance and neuro-inflammation (anxiety) management.
- Oligodendrocytes: Myelination of frequently used high-trust pathways.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional
import logging

from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator

logger = logging.getLogger(__name__)

class GlialSystem(nn.Module):
    """
    The support infrastructure for the neural network, managing waste, 
    energy, and structural optimization.
    """
    def __init__(self, num_nodes: int):
        super().__init__()
        self.num_nodes = num_nodes
        
        # Myelination levels [num_nodes, num_nodes]
        # (Simplified: per-node efficiency for now)
        self.register_buffer('myelination_levels', torch.ones(num_nodes))
        
        # Glial activity state
        self.register_buffer('astrocyte_buffer', torch.zeros(num_nodes))

        # Ground Loop Isolation prevents astrocyte buffer from accumulating
        # chronic DC-drift inhibition (sustained suppression of healthy nodes).
        self._gli = GroundLoopIsolator(isolation_ratio=0.04)

    def step_astrocytes(self, energy: torch.Tensor, dt: float = 0.01):
        """
        Energy redistribution. Astrocytes move nutrients from high-energy 
        areas to low-energy starving nodes.
        """
        energy_flat = energy.flatten()
        mean_energy = energy_flat.mean()
        
        # Starving nodes (Energy < 2.0)
        starving_mask = energy_flat < 2.0
        # Rich nodes (Energy > 8.0)
        rich_mask = energy_flat > 8.0
        
        if starving_mask.any() and rich_mask.any():
            # Calculate total deficit
            deficit = (2.0 - energy_flat[starving_mask]).sum()
            surplus = (energy_flat[rich_mask] - 8.0).sum()
            
            # Transfer amount (bounded by surplus)
            transfer = min(deficit, surplus) * 0.5 * dt
            
            # Take from rich
            energy_flat[rich_mask] -= (transfer / rich_mask.sum().float())
            # Give to starving
            energy_flat[starving_mask] += (transfer / starving_mask.sum().float())
            
        return energy_flat.reshape(energy.shape)

    def step_microglia(self, metabolic_waste: torch.Tensor, is_sleeping: bool, dt: float = 0.01):
        """
        Waste clearance. Microglia clear toxins (metabolic waste). 
        Clearing is significantly faster during SLEEP.
        """
        # Base clearance rate
        clearance_rate = 0.1 * dt
        
        # 3x acceleration during sleep (The Glymphatic System)
        if is_sleeping:
            clearance_rate *= 3.0
            
        new_waste = metabolic_waste * (1.0 - clearance_rate)
        return torch.clamp(new_waste, min=0.0)

    def step_stabilization(self, activity: torch.Tensor, anxiety: torch.Tensor, dt: float = 0.01):
        """
        Substrate stabilization. Prevents neural saturation (burnout).
        If nodes are over-active and anxious, astrocytes force a dampening factor.
        GLI shunts astrocyte_buffer DC-drift so healthy nodes aren't chronically suppressed.
        """
        saturation_risk = (activity.squeeze(-1) > 0.9) & (anxiety.squeeze(-1) > 3.0)
        
        # Apply inhibition to saturated nodes
        if saturation_risk.any():
            self.astrocyte_buffer[saturation_risk] += 0.5 * dt
        else:
            self.astrocyte_buffer *= (1.0 - 0.1 * dt) # Slowly clear buffer

        # Apply GLI to the buffer to shunt low-level DC drift accumulation.
        # This prevents the slow-clear rate from becoming a permanent suppression baseline.
        self.astrocyte_buffer = self._gli(self.astrocyte_buffer).clamp(0.0, 1.0)
            
        # Returns health_gain factor [1.0 (Healthy) -> 0.5 (Suppressed)]
        return torch.clamp(1.0 - self.astrocyte_buffer, 0.5, 1.0)

    def step_oligodendrocytes(self, trust_matrix: Optional[torch.Tensor], dt: float = 0.01):
        """
        Myelination. Frequently used, high-trust pathways get 'insulated', 
        becoming more stable and faster.
        """
        if trust_matrix is None:
            return self.myelination_levels
            
        # Average trust for each node
        avg_trust = trust_matrix.mean(dim=0)
        
        # Myelination increases for high trust nodes
        myelin_delta = (avg_trust - 0.7) * 0.1 * dt
        
        # Settlement Task 5: Cross-Modal Synergy
        # Accelerated myelination for nodes involved in sensory integration
        # (Heuristic: High-activity nodes during multi-modal grounding)
        self.myelination_levels = torch.clamp(self.myelination_levels + myelin_delta, 1.0, 2.5)
        
        return self.myelination_levels

    def step_sensory_support(self, energy: torch.Tensor, sensory_load: float, dt: float = 0.01):
        """
        Settlement Task 6: Metabolic Shifting.
        Prioritizes energy delivery to nodes during extreme sensory throughput.
        """
        if sensory_load > 0.7:
            # Force energy boost for sensory cluster [Assuming nodes 0:50 are sensory-rich]
            energy[:, :50] += 0.2 * sensory_load * dt
        return energy

class GlialManager(nn.Module):
    """
    Orchestrator for glial interventions.
    """
    def __init__(self, num_nodes: int):
        super().__init__()
        self.glial = GlialSystem(num_nodes)
        
    def manage(self, node_state, somatic_system, social_context, current_phase: int):
        # 1. Astrocyte energy management
        node_state.energy = self.glial.step_astrocytes(node_state.energy)
        
        # 2. Microglia waste management
        is_sleeping = (current_phase == 1) # Phase.SLEEP
        somatic_system.microbiome.metabolic_waste = self.glial.step_microglia(
            somatic_system.microbiome.metabolic_waste, 
            is_sleeping
        )
        
        # 3. Oligodendrocyte myelination (structural stability)
        trust_matrix = social_context.trust_matrix if social_context is not None else None
        myelination = self.glial.step_oligodendrocytes(trust_matrix)
        
        # 4. Astrocyte Stabilization (Tier 4 Health)
        health_gain = self.glial.step_stabilization(node_state.activity, node_state.anxiety)
        
        # 5. Settlement Task 6: Metabolic Energy Shift
        # Identify sensory load from current batch (passed via node_state or metrics)
        sensory_load = getattr(node_state, 'sensory_load', 0.5)
        node_state.energy = self.glial.step_sensory_support(node_state.energy, sensory_load)

        # 6. Recovery Boost (Bravery-based metabolism)
        # Braver nodes recover energy faster during sleep/rest
        if hasattr(node_state, 'bravery'):
            # Ensure bravery_bonus can broadcast to [batch, nodes, 1]
            # bravery is likely [1, nodes, 1]
            b_val = node_state.bravery
            if b_val.dim() == 3:
                # [1, nodes, 1] broadcasts to [batch, nodes, 1]
                node_state.energy += b_val * 0.1
            else:
                # Fallback for alternative shapes
                bonus = b_val.view(1, -1, 1) if b_val.dim() < 3 else b_val
                node_state.energy += bonus * 0.1
        
        return {
            'myelination': myelination.mean().item(),
            'health_gain': health_gain.mean().item(),
            'waste_cleared': not is_sleeping
        }
