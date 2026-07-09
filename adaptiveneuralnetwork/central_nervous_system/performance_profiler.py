"""
Performance Profiler: Hardware-Aware Diagnostics.
Measures latency, throughput, memory overhead, and metabolic efficiency.
"""

import torch
import torch.nn as nn
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PerformanceProfiler:
    """
    Profiles the computational and energetic efficiency of the neural network.
    """
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.latency_history: List[float] = []
        self.throughput_history: List[float] = []
        self.energy_per_pulse: List[float] = []
        
        # Hardware context
        self.is_cuda = 'cuda' in device
        
    def start_pulse(self) -> float:
        """Starts timing a conscious pulse."""
        if self.is_cuda:
            torch.cuda.synchronize()
        return time.perf_counter()

    def end_pulse(self, start_time: float, batch_size: int, node_state: Any):
        """Ends timing and calculates metrics."""
        if self.is_cuda:
            torch.cuda.synchronize()
        
        end_time = time.perf_counter()
        latency = (end_time - start_time) * 1000 # ms
        throughput = batch_size / (end_time - start_time) # thoughts/sec
        
        # Energy Approximation (Hardware dependent)
        # EpJ = sum(abs(activations)) * voltage_surrogate
        activity = getattr(node_state, 'activity', torch.zeros(1, device=self.device))
        if not isinstance(activity, torch.Tensor):
            activity = torch.tensor(activity, device=self.device)
            
        energy = torch.sum(torch.abs(activity)).item() * 0.01 
        
        self.latency_history.append(latency)
        self.throughput_history.append(throughput)
        self.energy_per_pulse.append(energy)
        
        if len(self.latency_history) % 100 == 0:
            self._log_performance(latency, throughput, energy)

    def _log_performance(self, latency: float, throughput: float, energy: float):
        """Logs real-time performance stats."""
        mem_used = 0
        if self.is_cuda:
            mem_used = torch.cuda.max_memory_allocated() / (1024 ** 2) # MB
            
        logger.info(f"Performance Profile - Latency: {latency:.2f}ms | Throughput: {throughput:.1f} CT/s | Energy: {energy:.4f} J | GPU Mem: {mem_used:.1f}MB")

    def get_readiness_report(self) -> Dict[str, Any]:
        """Generates a summary for the deep audit."""
        if not self.latency_history:
            return {}
            
        avg_latency = sum(self.latency_history) / len(self.latency_history)
        avg_throughput = sum(self.throughput_history) / len(self.throughput_history)
        avg_energy = sum(self.energy_per_pulse) / len(self.energy_per_pulse)
        
        # Readiness factor: Stable latency (< 20ms) and High efficiency
        latency_factor = max(0.0, 1.0 - (avg_latency / 50.0))
        efficiency_factor = max(0.0, 1.0 - (avg_energy / 10.0))
        
        return {
            'avg_latency_ms': avg_latency,
            'avg_throughput_cts': avg_throughput,
            'avg_energy_joules': avg_energy,
            'performance_readiness': (latency_factor + efficiency_factor) / 2.0
        }

    def reset(self):
        """Clears history for a new audit run."""
        self.latency_history = []
        self.throughput_history = []
        self.energy_per_pulse = []
        if self.is_cuda:
            torch.cuda.reset_peak_memory_stats()
