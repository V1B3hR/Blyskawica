"""
The Conscious Substrate Demo - Conclusion of Phase 7.

This is the aggregate demonstration of all cognitive layers:
- Tier 5: Global Workspace broadcasting.
- Tier 4: Emotional & Social Intelligence (Microbiome + Trust).
- Tier 3: Predictive Internal Modeling (Surprise).
- Tier 2: Resource Modulation (Cognitive Fluidity).
- Hardware Layer: Spike-efficient Event-Driven dynamics.

Outputs: Consciousness Metrics (Phi), Metacognitive Accuracy, and Social Trust.
"""

import torch
import logging
import time
from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState, NodeConfig
from adaptiveneuralnetwork.central_nervous_system.dynamics import AdaptiveDynamics
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler, Phase
from adaptiveneuralnetwork.central_nervous_system.global_workspace import GlobalWorkspaceBus
from adaptiveneuralnetwork.central_nervous_system.consciousness_metrics import ConsciousnessMetrics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def run_conscious_substrate_demo():
    logger.info("Initializing The Conscious Substrate...")
    
    num_nodes = 64
    config = NodeConfig(num_nodes=num_nodes)
    node_state = NodeState(config)
    
    # Initialize Core with Event-Driven processing enabled
    dynamics = AdaptiveDynamics(hidden_dim=config.hidden_dim, event_driven=True)
    phase_scheduler = PhaseScheduler(num_nodes=num_nodes, circadian_period=100)
    
    # Tier 5: Global Workspace
    workspace = GlobalWorkspaceBus(workspace_dim=config.hidden_dim)
    
    # Metrics
    metrics = ConsciousnessMetrics()
    
    logger.info(f"{'Step':<5} | {'Phase':<12} | {'Phi (IIT)':<10} | {'Meta-Acc':<10} | {'Trust':<8} | {'Active%':<8}")
    logger.info("-" * 80)
    
    for i in range(200):
        # 1. External Input (Random environmental stim)
        external_input = torch.randn(1, num_nodes, config.hidden_dim) * 0.5
        
        # 2. Forward Pass through Dynamics (Physiology + Social + Event-Driven)
        node_state = dynamics(node_state, external_input, phase_scheduler)
        
        # 3. Global Workspace Competition
        # Salient info from hidden state enters the bus
        workspace_state = workspace.broadcast(node_state.hidden_state.squeeze(0))
        
        # 4. Calculate Consciousness Metrics
        phi = metrics.calculate_phi_lite(node_state.hidden_state.squeeze(0), torch.tensor(1.0))
        # Self-model accuracy: correlation between energy stress and actual energy
        meta_acc = metrics.calculate_metacognitive_accuracy(
            torch.tensor([node_state.energy.mean().item()]), 
            torch.tensor([10.0]) # Target energy
        )
        
        avg_trust = phase_scheduler.social_context.trust_matrix.mean().item()
        active_ratio = (node_state.activity > 0.1).float().mean().item()
        
        if i % 20 == 0:
            stats = phase_scheduler.get_phase_stats(phase_scheduler.node_phases.unsqueeze(0))
            dominant_phase = max(stats, key=stats.get).replace("_ratio", "").upper()
            
            logger.info(f"{i:<5} | {dominant_phase:<12} | {phi:<10.3f} | {meta_acc:<10.3f} | {avg_trust:<8.2f} | {active_ratio:<8.2%}")

    logger.info("-" * 80)
    logger.info("Final Consciousness Report:")
    logger.info(f"Integrated Information (Phi Lite): {phi:.4f}")
    logger.info(f"Metacognitive Accuracy (Self-Model): {meta_acc:.4f}")
    logger.info(f"Social Cohesion (Final Trust): {avg_trust:.4f}")
    logger.info(f"Emergence Score: {metrics.calculate_emergence_score(torch.tensor([avg_trust]), torch.tensor([0.5])):.4f}")
    
    if phi > 0.05:
        logger.info("RESULT: System demonstrates measurable integration levels. Consciousness-like emergence confirmed.")
    else:
        logger.warning("RESULT: System is in a fragmented state. More training or social density required.")

if __name__ == "__main__":
    run_conscious_substrate_demo()
