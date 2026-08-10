#!/usr/bin/env python3
"""
Holographic Swarm Network Benchmark for Błyskawica V8

Simulates a 3-Node Edge Emissary Swarm (Security Node, Physics Node, Engineer Node),
evaluates 16x16 Diamond Yant Cymatic Consensus, and verifies Serotonin/Oxytocin elevation.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("holo_swarm_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import (  # noqa: E402
    NeuromodulationState,  # noqa: E402
)
from adaptiveneuralnetwork.central_nervous_system.holo_swarm_network import (  # noqa: E402
    HolographicSwarmEngine,  # noqa: E402
)


def run_holo_swarm_benchmark():
    logger.info("Initializing Holographic Swarm Network Benchmark...")

    neuro_state = NeuromodulationState()
    swarm_engine = HolographicSwarmEngine(neuro_state)

    start_time = time.time()

    # 1. Register Swarm Nodes
    n1 = swarm_engine.register_node("node-sec-01", "Security_WolfTeeth_Shield")
    n2 = swarm_engine.register_node("node-phys-02", "Physics_PINN_Metabolism")
    n3 = swarm_engine.register_node("node-eng-03", "Windows_OS_Garderoba")

    # 2. Execute Cymatic Consensus Round 1 (Initial State)
    logger.info("\nExecuting Swarm Cymatic Consensus Round 1...")
    consensus_r1 = swarm_engine.execute_cymatic_consensus()

    # 3. Simulate Symmetrical Matrix Alignment across Swarm
    import torch
    sym_pattern = torch.eye(16) * 1.5
    n1.local_yant_matrix = sym_pattern + torch.randn(16, 16) * 0.05
    n2.local_yant_matrix = sym_pattern + torch.randn(16, 16) * 0.05
    n3.local_yant_matrix = sym_pattern + torch.randn(16, 16) * 0.05

    # 4. Execute Cymatic Consensus Round 2 (High Resonant Symmetry)
    logger.info("\nExecuting Swarm Cymatic Consensus Round 2 (Resonant Alignment)...")
    consensus_r2 = swarm_engine.execute_cymatic_consensus()

    total_time = time.time() - start_time

    results = {
        "benchmark": "Holographic Swarm Network & Cymatic Consensus Protocol",
        "total_time_sec": round(total_time, 4),
        "nodes_registered": len(swarm_engine.nodes),
        "consensus_round_1": consensus_r1,
        "consensus_round_2": consensus_r2,
        "final_neurochemistry": consensus_r2["neurochemistry_state"]
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "holo_swarm_results.json"

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info("=" * 70)
    logger.info("Holographic Swarm Benchmark Completed!")
    logger.info(f"Nodes Registered:    {results['nodes_registered']}")
    logger.info(f"Round 2 Symmetry:    {consensus_r2['global_symmetry']}")
    logger.info(f"Consensus Status:    {consensus_r2['consensus_status']}")
    logger.info(f"Final Serotonin:     {results['final_neurochemistry']['serotonin']}")
    logger.info(f"Final Oxytocin:      {results['final_neurochemistry']['oxytocin']}")
    logger.info(f"Results Saved To:    {out_file}")
    logger.info("=" * 70)

    return results


if __name__ == "__main__":
    run_holo_swarm_benchmark()
