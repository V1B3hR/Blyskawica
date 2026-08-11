"""
Forgetting Manager for Adaptive Neural Network.

Implements biologically-inspired controlled forgetting and synaptic pruning.
"""

import logging
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class ForgettingManager:
    """
    Manages controlled forgetting and structural pruning.
    """

    def __init__(
        self,
        model: nn.Module,
        pruning_ratio: float = 0.05,
        downscale_factor: float = 0.9,
        importance_metric: str = 'magnitude'
    ):
        self.model = model
        self.pruning_ratio = pruning_ratio
        self.downscale_factor = downscale_factor
        self.importance_metric = importance_metric

        self.forgetting_stats: dict[str, Any] = {
            'total_pruned': 0,
            'total_downscaled': 0,
            'last_forgetting_event': 0
        }

    def sleep_dependent_forgetting(self, micro_phases: torch.Tensor):
        """Apply forgetting logic during DEEP_SLEEP."""
        # Deep sleep is phase index 5
        deep_sleep_mask = (micro_phases == 5)

        if deep_sleep_mask.any():
            deep_sleep_ratio = deep_sleep_mask.float().mean().item()

            if deep_sleep_ratio > 0.1:
                self.downscale_synapses(intensity=deep_sleep_ratio)

                if deep_sleep_ratio > 0.5:
                    self.prune_low_importance(ratio=self.pruning_ratio * (deep_sleep_ratio * 2))

    def downscale_synapses(self, intensity: float = 1.0):
        factor = 1.0 - (1.0 - self.downscale_factor) * intensity
        with torch.no_grad():
            for param in self.model.parameters():
                if param.requires_grad:
                    param.data.mul_(factor)
        self.forgetting_stats['total_downscaled'] += 1

    def prune_low_importance(self, ratio: float | None = None):
        ratio = ratio or self.pruning_ratio
        if ratio <= 0:
            return

        with torch.no_grad():
            for name, module in self.model.named_modules():  # noqa: B007
                if isinstance(module, (nn.Linear, nn.Conv2d)):
                    self._prune_module(module, ratio)
        self.forgetting_stats['total_pruned'] += 1

    def _prune_module(self, module: nn.Module, ratio: float):
        if not hasattr(module, 'weight'):
            return
        weight = module.weight.data
        importance = torch.abs(weight)
        flat_importance = importance.view(-1)
        k = int(ratio * flat_importance.numel())
        if k > 0:
            threshold = torch.topk(flat_importance, k, largest=False).values.max()
            mask = importance > threshold
            module.weight.data.mul_(mask.float())

    def get_stats(self) -> dict[str, Any]:
        return self.forgetting_stats
