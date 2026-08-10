"""
Node State Bridge for Adaptive Neural Network.

Bridges the gap between biological node states and tensor-based ML processing.
"""

from typing import Any

import torch


class NodeStateBridge:
    def __init__(self, device: str = 'cpu'):
        self.device = torch.device(device)

    def bridge_state(self, node_state: Any) -> dict[str, torch.Tensor]:
        """Convert biological node state objects/tensors into modulatory signals."""

        # Unified State Extraction (Handles both objects and dictionaries)
        energy = None
        activity = None

        if hasattr(node_state, 'energy'):
            energy = getattr(node_state, 'energy', 10.0)
            activity = getattr(node_state, 'activity', 1.0)
        elif isinstance(node_state, dict):
            energy = node_state.get('energy', 10.0)
            activity = node_state.get('activity') or node_state.get('focus') or 1.0

        # Ensure they are tensors on the correct device
        if energy is not None:
            energy = torch.as_tensor(energy, device=self.device)
            activity = torch.as_tensor(activity, device=self.device)

        if energy is not None:
            # Heuristic: gradient scale = f(energy, activity)
            # High energy nodes learn faster (scale > 1.0)
            grad_scale = torch.clamp(energy / 10.0, 0.1, 2.0) if energy.numel() > 0 else torch.tensor(1.0)

            # Heuristic: Focus = f(activity, anxiety)
            focus = activity
            resilience = torch.ones_like(energy)
            anxiety = torch.zeros_like(energy)

            return {
                'gradient_scale': grad_scale,
                'focus': focus,
                'resilience': resilience,
                'anxiety': anxiety
            }

        return {}
