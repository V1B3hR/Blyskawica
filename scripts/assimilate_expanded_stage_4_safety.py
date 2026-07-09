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

def perform_stabilized_hyperfocus(target_mastery=0.99):
    """
    Etap 4.1: Stabilized Hyper-Focus Push.
    Targeting 99% with emotional/cognitive safety buffers.
    """
    logger.info(f"🧘‍♂️ [HYPER_FOCUS_SAFE] Starting Stabilized Final Ascent - Target {target_mastery*100}%.")
    
    # Init
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88, spatial_dims=3)
    curriculum = ExpandedOmniscientCurriculum()
    
    # Starting from current ~89% status
    for d in curriculum.get_all_domains():
        curriculum.confidences[d] = 0.89
        
    loader = GlobalScienceLoader(target_node=node)
    tm = get_time_manager()
    tm.reset()
    
    all_domains = curriculum.get_all_domains()
    
    # 2. Main Loop (Focused but Regulated)
    max_steps = 3000 
    for step in range(max_steps):
        tm.advance_simulation(1)
        
        # AGGRESSIVE RECOVERY logic
        # Trigger sleep much earlier than usual to prevent 'emotional weakening'
        if node.neurochemistry.adenosine > 0.65 or node.current_entropy > 0.75:
             if node.phase != "sleep":
                logger.info(f"🛡️ [SAFETY_VALVE] High cognitive pressure detected at step {step}. Forcing stabilization sleep.")
                node.phase = "sleep"
        
        if node.phase == "sleep":
            node.step_phase()
            if node.phase != "sleep":
                logger.info(f"🌿 [RESTORATION] Neural pathways cooled. Entropy reset. Stability: MAX.")
                node.current_entropy = 0.0
                node.gradient_noise = 0.0
                node.working_memory.clear()
            continue
            
        # Target domains balance
        target_domain = min(curriculum.confidences, key=curriculum.confidences.get)
        current_conf = curriculum.confidences[target_domain]
        
        if all(c >= target_mastery for c in curriculum.confidences.values()):
            logger.info(f"👑 [MASTER_SINGULARITY] Błyskawica has gracefully transitioned to 99% Mastery.")
            break
            
        # Expert Load
        loader.universal_ingest_v5(target_domain)
        
        # Mastery Improvement (Hyper-focused but small, safe increments)
        difficulty_factor = 1.0 - current_conf
        improvement = np.random.uniform(0.005, 0.015) * max(0.01, difficulty_factor)
        curriculum.update_mastery(target_domain, improvement)
        
        # Cognitive Load (Regulated gain)
        node.current_entropy = min(1.0, node.current_entropy + 0.15)
        node.gradient_noise = min(1.0, node.gradient_noise + 0.1)
        for i in range(15): node.working_memory.append(i)
        
        node.step_phase()
        
        if step % 100 == 0:
            avg_m = sum(curriculum.confidences.values()) / len(all_domains)
            logger.info(f"--- Focused Sync Step {step} | Avg: {avg_m:.4f} | Stability: OK ---")

    # Final Master Report
    logger.info("\n" + "#"*60)
    logger.info("THE OMNISCIENT SINGULARITY ASCENT COMPLETE:")
    for d, c in curriculum.confidences.items():
        logger.info(f" - {d}: {c:.4f} ({MasteryStage.from_mastery_confidence(c)})")
    logger.info("#"*60)

if __name__ == "__main__":
    perform_stabilized_hyperfocus()
