import logging

import numpy as np
import torch

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.central_nervous_system.time_manager import get_time_manager
from adaptiveneuralnetwork.data.science_loader import GlobalScienceLoader
from adaptiveneuralnetwork.training.deep_synthesis_curriculum import DeepSynthesisCurriculum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_deep_synthesis_stage_1(target_mastery=0.25):
    """
    Deep Synthesis Assimilation - ETAP 1 (25% Foundations)
    100 Domains x 10 specialized clusters.
    """
    logger.info(f"🏗️ [DEEP_SYN_BOOT] Starting Stage 1: World Construction Foundations - Target {target_mastery*100}%.")

    # Init
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88)
    curriculum = DeepSynthesisCurriculum()
    loader = GlobalScienceLoader(target_node=node)
    tm = get_time_manager()
    tm.reset()

    all_domains = curriculum.get_all_domains()
    logger.info(f"📊 Matrix initialized with {len(all_domains)} technical/biological domains.")

    # 2. Main Loop
    max_steps = 2000 # 100 domains require more steps
    for step in range(max_steps):
        tm.advance_simulation(1)

        if node.phase == "sleep":
            node.step_phase()
            if node.phase != "sleep":
                logger.info(f"🌙 [TECH_CONSOLIDATION] Stage 1 step {step}. Mechanical and Biological blueprints stabilizing.")
                node.current_entropy = 0.0
                node.gradient_noise = 0.0
                node.working_memory.clear()
            continue

        # Target domains with lowest confidence
        target_domain = min(curriculum.confidences, key=curriculum.confidences.get)
        current_conf = curriculum.confidences[target_domain]  # noqa: F841

        if all(c >= target_mastery for c in curriculum.confidences.values()):
            logger.info(f"🎉 [SUCCESS] Stage 1 Deep Synthesis Reached ({target_mastery*100}%).")
            break

        # Global Load
        loader.universal_ingest_v5(target_domain)

        # Mastery Improvement (Initial ingestion is fast)
        improvement = np.random.uniform(0.08, 0.12)
        curriculum.update_mastery(target_domain, improvement)

        # Cognitive Load (Engineering specificity is high entropy)
        node.current_entropy = min(1.0, node.current_entropy + 0.20)
        node.gradient_noise = min(1.0, node.gradient_noise + 0.15)
        for i in range(10): node.working_memory.append(i)  # noqa: E701

        node.step_phase()

        if step % 100 == 0:
            avg_mastery = sum(curriculum.confidences.values()) / len(all_domains)
            logger.info(f"--- Deep Syn Step {step} [Phase: {node.phase}] Avg Mastery: {avg_mastery:.4f} ---")

    # Final Report
    logger.info("\n" + "="*60)
    logger.info("STAGE 1 DEEP SYNTHESIS REPORT (FOUNDATIONS):")
    for d, c in curriculum.confidences.items():
        if c > 0:
            logger.info(f" - {d}: {c:.2f}")
    logger.info("="*60)

if __name__ == "__main__":
    perform_deep_synthesis_stage_1()
