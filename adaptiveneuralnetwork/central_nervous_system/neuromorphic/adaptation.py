"""
Environmental and real-time parameter adaptation for the neuromorphic substrate.
Integrates with DeviceManager for local hardware telemetry.
Part of the modular Purity Refactor.
"""

import logging
import time
from collections import defaultdict, deque

import numpy as np

from ..device_manager import device_manager
from .config import NeuromorphicConfig

logger = logging.getLogger(__name__)

class EnvironmentalAdaptationEngine:
    """
    Optimizes neuromorphic parameters based on environmental and hardware constraints.
    Enables Błyskawica to adapt to local PC thermal and power states.
    """

    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.adaptation_config = config.real_time_adaptation
        self.history = defaultdict(lambda: deque(maxlen=1000))

    def adapt(self) -> dict[str, float]:
        """Perform comprehensive adaptation based on local hardware state."""
        telemetry = device_manager.get_telemetry()
        adaptations = {}

        # Noise adaptation based on CPU stress
        if self.adaptation_config.noise_adaptation:
            cpu_usage = telemetry['cpu_usage']
            # Scale neuromorphic noise floor based on system jitter (proxied by CPU usage)
            adaptations['noise_amplitude'] = self.config.noise_amplitude + (cpu_usage / 1000.0)

        # Power scaling (Battery/Power state proxy)
        if self.adaptation_config.power_scaling:
            ram_usage = telemetry['ram_usage']
            if ram_usage > 85.0:
                # High memory pressure: reduce bit precision or spike rate
                adaptations['max_spike_rate'] = self.config.max_spike_rate * 0.8
                logger.warning("[ADAPTATION] High RAM pressure detected. Throttling spike rate.")

        # Apply adaptations to config
        if adaptations:
            self.config._log_parameter_state("hardware_adaptation")
            for k, v in adaptations.items():
                if hasattr(self.config, k):
                    setattr(self.config, k, v)

        return adaptations


class RealTimeParameterManager:
    """
    Manages dynamic parameter shifts during execution based on performance metrics.
    """

    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.performance_history = deque(maxlen=1000)
        self.last_update = time.time()

    def update_performance(self, accuracy: float):
        self.performance_history.append(accuracy)

    def step(self):
        """Perform routine parameter maintenance."""
        now = time.time()
        if now - self.last_update < self.config.real_time_adaptation.update_frequency:
            return

        if not self.performance_history:
            return

        avg_perf = np.mean(list(self.performance_history)[-10:])

        # Adaptive Learning Rate scaling based on performance
        if avg_perf < self.config.real_time_adaptation.performance_threshold:
            # Performance dip: increase learning exploration
            for rule in self.config.plasticity_rules:
                if rule.adaptive_learning_rate:
                    rule.learning_rate = min(rule.learning_rate * 1.05, rule.max_learning_rate)

        self.last_update = now
