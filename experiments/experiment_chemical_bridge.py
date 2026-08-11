"""
Trial #21: The Chemical Bridge
Integrates Chemistry as a bridge between Physics and Biology.
Tests Triple-Modal Synthesis + Dynamic Plasticity.
"""

import logging

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from adaptiveneuralnetwork.applications.multimodal_continual_learning import (
    ContinualLearningConfig,
    MultimodalContinualLearningSystem,
    VisionLanguageConfig,
)
from adaptiveneuralnetwork.central_nervous_system.neuromorphic_v3.temporal_coding import (
    TemporalConfig,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ChemBridge - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_triple_modal_data(domain="chemistry", num_samples=50):
    """Generate synthetic image, text, and audio data for a specific domain."""
    # 1. Images (224x224 RGB)
    images = torch.randn(num_samples, 3, 224, 224)
    if domain == "biology":
        # Circular patterns (Cells)
        images += torch.exp(-((torch.linspace(-1, 1, 224).view(1, 1, 224, 1)**2 +
                              torch.linspace(-1, 1, 224).view(1, 1, 1, 224)**2) / 0.1))
    elif domain == "physics":
        # Linear patterns (Rays)
        images[:, :, 100:120, :] += 2.0
    else:
        # Hexagonal patterns (Chemistry/Benzene)
        x = torch.linspace(-1, 1, 224)
        y = torch.linspace(-1, 1, 224)
        grid_x, grid_y = torch.meshgrid(x, y, indexing='ij')
        # Simple hexagonal approximation
        hex_pattern = (torch.abs(grid_x) + torch.abs(0.5*grid_x + 0.86*grid_y) + torch.abs(0.5*grid_x - 0.86*grid_y)) < 0.5
        images += hex_pattern.view(1, 1, 224, 224).float()

    # 2. Text (Sequence of tokens)
    text_tokens = torch.randint(0, 1000, (num_samples, 32))

    # 3. Audio (Spectrogram: 256 frequency bins)
    audio = torch.zeros(num_samples, 256)
    if domain == "biology":
        audio[:, 10:20] = 1.0 # Heartbeat
    elif domain == "physics":
        for i in range(num_samples):
            audio[i, i % 200 : (i % 200) + 50] = 1.0 # Doppler sweep
    else:
        # IR Spectrum - multiple sharp peaks
        audio[:, 40:45] = 1.0
        audio[:, 120:125] = 1.0
        audio[:, 200:205] = 1.0

    # 4. Labels (0: Bio, 1: Phys, 2: Chem)
    if domain == "biology": labels = torch.zeros(num_samples, dtype=torch.long)  # noqa: E701
    elif domain == "physics": labels = torch.ones(num_samples, dtype=torch.long)  # noqa: E701
    else: labels = torch.full((num_samples,), 2, dtype=torch.long)  # noqa: E701

    return images, text_tokens, audio, labels

def run_trial_21():
    logger.info("--- Starting Trial #21: The Chemical Bridge ---")

    # 1. Setup Configurations (Increased output_size to 3)
    vl_config = VisionLanguageConfig(fusion_dim=384, num_attention_heads=12)
    vl_config.audio_feature_dim = 256

    cl_config = ContinualLearningConfig(
        input_size=256,
        hidden_layers=[512, 256],
        output_size=3,
        enable_sparse_coding=True,
        synaptic_consolidation=True,
        consolidation_strength=5.0 # Strong base consolidation
    )

    temporal_config = TemporalConfig(pattern_window=0.05, oscillation_frequencies=[40.0])

    # 2. Initialize System
    system = MultimodalContinualLearningSystem(vl_config, cl_config, temporal_config)

    # 3. Sequence: Biology -> Physics -> Chemistry
    # Note: Physics failed in Trial 20 because of "Catastrophic Stability".
    # Now we test if Dynamic Plasticity fixes it.

    domains = ["biology", "physics", "chemistry"]
    loaders = []

    for i, domain in enumerate(domains):
        logger.info(f"Learning Task {i}: {domain.capitalize()}")
        img, txt, aud, lbl = generate_triple_modal_data(domain)
        loader = DataLoader(TensorDataset(img, txt, aud, lbl), batch_size=16, shuffle=True)
        loaders.append(loader)

        system.learn_task(loader, task_id=i, epochs=4) # 4 epochs per domain

        # Evaluate current domain
        acc = system.evaluate_task(loader)
        logger.info(f"Accuracy on {domain.capitalize()} after training: {acc*100:.2f}%")

    # 4. Final Knowledge Retention Test (The Bridge)
    logger.info("--- Final Multi-Domain Evaluation ---")
    results = {}
    for i, domain in enumerate(domains):
        results[domain] = system.evaluate_task(loaders[i])
        logger.info(f"Accuracy on {domain.capitalize()} (Final): {results[domain]*100:.2f}%")

    avg_acc = np.mean(list(results.values()))
    logger.info(f"Average Mastery Level: {avg_acc*100:.2f}%")

    if avg_acc > 0.6:
        logger.info("✅ SUCCESS: The Chemical Bridge is established. Multimodal sciences are connected.")
    else:
        logger.warning("⚠️ WARNING: Knowledge imbalance detected. Further refinement of Plasticity mechanism needed.")

if __name__ == "__main__":
    run_trial_21()
