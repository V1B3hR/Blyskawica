#!/usr/bin/env python3
"""
Hybrid Vibe Telemetry & Bio-Quantum KEGG Benchmark Script for Błyskawica V8

Executes end-to-end benchmark testing:
- Live Vibe Telemetry Bridge aggregation across all 4 streams
- Microtubule Quantum Coherence survival times (in picoseconds)
- KEGG Cellular ATP energy output (Glycolysis + TCA + OxPhos)
"""

import json
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hybrid_vibe_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.bio_quantum_kegg_pipeline import (  # noqa: E402
    BioQuantumKEGGPipeline,
)
from blyskawica_app.backend.vibe_telemetry_bridge import vibe_telemetry_bridge  # noqa: E402


def run_benchmark():
    logger.info("Initializing Hybrid Vibe Telemetry & Bio-Quantum KEGG Benchmark...")

    bq_pipeline = BioQuantumKEGGPipeline(vibe_telemetry_bridge.neuro_state)

    start_time = time.time()

    # 1. Quantum Phonon & KEGG Metabolic Step
    logger.info("Simulating Microtubule Quantum Phonon Coherence & KEGG ATP Yield...")
    bio_quantum_metrics = bq_pipeline.step_bio_quantum(glucose_flux=2.0)

    # 2. Live Telemetry Bridge Snapshot
    logger.info("Capturing live backend telemetry snapshot across all 4 Vibe Streams...")
    telemetry_snapshot = vibe_telemetry_bridge.get_live_vibe_state()

    total_time = time.time() - start_time

    combined_results = {
        "benchmark": "Hybrid Vibe Telemetry & Bio-Quantum KEGG Integration",
        "total_time_sec": round(total_time, 4),
        "bio_quantum_metabolism": bio_quantum_metrics,
        "live_telemetry_snapshot": telemetry_snapshot
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "hybrid_vibe_telemetry_results.json"

    with open(out_file, "w") as f:
        json.dump(combined_results, f, indent=2)

    logger.info("=" * 70)
    logger.info("Hybrid Benchmark Completed!")
    logger.info(f"Quantum Coherence Time: {bio_quantum_metrics['coherence_time_ps']} ps")
    logger.info(f"Total ATP Yield:        {bio_quantum_metrics['metabolic_yield']['total_atp_yield_moles']} moles")
    logger.info(f"Quantum Stability:      {bio_quantum_metrics['quantum_stability_index']}")
    logger.info(f"Results Saved To:       {out_file}")
    logger.info("=" * 70)

    return combined_results


if __name__ == "__main__":
    run_benchmark()
