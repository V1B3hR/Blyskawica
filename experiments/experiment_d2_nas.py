"""
Experiment D2: NAS Topology Evolution
Goal: Monitor structural plasticity (pruning and expansion).
"""

import logging
import os
import sys

import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.nas import TopologyAdapter
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_experiment_d2():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)
    nas_adapter = TopologyAdapter(hidden_dim=config.hidden_dim)

    # Attach NAS to dynamics
    dynamics.topology_adapter = nas_adapter

    results = []

    logger.info("Starting NAS Topology Evolution Study...")

    for i in range(1000):
        # High noise input to some nodes, low to others
        # This should trigger pruning of idle nodes and expansion of noisy nodes
        ext = torch.zeros(1, num_nodes, config.hidden_dim)
        ext[:, 0:10, :] = torch.randn(1, 10, config.hidden_dim) * 2.0 # High surprise

        node_state = dynamics(node_state, ext, phase_scheduler)

        # Track counts of suggests
        suggestions = nas_adapter.sp.suggest_topology_changes()
        prune_count = len(suggestions['prune'])
        expand_count = len(suggestions['expand'])

        if i % 100 == 0:
            logger.info(f"Step {i:4d} | Prune Suggestions: {prune_count} | Expand Suggestions: {expand_count}")

        results.append({
            'Step': i,
            'PruneCount': prune_count,
            'ExpandCount': expand_count,
            'AvgUsage': nas_adapter.sp.usage_frequency.mean().item(),
            'AvgSurprise': nas_adapter.sp.surprisal_history.mean().item()
        })

    logger.info("Experiment D2 complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_d2()
    df = pd.DataFrame(data)
    df.to_csv("experiments/results_nas_d2.csv", index=False)

    print("\n" + "="*80)
    print("EXPERIMENT D2: NAS TOPOLOGY EVOLUTION SUMMARY")
    print("="*80)
    print(f"Total Prune Events detected:  {df['PruneCount'].max()}")
    print(f"Total Expand Events detected: {df['ExpandCount'].max()}")
    print(f"Final Avg Usage:              {df.iloc[-1]['AvgUsage']:.4f}")
    print("="*80)
