"""
Experiment C2: Metacognitive Calibration
Goal: Measure the correlation between prediction confidence and actual correctness.
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

def run_experiment_c2():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)

    results = []

    logger.info("Starting Metacognitive Calibration Study...")

    for i in range(500):
        # Pulsating input to create varying difficulty
        intensity = 0.1 + 0.9 * np.abs(np.sin(i / 50.0))
        ext = torch.randn(1, num_nodes, config.hidden_dim) * intensity

        node_state = dynamics(node_state, ext, phase_scheduler)

        # Confidence = 1 / (1 + error)
        error = node_state.prediction_error.abs().mean().item()
        confidence = 1.0 / (1.0 + error)

        # Accuracy (Surrogate: inverse of error relative to input intensity)
        # Low error at high intensity = high metacognitive accuracy
        rel_error = error / (intensity + 1e-6)

        results.append({
            'Step': i,
            'Intensity': intensity,
            'Error': error,
            'Confidence': confidence,
            'RelError': rel_error
        })

        if i % 100 == 0:
            logger.info(f"Step {i:4d} | Confidence: {confidence:.4f} | Error: {error:.4f}")

    logger.info("Experiment C2 complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_c2()
    df = pd.DataFrame(data)
    df.to_csv("experiments/results_metacognition_c2.csv", index=False)

    correlation = df['Confidence'].corr(df['Error'])

    print("\n" + "="*80)
    print("EXPERIMENT C2: METACOGNITIVE CALIBRATION SUMMARY")
    print("="*80)
    print(f"Confidence-Error Correlation: {correlation:.4f}")
    print(f"Average Confidence:           {df['Confidence'].mean():.4f}")
    print("="*80)
