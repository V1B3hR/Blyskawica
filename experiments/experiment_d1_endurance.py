"""
Experiment D1: 10,000-Step Endurance Run
Goal: Verify long-term metabolic and dynamical stability of the substrate.

Method: Run for 10,000 steps with realistic cyclical pulse input.
"""

import logging
import os
import sys

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_experiment_d1():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)

    steps = 10000
    log_interval = 100
    results = []

    logger.info("Starting 10,000-Step Endurance Run...")

    for i in range(steps):
        # Realistic pulsating input (circadian simulation)
        # Period of 1000 steps
        phase_in_cycle = (i % 1000) / 1000.0
        # High intensity during the middle of the cycle, low intensity at start/end
        intensity = np.sin(np.pi * phase_in_cycle) ** 2

        ext = torch.randn(1, num_nodes, config.hidden_dim) * intensity * 0.5
        node_state = dynamics(node_state, ext, phase_scheduler)

        if i % log_interval == 0:
            stats = phase_scheduler.somatic_stats
            avg_energy = node_state.energy.mean().item()
            avg_anxiety = node_state.anxiety.mean().item()

            logger.info(f"Step {i:5d} | Energy: {avg_energy:6.2f} | Anxiety: {avg_anxiety:6.2f} | Health: {stats['microbiome_health']:4.2f}")

            results.append({
                'Step': i,
                'Energy': avg_energy,
                'Anxiety': avg_anxiety,
                'Health': stats['microbiome_health'],
                'Hormone_S': stats['hormones']['serotonin'],
                'Hormone_C': stats['hormones']['cortisol'],
                'Threshold': stats['anxiety_threshold']
            })

            # Check for crash
            if torch.isnan(node_state.hidden_state).any():
                logger.error(f"NaN detected at step {i}!")
                break

    logger.info("Endurance run complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_d1()
    df = pd.DataFrame(data)
    df.to_csv("experiments/results_endurance_d1.csv", index=False)

    print("\n" + "="*80)
    print("EXPERIMENT D1: 10,000-STEP ENDURANCE SUMMARY")
    print("="*80)
    print(f"Final Energy:  {df.iloc[-1]['Energy']:.2f}")
    print(f"Mean Anxiety:  {df['Anxiety'].mean():.2f}")
    print(f"Stable Health: {df.iloc[-1]['Health']:.2f}")
    print("="*80)
