"""
Cognitive Fluidity and Dynamic Resource Management for 4th generation neuromorphic AI.

This module implements mechanisms for shifting computational resources, 
modulating network sparsity, and adapting processing depth based on 
metacognitive load and task difficulty.
"""  # noqa: W291

import logging
from typing import Any

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

class CognitiveMonitor(nn.Module):
    """
    Monitors internal dynamics to estimate 'Cognitive Load'.
    
    Combines:
    - Activity Sparsity (High sparsity = Low load)
    - Gradient Variance (High variance = High load/uncertainty)
    - Metacognitive Discordance (Mismatch between predicted and actual rates)
    """  # noqa: W293
    def __init__(self, history_size: int = 100):
        super().__init__()
        self.register_buffer('load_history', torch.zeros(history_size))
        self.register_buffer('history_index', torch.tensor(0, dtype=torch.long))

    def estimate_load(self,
                      activity: torch.Tensor,
                      performance_signal: torch.Tensor | None = None,
                      energy_consumption: torch.Tensor | None = None) -> torch.Tensor:
        """
        Estimate the current cognitive load.
        Load = (1 - Sparsity) * sqrt(Entropy) modulated by energy.
        """
        sparsity = (activity < 1e-4).float().mean()

        # Approximate entropy from activity distribution
        flattened = activity.flatten()
        prob = torch.clamp(flattened, 1e-6, 1.0)
        entropy = -torch.sum(prob * torch.log(prob)) / flattened.size(0)

        load = (1.0 - sparsity) * torch.sqrt(entropy + 1e-6)

        if performance_signal is not None:
             # High error increases load perception (stress response)
             load = load * (1.0 + performance_signal.mean())

        # Update history
        idx = self.history_index % self.load_history.size(0)
        self.load_history[idx] = load
        self.history_index += 1

        return load

class DynamicResourceAllocator(nn.Module):
    """
    Adjusts network parameters to manage cognitive load.
    
    Tactics:
    - Increase Sparsity: Clamp more neurons to zero.
    - Modulate Gain: Reduce firing sensitivity.
    - Path Pruning: Bypass certain layers/modules if load is too high (metabolic protection).
    """  # noqa: W293
    def __init__(self, num_subnetworks: int = 1):
        super().__init__()
        self.num_subnetworks = num_subnetworks
        # Dynamic gating probabilities for subnetworks
        self.gate_probs = nn.Parameter(torch.ones(num_subnetworks))

    def allocate(self, current_load: torch.Tensor, metabolic_state: float = 1.0) -> dict[str, Any]:
        """
        Produce modulatory signals based on load.
        """
        # If load is high, increase sparsity and decrease gain
        # If load is low, expand capacity (reduce sparsity)

        target_sparsity_base = 0.05
        # Load-dependent sparsity scale
        dynamic_sparsity = target_sparsity_base * (1.0 + current_load.item() * 5.0)
        dynamic_sparsity = np.clip(dynamic_sparsity, 0.01, 0.5)

        # Gain modulation (Attention narrowing)
        # High load -> Narrow focus (high gains on few, low on others)
        gain_modulation = 1.0 / (1.0 + current_load.item())

        # Metabolic gating: Disable subnetworks if resources are critical
        metabolic_gate = 1.0 if metabolic_state > 0.3 else 0.0

        return {
            'sparsity_threshold': dynamic_sparsity,
            'gain_scale': gain_modulation,
            'metabolic_gate': metabolic_gate,
            'attention_width': 1.0 / (1.0 + current_load.item() * 2.0)
        }

class CognitiveFluiditySystem(nn.Module):
    """
    Integrated system for cognitive fluidity.
    Bridges the monitor with the allocator.
    """
    def __init__(self, num_layers: int):
        super().__init__()
        self.monitor = CognitiveMonitor()
        self.allocator = DynamicResourceAllocator(num_subnetworks=num_layers)

    def step(self,
             activity: torch.Tensor,
             performance: torch.Tensor | None = None) -> dict[str, Any]:

        load = self.monitor.estimate_load(activity, performance)
        controls = self.allocator.allocate(load)

        logger.debug(f"Cognitive Fluidity Step - Load: {load.item():.4f}, Sparsity: {controls['sparsity_threshold']:.4f}")

        return {
            'load': load,
            'controls': controls
        }
