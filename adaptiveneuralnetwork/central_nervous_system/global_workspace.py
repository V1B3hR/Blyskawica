"""
Global Workspace Bus for Phase 7.3.

Implements the Baars' Global Workspace Theory (GWT) where selective 
high-salience information is broadcasted to the entire network, 
enabling "conscious" access and multi-module coordination.
"""  # noqa: W291

import logging

import torch
import torch.nn as nn

from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator

logger = logging.getLogger(__name__)

class GlobalWorkspaceBus(nn.Module):
    """
    The central bus that selects and broadcasts high-salience signals.
    """
    def __init__(self, workspace_dim: int = 256, salience_threshold: float = 0.5):
        super().__init__()
        self.workspace_dim = workspace_dim
        self.salience_threshold = salience_threshold

        # Workspace memory (Working Memory)
        self.register_buffer('workspace_state', torch.zeros(workspace_dim))

        # Projection layers to/from workspace
        # These would normally be dynamically learned
        self.encoder = nn.Linear(workspace_dim, workspace_dim)
        self.decoder = nn.Linear(workspace_dim, workspace_dim)

        # Synaptic Ground Loop Isolation
        self.gli = GroundLoopIsolator(isolation_ratio=0.05)

    def broadcast(self, incoming_signals: torch.Tensor) -> torch.Tensor:
        """
        Select signals above salience threshold and broadcast to workspace.
        """
        # Dimensional Armor for broadcast input
        signals = incoming_signals
        if signals.size(-1) != self.workspace_dim:
            if signals.size(-1) < self.workspace_dim:
                padding = torch.zeros(*signals.shape[:-1], self.workspace_dim - signals.size(-1), device=signals.device)
                signals = torch.cat([signals, padding], dim=-1)
            else:
                signals = signals[..., :self.workspace_dim]

        # Calculate salience (magnitude for now)
        salience = torch.norm(signals, dim=-1)

        # Competition: Only the most salient signals enter the workspace
        mask = (salience > self.salience_threshold).float().unsqueeze(-1)

        # Update workspace state (Heuristic: Weighted average of salient signals)
        if mask.any():
            new_info = (signals * mask).mean(dim=0)
            # Ensure new_info is 1D workspace_state size
            if new_info.dim() > 1:
                new_info = new_info.view(-1)[:self.workspace_dim]

            # Filter incoming signal with Ground Loop Isolation to shunt infinite echoes
            new_info_tensor = new_info.unsqueeze(0)
            new_info_stabilized = self.gli(new_info_tensor).squeeze(0)

            self.workspace_state = 0.9 * self.workspace_state + 0.1 * new_info_stabilized

        # Broadcast the workspace state back to all receivers
        return self.workspace_state

class SelectiveAttentionGating(nn.Module):
    """
    Gating mechanism for modules to interact with the Global Workspace.
    """
    def __init__(self, input_dim: int, workspace_dim: int):
        super().__init__()
        self.input_dim = input_dim
        self.workspace_dim = workspace_dim
        self.query = nn.Linear(input_dim, workspace_dim)
        self.gate = nn.Sequential(
            nn.Linear(input_dim + workspace_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, local_state: torch.Tensor, workspace_state: torch.Tensor) -> torch.Tensor:
        # Dimensional Armor for local_state vs gate input_dim
        ls = local_state
        if ls.size(-1) != self.input_dim:
            if ls.size(-1) < self.input_dim:
                padding = torch.zeros(*ls.shape[:-1], self.input_dim - ls.size(-1), device=ls.device)
                ls = torch.cat([ls, padding], dim=-1)
            else:
                ls = ls[..., :self.input_dim]

        # Armor for workspace_state vs expected workspace_dim
        # Handle dict (summary) input by using a neutral representative vector if needed
        ws = workspace_state
        if isinstance(ws, dict):
             # Heuristic: convert diagnostics to a representative scalar or flat vector
             # For attention gating, we just care if it's salient
             salience = ws.get('avg_salience', 0.5)
             ws = torch.full((ls.size(0), self.workspace_dim), salience, device=ls.device)

        if ws.size(-1) != self.workspace_dim:
            if ws.size(-1) < self.workspace_dim:
                 ws = torch.cat([ws, torch.zeros(*ws.shape[:-1], self.workspace_dim - ws.size(-1), device=ws.device)], dim=-1)
            else:
                 ws = ws[..., :self.workspace_dim]

        # Cross-modal interaction
        # Ensure ws is expanded to match batch of ls
        ws_expanded = ws.expand(ls.size(0), -1)
        if ws_expanded.dim() < ls.dim():
             # ls might be [batch, nodes, features]
             for _ in range(ls.dim() - ws_expanded.dim()):
                 ws_expanded = ws_expanded.unsqueeze(1)
             ws_expanded = ws_expanded.expand(*ls.shape[:-1], -1)

        combined = torch.cat([ls, ws_expanded], dim=-1)
        relevance = self.gate(combined)

        # Only allow interaction if relevance is high
        return local_state * (1.0 + relevance * ws_expanded)
