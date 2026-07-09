"""
Time Management System for Adaptive Neural Network

Provides centralized time management to separate simulation time from real-world time,
addressing the issue of mixed time representations throughout the codebase.
"""

import time
from dataclasses import dataclass
from typing import Any
from enum import Enum
from collections import deque


class ProcessingLane(Enum):
    FAST_AI = "fast_ai"      # AI <-> AI communication, high speed, internal processing
    SLOW_HUMAN = "slow_human" # AI <-> Human communication, buffered, paced

@dataclass
class TimeConfig:
    """Configuration for time management"""
    simulation_time_scale: float = 1.0  # How fast simulation time progresses relative to real time
    circadian_cycle_hours: int = 24     # Length of circadian cycle in simulation hours
    enable_real_time_tracking: bool = True  # Whether to track real time for performance metrics
    
    # Bi-dynamic Adaptation parameters
    fast_lane_multiplier: float = 100.0   # Scale multiplier when operating in FAST_AI lane
    slow_lane_multiplier: float = 1.0     # Scale multiplier for SLOW_HUMAN lane
    human_interaction_timeout: float = 300.0 # Seconds before reverting to FAST_AI if human is inactive



class TimeManager:
    """
    Centralized time management system that separates simulation time from real time.
    
    This addresses the problem where the system mixed discrete simulation steps 
    with real wall-clock time, making it difficult to:
    - Run simulations at different speeds
    - Have reproducible timing behavior  
    - Properly separate simulation logic from performance measurement
    """

    def __init__(self, config: TimeConfig | None = None):
        self.config = config or TimeConfig()

        # Simulation time tracking
        self._simulation_step: int = 0
        self._simulation_start_real_time: float = time.time()

        # Real time tracking for performance metrics
        self._performance_start_time: float | None = None
        self._last_tick_real_time: float = time.time()

        # Statistics
        self._tick_count: int = 0
        self._total_real_time: float = 0.0

        # Bi-dynamic Adaptation state
        self._current_lane: ProcessingLane = ProcessingLane.FAST_AI
        self._last_human_interaction_time: float = time.time()
        self._human_output_buffer: deque = deque(maxlen=100) # Buffer for AI->Human messages

    @property
    def simulation_step(self) -> int:
        """Current simulation step (discrete integer time)"""
        return self._simulation_step

    @property
    def circadian_time(self) -> int:
        """Current time in circadian cycle (0-23 hours)"""
        return self._simulation_step % self.config.circadian_cycle_hours

    @property
    def real_time(self) -> float:
        """Current real wall-clock time"""
        return time.time()

    @property
    def simulation_elapsed_real_time(self) -> float:
        """Real time elapsed since simulation started"""
        return time.time() - self._simulation_start_real_time

    def advance_simulation(self, steps: int = 1) -> None:
        """Advance simulation time by the specified number of steps"""
        self._simulation_step += steps
        self._tick_count += steps

    # --- Bi-dynamic Adaptation Methods ---
    def switch_lane(self, lane: ProcessingLane) -> None:
        """Switch the processing lane (bandwidth)"""
        self._current_lane = lane
        if lane == ProcessingLane.SLOW_HUMAN:
            self._last_human_interaction_time = time.time()
            self.config.simulation_time_scale = self.config.slow_lane_multiplier
        else:
            self.config.simulation_time_scale = self.config.fast_lane_multiplier

    def register_human_interaction(self) -> None:
        """Called when user interacts, switches to SLOW_HUMAN lane temporarily"""
        self.switch_lane(ProcessingLane.SLOW_HUMAN)

    def auto_adjust_lane(self) -> None:
        """Revert to FAST_AI if human hasn't interacted for a while"""
        if self._current_lane == ProcessingLane.SLOW_HUMAN:
            if time.time() - self._last_human_interaction_time > self.config.human_interaction_timeout:
                self.switch_lane(ProcessingLane.FAST_AI)

    def buffer_human_output(self, data: Any) -> None:
        """Buffer data meant for the human so it doesn't overwhelm the slow lane"""
        self._human_output_buffer.append({"timestamp": self.real_time, "data": data})

    def get_buffered_human_output(self) -> list[Any]:
        """Retrieve buffered output for human consumption"""
        outputs = list(self._human_output_buffer)
        self._human_output_buffer.clear()
        return outputs
    # -------------------------------------

    def start_performance_measurement(self) -> None:
        """Start measuring performance for the current operation"""
        if self.config.enable_real_time_tracking:
            self._performance_start_time = time.perf_counter()

    def end_performance_measurement(self) -> float:
        """End performance measurement and return duration in seconds"""
        if not self.config.enable_real_time_tracking or self._performance_start_time is None:
            return 0.0

        duration = time.perf_counter() - self._performance_start_time
        self._total_real_time += duration
        self._performance_start_time = None
        return duration

    def get_timestamp(self) -> float:
        """Get a timestamp for logging/tracking purposes"""
        return time.time()

    def network_tick(self) -> None:
        """Called when the network performs a tick - advances simulation and tracks performance"""
        current_real_time = time.time()
        tick_duration = current_real_time - self._last_tick_real_time
        self._last_tick_real_time = current_real_time

        # Advance simulation time based on configured scale
        # Adjust scale dynamically based on the active lane
        self.auto_adjust_lane()
        
        steps_to_advance = max(1, int(tick_duration * self.config.simulation_time_scale))
        self.advance_simulation(steps_to_advance)

    def get_statistics(self) -> dict[str, Any]:
        """Get timing statistics"""
        avg_real_time_per_tick = (
            self._total_real_time / self._tick_count if self._tick_count > 0 else 0.0
        )

        return {
            "simulation_step": self._simulation_step,
            "circadian_time": self.circadian_time,
            "tick_count": self._tick_count,
            "total_real_time": self._total_real_time,
            "avg_real_time_per_tick": avg_real_time_per_tick,
            "simulation_elapsed_real_time": self.simulation_elapsed_real_time,
            "simulation_time_scale": self.config.simulation_time_scale,
            "current_lane": self._current_lane.value,
        }

    def reset(self) -> None:
        """Reset all time tracking"""
        self._simulation_step = 0
        self._simulation_start_real_time = time.time()
        self._performance_start_time = None
        self._last_tick_real_time = time.time()
        self._tick_count = 0
        self._total_real_time = 0.0


# Global time manager instance for backward compatibility
_global_time_manager: TimeManager | None = None


def get_time_manager() -> TimeManager:
    """Get the global time manager instance"""
    global _global_time_manager
    if _global_time_manager is None:
        _global_time_manager = TimeManager()
    return _global_time_manager


def set_time_manager(time_manager: TimeManager) -> None:
    """Set the global time manager instance"""
    global _global_time_manager
    _global_time_manager = time_manager


# Convenience functions for common operations
def get_simulation_time() -> int:
    """Get current simulation step"""
    return get_time_manager().simulation_step


def get_circadian_time() -> int:
    """Get current circadian time (0-23)"""
    return get_time_manager().circadian_time


def get_timestamp() -> float:
    """Get a real-time timestamp"""
    return get_time_manager().get_timestamp()


def advance_time(steps: int = 1) -> None:
    """Advance simulation time"""
    get_time_manager().advance_simulation(steps)
