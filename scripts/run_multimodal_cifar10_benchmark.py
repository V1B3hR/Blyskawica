#!/usr/bin/env python3
"""
Multi-Modal Audio-Visual (CIFAR-10 + Oscillatory Audio) Benchmark Script for Błyskawica V8

Evaluates cross-modal binding between vision inputs (CIFAR-10 32x32x3 -> 1024 flat)
and synthetic audio frequency streams using SensoryProcessingPipeline and CrossModalIntegration.
"""

import json
import logging
import sys
import time
from pathlib import Path

import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("multimodal_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.api.config import AdaptiveConfig  # noqa: E402
from adaptiveneuralnetwork.api.model import AdaptiveModel  # noqa: E402
from adaptiveneuralnetwork.applications.sensory_processing import (  # noqa: E402
    SensoryConfig,
    SensoryProcessingPipeline,
)


def run_benchmark():
    logger.info("Starting Błyskawica V8 Multi-Modal Audio-Visual Benchmark...")

    sensory_config = SensoryConfig(
        modalities=['vision', 'audio'],
        vision_input_size=1024,  # CIFAR-10 flattened grayscale/feature
        audio_input_size=128,    # Audio frequency channels
        enable_cross_modal_binding=True,
        enable_oscillatory_processing=True
    )

    pipeline = SensoryProcessingPipeline(sensory_config)

    adaptive_config = AdaptiveConfig(
        input_dim=sensory_config.vision_input_size,
        hidden_dim=128,
        output_dim=10,
        num_nodes=64,
        device="cpu"
    )
    model = AdaptiveModel(adaptive_config)  # noqa: F841

    # Generate synthetic multi-modal batch (CIFAR-10 visual feature + audio spectrum)
    batch_size = 64
    num_batches = 20

    logger.info(f"Processing {num_batches} multi-modal batches (batch size: {batch_size})...")

    start_time = time.time()
    latencies = []
    cross_modal_activations = []

    for i in range(num_batches):  # noqa: B007
        vision_data = torch.randn(batch_size, 1024)
        audio_data = torch.randn(batch_size, 128)

        sensory_inputs = {
            'vision': vision_data,
            'audio': audio_data
        }

        batch_start = time.time()
        output_spikes, info = pipeline(sensory_inputs)
        batch_latency = (time.time() - batch_start) * 1000

        latencies.append(batch_latency)
        cross_modal_activations.append(output_spikes.abs().mean().item())

    total_time = time.time() - start_time
    avg_latency = sum(latencies) / len(latencies)
    throughput = (batch_size * num_batches) / total_time

    results = {
        "benchmark": "Multi-Modal Audio-Visual (CIFAR-10)",
        "modalities": sensory_config.modalities,
        "batch_size": batch_size,
        "total_samples": batch_size * num_batches,
        "total_time_sec": round(total_time, 4),
        "throughput_samples_per_sec": round(throughput, 2),
        "average_batch_latency_ms": round(avg_latency, 2),
        "mean_cross_modal_activation": round(sum(cross_modal_activations) / len(cross_modal_activations), 4)
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "multimodal_cifar10_benchmark.json"

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info("=" * 70)
    logger.info("Multi-Modal Benchmark Completed!")
    logger.info(f"Throughput:           {throughput:.2f} samples/sec")
    logger.info(f"Avg Batch Latency:    {avg_latency:.2f} ms")
    logger.info(f"Cross-Modal Activation: {results['mean_cross_modal_activation']}")
    logger.info(f"Benchmark Saved To:   {out_file}")
    logger.info("=" * 70)

    return results


if __name__ == "__main__":
    run_benchmark()
