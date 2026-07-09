"""
Callback interface for training loop extensibility.

This module provides a flexible callback system that allows hooking into
different stages of the training process without modifying core training logic.
"""

import time
import logging
from abc import ABC
from typing import Any

import torch

logger = logging.getLogger(__name__)


class Callback(ABC):
    """
    Base class for training callbacks.
    
    Callbacks provide hooks at key points in the training lifecycle:
    - on_train_begin/end: Called at start/end of training
    - on_epoch_begin/end: Called at start/end of each epoch
    - on_batch_begin/end: Called at start/end of each batch
    - on_backward_end: Called after backward pass
    - on_evaluate_begin/end: Called at start/end of evaluation
    """

    def on_train_begin(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the beginning of training."""
        pass

    def on_train_end(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the end of training."""
        pass

    def on_epoch_begin(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the beginning of each epoch."""
        pass

    def on_epoch_end(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the end of each epoch."""
        pass

    def on_batch_begin(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the beginning of each batch."""
        pass

    def on_batch_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the end of each batch."""
        pass

    def on_backward_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called after the backward pass."""
        pass

    def on_evaluate_begin(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the beginning of evaluation."""
        pass

    def on_evaluate_end(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Called at the end of evaluation."""
        pass


class LoggingCallback(Callback):
    """
    Callback for logging training metrics.
    
    Logs throughput (samples/sec, batches/sec), loss, and accuracy at
    configurable intervals.
    """

    def __init__(self, log_interval: int = 10, verbose: bool = True):
        """
        Initialize logging callback.
        
        Args:
            log_interval: Log every N batches
            verbose: Print logs to console
        """
        self.log_interval = log_interval
        self.verbose = verbose
        self.epoch_start_time = None
        self.batch_start_time = None
        self.epoch_metrics = {}
        self.batch_count = 0
        self.sample_count = 0

    def on_epoch_begin(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Initialize epoch timing."""
        self.epoch_start_time = time.time()
        self.batch_count = 0
        self.sample_count = 0
        self.epoch_metrics = {}

        if self.verbose:
            logger.info(f"{'='*60}")
            logger.info(f"Epoch {epoch + 1}/{trainer.num_epochs}")
            logger.info(f"{'='*60}")

    def on_batch_begin(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Initialize batch timing."""
        self.batch_start_time = time.time()

    def on_batch_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Log batch metrics."""
        self.batch_count += 1
        batch_size = logs.get('batch_size', 0) if logs else 0
        self.sample_count += batch_size

        # Log at specified intervals
        if self.verbose and batch_idx % self.log_interval == 0:
            batch_time = time.time() - self.batch_start_time if self.batch_start_time else 0
            loss = logs.get('loss', 0) if logs else 0
            accuracy = logs.get('accuracy', 0) if logs else 0

            samples_per_sec = batch_size / batch_time if batch_time > 0 else 0

            logger.info(f"Batch {batch_idx:4d} | "
                        f"Loss: {loss:.4f} | "
                        f"Acc: {accuracy:.2%} | "
                        f"Throughput: {samples_per_sec:.1f} samples/s")

    def on_epoch_end(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Log epoch summary."""
        epoch_time = time.time() - self.epoch_start_time if self.epoch_start_time else 0

        if self.verbose and logs:
            train_loss = logs.get('train_loss', 0)
            train_acc = logs.get('train_accuracy', 0)
            val_loss = logs.get('val_loss', None)
            val_acc = logs.get('val_accuracy', None)

            samples_per_sec = self.sample_count / epoch_time if epoch_time > 0 else 0
            batches_per_sec = self.batch_count / epoch_time if epoch_time > 0 else 0

            logger.info(f"{'-'*60}")
            logger.info(f"Epoch {epoch + 1} Summary:")
            logger.info(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2%}")
            if val_loss is not None and val_acc is not None:
                logger.info(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2%}")
            logger.info(f"  Time: {epoch_time:.2f}s | "
                        f"Throughput: {samples_per_sec:.1f} samples/s, {batches_per_sec:.2f} batches/s")
            logger.info(f"{'-'*60}")


class ProfilingCallback(Callback):
    """
    Callback for profiling training performance.
    
    Tracks timing, memory usage, and computational metrics for performance
    analysis and optimization.
    """

    def __init__(self, profile_memory: bool = True, profile_cuda: bool = True):
        """
        Initialize profiling callback.
        
        Args:
            profile_memory: Track memory usage
            profile_cuda: Profile CUDA operations (if available)
        """
        self.profile_memory = profile_memory
        self.profile_cuda = profile_cuda and torch.cuda.is_available()

        self.metrics = {
            'epoch_times': [],
            'batch_times': [],
            'forward_times': [],
            'backward_times': [],
            'optimizer_times': [],
        }

        if self.profile_memory:
            self.metrics['memory_allocated'] = []
            self.metrics['memory_reserved'] = []

        self.epoch_start_time = None
        self.batch_start_time = None
        self.forward_start_time = None
        self.backward_start_time = None

    def on_epoch_begin(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Start epoch profiling."""
        self.epoch_start_time = time.time()

        if self.profile_cuda:
            torch.cuda.synchronize()

    def on_batch_begin(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Start batch profiling."""
        self.batch_start_time = time.time()

        if self.profile_cuda:
            torch.cuda.synchronize()

    def on_batch_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Record batch profiling metrics."""
        if self.batch_start_time:
            batch_time = time.time() - self.batch_start_time
            self.metrics['batch_times'].append(batch_time)

        if self.profile_memory and self.profile_cuda:
            allocated = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
            reserved = torch.cuda.memory_reserved() / (1024 ** 2)  # MB
            self.metrics['memory_allocated'].append(allocated)
            self.metrics['memory_reserved'].append(reserved)

    def on_epoch_end(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Record epoch profiling metrics."""
        if self.epoch_start_time:
            epoch_time = time.time() - self.epoch_start_time
            self.metrics['epoch_times'].append(epoch_time)

    def on_train_end(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Print profiling summary."""
        import numpy as np

        print("\n" + "="*60)
        print("Profiling Summary")
        print("="*60)

        if self.metrics['epoch_times']:
            epoch_times = self.metrics['epoch_times']
            print(f"Epoch Times: mean={np.mean(epoch_times):.3f}s, "
                  f"std={np.std(epoch_times):.3f}s, "
                  f"min={np.min(epoch_times):.3f}s, "
                  f"max={np.max(epoch_times):.3f}s")

        if self.metrics['batch_times']:
            batch_times = self.metrics['batch_times']
            print(f"Batch Times: mean={np.mean(batch_times)*1000:.2f}ms, "
                  f"std={np.std(batch_times)*1000:.2f}ms")

        if self.profile_memory and self.metrics['memory_allocated']:
            mem_alloc = self.metrics['memory_allocated']
            print(f"GPU Memory Allocated: mean={np.mean(mem_alloc):.1f}MB, "
                  f"max={np.max(mem_alloc):.1f}MB")

        print("="*60 + "\n")

    def get_metrics(self) -> dict[str, Any]:
        """Get collected profiling metrics."""
        return self.metrics.copy()


class CallbackList:
    """
    Container for managing multiple callbacks.
    
    Ensures callbacks are called in the correct order and handles errors gracefully.
    """

    def __init__(self, callbacks: list[Callback] | None = None):
        """
        Initialize callback list.
        
        Args:
            callbacks: List of callback instances
        """
        self.callbacks = callbacks or []

    def append(self, callback: Callback) -> None:
        """Add a callback to the list."""
        self.callbacks.append(callback)

    def on_train_begin(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_train_begin for all callbacks."""
        for callback in self.callbacks:
            callback.on_train_begin(trainer, logs)

    def on_train_end(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_train_end for all callbacks."""
        for callback in self.callbacks:
            callback.on_train_end(trainer, logs)

    def on_epoch_begin(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_epoch_begin for all callbacks."""
        for callback in self.callbacks:
            callback.on_epoch_begin(epoch, trainer, logs)

    def on_epoch_end(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_epoch_end for all callbacks."""
        for callback in self.callbacks:
            callback.on_epoch_end(epoch, trainer, logs)

    def on_batch_begin(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_batch_begin for all callbacks."""
        for callback in self.callbacks:
            callback.on_batch_begin(batch_idx, trainer, logs)

    def on_batch_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_batch_end for all callbacks."""
        for callback in self.callbacks:
            callback.on_batch_end(batch_idx, trainer, logs)

    def on_backward_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_backward_end for all callbacks."""
        for callback in self.callbacks:
            callback.on_backward_end(batch_idx, trainer, logs)

    def on_evaluate_begin(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_evaluate_begin for all callbacks."""
        for callback in self.callbacks:
            callback.on_evaluate_begin(trainer, logs)

    def on_evaluate_end(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Call on_evaluate_end for all callbacks."""
        for callback in self.callbacks:
            callback.on_evaluate_end(trainer, logs)


class CognitiveHygieneCallback(Callback):
    """
    Automated Cognitive Hygiene for Błyskawica.
    Coordinates showers, bedding changes, and morning warm-ups.

    Sleep sub-phase awareness
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    The callback reads ``trainer.model.phase_scheduler.node_sub_phases`` to
    determine the dominant sub-phase and passes it to ``pre_sleep_routine``
    so that pre-REM transitions get only a gentle rinse (preserving optimizer
    momentum for memory consolidation replay).
    """

    def __init__(self, warm_up_steps: int = 500, device: str = "cpu"):
        self.hygiene = None  # Initialized on train begin
        self.warm_up_steps = warm_up_steps
        self.device = device
        self.last_phase = 0   # ACTIVE
        self.last_sub_phase = "none"  # Tracks sub-phase at sleep entry

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _dominant_sub_phase(trainer: Any) -> str:
        """
        Return the most common sleep sub-phase name among sleeping nodes.
        Falls back to ``'deep'`` when sub-phase info is unavailable.
        """
        try:
            scheduler = trainer.model.phase_scheduler
            sub_phases = scheduler.node_sub_phases  # [num_nodes] LongTensor
            # 0=NONE, 1=LIGHT, 2=REM, 3=DEEP  (SubPhase enum order)
            counts = [(sub_phases == v).sum().item() for v in range(4)]
            dominant = int(max(range(4), key=lambda i: counts[i]))
            return {0: "none", 1: "light", 2: "rem", 3: "deep"}.get(dominant, "deep")
        except AttributeError:
            return "deep"

    # ------------------------------------------------------------------
    # Callback hooks
    # ------------------------------------------------------------------

    def on_train_begin(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import CognitiveHygieneProtocol
        self.hygiene = CognitiveHygieneProtocol(trainer.optimizer, device=self.device)
        self.hygiene.target_warmup_steps = self.warm_up_steps
        # Initial post-sleep routine (Waking up for training)
        self.hygiene.post_sleep_routine(trainer)

    def on_batch_begin(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        if self.hygiene is None:
            return

        # Check for phase transitions (Sleep <-> Active)
        if hasattr(trainer.model, 'phase_scheduler'):
            # SLEEP = 1, ACTIVE = 0
            current_phase = trainer.model.phase_scheduler.node_phases.float().mean().item()
            current_phase_rounded = round(current_phase)

            # Transition: SLEEP -> ACTIVE (Waking up)
            if self.last_phase == 1 and current_phase_rounded == 0:
                from_rem = (self.last_sub_phase == "rem")
                self.hygiene.post_sleep_routine(trainer, from_rem=from_rem)

            # Transition: ACTIVE -> SLEEP (Going to bed)
            elif self.last_phase == 0 and current_phase_rounded == 1:
                sub_phase = self._dominant_sub_phase(trainer)
                self.last_sub_phase = sub_phase
                self.hygiene.pre_sleep_routine(trainer.model, sleep_sub_phase=sub_phase)

            self.last_phase = current_phase_rounded

        # Handle LR warm-up
        self.hygiene.step_warmup(trainer)

    def on_epoch_end(self, epoch: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """End-of-epoch hygiene: light cleanse after each full day of training."""
        if self.hygiene is not None:
            self.hygiene.shower.cleanse(trainer.model)


class NeuromodulationCallback(Callback):
    """
    Bio-inspired Neuromodulation for Błyskawica.
    Dynamically adjusts learning parameters based on energy, neurochemistry, and trust.
    """

    def __init__(self, base_lr: float | None = None):
        self.base_lr = base_lr
        self.last_energy = 1.0
        self.dopamine_threshold = 0.5

    def on_train_begin(self, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        if self.base_lr is None:
            self.base_lr = trainer.optimizer.param_groups[0]['lr']

    def on_batch_begin(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        if not hasattr(trainer.model, 'nodes'):
            return

        # 1. Energy-based Modulation
        # If energy is low, we reduce learning rate to avoid "noisy" updates during exhaustion
        energy = trainer.model.nodes.energy
        capacity = getattr(trainer.model.nodes, 'energy_capacity', 10.0)
        energy_ratio = energy / capacity
        
        # 2. Neurochemical Modulation (Dopamine/Cortisol)
        dopamine = 1.0
        cortisol = 0.0
        if hasattr(trainer.model.nodes, 'neurochemistry'):
            dopamine = trainer.model.nodes.neurochemistry.dopamine
            cortisol = trainer.model.nodes.neurochemistry.cortisol

        # 3. Calculate Modulation Factor
        # High dopamine = High plasticity (exploration)
        # High cortisol = Low plasticity (stress/defense)
        # Low energy = Very low plasticity (preservation)
        modulation = (energy_ratio ** 0.5) * (1.0 + dopamine * 0.5) / (1.0 + cortisol * 0.3)
        
        # Clamp modulation to safe ranges
        modulation = max(0.01, min(2.0, modulation))
        
        # Apply to optimizer
        new_lr = self.base_lr * modulation
        for group in trainer.optimizer.param_groups:
            group['lr'] = new_lr

        if batch_idx % 20 == 0:
            trainer.model.nodes.emotional_state['arousal'] = 0.5 + (dopamine * 0.5) - (cortisol * 0.2)

    def on_batch_end(self, batch_idx: int, trainer: Any, logs: dict[str, Any] | None = None) -> None:
        """Update neurochemistry based on results (Success/Failure)"""
        if not hasattr(trainer.model, 'nodes') or logs is None:
            return
            
        loss = logs.get('loss', 1.0)
        
        # If loss is low (success), trigger small dopamine release
        if loss < 0.1:
            if hasattr(trainer.model.nodes.neurochemistry, 'trigger_dopamine_spike'):
                trainer.model.nodes.neurochemistry.trigger_dopamine_spike(0.05)
        
        # If loss is very high (failure/surprise), trigger cortisol
        elif loss > 2.0:
            if hasattr(trainer.model.nodes.neurochemistry, 'trigger_cortisol_spike'):
                trainer.model.nodes.neurochemistry.trigger_cortisol_spike(0.02)

