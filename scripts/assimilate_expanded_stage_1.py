import logging
import torch
import numpy as np
from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.data.science_loader import GlobalScienceLoader
from adaptiveneuralnetwork.training.expanded_curriculum import ExpandedOmniscientCurriculum, MasteryStage
from adaptiveneuralnetwork.central_nervous_system.time_manager import get_time_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_expanded_assimilation_stage_1(target_mastery=0.25):
    """
    Expanded Omniscient Assimilation - ETAP 1 (25% Foundations)
    35 Domains x 7 Sub-points.
    """
    logger.info(f"⚡ [EXPANSION_BOOT] Starting Stage 1: Holographic Foundations - Target {target_mastery*100}%.")
    
    # Init
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88, spatial_dims=3)
    curriculum = ExpandedOmniscientCurriculum()
    loader = GlobalScienceLoader(target_node=node)
    tm = get_time_manager()
    tm.reset()
    
    all_domains = curriculum.get_all_domains()
    logger.info(f"📊 Matrix initialized with {len(all_domains)} high-order domains.")
    
    # 2. Main Loop
    max_steps = 1000 # Large material volume
    for step in range(max_steps):
        tm.advance_simulation(1)
        
        if node.phase == "sleep":
            node.step_phase()
            if node.phase != "sleep":
                logger.info(f"🌙 [SYNTHESIS_DREAM] Stage 1 Consolidation step {step}. Wide-angle patterns stabilizing.")
                node.current_entropy = 0.0
                node.gradient_noise = 0.0
                node.working_memory.clear()
            continue
            
        # Target domains with lowest confidence
        target_domain = min(curriculum.confidences, key=curriculum.confidences.get)
        current_conf = curriculum.confidences[target_domain]
        
        if all(c >= target_mastery for c in curriculum.confidences.values()):
            logger.info(f"🎉 [SUCCESS] Stage 1 Mastery Reached ({target_mastery*100}%). Foundations ready for Stage 2.")
            break
            
        # Load specialized data
        loader.universal_ingest_v5(target_domain)
        
        # Mastery Improvement (Broad ingestion is faster initially)
        improvement = np.random.uniform(0.1, 0.15) 
        curriculum.update_mastery(target_domain, improvement)
        
        # Cognitive Load (Broad horizontal learning is stressful)
        node.current_entropy = min(1.0, node.current_entropy + 0.18)
        node.gradient_noise = min(1.0, node.gradient_noise + 0.12)
        for i in range(5): node.working_memory.append(i)
        
        node.step_phase()
        
        if step % 50 == 0:
            avg_mastery = sum(curriculum.confidences.values()) / len(all_domains)
            logger.info(f"--- Expansion Step {step} [Phase: {node.phase}] Avg Mastery: {avg_mastery:.4f} ---")

    # Final Report
    logger.info("\n" + "="*60)
    logger.info("STAGE 1 EXPANDED ASSIMILATION REPORT:")
    for d, c in curriculum.confidences.items():
        if c > 0:
            logger.info(f" - {d}: {c:.2f} ({MasteryStage.from_mastery_confidence(c)})")
    logger.info("="*60)

if __name__ == "__main__":
    perform_expanded_assimilation_stage_1()
