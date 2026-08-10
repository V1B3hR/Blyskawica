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

def perform_assimilation_cycle():
    """
    Phase 9: High-Velocity Polifazic Assimilation Cycle.
    Demonstrates Błyskawica's transition through Phase I of the Omniscient Assimilation Chain.
    """
    logger.info("⚡ [BOOT] Starting Phase I: Silicon Foundations - Omniscient Assimilation.")

    # 1. Initialize Node & Core Systems
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88, spatial_dims=3)

    curriculum = DeepEducationCurriculum()
    phase_1_domains = curriculum.get_phase_domains("Phase 1: Silicon & Digital Foundations")

    budget_manager = LearningBudgetManager(domains=phase_1_domains)
    loader = GlobalScienceLoader(target_node=node)

    # 2. Time Synchronization (Setting to 'Daylight' for start)
    tm = get_time_manager()
    tm.reset()
    tm.advance_simulation(10) # 10:00 AM

    logger.info(f"📚 Curriculum loaded. Phase I Domains: {phase_1_domains}")

    # 3. Learning Loop: Ingest until Micro-Sleep
    max_steps = 500 # Increase to be safe
    for step in range(max_steps):
        tm.advance_simulation(1)
        logger.info(f"\n--- Cycle Step {step} [Phase: {node.phase}, Time: {tm.circadian_time:02d}:00] ---")

        if node.phase == "sleep":
            logger.info("🛌 [CONSOLIDATION] Node is in Micro-Sleep. Performing cognitive EMA Merges and Data Synthesis...")
            # Simulate recovery and consolidation
            node.step_phase()
            if node.phase != "sleep":
                logger.info("☀️ [WAKE] Consolidation complete. System is fresh.")
                # Reset cognitive load after sleep
                node.current_entropy = 0.0
                node.gradient_noise = 0.0
                node.working_memory.clear()
            continue

        # Ingest data for the least mastered domain
        target_domain = min(budget_manager.domain_confidence, key=budget_manager.domain_confidence.get)
        logger.info(f"🎯 Target Domain: {target_domain} (Confidence: {budget_manager.domain_confidence[target_domain]:.2f})")

        # Simulate high-intensity learning (generates entropy and noise)
        payload = {}
        if target_domain == "Electronics_LowLevel":
            payload = loader.load_electronics_low_level()
        elif target_domain == "Software_Architecture":
            payload = loader.load_software_architecture_deep()
        elif target_domain == "Cybersecurity_Intelligence":
            payload = loader.load_cybersecurity_intelligence()  # noqa: F841

        # Inject "Learning Fatigue" (Entropy and Noise)
        node.current_entropy = min(1.0, node.current_entropy + 0.15)
        node.gradient_noise = min(1.0, node.gradient_noise + 0.1)

        # Increase mastery
        improvement = np.random.uniform(0.05, 0.1)
        acc_before = budget_manager.domain_confidence[target_domain]
        acc_after = min(1.0, acc_before + improvement)

        budget_manager.record_attempt(
            domain=target_domain,
            accuracy_before=acc_before,
            accuracy_after=acc_after
        )

        # Step the phase logic (will trigger sleep if entropy is high)
        node.step_phase()

        # Check if we finished Phase I (Target: 70% for all)
        if all(c >= 0.70 for c in budget_manager.domain_confidence.values()):
            logger.info("🏆 [MASTERY] Phase I: Silicon Foundations - TARGET REACHED (70%+).")
            break

    # 4. Final Status
    logger.info("\n" + "="*50)
    logger.info("FINAL ASSIMILATION STATUS:")
    for d, c in budget_manager.domain_confidence.items():
        logger.info(f"- {d}: Mastery {c:.2f}")
    logger.info("="*50)

if __name__ == "__main__":
    perform_assimilation_cycle()
