"""
Experiment B1: Social Trust Convergence
Goal: Verify that reputation converges in the social substrate.
"""

import sys
import os
import torch
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState, NodeConfig
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_experiment_b1():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)
    
    results = []
    
    logger.info("Starting Trust Convergence Study...")
    
    for i in range(500):
        # Stable random input
        ext = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        node_state = dynamics(node_state, ext, phase_scheduler)
        
        reputation = phase_scheduler.social_context.reputation if phase_scheduler.social_context else torch.zeros(num_nodes)
        std_dev = reputation.std().item()
        mean_trust = reputation.mean().item()
        
        if i % 50 == 0:
            logger.info(f"Step {i:4d} | Mean Trust: {mean_trust:.4f} | Trust StdDev: {std_dev:.4f}")
            
        results.append({
            'Step': i,
            'MeanTrust': mean_trust,
            'TrustStdDev': std_dev
        })
        
    logger.info("Experiment B1 complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_b1()
    df = pd.DataFrame(data)
    df.to_csv("experiments/results_trust_b1.csv", index=False)
    
    initial_std = df.iloc[0]['TrustStdDev']
    final_std = df.iloc[-1]['TrustStdDev']
    improvement = (initial_std - final_std) / (initial_std + 1e-6)
    
    print("\n" + "="*80)
    print("EXPERIMENT B1: TRUST CONVERGENCE SUMMARY")
    print("="*80)
    print(f"Initial StdDev: {initial_std:.4f}")
    print(f"Final StdDev:   {final_std:.4f}")
    print(f"Convergence:    {improvement:.2%}")
    print("="*80)
