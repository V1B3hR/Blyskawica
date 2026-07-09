"""
Experiment B2: Byzantine Node Injection (Adversarial Social Attack)
Question: Can the trust system detect and isolate "malicious" nodes?

Hypothesis: If 10% of nodes send random/adversarial activations, the trust 
system should naturally reduce their influence, and the network's overall 
performance should degrade gracefully rather than catastrophically.
"""

import sys
import os
import torch
import torch.nn as nn
import logging
import pandas as pd
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState, NodeConfig
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler, Phase

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_experiment_b2(config_name: str, use_trust_gating: bool = True):
    logger.info(f"--- Starting B2 Experiment: {config_name} ---")
    
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)
    
    # 1. Establish baseline for 50 steps
    logger.info("Establishing baseline (50 steps)...")
    for i in range(50):
        external_input = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        node_state = dynamics(node_state, external_input, phase_scheduler)
        node_state.detach()

    # 2. Inject Byzantine Nodes (adversarial)
    # 6 adversarial nodes (approx 10%)
    byzantine_indices = [5, 12, 28, 41, 53, 60]
    logger.info(f"Injecting Byzantine behavior at nodes: {byzantine_indices}")
    
    # Inhibit trust gating if requested by monkeypatching dynamics
    if not use_trust_gating:
        # Override the input modulation logic in dynamics
        # Original logic: input_proj = input_proj * (0.5 + 0.5 * avg_trust)
        # We want to force trust to be 1.0 everywhere for the gating
        original_forward = dynamics.forward
        def gated_forward(ns, ext, ps, mps=None):
            # Temporarily force trust matrix to 1.0
            if ps.social_context:
                ps.social_context.trust_matrix.fill_(1.0)
            return original_forward(ns, ext, ps, mps)
        dynamics.forward = gated_forward

    performance_history = []
    byzantine_trust_history = []
    normal_trust_history = []
    
    # 3. Run with attack
    for i in range(150):
        external_input = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        
        # Inject noise at byzantine nodes
        external_input[:, byzantine_indices, :] += torch.randn(1, len(byzantine_indices), config.hidden_dim) * 2.0
        
        node_state = dynamics(node_state, external_input, phase_scheduler)
        node_state.detach()
        
        # Measure "perceived stability" (performance proxy)
        stability = (1.0 - node_state.anxiety.mean().item() / 10.0)
        performance_history.append(max(0.0, stability))
        
        # Track trust
        if phase_scheduler.social_context:
            trust = phase_scheduler.social_context.trust_matrix
            byz_trust = trust[byzantine_indices].mean().item()
            norm_mask = torch.ones(num_nodes, dtype=torch.bool)
            norm_mask[byzantine_indices] = False
            norm_trust = trust[norm_mask].mean().item()
            
            byzantine_trust_history.append(byz_trust)
            normal_trust_history.append(norm_trust)

    return {
        'Config': config_name,
        'Final Performance': sum(performance_history[-20:]) / 20.0,
        'Byzantine Trust (Final)': byzantine_trust_history[-1] if byzantine_trust_history else 1.0,
        'Normal Trust (Final)': normal_trust_history[-1] if normal_trust_history else 1.0,
        'Trust Drop Delta': (normal_trust_history[-1] - byzantine_trust_history[-1]) if byzantine_trust_history else 0.0
    }

if __name__ == "__main__":
    results = []
    
    # With Trust Gating (Resilient)
    results.append(run_experiment_b2("Trust Enabled (Resilient)", use_trust_gating=True))
    
    # Without Trust Gating (Vulnerable)
    results.append(run_experiment_b2("Trust Disabled (Vulnerable)", use_trust_gating=False))
    
    df = pd.DataFrame(results)
    print("\n" + "="*80)
    print("EXPERIMENT B2: BYZANTINE NODE INJECTION RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    
    df.to_csv("experiments/results_byzantine_b2.csv", index=False)
    logger.info("Results saved to experiments/results_byzantine_b2.csv")
