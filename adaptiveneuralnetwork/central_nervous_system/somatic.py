"""
Virtual Microbiome and Somatic System logic for Phase 7.4.
Simulates the "Gut-Brain Axis" and its influence on cognitive thresholds.
"""

from typing import Any

import torch
import torch.nn as nn


class VirtualMicrobiome(nn.Module):
    """
    Simulates a population of virtual 'bacteria' that respond to 
    system stress and energy consumption.
    """  # noqa: W291
    def __init__(self, size: int = 100):
        super().__init__()
        self.size = size
        # Bacterial population health (0.0 to 1.0)
        self.register_buffer('health', torch.ones(1))
        # Metabolic waste accumulation
        self.register_buffer('metabolic_waste', torch.zeros(1))

    def update(self, energy_consumption: float, is_sleeping: bool):
        # Stress (from high consumption) reduces health
        # Threshold lowered to 0.2 to match per-node mean drain during stress
        if energy_consumption > 0.2:
            self.health -= 0.01
            self.metabolic_waste += 0.05
        else:
            # Slow recovery
            self.health += 0.005

        # Waste clearance is handled by Glial cells, but here we add accumulation
        self.health = torch.clamp(self.health, 0.1, 1.0)
        self.metabolic_waste = torch.clamp(self.metabolic_waste, 0.0, 10.0)

    def get_hormone_signals(self) -> dict[str, float]:
        """
        Calculates hormone levels based on microbiome state.
        - Serotonin: Produced by healthy microbiome (promotes calm/trust)
        - Cortisol: Produced by stressed microbiome (promotes anxiety/focus)
        """
        serotonin = self.health.item() * 0.8
        cortisol = self.metabolic_waste.item() * 0.1
        return {'serotonin': serotonin, 'cortisol': cortisol}

class SomaticSystem(nn.Module):
    """
    The Somatic Manager bridging physiology and emotional thresholds.
    """
    def __init__(self):
        super().__init__()
        self.microbiome = VirtualMicrobiome()

    def step(self,
             energy_consumption: float,
             avg_phase: int) -> dict[str, Any]:

        is_sleeping = (avg_phase == 1) # Phase.SLEEP

        self.microbiome.update(energy_consumption, is_sleeping)

        # Dynamic Anxiety Threshold Modulation (The Gut-Brain Link)
        # Base threshold is 6.0
        hormones = self.microbiome.get_hormone_signals()

        # Serotonin raises threshold (more resilient)
        # Cortisol lowers threshold (more sensitive)
        anxiety_threshold = 6.0 + (hormones['serotonin'] * 2.0) - (hormones['cortisol'] * 4.0)

        return {
            'anxiety_threshold': max(2.0, anxiety_threshold),
            'hormones': hormones,
            'waste': self.microbiome.metabolic_waste.item(),
            'microbiome_health': self.microbiome.health.item()
        }
