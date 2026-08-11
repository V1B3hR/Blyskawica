"""
Trial #22: The Great Tuning (Calibration)
Sweeps hyper-parameters to find the optimal 'Tension' for Błyskawica's 
triple-modal knowledge bridge (Bio, Phys, Chem).
"""  # noqa: W291

import os
import sys

sys.path.append(os.getcwd())

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

# Import data generator from Trial 21
from experiments.experiment_chemical_bridge import generate_triple_modal_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Calibration - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_calibration():
    logger.info("--- Starting Trial #22: The Great Tuning ---")
    torch.autograd.set_detect_anomaly(True)

    # Define candidates for Consolidation Strength (Naciąg)
    # We saw that 5.0 was too stiff. Let's try lighter ones.
    strengths = [0.1, 0.5, 1.0, 2.5]

    results = []

    # Load data once for all trials to ensure consistency
    domains = ["biology", "physics", "chemistry"]
    task_data = {}
    for i, domain in enumerate(domains):
        img, txt, aud, lbl = generate_triple_modal_data(domain, num_samples=30) # Fewer samples for speed
        task_data[i] = DataLoader(TensorDataset(img, txt, aud, lbl), batch_size=16, shuffle=True)

    for strength in strengths:
        logger.info(f"== Testing Consolidation Strength: {strength} ==")

        vl_config = VisionLanguageConfig(fusion_dim=384, num_attention_heads=4)
        vl_config.audio_feature_dim = 256

        cl_config = ContinualLearningConfig(
            input_size=256,
            hidden_layers=[512, 256],
            output_size=3,
            synaptic_consolidation=True,
            consolidation_strength=strength
        )

        temporal_config = TemporalConfig(pattern_window=0.05, oscillation_frequencies=[40.0])

        system = MultimodalContinualLearningSystem(vl_config, cl_config, temporal_config)

        # Train on sequence
        for task_id in range(len(domains)):
            system.learn_task(task_data[task_id], task_id=task_id, epochs=2)

        # Final Evaluation
        accuracies = []
        for task_id in range(len(domains)):
            acc = system.evaluate_task(task_data[task_id])
            accuracies.append(acc)

        avg_acc = np.mean(accuracies)
        logger.info(f"Strength {strength} -> Final Accuracies: {accuracies}, Avg: {avg_acc:.4f}")
        results.append((strength, avg_acc, accuracies))

    # Find best strength
    best_strength, best_avg, best_accs = max(results, key=lambda x: x[1])
    logger.info("--- Calibration Complete ---")
    logger.info(f"🏆 Best Consolidation Strength: {best_strength}")
    logger.info(f"Final Average Mastery: {best_avg*100:.2f}%")
    logger.info(f"Accuracies: [Bio: {best_accs[0]*100:.1f}%, Phys: {best_accs[1]*100:.1f}%, Chem: {best_accs[2]*100:.1f}%]")

if __name__ == "__main__":
    run_calibration()
