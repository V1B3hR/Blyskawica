#!/usr/bin/env python3
"""
Stream 2: Cognitive Physics (PINN & Energy Management - Metabolism) Benchmark Script

Ingests simulated CPU sensor & energy telemetry streams modeling UCI sensor and CommonCrawl physics.
Evaluates thermodynamic homeostasis, PINN Fourier heat loss, Dopamine energy throttling, 
and Geometric-Harmonic-Symmetry cymatics.
"""  # noqa: W291

import json
import logging
import random
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("physics_stream_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import (  # noqa: E402
    NeuromodulationState,  # noqa: E402
)
from adaptiveneuralnetwork.cognitive_tools.physics_stream_pipeline import (  # noqa: E402
    CognitivePhysicsEngine,
    TelemetrySensorSample,
)


def generate_synthetic_telemetry(
    dataset_name: str,
    num_samples: int = 50,
    intensity: str = "normal"
) -> list[TelemetrySensorSample]:
    """Generates synthetic telemetry stream modeling UCI CPU sensor data."""
    samples = []
    for _ in range(num_samples):
        if intensity == "high_compute":
            sample = TelemetrySensorSample(
                clock_frequency_ghz=random.uniform(4.2, 5.0),
                cpu_utilization_pct=random.uniform(85.0, 100.0),
                voltage_volts=random.uniform(1.3, 1.45),
                power_draw_watts=random.uniform(180.0, 240.0),
                ambient_temp_celsius=random.uniform(25.0, 30.0),
                source_dataset=dataset_name
            )
        else: # normal
            sample = TelemetrySensorSample(
                clock_frequency_ghz=random.uniform(2.0, 3.5),
                cpu_utilization_pct=random.uniform(15.0, 45.0),
                voltage_volts=random.uniform(0.9, 1.1),
                power_draw_watts=random.uniform(35.0, 85.0),
                ambient_temp_celsius=random.uniform(20.0, 25.0),
                source_dataset=dataset_name
            )
        samples.append(sample)
    return samples


def run_benchmark():
    logger.info("Initializing Stream 2: Cognitive Physics (PINN & Digital Metabolism) Pipeline...")

    neuro_state = NeuromodulationState()
    engine = CognitivePhysicsEngine(neuro_state, thermal_ceiling=85.0)

    datasets = ["UCI_Sensors", "CommonCrawl_Physics"]
    stream_results = {}

    start_time = time.time()
    total_processed_samples = 0
    throttling_events = 0

    for ds_name in datasets:
        logger.info(f"Ingesting physics telemetry stream for dataset '{ds_name}'...")

        # 1. Normal compute baseline (50 samples)
        normal_samples = generate_synthetic_telemetry(ds_name, num_samples=50, intensity="normal")
        _, normal_metrics = engine.step_metabolism(normal_samples)

        # 2. High-compute load surge (100 samples - triggers temperature rise & thermal throttling)
        heavy_samples = generate_synthetic_telemetry(ds_name, num_samples=100, intensity="high_compute")
        _, heavy_metrics = engine.step_metabolism(heavy_samples)

        total_processed_samples += 150
        if heavy_metrics["is_throttled"]:
            throttling_events += 1

        stream_results[ds_name] = {
            "normal_baseline": normal_metrics,
            "heavy_surge": heavy_metrics
        }

    total_time = time.time() - start_time
    throughput = total_processed_samples / total_time

    summary = {
        "stream_name": "Stream 2: Cognitive Physics (PINN Engine)",
        "datasets_ingested": datasets,
        "total_samples_processed": total_processed_samples,
        "total_time_sec": round(total_time, 4),
        "throughput_samples_per_sec": round(throughput, 2),
        "throttling_events_triggered": throttling_events,
        "final_temperature_celsius": round(engine.current_temperature, 2),
        "final_dopamine_level": round(float(neuro_state.dopamine), 4),
        "stream_results": stream_results
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "physics_stream_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("Stream 2 Benchmark Completed!")
    logger.info(f"Throughput:            {throughput:.2f} samples/sec")
    logger.info(f"Throttling Events:     {throttling_events}/{len(datasets)}")
    logger.info(f"Final Temperature:     {summary['final_temperature_celsius']} °C")
    logger.info(f"Results Saved To:      {out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_benchmark()
