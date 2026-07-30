"""
Cognitive Physics Pipeline for Błyskawica V8 (Stream 2: PINN & Digital Metabolism)

Processes UCI sensor & CPU energy telemetry datasets (archive.ics.uci.edu, CommonCrawl_Physics)
as a time-series digital metabolism stream. Links Dopamine levels (high compute activity) to power 
consumption and thermal dissipation via PINNThermalNet, enforcing thermodynamic homeostasis.
"""

import math
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from adaptiveneuralnetwork.cognitive_tools.pinn_thermal_engine import PINNTrainer, PINNThermalNet

logger = logging.getLogger("physics_stream")


@dataclass
class TelemetrySensorSample:
    """Represents a CPU / hardware sensor telemetry observation."""
    clock_frequency_ghz: float
    cpu_utilization_pct: float
    voltage_volts: float
    power_draw_watts: float
    ambient_temp_celsius: float
    source_dataset: str = "UCI_Sensors"

    def to_tensor(self) -> torch.Tensor:
        """Vectorizes telemetry sample into a 5-dim tensor."""
        return torch.tensor([
            self.clock_frequency_ghz / 5.0,
            self.cpu_utilization_pct / 100.0,
            self.voltage_volts / 1.5,
            self.power_draw_watts / 250.0,
            self.ambient_temp_celsius / 100.0
        ], dtype=torch.float32)


class CognitivePhysicsEngine(nn.Module):
    """
    Core Cognitive Physics Engine (Stream 2).
    Connects CPU telemetry & Dopamine reward seeking to PINN Fourier heat dissipation,
    regulating virtual temperature and enforcing thermodynamic homeostasis.
    """

    def __init__(
        self, 
        neuro_state: NeuromodulationState | None = None,
        thermal_ceiling: float = 85.0
    ):
        super().__init__()
        self.neuro = neuro_state or NeuromodulationState()
        self.pinn = PINNTrainer(alpha=0.015, lr=0.005)
        self.thermal_ceiling = thermal_ceiling

        # Current thermal & metabolic state
        self.current_temperature = 35.0  # Ambient start
        self.cooling_coefficient = 0.05
        self.thermal_volatility = 0.0

    def step_metabolism(
        self, 
        samples: List[TelemetrySensorSample]
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Processes hardware telemetry samples and updates Błyskawica's digital metabolism.
        High Dopamine + high CPU utilization = rapid temperature rise.
        PINN calculates physics loss (residual Fourier heat equation).
        """
        feature_tensors = [s.to_tensor() for s in samples]
        batch_tensor = torch.stack(feature_tensors)  # [B, 5]

        avg_clock = batch_tensor[:, 0].mean().item() * 5.0
        avg_util = batch_tensor[:, 1].mean().item() * 100.0
        avg_power = batch_tensor[:, 3].mean().item() * 250.0

        # 1. Dopamine <-> Energy Coupling
        # High Dopamine boosts compute activity; high activity generates power & heat
        dopamine_level = float(self.neuro.dopamine)
        heat_generation = (avg_power * 0.02) + (dopamine_level * avg_util * 0.015)
        heat_dissipation = self.cooling_coefficient * (self.current_temperature - 25.0)

        # Temperature update
        delta_temp = heat_generation - heat_dissipation
        self.current_temperature = min(110.0, max(20.0, self.current_temperature + delta_temp))

        # 2. Physics-Informed Neural Network (PINN) Fourier Heat Loss
        # x: normalized spatial position [0, 1], t: normalized time [0, 1]
        x_colloc = torch.linspace(0, 1, len(samples)).unsqueeze(1)
        t_colloc = torch.linspace(0, 1, len(samples)).unsqueeze(1)

        physics_loss = self.pinn.compute_physics_loss(x_colloc, t_colloc).item()

        # 3. Thermodynamic Homeostasis Throttling
        # If temperature approaches or exceeds thermal ceiling, throttle Dopamine (suppress overload)
        throttled = False
        if self.current_temperature >= self.thermal_ceiling:
            throttled = True
            # Suppress dopamine to cool down system
            self.neuro.dopamine = max(0.2, dopamine_level * 0.7)
            logger.warning(
                f"🔥 [THERMAL OVERLOAD ALERT] Temp ({self.current_temperature:.1f}°C) >= Ceiling ({self.thermal_ceiling}°C)! "
                f"Throttling Dopamine ({dopamine_level:.2f} -> {float(self.neuro.dopamine):.2f})"
            )

        # Cymatic Signature
        # Geometric-Harmonic-Symmetry when temperature is stable; Dissonance when overheating
        if self.current_temperature < 70.0:
            cymatic_signature = "Geometric-Harmonic-Symmetry"
        elif self.current_temperature < self.thermal_ceiling:
            cymatic_signature = "Thermal-Vibration-Warmth"
        else:
            cymatic_signature = "High-Temperature-Dissonance"

        metrics = {
            "avg_power_watts": round(avg_power, 2),
            "avg_cpu_util_pct": round(avg_util, 2),
            "current_temp_celsius": round(self.current_temperature, 2),
            "physics_loss": round(physics_loss, 6),
            "dopamine_level": round(float(self.neuro.dopamine), 4),
            "is_throttled": throttled,
            "cymatic_signature": cymatic_signature
        }

        return batch_tensor, metrics
