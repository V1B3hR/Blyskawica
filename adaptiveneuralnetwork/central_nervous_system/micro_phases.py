"""
Micro-Phase Scheduler for Adaptive Neural Network.

Handles fine-grained subconscious rhythms (sub-phases) within 
major phases (Active, Sleep, etc.).
"""

import torch
import torch.nn as nn
from enum import Enum
from typing import Dict, Any

class MicroPhase(Enum):
    # ACTIVE sub-phases
    FOCUSED = 0
    EXPLORATORY = 1
    # SLEEP sub-phases
    LIGHT_SLEEP = 3
    REM = 4
    DEEP_SLEEP = 5
    MEMORY_REPLAY = 6
    # INTERACTIVE / INSPIRED
    SOCIAL_FOCUS = 7
    CREATIVE_FLOW = 8

MICRO_PHASE_PARAMS = {
    MicroPhase.FOCUSED: {"lr_scale": 1.0, "attention_width": 1.0},
    MicroPhase.EXPLORATORY: {"lr_scale": 1.2, "attention_width": 2.0},
    MicroPhase.REM: {"lr_scale": 0.8, "replay_intensity": 1.0},
    MicroPhase.DEEP_SLEEP: {"lr_scale": 0.1, "pruning_threshold": 0.5},
}

class MicroPhaseScheduler(nn.Module):
    """
    Manages Tier 1 (granular) phase transitions for individual nodes.
    """
    def __init__(self, num_nodes: int, device: str = 'cpu'):
        super().__init__()
        self.num_nodes = num_nodes
        self.device = torch.device(device)
        
        # Buffer for current node micro-phases
        self.register_buffer("node_phases", torch.zeros(num_nodes, dtype=torch.long))
        self.register_buffer("phase_timer", torch.zeros(num_nodes))
        
    def step(self, major_phase: int = 0, *args, **kwargs):
        """Update micro-phases based on major phase context (polymorphic)."""
        major_phase_val = major_phase
        if 'major_phases' in kwargs:
            major_phase_val = kwargs['major_phases']
            
        if hasattr(major_phase_val, "dim") and major_phase_val.dim() > 0:
            major_phase_val = int(major_phase_val.view(-1)[0].item())
        else:
            try:
                major_phase_val = int(major_phase_val)
            except (TypeError, ValueError):
                major_phase_val = 0

        # Biologically inspired transitions
        with torch.no_grad():
            self.phase_timer += 1.0
            
            # Simple heuristic: change micro-phase every 50 steps
            change_mask = (self.phase_timer >= 50.0)
            
            if change_mask.any():
                if major_phase_val == 0:  # ACTIVE
                    new_phases = torch.randint(0, 2, (change_mask.sum().item(),), device=self.device)
                elif major_phase_val == 1:  # SLEEP
                    new_phases = torch.randint(3, 7, (change_mask.sum().item(),), device=self.device)
                else:
                    new_phases = torch.zeros(change_mask.sum().item(), dtype=torch.long, device=self.device)
                
                self.node_phases[change_mask] = new_phases
                self.phase_timer[change_mask] = 0.0
                
        return self.node_phases

    def reset(self) -> None:
        """Reset the micro-phase scheduler to initial state."""
        self.node_phases.zero_()
        self.phase_timer.zero_()

    def get_micro_phase_distribution(self) -> Dict[str, float]:
        """Get the distribution of micro-phases across nodes."""
        dist = {}
        for phase in MicroPhase:
            count = (self.node_phases == phase.value).sum().item()
            dist[phase.name] = float(count)
        return dist

    def get_sleep_cycle_stats(self) -> Dict[str, float]:
        """Get sleep cycle stats (e.g. ratios, transition times)."""
        total = float(self.num_nodes) if self.num_nodes > 0 else 1.0
        rem_count = (self.node_phases == MicroPhase.REM.value).sum().item()
        deep_count = (self.node_phases == MicroPhase.DEEP_SLEEP.value).sum().item()
        light_count = (self.node_phases == MicroPhase.LIGHT_SLEEP.value).sum().item()
        
        return {
            "rem_ratio": rem_count / total,
            "deep_sleep_ratio": deep_count / total,
            "light_sleep_ratio": light_count / total,
            "mean_timer": self.phase_timer.mean().item()
        }
