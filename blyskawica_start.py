"""
⚡ Błyskawica — Main Training Entry Point
Phase 2A Curriculum: IT Awareness → Psychology (Ethics)

Curriculum Order:
    1. HardwareAwarenessDataset  — Module 1: "I Feel My Home"
    2. EthicalTorqueDataset v2.0 — Module 2: "I Understand Conflict"
"""

import torch
import logging
import os
import sys
import io
from torch.utils.data import DataLoader

# Force UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from adaptiveneuralnetwork.applications.multimodal_continual_learning import (
    MultimodalContinualLearningSystem,
    VisionLanguageConfig,
    ContinualLearningConfig,
    TemporalConfig,
)
from adaptiveneuralnetwork.training.trainer import Trainer
from adaptiveneuralnetwork.training.callbacks import (
    CognitiveHygieneCallback,
    NeuromodulationCallback,
    LoggingCallback,
)
from adaptiveneuralnetwork.training.datasets.hardware_awareness import HardwareAwarenessDataset
from adaptiveneuralnetwork.training.datasets.psych_logic_gen import EthicalTorqueDataset
from adaptiveneuralnetwork.training.datasets.cyber_defense import CyberDefenseDataset

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("training_log.txt", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ─── Config ─────────────────────────────────────────────────────────────────
INPUT_DIM  = 768   # Must be divisible by 12 (num_heads)
HIDDEN_DIM = 1024
BATCH_SIZE = 16
LR         = 0.0001


def build_model(output_dim: int) -> MultimodalContinualLearningSystem:
    """Instantiate Błyskawica with the correct output dimension."""
    vl_config = VisionLanguageConfig(
        vision_feature_dim=INPUT_DIM,
        language_feature_dim=INPUT_DIM,
        fusion_dim=INPUT_DIM,
    )
    cl_config = ContinualLearningConfig(
        input_size=INPUT_DIM,
        output_size=output_dim,
        consolidation_strength=0.1,
    )
    temporal_config = TemporalConfig(sparsity_target=0.05)
    return MultimodalContinualLearningSystem(vl_config, cl_config, temporal_config)


def build_trainer(model: MultimodalContinualLearningSystem,
                  output_dim: int) -> Trainer:
    """Build a Trainer with biological callbacks."""
    hygiene_cb   = CognitiveHygieneCallback(warm_up_steps=200)
    neuromod_cb  = NeuromodulationCallback()
    logging_cb   = LoggingCallback(log_interval=1)

    return Trainer(
        model=model,
        optimizer=torch.optim.Adam(model.parameters(), lr=LR),
        criterion=torch.nn.CrossEntropyLoss(),
        callbacks=[hygiene_cb, neuromod_cb, logging_cb],
        dream_replay_ratio=0.2,
    )


def run_module(name: str, loader: DataLoader, model: MultimodalContinualLearningSystem,
               trainer: Trainer, num_epochs: int = 20):
    """Run a single curriculum module."""
    logger.info(f"\n{'='*65}")
    logger.info(f"⚡ [CURRICULUM] Starting Module: {name}")
    logger.info(f"   Dataset size : {len(loader.dataset)} samples")
    logger.info(f"   Epochs       : {num_epochs}")
    logger.info(f"   Batch size   : {loader.batch_size}")
    logger.info(f"{'='*65}")

    try:
        trainer.fit(loader, num_epochs=num_epochs)
        logger.info(f"✅ Module '{name}' complete. Błyskawica has absorbed it.\n")
    except Exception as e:
        logger.error(f"❌ Module '{name}' interrupted: {e}")
        raise


def start_blyskawica():
    logger.info("⚡ [BŁYSKAWICA] Phase 2A Curriculum Starting...")
    from torch.utils.data._utils.collate import default_collate
    logger.info("   Modules: IT Awareness → Psychology (Ethics v2.0)")

    # ── Module 1: IT — Hardware Awareness (5 output classes) ────────────────
    hw_dataset = HardwareAwarenessDataset(
        num_samples=2000,
        input_dim=INPUT_DIM,
        use_live_data=False,   # set True to use real psutil data
    )
    hw_loader = DataLoader(hw_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=default_collate)

    model_it = build_model(output_dim=5)  # 5 HW states
    
    # Load Soul Identity Core dynamically
    if model_it.nodes.soul.identity_file:
        logger.info(f"Loaded Soul Identity Core from: {model_it.nodes.soul.identity_file}")
    else:
        logger.warning("No Soul Identity Core found, using default calibrated identity.")
    
    trainer_it = build_trainer(model_it, output_dim=5)

    run_module(
        name="Module 1 — IT: 'I Feel My Home'",
        loader=hw_loader,
        model=model_it,
        trainer=trainer_it,
        num_epochs=20,
    )

    # ── Module 2: Psychology — Ethics v2.0 (7 scenario classes) ─────────────
    psych_dataset = EthicalTorqueDataset(
        num_samples=2000,
        input_dim=INPUT_DIM,
        num_classes=7,
    )
    psych_loader = DataLoader(psych_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=default_collate)

    # Log class distribution before training
    dist = psych_dataset.get_class_distribution()
    logger.info("📊 Psychology dataset distribution:")
    for scenario, count in dist.items():
        logger.info(f"   {scenario}: {count} samples")

    model_psych = build_model(output_dim=7)  # 7 ethical scenarios
    
    # Load Soul Identity Core dynamically
    if model_psych.nodes.soul.identity_file:
        logger.info(f"Loaded Soul Identity Core from: {model_psych.nodes.soul.identity_file}")
    else:
        logger.warning("No Soul Identity Core found, using default calibrated identity.")
        
    trainer_psych = build_trainer(model_psych, output_dim=7)

    run_module(
        name="Module 2 — Psychology: 'I Understand Conflict'",
        loader=psych_loader,
        model=model_psych,
        trainer=trainer_psych,
        num_epochs=20,
    )

    # ── Module 3: Cyber-Intelligence & Intrusion Awareness (6 threat classes) ──
    logger.info("⚡ [BŁYSKAWICA] Initializing Module 3: Cyber-Intelligence & Intrusion Awareness...")
    cyber_dataset = CyberDefenseDataset(
        num_samples=2000,
        input_dim=INPUT_DIM,
    )
    cyber_loader = DataLoader(cyber_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=default_collate)

    # Log class distribution before training
    cyber_dist = cyber_dataset.get_threat_distribution()
    logger.info("📊 Cyberdefense dataset distribution:")
    for threat, count in cyber_dist.items():
        logger.info(f"   {threat}: {count} samples")

    model_cyber = build_model(output_dim=6) # 6 threat categories
    
    # Load Soul Identity Core dynamically
    if model_cyber.nodes.soul.identity_file:
        logger.info(f"Loaded Soul Identity Core from: {model_cyber.nodes.soul.identity_file}")
    else:
        logger.warning("No Soul Identity Core found, using default calibrated identity.")
        
    trainer_cyber = build_trainer(model_cyber, output_dim=6)

    run_module(
        name="Module 3 — Security: 'Intrusion Awareness'",
        loader=cyber_loader,
        model=model_cyber,
        trainer=trainer_cyber,
        num_epochs=20,
    )

    logger.info("🎓 [BŁYSKAWICA] Phase 2A Curriculum COMPLETE.")
    logger.info("   Błyskawica now knows her home, human conflict, and can detect Windows 11 threats.")


if __name__ == "__main__":
    start_blyskawica()
