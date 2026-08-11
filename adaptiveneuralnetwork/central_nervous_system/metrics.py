"""
Consciousness Metrics and Substrate Health implementation for Błyskawica.

Includes:
- PhiCalculator: Spectral approximation of Integrated Information (IIT).
- NeuralHealthMonitor: Assessment of biological stability and burnout risk.
"""


import torch


class PhiCalculator:
    """
    Calculates an approximation of Integrated Information (Φ) 
    based on information sharing between conscious threads.
    """  # noqa: W291
    def __init__(self, num_threads: int = 4):
        self.num_threads = num_threads

    def calculate_phi(self, thread_memories: torch.Tensor) -> float:
        """Approximate Φ based on information sharing between conscious threads."""
        thread_features = thread_memories.reshape(self.num_threads, -1)
        sim_matrix = torch.matmul(thread_features, thread_features.T) / (
            torch.norm(thread_features, dim=1, keepdim=True) * torch.norm(thread_features, dim=1).T + 1e-8
        )
        integration = sim_matrix.mean().item()
        differentiation = sim_matrix.std().item()
        phi = 4.0 * integration * differentiation
        return float(torch.clamp(torch.tensor(phi), 0.0, 1.0))

    def calculate_full_phi(self, weights: torch.Tensor, activations: torch.Tensor) -> float:
        """
        Approximate Φ for the entire substrate.
        Hybrid approach: Integration = Spectral Entropy of Weights * Temporal Complexity.
        """
        # [num_nodes, features]
        if weights is None:
            weights = torch.eye(self.num_threads * 2)
        W = weights.detach()

        # [batch, nodes, features] or [batch, features]
        if activations is None:
            activations = torch.zeros(1, W.size(-1), device=W.device)
        A = activations.detach()

        if A.dim() == 3:
            A = A.mean(dim=0) # [nodes, features]
        elif A.dim() == 2:
            # Treat batch as time/samples and features as individual "nodes"
            # to calculate differentiation across the population
            A = A.T # [nodes, batch/time]

        # Ensure A has the same feature dimension as W
        # If A was transposed, W's first dimension matches A's nodes
        target_features = W.size(0) if A.dim() == 2 else W.size(-1)
        # W size is [hidden_out, hidden_in]
        # A size is [batch, features]
        if A.size(-1) != target_features:
            # Dimensional mismatch: likely auditing a sub-layer
            # Project A to W's input dimension using interpolation or padding
            if A.size(-1) < target_features:
                padding = torch.zeros(*A.shape[:-1], target_features - A.size(-1), device=A.device)
                A = torch.cat([A, padding], dim=-1)
            else:
                A = A[..., :target_features]

        # 1. Integration: Spectral Entropy of the adjacency matrix
        try:
            # SVD for stability
            s = torch.linalg.svdvals(W)
            p = (s**2) / (torch.sum(s**2) + 1e-8)
            spectral_entropy = -torch.sum(p * torch.log(p + 1e-8)) / torch.log(torch.tensor(max(W.shape)).float() + 1e-8)
            integration = 1.0 - spectral_entropy.item()
        except:  # noqa: E722
            integration = 0.5

        # 2. Differentiation: Spatial diversity of activations
        # We need a meaningful differentiation measure
        try:
            # How unique is each node's behavior?
            # Integration * (1 - Correlation)
            A_norm = A / (torch.norm(A, dim=-1, keepdim=True) + 1e-8)
            corr = torch.matmul(A_norm, A_norm.T).mean().item()
            differentiation = 1.0 - abs(corr)
        except:  # noqa: E722
            differentiation = 0.5

        phi = 4.0 * integration * differentiation
        return float(torch.clamp(torch.tensor(phi), 0.0, 1.0))

class NeuralHealthMonitor:
    """
    Evaluates the 'Mental Health' of the neural substrate.
    """
    def __init__(self):
        self.health_history = []

    def calculate_health_index(self,
                               activity: torch.Tensor | float,
                               energy: torch.Tensor | float,
                               anxiety: torch.Tensor | float,
                               waste: torch.Tensor | None = None) -> float:
        """
        Computes a composite Neural Health Score [0.0 - 1.0].
        """
        # Ensure inputs are tensors
        if not isinstance(activity, torch.Tensor):
            activity = torch.tensor([activity])
        if not isinstance(energy, torch.Tensor):
            energy = torch.tensor([energy])
        if not isinstance(anxiety, torch.Tensor):
            anxiety = torch.tensor([anxiety])

        # A. Excitation/Inhibition Balance (Avoid Saturation or Silence)
        # Optimal variance: activity should be distributed, not binary.
        if activity.numel() > 1:
            ei_balance = 1.0 - torch.abs(activity.std() - 0.25) / 0.25
        else:
            ei_balance = 1.0 # Default for single node

        # B. Metabolic Reserves
        # Low energy = High stress
        metabolic_score = torch.clamp(energy.mean() / 10.0, 0.0, 1.0)

        # C. Emotional Load
        # High anxiety = Low health
        anxiety_load = 1.0 - torch.clamp(anxiety.mean() / 5.0, 0.0, 1.0)

        # D. Waste factor (Glimphatic load)
        waste_penalty = 1.0
        if waste is not None:
            waste_penalty = 1.0 - torch.clamp(waste.mean() / 2.0, 0.0, 1.0)

        # Composite Health Index
        health_idx = (ei_balance + metabolic_score + anxiety_load + waste_penalty) / 4.0
        return float(torch.clamp(health_idx, 0.0, 1.0))

    def calculate_structural_entropy(self, weights: torch.Tensor) -> float:
        """
        Measure the 'Information Capacity' of the topology.
        Entropy of weight distributions.
        """
        w_abs = torch.abs(weights.detach())
        w_norm = w_abs / (w_abs.sum() + 1e-8)
        entropy = -torch.sum(w_norm * torch.log(w_norm + 1e-8)) / torch.log(torch.tensor(weights.numel()).float())
        return float(torch.clamp(entropy, 0.0, 1.0))
