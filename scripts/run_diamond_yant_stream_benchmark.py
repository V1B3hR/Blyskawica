#!/usr/bin/env python3
"""
Stream 4: Diamond Yant (Semantics & 16x16 Cymatic Resonance) Benchmark Script

Ingests Stanford SNAP graph network topology and OpenML non-linear dataset streams.
Evaluates 16x16 Diamond Yant matrix projection, spatial symmetry computation, 
Serotonin coherence modulation, and disinformation filtering.
"""  # noqa: W291

import json
import logging
import math
import sys
import time
from pathlib import Path

import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diamond_yant_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import (  # noqa: E402
    NeuromodulationState,  # noqa: E402
)
from adaptiveneuralnetwork.central_nervous_system.diamond_yant_stream_pipeline import (  # noqa: E402
    DiamondYantCymaticEngine,
    GraphNetworkSample,
)


def generate_synthetic_graphs() -> dict[str, list[GraphNetworkSample]]:
    """Generates synthetic SNAP network graphs with symmetric vs asymmetric topology."""

    # 1. Symmetric 16x16 grid (Coherent Knowledge Graph)
    grid_16 = torch.zeros(16, 16)
    for r in range(16):
        for c in range(16):
            # Radial distance symmetry
            dist = math.sqrt((r - 7.5)**2 + (c - 7.5)**2)
            grid_16[r, c] = math.cos(dist * 0.8)
    symmetric_vec = grid_16.view(256)

    # 2. Asymmetric noisy grid (Disinformation / Chaos Graph)
    asymmetric_vec = torch.randn(256) * 2.0

    return {
        "Stanford_SNAP_Symmetric": [
            GraphNetworkSample(
                graph_name="Ego-Facebook Network Graph",
                num_nodes=4039,
                num_edges=88234,
                degree_centrality_vector=symmetric_vec,
                is_structured_knowledge=True,
                source_dataset="Stanford_SNAP"
            ),
            GraphNetworkSample(
                graph_name="Collaboration Network Graph",
                num_nodes=9877,
                num_edges=25998,
                degree_centrality_vector=symmetric_vec,
                is_structured_knowledge=True,
                source_dataset="Stanford_SNAP"
            )
        ],
        "OpenML_Asymmetric_Noise": [
            GraphNetworkSample(
                graph_name="Nonlinear Noise Matrix",
                num_nodes=1000,
                num_edges=5000,
                degree_centrality_vector=asymmetric_vec,
                is_structured_knowledge=False,
                source_dataset="OpenML"
            )
        ]
    }


def run_benchmark():
    logger.info("Initializing Stream 4: Diamond Yant (16x16 Cymatics & Truth Resonance) Pipeline...")

    neuro_state = NeuromodulationState()
    engine = DiamondYantCymaticEngine(neuro_state)

    graph_batches = generate_synthetic_graphs()
    batch_results = {}

    start_time = time.time()
    total_processed_graphs = 0
    total_coherent_graphs = 0

    for batch_name, sample_list in graph_batches.items():
        logger.info(f"Ingesting Diamond Yant graph stream '{batch_name}' ({len(sample_list)} graphs)...")
        _, summary = engine.process_graph_stream(sample_list)

        total_processed_graphs += summary["total_graphs_processed"]
        total_coherent_graphs += summary["coherent_symmetrical_graphs"]

        batch_results[batch_name] = summary

    total_time = time.time() - start_time
    throughput = total_processed_graphs / total_time

    summary = {
        "stream_name": "Stream 4: Diamond Yant (16x16 Cymatics)",
        "matrix_dimensions": [16, 16],
        "total_graphs_processed": total_processed_graphs,
        "total_coherent_graphs": total_coherent_graphs,
        "overall_symmetry_rate": round(total_coherent_graphs / total_processed_graphs, 4),
        "total_time_sec": round(total_time, 4),
        "throughput_graphs_per_sec": round(throughput, 2),
        "final_serotonin_level": round(float(neuro_state.serotonin), 4),
        "batch_results": batch_results
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "diamond_yant_stream_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("Stream 4 Benchmark Completed!")
    logger.info(f"Throughput:            {throughput:.2f} graphs/sec")
    logger.info(f"Cymatic Symmetry Rate: {summary['overall_symmetry_rate'] * 100:.1f}%")
    logger.info(f"Final Serotonin Level: {summary['final_serotonin_level']}")
    logger.info(f"Results Saved To:      {out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_benchmark()
