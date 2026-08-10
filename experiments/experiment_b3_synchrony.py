"""
Experiment B3: Social Synchronization
Goal: Measure phase alignment (synchrony) across the neural population.
"""

import logging
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_phase_entropy(phases):
    counts = Counter(phases)
    total = sum(counts.values())
    probs = [c/total for c in counts.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

def run_experiment_b3():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)

    results = []

    logger.info("Starting Social Synchronization Study...")

    for i in range(1000):
        # Apply high input to synchronize nodes into "Active/Interactive"
        phase_in_cycle = (i % 200) / 200.0
        intensity = 2.0 if 0.4 < phase_in_cycle < 0.6 else 0.1

        ext = torch.randn(1, num_nodes, config.hidden_dim) * intensity
        node_state = dynamics(node_state, ext, phase_scheduler)

        # current phases
        # For our substrate, we take the dominant phase for simple metrics
        # (Though each node could be in different states if we had per-node phases)
        # Assuming phase_scheduler.step returns [1, num_nodes] phases.

        # We simulate the diversity by looking at the energy distribution
        # for a proxy of phase diversity.

        # Actually, let's just use the PhaseScheduler results
        # We'll mock the diversity by slightly jittering energy

        # Get the phases
        p = phase_scheduler.step(node_state.energy, node_state.activity, node_state.anxiety)
        flat_phases = p.flatten().tolist()

        entropy = calculate_phase_entropy(flat_phases)

        if i % 100 == 0:
            logger.info(f"Step {i:4d} | Intensity: {intensity:.2f} | Phase Entropy: {entropy:.4f}")

        results.append({
            'Step': i,
            'Intensity': intensity,
            'PhaseEntropy': entropy,
            'AvgEnergy': node_state.energy.mean().item()
        })

    logger.info("Experiment B3 complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_b3()
    df = pd.DataFrame(data)
    df.to_csv("experiments/results_synchrony_b3.csv", index=False)

    # Correlation between intensity and entropy (Synchrony usually increases with intensity)
    corr = df['Intensity'].corr(df['PhaseEntropy'])

    print("\n" + "="*80)
    print("EXPERIMENT B3: SOCIAL SYNCHRONIZATION SUMMARY")
    print("="*80)
    print(f"Mean Phase Entropy: {df['PhaseEntropy'].mean():.4f}")
    print(f"Min Phase Entropy:  {df['PhaseEntropy'].min():.4f} (Peak Synchrony)")
    print(f"Intensity-Entropy Corr: {corr:.4f}")
    print("="*80)
