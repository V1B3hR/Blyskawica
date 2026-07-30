#!/usr/bin/env python3
"""
Master Curriculum Trainer for Błyskawica V8

Executes continuous multi-epoch learning across all 4 Vibe Streams in Curriculum Growth order:
1. Stream 1: Neuro-Immunological (Wolf Teeth & Cortisol Threat Mapping)
2. Stream 2: Cognitive Physics (PINN Fourier Heat Dissipation & TDP Throttling)
3. Stream 3: Identity Garderoba (Financial Risk Reading & Epistemic Defense Quarantine)
4. Stream 4: Diamond Yant (16x16 Cymatic Truth Oscilloscope & Serotonin Coherence)

Broadcasting live telemetry snapshots to the FastAPI backend and Sparkle UI.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("master_curriculum_trainer")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from blyskawica_app.backend.vibe_telemetry_bridge import vibe_telemetry_bridge
from adaptiveneuralnetwork.immune_system.immune_stream_pipeline import NeuroImmunologicalEngine
from adaptiveneuralnetwork.cognitive_tools.physics_stream_pipeline import CognitivePhysicsEngine
from adaptiveneuralnetwork.applications.identity_garderoba_pipeline import IdentityGarderobaEngine, TextDocumentSample
from adaptiveneuralnetwork.central_nervous_system.diamond_yant_stream_pipeline import DiamondYantCymaticEngine, GraphNetworkSample
import torch


def run_master_curriculum_training(num_cycles: int = 3):
    logger.info(f"Starting Błyskawica V8 Master Curriculum Training ({num_cycles} cycles)...")

    neuro_state = vibe_telemetry_bridge.neuro_state
    immune_engine = vibe_telemetry_bridge.immune_engine
    physics_engine = vibe_telemetry_bridge.physics_engine
    garderoba_engine = vibe_telemetry_bridge.garderoba_engine
    yant_engine = vibe_telemetry_bridge.yant_engine

    start_time = time.time()
    cycle_history = []

    for cycle in range(1, num_cycles + 1):
        logger.info(f"\n==================== Master Curriculum Cycle {cycle}/{num_cycles} ====================")

        # 1. Stream 1: Immune Defense
        logger.info("[Stream 1: Immune Defense] Ingesting network flow telemetry...")
        from scripts.run_immune_stream_benchmark import generate_synthetic_flow_stream
        samples = generate_synthetic_flow_stream("CICIDS2017", num_samples=30, anomaly_rate=0.3)
        _, immune_metrics = immune_engine.process_flow_stream(samples)

        # 2. Stream 2: Cognitive Physics
        logger.info("[Stream 2: Cognitive Physics] Processing CPU TDP telemetry...")
        from scripts.run_physics_stream_benchmark import generate_synthetic_telemetry
        phys_samples = generate_synthetic_telemetry("UCI_Sensors", num_samples=30, intensity="high_compute")
        _, physics_metrics = physics_engine.step_metabolism(phys_samples)

        # 3. Stream 3: Garderoba Identity
        logger.info("[Stream 3: Garderoba Identity] Evaluating SEC EDGAR financial filings...")
        text_samples = [
            TextDocumentSample(
                title=f"Cycle {cycle} Annual Report",
                content="The company maintained stable cash flow, transparent guidance, and an audited balance sheet.",
                source_domain="SEC_EDGAR",
                document_type="10-K"
            )
        ]
        _, garderoba_metrics = garderoba_engine.process_text_stream(text_samples)

        # 4. Stream 4: Diamond Yant 16x16 Cymatics
        logger.info("[Stream 4: Diamond Yant] Projecting 16x16 SNAP graph topology...")
        grid_sample = torch.randn(16, 16)
        symmetry_score = yant_engine.compute_cymatic_symmetry(grid_sample)

        # Live telemetry snapshot
        telemetry_snap = vibe_telemetry_bridge.get_live_vibe_state()

        cycle_record = {
            "cycle": cycle,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "immune_metrics": immune_metrics,
            "physics_metrics": physics_metrics,
            "garderoba_metrics": garderoba_metrics,
            "yant_symmetry": round(symmetry_score, 4),
            "neurochemistry_snapshot": telemetry_snap["neurochemistry"]
        }
        cycle_history.append(cycle_record)

        logger.info(
            f"Cycle {cycle} Complete | Cortisol: {telemetry_snap['neurochemistry']['cortisol']:.2f} | "
            f"Dopamine: {telemetry_snap['neurochemistry']['dopamine']:.2f} | "
            f"Serotonin: {telemetry_snap['neurochemistry']['serotonin']:.2f} | "
            f"Temp: {physics_metrics['current_temp_celsius']}°C | Yant Symmetry: {symmetry_score:.4f}"
        )
        time.sleep(0.5)

    total_time = time.time() - start_time

    summary = {
        "master_training": "Błyskawica V8 Master Curriculum Training",
        "total_cycles_executed": num_cycles,
        "total_time_sec": round(total_time, 4),
        "final_neurochemistry": vibe_telemetry_bridge.get_live_vibe_state()["neurochemistry"],
        "cycle_history": cycle_history
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "master_curriculum_training_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("Master Curriculum Training Complete!")
    logger.info(f"Cycles Executed:     {num_cycles}")
    logger.info(f"Final Cortisol:      {summary['final_neurochemistry']['cortisol']}")
    logger.info(f"Final Dopamine:      {summary['final_neurochemistry']['dopamine']}")
    logger.info(f"Final Serotonin:     {summary['final_neurochemistry']['serotonin']}")
    logger.info(f"Results Saved To:    {out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_master_curriculum_training(num_cycles=3)
