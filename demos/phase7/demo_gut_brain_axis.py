"""
Demo for Phase 7.4: Virtual Microbiome and the Gut-Brain Axis.

This script demonstrates how virtual bacterial colonies living in the 
'somatic' layer modulate the network's emotional state, energy usage, 
and sleep cycles.

Workflow:
1. Initialize a population of nodes with a Somatic System.
2. Simulate a 'stressful day' (high energy drain).
3. Observe the namnam (growth) of stressogenic bacteria and cortisol spike.
4. Observe the 'Metabolic Sleep Drive' forcing the system into REM.
5. Simulate recovery during sleep and serotonin replenishment.
"""  # noqa: W291

import logging

import torch

from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeConfig, NodeState
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def run_gut_brain_demo():
    logger.info("Starting Phase 7.4 Gut-Brain Axis Demo")

    num_nodes = 50
    config = NodeConfig(num_nodes=num_nodes, energy_decay=0.05)
    node_state = NodeState(config)
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes, circadian_period=50)

    # Simulate 100 steps of 'Life'
    logger.info(f"{'Step':<5} | {'Phase':<12} | {'Energy':<8} | {'Waste':<8} | {'Cortisol':<8} | {'Avg Trust':<10} | {'ToM Anxiety':<12}")
    logger.info("-" * 90)

    for i in range(120):
        # ... generate input ...
        if i < 40:
             external_input = torch.randn(1, num_nodes, config.hidden_dim) * 2.0
        else:
             external_input = torch.randn(1, num_nodes, config.hidden_dim) * 0.1

        # Forward
        node_state = dynamics(node_state, external_input, phase_scheduler)

        # Stats
        stats = phase_scheduler.get_phase_stats(phase_scheduler.node_phases.unsqueeze(0))
        s_stats = phase_scheduler.somatic_stats
        social = phase_scheduler.social_context

        # Most frequent phase
        dominant_phase = max(stats, key=stats.get).replace("_ratio", "").upper()

        if i % 10 == 0:
            avg_trust = social.trust_matrix.mean().item()
            tom_anxiety = social.tom_anxiety_predictions.mean().item()
            logger.info(f"{i:<5} | {dominant_phase:<12} | {node_state.energy.mean():<8.2f} | {s_stats['waste']:<8.2f} | "
                        f"{s_stats['cortisol']:<8.2f} | {avg_trust:<10.2f} | {tom_anxiety:<12.2f}")

        # Slow down for visibility if running interactively
        # time.sleep(0.05)

    logger.info("-" * 80)
    logger.info("Demo Summary:")
    logger.info(f"Final Symbiotic Bacteria: {phase_scheduler.somatic_system.microbiome.symbiotic_count.item():.1f}")
    logger.info(f"Final Stressogenic Bacteria: {phase_scheduler.somatic_system.microbiome.stressogenic_count.item():.1f}")

    if phase_scheduler.somatic_system.microbiome.symbiotic_count > 1000:
        logger.info("SUCCESS: Microbiome recovered after stress. The AI is 'feeling' better.")
    else:
        logger.warning("The AI is still feeling stressed. Consider a longer sleep cycle.")

if __name__ == "__main__":
    run_gut_brain_demo()
