"""
Experiment C3: Insight Sequences
Goal: Identify phase transition patterns that lead to "insight" (step loss drops).
"""

import sys
import os
import torch
import logging
import pandas as pd
import numpy as np
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState, NodeConfig
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_experiment_c3():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)
    
    phase_history = []
    error_history = []
    
    logger.info("Starting Insight Sequence Mining...")
    
    for i in range(1000):
        # Pulsating input
        intensity = 0.5 + 0.5 * np.sin(i / 10.0)
        ext = torch.randn(1, num_nodes, config.hidden_dim) * intensity
        
        node_state = dynamics(node_state, ext, phase_scheduler)
        
        # Get phase
        p = phase_scheduler.step(node_state.energy, node_state.activity, node_state.anxiety)
        # Dominant phase for simplicity
        p_val = int(p[0, 0].item())
        
        phase_history.append(p_val)
        error_history.append(node_state.prediction_error.abs().mean().item())
        
    # Analyze sequences
    # Look for sequences of length 3
    sequences = []
    for i in range(len(phase_history) - 3):
        seq = tuple(phase_history[i:i+3])
        # Performance delta after sequence
        improvement = error_history[i+2] - error_history[i+3] if i+3 < len(error_history) else 0
        sequences.append({'seq': seq, 'improvement': improvement})
        
    df_seq = pd.DataFrame(sequences)
    insight_patterns = df_seq.groupby('seq')['improvement'].mean().sort_values(ascending=False)
    
    logger.info("Experiment C3 complete.")
    return insight_patterns.head(10)

if __name__ == "__main__":
    top_patterns = run_experiment_c3()
    print("\n" + "="*80)
    print("EXPERIMENT C3: TOP INSIGHT SEQUENCES (Phase Patterns)")
    print("="*80)
    print(top_patterns)
    print("="*80)
    top_patterns.to_csv("experiments/results_insight_c3.csv")
