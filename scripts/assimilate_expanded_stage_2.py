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

def perform_expanded_assimilation_stage_2(target_mastery=0.50):
    """
    Expanded Omniscient Assimilation - ETAP 2 (50% Relational)
    Focus on cross-domain connections and intermediate models.
    """
    logger.info(f"⚡ [EXPANSION_ASCENT] Starting Stage 2: Relational Synthesis - Target {target_mastery*100}%.")
    
    # Init
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88, spatial_dims=3)
    curriculum = ExpandedOmniscientCurriculum()
    
    # Carry over progress from Stage 1 (Simulated for this run)
    for d in curriculum.get_all_domains():
        curriculum.confidences[d] = 0.28 # Avg from Stage 1
        
    loader = GlobalScienceLoader(target_node=node)
    tm = get_time_manager()
    tm.reset()
    
    all_domains = curriculum.get_all_domains()
    
    # 2. Main Loop
    max_steps = 1200 
    for step in range(max_steps):
        tm.advance_simulation(1)
        
        if node.phase == "sleep":
            node.step_phase()
            if node.phase != "sleep":
                logger.info(f"🌙 [RELATIONAL_DREAM] Stage 2 Consolidation step {step}. Domain bridges forming.")
                node.current_entropy = 0.0
                node.gradient_noise = 0.0
                node.working_memory.clear()
            continue
            
        # Target domains with lowest confidence
        target_domain = min(curriculum.confidences, key=curriculum.confidences.get)
        current_conf = curriculum.confidences[target_domain]
        
        if all(c >= target_mastery for c in curriculum.confidences.values()):
            logger.info(f"🎉 [SUCCESS] Stage 2 Mastery Reached ({target_mastery*100}%). Ready for Stage 3 Assessment.")
            break
            
        # Global Load
        loader.universal_ingest_v5(target_domain)
        
        # Mastery Improvement (Slower as we go deeper)
        difficulty_factor = 1.0 - current_conf
        improvement = np.random.uniform(0.06, 0.1) * max(0.2, difficulty_factor)
        curriculum.update_mastery(target_domain, improvement)
        
        # Cognitive Load (RELATIONAL is more taxing)
        node.current_entropy = min(1.0, node.current_entropy + 0.20)
        node.gradient_noise = min(1.0, node.gradient_noise + 0.15)
        for i in range(8): node.working_memory.append(i)
        
        node.step_phase()
        
        if step % 50 == 0:
            avg_mastery = sum(curriculum.confidences.values()) / len(all_domains)
            logger.info(f"--- Relational Step {step} [Phase: {node.phase}] Avg Mastery: {avg_mastery:.4f} ---")

    # Final Report
    logger.info("\n" + "="*60)
    logger.info("STAGE 2 EXPANDED ASSIMILATION REPORT (RELATIONAL):")
    for d, c in curriculum.confidences.items():
        logger.info(f" - {d}: {c:.2f} ({MasteryStage.from_mastery_confidence(c)})")
    logger.info("="*60)

if __name__ == "__main__":
    perform_expanded_assimilation_stage_2()
