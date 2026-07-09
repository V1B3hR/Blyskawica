"""
Experiment A2: Gut-Brain Stress Response
Goal: Validate the virtual microbiome and physiological Affect.

Method: Moderate baseline, followed by extreme sustained stress, then recovery.
"""

import sys
import os
import torch
import logging
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState, NodeConfig
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_experiment_a2():
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)
    
    results = []
    
    # 1. Baseline (Steps 1-100)
    logger.info("Phase 1: Baseline (Moderate Input)...")
    for i in range(100):
        ext = torch.randn(1, num_nodes, config.hidden_dim) * 0.1
        node_state = dynamics(node_state, ext, phase_scheduler)
        
        stats = phase_scheduler.somatic_stats
        results.append({
            'Step': i,
            'Tag': 'Baseline',
            'Cortisol': stats['hormones']['cortisol'],
            'Serotonin': stats['hormones']['serotonin'],
            'Health': stats['microbiome_health'],
            'Energy': node_state.energy.mean().item(),
            'Anxiety': node_state.anxiety.mean().item(),
            'Threshold': stats['anxiety_threshold']
        })

    # 2. Stress Phase (Steps 101-400)
    logger.info("Phase 2: Stress (High Amplitude Input)...")
    for i in range(100, 400):
        ext = torch.randn(1, num_nodes, config.hidden_dim) * 2.0 # High noise/energy
        node_state = dynamics(node_state, ext, phase_scheduler)
        
        stats = phase_scheduler.somatic_stats
        results.append({
            'Step': i,
            'Tag': 'Stress',
            'Cortisol': stats['hormones']['cortisol'],
            'Serotonin': stats['hormones']['serotonin'],
            'Health': stats['microbiome_health'],
            'Energy': node_state.energy.mean().item(),
            'Anxiety': node_state.anxiety.mean().item(),
            'Threshold': stats['anxiety_threshold']
        })

    # 3. Recovery Phase (Steps 401-600)
    logger.info("Phase 3: Recovery (Zero Input)...")
    for i in range(400, 600):
        ext = torch.zeros(1, num_nodes, config.hidden_dim)
        node_state = dynamics(node_state, ext, phase_scheduler)
        
        stats = phase_scheduler.somatic_stats
        results.append({
            'Step': i,
            'Tag': 'Recovery',
            'Cortisol': stats['hormones']['cortisol'],
            'Serotonin': stats['hormones']['serotonin'],
            'Health': stats['microbiome_health'],
            'Energy': node_state.energy.mean().item(),
            'Anxiety': node_state.anxiety.mean().item(),
            'Threshold': stats['anxiety_threshold']
        })

    logger.info("Experiment A2 complete.")
    return results

if __name__ == "__main__":
    data = run_experiment_a2()
    df = pd.DataFrame(data)
    
    # Analyze results
    baseline_th = df[df['Tag'] == 'Baseline']['Threshold'].mean()
    stress_th = df[df['Tag'] == 'Stress']['Threshold'].mean()
    min_health = df['Health'].min()
    
    print("\n" + "="*80)
    print("EXPERIMENT A2: GUT-BRAIN STRESS RESPONSE SUMMARY")
    print("="*80)
    print(f"Baseline Threshold: {baseline_th:.2f}")
    print(f"Stress Threshold:   {stress_th:.2f}")
    print(f"Min Health:         {min_health:.2f}")
    print(f"Health Recovery:    {df.iloc[-1]['Health']:.2f}")
    print("="*80)
    
    df.to_csv("experiments/results_stress_a2.csv", index=False)
