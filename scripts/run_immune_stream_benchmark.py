#!/usr/bin/env python3
"""
Stream 1: Neuro-Immunological (Wolf Teeth & Immune System) Benchmark Script

Ingests simulated network traffic streams modeling CICIDS2017, UNSW-NB15, and TON_IoT datasets.
Tests Cortisol surge mapping, high-frequency cymatic dissonance detection, and automated 
Wolf Teeth threat quarantine.
"""

import json
import logging
import random
import sys
import time
from pathlib import Path
import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("immune_stream_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from adaptiveneuralnetwork.immune_system.immune_stream_pipeline import (
    NeuroImmunologicalEngine, 
    NetworkFlowSample
)


def generate_synthetic_flow_stream(dataset_name: str, num_samples: int = 100, anomaly_rate: float = 0.2) -> list[NetworkFlowSample]:
    """Generates synthetic time-series network traffic stream modeling CICIDS2017/UNSW/TON_IoT."""
    samples = []
    for _ in range(num_samples):
        is_attack = random.random() < anomaly_rate
        if is_attack:
            # Attack profile: high packet burst, port scan entropy, SYN flood
            sample = NetworkFlowSample(
                flow_duration_ms=random.uniform(10.0, 500.0),
                total_fwd_packets=random.randint(500, 5000),
                total_bwd_packets=random.randint(0, 10),
                flow_bytes_per_sec=random.uniform(1e6, 5e7),
                flow_packets_per_sec=random.uniform(1e4, 1e5),
                syn_flag_count=random.randint(50, 500),
                ack_flag_count=0,
                dst_port_entropy=random.uniform(3.5, 5.0),
                is_anomaly=True,
                source_dataset=dataset_name
            )
        else:
            # Normal network breathing: steady flow, low entropy
            sample = NetworkFlowSample(
                flow_duration_ms=random.uniform(100.0, 5000.0),
                total_fwd_packets=random.randint(5, 50),
                total_bwd_packets=random.randint(5, 50),
                flow_bytes_per_sec=random.uniform(1e3, 5e5),
                flow_packets_per_sec=random.uniform(10, 500),
                syn_flag_count=1,
                ack_flag_count=1,
                dst_port_entropy=random.uniform(0.1, 1.2),
                is_anomaly=False,
                source_dataset=dataset_name
            )
        samples.append(sample)
    return samples


def run_benchmark():
    logger.info("Initializing Stream 1: Neuro-Immunological (Wolf Teeth & Immune System) Pipeline...")

    neuro_state = NeuromodulationState()
    engine = NeuroImmunologicalEngine(neuro_state)

    datasets = ["CICIDS2017", "UNSW-NB15", "TON_IoT"]
    stream_results = {}

    start_time = time.time()
    total_processed_samples = 0
    quarantine_events = 0

    for ds_name in datasets:
        logger.info(f"Ingesting time-series stream for dataset '{ds_name}'...")
        
        # 1. Normal traffic baseline phase (50 samples, 0% anomaly)
        normal_samples = generate_synthetic_flow_stream(ds_name, num_samples=50, anomaly_rate=0.0)
        _, normal_metrics = engine.process_flow_stream(normal_samples)

        # 2. Cyberattack surge phase (50 samples, 80% anomaly spike)
        attack_samples = generate_synthetic_flow_stream(ds_name, num_samples=50, anomaly_rate=0.8)
        _, attack_metrics = engine.process_flow_stream(attack_samples)

        total_processed_samples += 100
        if attack_metrics["threat_active"]:
            quarantine_events += 1

        stream_results[ds_name] = {
            "normal_baseline": normal_metrics,
            "attack_surge": attack_metrics
        }

    total_time = time.time() - start_time
    throughput = total_processed_samples / total_time

    summary = {
        "stream_name": "Stream 1: Neuro-Immunological (Wolf Teeth)",
        "datasets_ingested": datasets,
        "total_samples_processed": total_processed_samples,
        "total_time_sec": round(total_time, 4),
        "throughput_samples_per_sec": round(throughput, 2),
        "quarantine_events_triggered": quarantine_events,
        "final_cortisol_level": round(neuro_state.cortisol.item(), 4),
        "stream_results": stream_results
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "immune_stream_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("Stream 1 Benchmark Completed!")
    logger.info(f"Throughput:            {throughput:.2f} samples/sec")
    logger.info(f"Quarantine Events:     {quarantine_events}/{len(datasets)}")
    logger.info(f"Final Cortisol Level:  {summary['final_cortisol_level']}")
    logger.info(f"Results Saved To:      {out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_benchmark()
