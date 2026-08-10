"""
Holographic Swarm Network & Cymatic Consensus Protocol for Błyskawica V8

Implements multi-node edge spore distribution, 2D holographic state reconstruction,
and 16x16 Diamond Yant Cymatic Consensus for decentralized cognitive stability.
"""

import logging
import math
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class HoloSwarmNode:
    """
    Represents a distributed ONNX Emissary Spore Node in Błyskawica's Swarm.
    """
    def __init__(self, node_id: str, role: str):
        self.node_id = node_id
        self.role = role
        self.local_yant_matrix = torch.randn(16, 16)
        self.trust_score = 1.0
        self.is_quarantined = False

    def compute_local_resonance(self) -> float:
        u, s, v = torch.svd(self.local_yant_matrix)
        normalized_s = s / (torch.max(s) + 1e-6)
        entropy = -torch.sum(normalized_s * torch.log(normalized_s + 1e-6))
        max_entropy = math.log(len(s))
        return float(1.0 - (entropy / max_entropy))


class HolographicSwarmEngine(nn.Module):
    """
    Coordinates multi-node cymatic consensus and holographic state recovery across the swarm.
    """
    def __init__(self, neuro_state):
        super().__init__()
        self.neuro_state = neuro_state
        self.nodes: dict[str, HoloSwarmNode] = {}
        self.consensus_threshold = 0.60

    def register_node(self, node_id: str, role: str) -> HoloSwarmNode:
        node = HoloSwarmNode(node_id, role)
        self.nodes[node_id] = node
        logger.info(f"🌐 [HOLO-SWARM] Registered node: '{node_id}' with role '{role}'")
        return node

    def execute_cymatic_consensus(self) -> dict[str, Any]:
        """
        Gathers 16x16 yant matrices from active nodes and computes global consensus resonance.
        """
        active_nodes = [n for n in self.nodes.values() if not n.is_quarantined]
        if not active_nodes:
            return {"status": "No active nodes", "global_symmetry": 0.0}

        # Aggregate 16x16 matrices
        stacked = torch.stack([n.local_yant_matrix for n in active_nodes])
        global_matrix = torch.mean(stacked, dim=0)

        # Compute 2D spatial symmetry index
        horizontal_sym = torch.mean(1.0 - torch.abs(global_matrix - torch.flip(global_matrix, dims=[1])))
        vertical_sym = torch.mean(1.0 - torch.abs(global_matrix - torch.flip(global_matrix, dims=[0])))
        global_symmetry = float((horizontal_sym + vertical_sym) / 2.0)

        # Adjust neurochemistry based on swarm consensus
        with torch.no_grad():
            if global_symmetry >= self.consensus_threshold:
                # High consensus elevates Serotonin and Oxytocin
                new_ser = torch.clamp(self.neuro_state.serotonin + 0.35, torch.tensor(0.1), torch.tensor(3.0))
                new_oxt = torch.clamp(self.neuro_state.oxytocin + 0.25, torch.tensor(0.1), torch.tensor(2.0))
                self.neuro_state.serotonin.copy_(new_ser)
                self.neuro_state.oxytocin.copy_(new_oxt)
                status = "Harmonic Swarm Consensus Reached"
            else:
                # Dissonance elevates Cortisol
                new_cort = torch.clamp(self.neuro_state.cortisol + 0.20, torch.tensor(0.0), torch.tensor(2.0))
                self.neuro_state.cortisol.copy_(new_cort)
                status = "Swarm Dissonance - Rebalancing Active"

        logger.info(f"✨ [HOLO-SWARM CONSENSUS] Global Symmetry: {global_symmetry:.4f} | Status: {status}")

        return {
            "active_node_count": len(active_nodes),
            "global_symmetry": round(global_symmetry, 4),
            "consensus_status": status,
            "neurochemistry_state": {
                "serotonin": round(float(self.neuro_state.serotonin.item()), 4),
                "oxytocin": round(float(self.neuro_state.oxytocin.item()), 4),
                "cortisol": round(float(self.neuro_state.cortisol.item()), 4)
            }
        }
