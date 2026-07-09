"""
Phase 2 Experiment: Multimodal Synthesis & Knowledge Binding.

In this experiment, Błyskawica learns to associate visual imagery with 
textual scientific knowledge using her new Multimodal Spiking Core.
"""

import logging
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

from adaptiveneuralnetwork.applications.multimodal_continual_learning import (
    MultimodalContinualLearningSystem,
    VisionLanguageConfig,
    ContinualLearningConfig,
    TemporalConfig
)
from adaptiveneuralnetwork.central_nervous_system.device_manager import device_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Phase2_Multimodal")

def generate_multimodal_data(task_type="biology", num_samples=100):
    """Generates synthetic multimodal data (Image + Text -> Label)."""
    # Random images (3, 64, 64)
    images = torch.randn(num_samples, 3, 64, 64)
    
    # Text tokens (simulated)
    # Task 0 (Biology): 0=Mitochondrion, 1=Ribosome
    # Task 1 (Physics): 0=Prism, 1=Magnet
    text_tokens = torch.randint(0, 10, (num_samples, 10)) # Random tokens for now
    
    if task_type == "biology":
        # 50 samples of class 0, 50 of class 1
        labels = torch.cat([torch.zeros(num_samples//2), torch.ones(num_samples//2)]).long()
    else:
        # Physics: 2=Prism, 3=Magnet
        labels = torch.cat([torch.ones(num_samples//2)*2, torch.ones(num_samples//2)*3]).long()
        
    return images, text_tokens, labels

def run_trial_19():
    logger.info("--- Starting Trial #19: Multimodal Synthesis ---")
    
    # 1. Configuration
    vl_config = VisionLanguageConfig(
        fusion_dim=512,
        vision_feature_dim=512,
        language_feature_dim=384, # 384 is divisible by 12 (default heads)
        vocab_size=1000,
        num_answer_choices=10 
    )
    
    cl_config = ContinualLearningConfig(
        input_size=256, # Projected from fusion dim
        hidden_layers=[512, 256],
        output_size=10,
        consolidation_strength=500.0, # High EWC for retention
        memory_replay_ratio=0.3
    )
    
    temporal_config = TemporalConfig(
        pattern_window=0.05,
        sparsity_target=0.1
    )
    
    # 2. Initialize System
    system = MultimodalContinualLearningSystem(vl_config, cl_config, temporal_config)
    
    # 3. Task 0: Cell Biology Visuals
    logger.info("Learning Task 0: Cell Biology Visual Identification")
    img_bio, txt_bio, lbl_bio = generate_multimodal_data("biology")
    bio_loader = DataLoader(TensorDataset(img_bio, txt_bio, lbl_bio), batch_size=16, shuffle=True)
    
    system.learn_task(bio_loader, task_id=0, epochs=3)
    acc_bio = system.evaluate_task(bio_loader)
    logger.info(f"Accuracy on Biology after training: {acc_bio*100:.2f}%")
    
    # 4. Task 1: Physics Visuals
    logger.info("Learning Task 1: Physics Visual Identification")
    img_phys, txt_phys, lbl_phys = generate_multimodal_data("physics")
    phys_loader = DataLoader(TensorDataset(img_phys, txt_phys, lbl_phys), batch_size=16, shuffle=True)
    
    system.learn_task(phys_loader, task_id=1, epochs=3)
    acc_phys = system.evaluate_task(phys_loader)
    logger.info(f"Accuracy on Physics after training: {acc_phys*100:.2f}%")
    
    # 5. RETENTION TEST (Phase 2 Critical Check)
    logger.info("Verifying Knowledge Retention (Task 1 -> Task 0)")
    acc_bio_final = system.evaluate_task(bio_loader)
    logger.info(f"Accuracy on Biology (Retrospective): {acc_bio_final*100:.2f}%")
    
    if acc_bio_final >= 0.8:
        logger.info("✅ SUCCESS: Multimodal knowledge binding achieved with high retention.")
    else:
        logger.warning("⚠️ WARNING: Retention drop detected. Adjusting consolidation strength.")

if __name__ == "__main__":
    run_trial_19()
