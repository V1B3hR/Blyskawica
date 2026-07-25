import logging
import sys
sys.stdout.reconfigure(encoding='utf-8')
import torch
import numpy as np
import time
from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.data.science_loader import GlobalScienceLoader
from adaptiveneuralnetwork.training.deep_education_curriculum import DeepEducationCurriculum
from adaptiveneuralnetwork.training.learning_budget import LearningBudgetManager, LearningAttempt
from adaptiveneuralnetwork.central_nervous_system.time_manager import get_time_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_layered_assimilation(start_phase=3, end_phase=7, target_mastery=0.50):
    """
    Omniscient Assimilation Chain - Layered Progress.
    Targets 50% mastery across all specified phases.
    """
    logger.info(f"⚡ [BOOT] Starting Layered Assimilation (Phases {start_phase}-{end_phase}) - Target {target_mastery*100}% Mastery.")
    
    # Init
    pos = torch.zeros(3)
    vel = torch.zeros(3)
    node = AliveLoopNode(position=pos, velocity=vel, node_id=88, spatial_dims=3)
    curriculum = DeepEducationCurriculum()
    loader = GlobalScienceLoader()
    tm = get_time_manager()
    tm.reset()
    
    phases_to_process = [
        ("Phase 3: Harmony & Resonance", "III"),
        ("Phase 4: Spatial & Environmental Systems", "IV"),
        ("Phase 5: Human Macro-Structures", "V"),
        ("Phase 6: Biology, Medicine & Mind", "VI"),
        ("Phase 7: Ethics, Sovereignty & Abstraction", "VII")
    ]
    
    # Filter by requested range
    active_phases = [p for i, p in enumerate(phases_to_process) if i + 3 >= start_phase and i + 3 <= end_phase]
    
    for phase_name, phase_id in active_phases:
        logger.info(f"\n" + "!"*60)
        logger.info(f"🚀 INITIATING {phase_name.upper()}...")
        logger.info("!"*60)
        
        domains = curriculum.get_phase_domains(phase_id)
        if not domains:
            logger.warning(f"No domains found for Phase {phase_id}. Skipping.")
            continue
            
        budget_manager = LearningBudgetManager(domains=domains)
        
        # Assimilate until target reached
        max_steps = 300
        for step in range(max_steps):
            tm.advance_simulation(1)
            
            if node.phase == "sleep":
                node.step_phase()
                if node.phase != "sleep":
                    logger.info(f"☀️ [WAKE] Phase {phase_id} - System fresh at step {step}.")
                continue
            
            # Select target
            target_domain = min(budget_manager.domain_confidence, key=budget_manager.domain_confidence.get)
            
            # Simulated data load (Phase-aware)
            if phase_id == "III": loader.load_it_networking_patterns()
            elif phase_id == "IV": loader.load_os_encyclopedia()
            elif phase_id == "V": loader.load_software_dev_vault()
            elif phase_id == "VI": loader.load_advanced_genetics()
            elif phase_id == "VII": loader.load_advanced_physics()

            # Cognitive friction
            friction = 0.1 + (int(ord(phase_id[-1])) - ord('I')) * 0.05
            node.anxiety = min(1.0, node.anxiety + friction)
            node.gradient_noise = min(1.0, node.gradient_noise + 0.1)
            for i in range(5): node.working_memory.append(i)
            
            # Mastery
            improvement = np.random.uniform(0.05, 0.1)
            acc_before = budget_manager.domain_confidence[target_domain]
            acc_after = min(1.0, acc_before + improvement)
            budget_manager.record_attempt(target_domain, acc_before, acc_after)
            
            node.step_phase()
            
            if all(c >= target_mastery for c in budget_manager.domain_confidence.values()):
                logger.info(f"🏆 [SUCCESS] {phase_name} reached {target_mastery*100}% mastery.")
                break
                
        # Phase switch summary
        logger.info(f"Phase {phase_id} Summary:")
        for d, c in budget_manager.domain_confidence.items():
            logger.info(f"  - {d}: {c:.2f}")

    logger.info("\n" + "#"*60)
    logger.info("OMNISCIENT LAYERED ASSIMILATION COMPLETE.")
    logger.info("#"*60)

if __name__ == "__main__":
    perform_layered_assimilation()
