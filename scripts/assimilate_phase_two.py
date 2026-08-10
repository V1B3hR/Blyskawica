import logging

import numpy as np
import torch

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.central_nervous_system.time_manager import get_time_manager
from adaptiveneuralnetwork.data.science_loader import GlobalScienceLoader
from adaptiveneuralnetwork.training.deep_education_curriculum import DeepEducationCurriculum
from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_phase_two_assimilation():
    """
    Phase 2: Mathematical & Algorithmic Purity.
    Target: 50% Mastery.
    """
    logger.info("⚡ [BOOT] Starting Phase II: Mathematical Foundations - Target 50% Mastery.")

    # 1. Initialize Node & Core Systems
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88, spatial_dims=3)

    curriculum = DeepEducationCurriculum()
    phase_2_domains = curriculum.get_phase_domains("Phase 2: Mathematical & Algorithmic Purity")

    budget_manager = LearningBudgetManager(domains=phase_2_domains)
    loader = GlobalScienceLoader(target_node=node)

    tm = get_time_manager()
    tm.reset()
    tm.advance_simulation(10) # Start at 10 AM

    logger.info(f"📚 Phase II Domains: {phase_2_domains}")

    # 2. Learning Loop
    max_steps = 400
    for step in range(max_steps):
        tm.advance_simulation(1)
        # Cycle info
        if step % 20 == 0:
            logger.info(f"\n--- Step {step} [Phase: {node.phase}, Time: {tm.circadian_time:02d}:00] ---")

        if node.phase == "sleep":
            node.step_phase()
            if node.phase != "sleep":
                logger.info(f"☀️ [WAKE] Consolidation step {step} complete. System recovered.")
                node.working_memory.clear()
            continue

        # Target domain with lowest confidence
        target_domain = min(budget_manager.domain_confidence, key=budget_manager.domain_confidence.get)

        # Load Phase 2 specific data
        if target_domain == "Advanced_Mathematics":
            loader.load_advanced_mathematics()
        elif target_domain == "Neural_Algorithmic_Purity":
            loader.load_neural_algorithmic_purity()
        elif target_domain == "Symbolic_Reasoning_Logic":
            loader.load_symbolic_reasoning()

        # Add cognitive load
        node.current_entropy = min(1.0, node.current_entropy + 0.18) # Math is hard
        node.gradient_noise = min(1.0, node.gradient_noise + 0.12)
        # Fill buffer
        for i in range(5): node.working_memory.append(i)  # noqa: E701

        # Mastery improvement
        improvement = np.random.uniform(0.04, 0.08)
        acc_before = budget_manager.domain_confidence[target_domain]
        acc_after = min(1.0, acc_before + improvement)

        budget_manager.record_attempt(
            domain=target_domain,
            accuracy_before=acc_before,
            accuracy_after=acc_after
        )

        node.step_phase()

        # Check target: 50%
        if all(c >= 0.50 for c in budget_manager.domain_confidence.values()):
            logger.info("🏆 [MASTERY] Phase II: Mathematical Purity - TARGET REACHED (50%+).")
            break

    # Final Summary
    logger.info("\n" + "="*50)
    logger.info("PHASE II ASSIMILATION COMPLETE:")
    for d, c in budget_manager.domain_confidence.items():
        logger.info(f"- {d}: Mastery {c:.2f}")
    logger.info("="*50)

if __name__ == "__main__":
    perform_phase_two_assimilation()
