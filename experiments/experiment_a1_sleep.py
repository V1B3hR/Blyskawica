"""
Experiment A1: Sleep Deprivation Study
Question: Does the SLEEP phase protect against catastrophic forgetting?

Hypothesis: A network that is allowed to sleep (with glial waste clearance) 
will retain Task A performance better than a sleep-deprived variant after 
learning Task B.
"""

import sys
import os
import torch
import torch.nn as nn
import torch.optim as optim
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState, NodeConfig
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler, Phase
from adaptiveneuralnetwork.central_nervous_system.consciousness_metrics import ConsciousnessMetrics

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def generate_task_data(num_samples: int, input_dim: int, hidden_dim: int, task_id: int):
    """Generates synthetic pattern association data."""
    torch.manual_seed(task_id)
    # Different tasks have different input-to-hidden mappings
    task_transform = torch.randn(input_dim, hidden_dim) * 0.5
    X = torch.randn(num_samples, input_dim)
    Y = torch.tanh(X @ task_transform)
    return X, Y

def run_experiment_a1(config_name: str, force_active: bool = False, disable_glial: bool = False):
    logger.info(f"--- Starting A1 Experiment: {config_name} ---")
    
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    # Use a faster circadian rhythm for the experiment (20 steps per cycle)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes, circadian_period=50)
    
    if disable_glial:
        phase_scheduler.glial_manager = None

    optimizer = optim.Adam(dynamics.parameters(), lr=0.005)
    
    # Task A
    X_a, Y_a = generate_task_data(200, num_nodes, config.hidden_dim, 42)
    # Task B
    X_b, Y_b = generate_task_data(200, num_nodes, config.hidden_dim, 99)
    
    def train_step(X, Y, steps=100, record_phi=False):
        phi_values = []
        for i in range(steps):
            idx = i % X.shape[0]
            # [batch=1, nodes, dim]
            input_data = X[idx].unsqueeze(0).unsqueeze(0).expand(1, num_nodes, -1)
            target = Y[idx].unsqueeze(0).unsqueeze(0).expand(1, num_nodes, -1)
            
            optimizer.zero_grad()
            
            # Force phase if requested
            if force_active:
                # Monkeypatch phase scheduler during this step
                original_step = phase_scheduler.step
                phase_scheduler.step = lambda e, a, anx: torch.zeros(num_nodes, dtype=torch.long) # Phase.ACTIVE
            
            node_state_out = dynamics(node_state, input_data, phase_scheduler)
            
            if force_active:
                phase_scheduler.step = original_step
            
            # Simple loss based on hidden state vs target
            loss = torch.mean((node_state_out.hidden_state - target)**2)
            loss.backward()
            optimizer.step()
            
            node_state.detach()
            
            if record_phi:
                phi = ConsciousnessMetrics.calculate_phi_lite(node_state_out.hidden_state, torch.tensor(1.0))
                phi_values.append(phi)
                
        return sum(phi_values)/len(phi_values) if phi_values else 0.0

    def evaluate(X, Y):
        dynamics.eval()
        total_loss = 0
        with torch.no_grad():
            for i in range(len(X)):
                input_data = X[i].unsqueeze(0).unsqueeze(0).expand(1, num_nodes, -1)
                target = Y[i].unsqueeze(0).unsqueeze(0).expand(1, num_nodes, -1)
                node_state_out = dynamics(node_state, input_data, phase_scheduler)
                total_loss += torch.mean((node_state_out.hidden_state - target)**2).item()
        dynamics.train()
        return total_loss / len(X)

    # 1. Train Task A
    logger.info("Training on Task A...")
    train_step(X_a, Y_a, steps=150)
    loss_a_initial = evaluate(X_a, Y_a)
    logger.info(f"Task A Initial Loss: {loss_a_initial:.4f}")
    
    # 2. Train Task B (The "interference" task)
    logger.info("Training on Task B (Interference)...")
    avg_phi_b = train_step(X_b, Y_b, steps=150, record_phi=True)
    loss_b_final = evaluate(X_b, Y_b)
    logger.info(f"Task B Final Loss: {loss_b_final:.4f}")
    
    # 3. Re-test Task A
    loss_a_final = evaluate(X_a, Y_a)
    forgetting = (loss_a_final - loss_a_initial) / (loss_a_initial + 1e-6)
    logger.info(f"Task A Final Loss: {loss_a_final:.4f} (Forgetting: {forgetting:.2%})")
    
    return {
        'Config': config_name,
        'Initial Loss A': loss_a_initial,
        'Final Loss A': loss_a_final,
        'Forgetting %': forgetting * 100,
        'Avg Phi (Task B)': avg_phi_b,
        'Energy': node_state.energy.mean().item()
    }

if __name__ == "__main__":
    results = []
    
    # Normal: Allowed to sleep & use Glial clearance
    results.append(run_experiment_a1("Normal (Sleep Allowed)"))
    
    # Sleep Deprived: Forced to ACTIVE phase
    results.append(run_experiment_a1("Sleep Deprived", force_active=True))
    
    # No Glial: Can sleep, but no waste clearance
    results.append(run_experiment_a1("No Glial Clearance", disable_glial=True))
    
    df = pd.DataFrame(results)
    print("\n" + "="*80)
    print("EXPERIMENT A1: SLEEP DEPRIVATION STUDY RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    
    df.to_csv("experiments/results_sleep_a1.csv", index=False)
    logger.info("Results saved to experiments/results_sleep_a1.csv")
