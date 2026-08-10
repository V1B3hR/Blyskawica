"""
Episodic Memory System for Adaptive Neural Network.

Implements a GPU-accelerated experience buffer for short-term 
experience replay and dream-state consolidation.
"""  # noqa: W291


import torch
import torch.nn as nn


class EpisodicMemory(nn.Module):
    """
    GPU-accelerated Episodic Memory buffer.
    
    Stores recent experiences (input, target, emotional_context)
    and allows for prioritized replay during sleep phases.
    """  # noqa: W293

    def __init__(
        self,
        memory_size: int = 50000,
        feature_size: int = 128,
        device: str = 'cpu'
    ):
        super().__init__()
        self.memory_size = memory_size
        self.feature_size = feature_size
        self.device = torch.device(device)

        # Buffers for persistence on GPU
        self.register_buffer("observations", torch.zeros(memory_size, feature_size))
        self.register_buffer("targets", torch.zeros(memory_size, dtype=torch.long))
        self.register_buffer("importance", torch.ones(memory_size))

        # Self-Context tags [memory_size, feature_size]
        self.register_buffer("self_contexts", torch.zeros(memory_size, feature_size))

        self.ptr = 0
        self.is_full = False

    def store(self,
              obs: torch.Tensor,
              target: torch.Tensor,
              importance: torch.Tensor | None = None,
              self_context: torch.Tensor | None = None):
        """Store a batch of experiences."""
        batch_size = obs.size(0)

        # handle potential wrap-around
        indices = torch.arange(self.ptr, self.ptr + batch_size) % self.memory_size

        self.observations[indices] = obs.detach().to(self.device).view(batch_size, -1)
        self.targets[indices] = target.detach().to(self.device)

        if importance is not None:
            self.importance[indices] = importance.detach().to(self.device)
        else:
            self.importance[indices] = 1.0

        if self_context is not None:
            self.self_contexts[indices] = self_context.detach().to(self.device).view(batch_size, -1)

        self.ptr = (self.ptr + batch_size) % self.memory_size
        if self.ptr < batch_size:
            self.is_full = True

    def sample(self, batch_size: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Sample a batch of memories using importance weighting."""
        max_idx = self.memory_size if self.is_full else self.ptr
        if max_idx == 0:
            return torch.empty(0), torch.empty(0), torch.empty(0)

        # Prioritized sampling
        probs = self.importance[:max_idx] / self.importance[:max_idx].sum()
        indices = torch.multinomial(probs, min(batch_size, max_idx), replacement=True)

        return (
            self.observations[indices],
            self.targets[indices],
            self.importance[indices],
            self.self_contexts[indices]
        )

    def consolidate(self, top_k: int = 1000):
        """
        Retain only the most important memories.
        Simulates long-term memory transfer.
        """
        if not self.is_full and self.ptr < top_k:
            return

        # Find top-k important memories
        _, indices = torch.topk(self.importance, top_k)

        # Re-initialize with only those memories
        new_obs = self.observations[indices]
        new_targets = self.targets[indices]
        new_imp = self.importance[indices]

        self.observations.zero_()
        self.targets.zero_()
        self.importance.fill_(0.1)  # Decay others

        self.observations[:top_k] = new_obs
        self.targets[:top_k] = new_targets
        self.importance[:top_k] = new_imp

        self.ptr = top_k
        self.is_full = False
