#!/usr/bin/env python3
"""
Continual Learning (Split-MNIST) Benchmark Script for Błyskawica V8

Executes a 5-task sequential learning benchmark evaluating:
- Per-task classification accuracy
- Backward Transfer (BWT) & Forgetting rate
- C.R.A. Digital Sabbath memory consolidation
"""

import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("continual_benchmark")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.api.config import AdaptiveConfig  # noqa: E402
from adaptiveneuralnetwork.api.model import AdaptiveModel  # noqa: E402
from adaptiveneuralnetwork.training.continual import (  # noqa: E402
    ablation_study_sleep_phases,
    split_mnist_benchmark,
)


def run_benchmark():
    logger.info("Starting Błyskawica V8 Continual Learning (Split-MNIST) Benchmark...")

    config = AdaptiveConfig(
        input_dim=784,
        hidden_dim=128,
        output_dim=10,
        num_nodes=64,
        num_epochs=2,
        batch_size=64,
        device="cpu"
    )

    model = AdaptiveModel(config)

    # 1. Run 5-Task Split-MNIST Benchmark
    logger.info("Executing 5-Task Split-MNIST Continual Benchmark...")
    results = split_mnist_benchmark(model, config, num_tasks=5, use_synthetic=True)

    # 2. Run Sleep-Phase Memory Consolidation Ablation Study
    logger.info("Executing Sleep-Phase Memory Consolidation Ablation Study...")
    ablation_results = ablation_study_sleep_phases(config)

    # Output directory setup
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "split_mnist_continual_benchmark.json"

    combined_results = {
        "continual_learning": results,
        "sleep_ablation": ablation_results
    }

    with open(out_file, "w") as f:
        json.dump(combined_results, f, indent=2)

    logger.info("=" * 70)
    logger.info("Split-MNIST Benchmark Completed!")
    logger.info(f"Final Average Accuracy: {results.get('final_average_accuracy', 0.0):.4f}")
    logger.info(f"Total Forgetting Rate:  {results.get('total_forgetting', 0.0):.4f}")
    logger.info(f"Benchmark Saved To:     {out_file}")
    logger.info("=" * 70)

    return combined_results


if __name__ == "__main__":
    run_benchmark()
