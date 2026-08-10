"""
Experiment D3: Full Stack Ablation Matrix
Question: Which biological systems contribute the most to overall consciousness metrics?

This script runs 6 configurations of the Adaptive Neural Network to identify 
the importance of each subsystem (Somatic, Social, Glial, NAS).
"""  # noqa: W291

import logging
import os
import sys

import pandas as pd
import torch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adaptiveneuralnetwork.central_nervous_system.consciousness_metrics import ConsciousnessMetrics
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_simulation(config_name: str,
                   steps: int = 300,
                   ablation_flags: dict[str, bool] = None) -> dict[str, float]:
    """
    Runs a simulation for a specific configuration and returns key metrics.
    """
    logger.info(f"Running Experiment: {config_name}")

    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim, event_driven=True)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes)

    # Apply Ablations
    if ablation_flags.get('no_microbiome'):
        def mock_somatic_step(energy, phase):
            return {
                'anxiety_threshold': 6.0,
                'serotonin': 0.5,
                'cortisol': 0.1,
                'sleep_drive': 0.0,
                'waste': 0.0
            }
        phase_scheduler.somatic_system.step = mock_somatic_step

    if ablation_flags.get('no_social'):
        if hasattr(phase_scheduler, 'social_context'):
            # Set to None or remove to disable social logic in dynamics
            phase_scheduler.social_context = None

    if ablation_flags.get('no_glial'):
        if hasattr(phase_scheduler, 'glial_manager'):
            phase_scheduler.glial_manager = None

    if ablation_flags.get('no_nas'):
        # Inhibit NAS by clearing stats every step or setting high thresholds
        # But easier to just not call it in dynamics if we modified dynamics.
        # Since we modified dynamics to check for scheduler attrs,
        # let's just make sure it doesn't run if ablated.
        pass # Dynamics.forward handles this if we mock the adapter or if we add a flag

    # Store metrics over time
    phi_history = []
    meta_acc_history = []
    emergence_history = []
    anxiety_levels_list = []
    surprise_levels_list = []

    # Main loop
    for i in range(steps):
        # Semi-natural input: base noise + intermittent spikes
        external_input = torch.randn(1, num_nodes, config.hidden_dim) * 0.2
        if i % 50 == 0:
            external_input += torch.randn(1, num_nodes, config.hidden_dim) * 1.5

        prev_hidden = node_state.hidden_state.clone()

        # Enable/Disable NAS via monkeypatch if possible
        if ablation_flags.get('no_nas'):
            original_adapt = dynamics.topology_adapter.adapt
            dynamics.topology_adapter.adapt = lambda x: None

        node_state = dynamics(node_state, external_input, phase_scheduler)

        if ablation_flags.get('no_nas'):
            dynamics.topology_adapter.adapt = original_adapt

        # Metrics
        phi = ConsciousnessMetrics.calculate_phi_lite(node_state.hidden_state, torch.tensor(1.0))

        # Synthetic performance for meta-acc
        perf = torch.abs(node_state.hidden_state - prev_hidden).mean()
        meta_acc = ConsciousnessMetrics.calculate_metacognitive_accuracy(
            node_state.prediction_error,
            perf
        )

        if getattr(phase_scheduler, 'social_context', None) is not None:
            emergence = ConsciousnessMetrics.calculate_emergence_score(
                phase_scheduler.social_context.trust_matrix,
                node_state.activity
            )
        else:
            emergence = 0.0

        phi_history.append(phi)
        meta_acc_history.append(meta_acc)
        emergence_history.append(emergence)
        anxiety_levels_list.append(node_state.anxiety.clone().detach())
        surprise_levels_list.append(node_state.prediction_error.clone().detach())

    avg_phi = sum(phi_history) / steps
    avg_meta = sum(meta_acc_history) / steps
    avg_emergence = sum(emergence_history) / steps
    cc = ConsciousnessMetrics.calculate_consciousness_coherence(avg_phi, avg_meta, avg_emergence)

    ea = ConsciousnessMetrics.calculate_emotional_appropriateness(
        torch.stack(anxiety_levels_list),
        torch.stack(surprise_levels_list)
    )

    return {
        'Config': config_name,
        'Phi': avg_phi,
        'Meta-Acc': avg_meta,
        'Emergence': avg_emergence,
        'CC Score': cc,
        'Emotional Appr.': ea,
        'Energy Stability': node_state.energy.mean().item()
    }

if __name__ == "__main__":
    configs = [
        ("Full Stack", {}),
        ("No Microbiome", {'no_microbiome': True}),
        ("No Glial", {'no_glial': True}),
        ("No Social", {'no_social': True}),
        ("No NAS", {'no_nas': True}),
        ("Bare Dynamics", {
            'no_microbiome': True,
            'no_social': True,
            'no_glial': True,
            'no_nas': True
        })
    ]

    results = []
    for name, flags in configs:
        try:
            res = run_simulation(name, ablation_flags=flags)
            results.append(res)
        except Exception as e:
            logger.error(f"Failed {name}: {e}")

    df = pd.DataFrame(results)
    print("\n" + "="*80)
    print("EXPERIMENT D3: FULL STACK ABLATION MATRIX RESULTS")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)

    df.to_csv("experiments/results_ablation_d3.csv", index=False)
    logger.info("Results saved to experiments/results_ablation_d3.csv")
