"""
Experiment C1: Phi Under Perturbation
Goal: Prove that Phi is a genuine structural metric.

Method: Measure Phi, cut cross-partition connections, and measure drop.
"""

import logging
import os
import sys

import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.consciousness_metrics import ConsciousnessMetrics
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_experiment_c1():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)

    # 1. Baseline
    logger.info("Gathering baseline Phi...")
    baseline_phi_list = []
    for _ in range(50):
        ext = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        node_state = dynamics(node_state, ext, phase_scheduler)
        phi = ConsciousnessMetrics.calculate_phi_lite(node_state.hidden_state, torch.tensor(1.0))
        baseline_phi_list.append(phi)

    avg_baseline = sum(baseline_phi_list) / len(baseline_phi_list)

    # 2. Perturbation (Partition Cut)
    logger.info("Applying 50% Partition Cut...")
    # Zero out weights from nodes [32:] to [0:32] and vice versa
    with torch.no_grad():
        weight = dynamics.state_update.weight
        # weight is [hidden_dim, hidden_dim]
        # Nodes are represented by sub-regions? No, AdaptiveDynamics treats them as a whole.
        # But we can split the hidden dimension as a proxy for network partitions.
        mid = config.hidden_dim // 2
        # Cut cross-talk
        weight[0:mid, mid:] = 0.0
        weight[mid:, 0:mid] = 0.0

    # 3. Post-Cut Measurement
    logger.info("Measuring Phi after cut...")
    cut_phi_list = []
    for _ in range(50):
        ext = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        node_state = dynamics(node_state, ext, phase_scheduler)
        phi = ConsciousnessMetrics.calculate_phi_lite(node_state.hidden_state, torch.tensor(1.0))
        cut_phi_list.append(phi)

    avg_cut = sum(cut_phi_list) / len(cut_phi_list)
    phi_drop = (avg_baseline - avg_cut) / (avg_baseline + 1e-6)

    logger.info(f"Baseline Phi: {avg_baseline:.4f}")
    logger.info(f"Cut Phi: {avg_cut:.4f}")
    logger.info(f"Phi Drop: {phi_drop:.2%}")

    return {
        'Config': 'Partition Cut (Bisection)',
        'Baseline Phi': avg_baseline,
        'Cut Phi': avg_cut,
        'Drop %': phi_drop * 100
    }

if __name__ == "__main__":
    res = run_experiment_c1()
    df = pd.DataFrame([res])
    print("\n" + "="*80)
    print("EXPERIMENT C1: PHI PERTURBATION RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    df.to_csv("experiments/results_perturbation_c1.csv", index=False)
