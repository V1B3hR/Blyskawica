#!/usr/bin/env python3
"""
Real-Time Telemetry & VR Driving Sensor Stream Benchmark Script for Błyskawica V8

Evaluates high-throughput temporal spike pattern extraction on dynamic 
continuous telemetry sensor streams using Neuromorphic Temporal Encoders and C.R.A.
"""  # noqa: W291

import json
import logging
import sys
import time
from pathlib import Path

import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vr_driving_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.neuromorphic.temporal_coding import (  # noqa: E402
    TemporalConfig,
    TemporalPatternEncoder,
)


def run_benchmark():
    logger.info("Starting Błyskawica V8 Real-Time Telemetry / VR Driving Benchmark...")

    temporal_config = TemporalConfig(
        pattern_window=0.05,
        max_pattern_length=20,
        phase_resolution=8
    )

    sensor_channels = 256  # High-density vehicle telemetry (steering, velocity, lidar distance, gaze)
    pattern_encoder = TemporalPatternEncoder(
        input_size=sensor_channels,
        pattern_size=64,
        config=temporal_config
    )

    batch_size = 128
    time_steps = 100  # 100 continuous temporal ticks

    logger.info(f"Simulating VR Driving telemetry stream: {time_steps} time steps, {sensor_channels} channels, batch size {batch_size}...")

    start_time = time.time()
    step_latencies = []
    spike_rates = []

    for step in range(time_steps):
        # Continuous sensor stream with smooth temporal dynamics + noise spikes
        current_time = step * 0.01
        raw_telemetry = torch.sin(torch.linspace(0, 10, sensor_channels) + current_time).unsqueeze(0).repeat(batch_size, 1)
        raw_telemetry += torch.randn_like(raw_telemetry) * 0.1

        t_start = time.time()
        pattern_output, info = pattern_encoder(raw_telemetry, current_time)
        step_latency = (time.time() - t_start) * 1000

        step_latencies.append(step_latency)
        spike_rates.append(pattern_output.abs().mean().item())

    total_time = time.time() - start_time
    total_ticks = batch_size * time_steps
    throughput = total_ticks / total_time
    avg_step_latency = sum(step_latencies) / len(step_latencies)

    results = {
        "benchmark": "VR Driving & Telemetry Sensor Stream",
        "sensor_channels": sensor_channels,
        "batch_size": batch_size,
        "total_time_steps": time_steps,
        "total_telemetry_ticks": total_ticks,
        "total_time_sec": round(total_time, 4),
        "throughput_ticks_per_sec": round(throughput, 2),
        "average_step_latency_ms": round(avg_step_latency, 3),
        "mean_pattern_spike_rate": round(sum(spike_rates) / len(spike_rates), 4)
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "vr_driving_telemetry_benchmark.json"

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info("=" * 70)
    logger.info("VR Driving Telemetry Benchmark Completed!")
    logger.info(f"Throughput:           {throughput:.2f} ticks/sec")
    logger.info(f"Avg Step Latency:     {avg_step_latency:.3f} ms")
    logger.info(f"Mean Spike Rate:      {results['mean_pattern_spike_rate']}")
    logger.info(f"Benchmark Saved To:   {out_file}")
    logger.info("=" * 70)

    return results


if __name__ == "__main__":
    run_benchmark()
