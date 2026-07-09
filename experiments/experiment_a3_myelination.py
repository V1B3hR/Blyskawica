"""
Experiment A3: Glial Myelination Stability
Goal: Ensure myelination levels plateau at healthy levels.
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

def run_experiment_a3():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)
    
    results = []
    
    logger.info("Starting Glial Myelination Stability Study...")
    
    for i in range(2000):
        # High trust input to trigger myelination
        ext = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        node_state = dynamics(node_state, ext, phase_scheduler)
        
        # Get myelination from glial
        glial_manager = phase_scheduler.glial_manager
        myel_flat = glial_manager.glial.myelination_levels
        mean_myel = myel_flat.mean().item()
        max_myel = myel_flat.max().item()
        
        if i % 200 == 0:
            logger.info(f"Step {i:4d} | Mean Myelination: {mean_myel:.4f} | Max: {max_myel:.4f}")
            
        results.append({
            'Step': i,
            'MeanMyelination': mean_myel,
            'MaxMyelination': max_myel
        })
        
    logger.info("Experiment A3 complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_a3()
    df = pd.DataFrame(data)
    df.to_csv("experiments/results_myelination_a3.csv", index=False)
    
    print("\n" + "="*80)
    print("EXPERIMENT A3: MYELINATION STABILITY SUMMARY")
    print("="*80)
    print(f"Initial Mean Myel: {df.iloc[0]['MeanMyelination']:.4f}")
    print(f"Final Mean Myel:   {df.iloc[-1]['MeanMyelination']:.4f}")
    print(f"Plateau Delta:     {df.iloc[-1]['MeanMyelination'] - df.iloc[-50]['MeanMyelination']:.6f}")
    print("="*80)
