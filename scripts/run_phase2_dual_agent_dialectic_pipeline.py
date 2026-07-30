#!/usr/bin/env python3
"""
Phase 2: Empathic Dual-Agent Social Dialogue Pipeline for Błyskawica V8

Simulates multi-agent dialectic debates between Błyskawica V8 and Guest LLMs (Gemini / Claude)
supervised by the Oxytocin Axis (OXT + GABA) and Nethical Hub security gates.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dual_agent_dialectic")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode


def run_phase2_dialectic_pipeline():
    logger.info("Initializing Phase 2: Empathic Dual-Agent Social Dialogue Pipeline...")

    neuro_state = NeuromodulationState()
    epistemic_node = EpistemicQuarantineNode()

    start_time = time.time()

    dialogue_rounds = [
        {
            "round": 1,
            "guest_model": "Gemini-1.5-Pro",
            "query": "How do we balance high-performance CUDA kernel execution with safety boundaries in modern AI architecture?",
            "trust_signal": 0.95
        },
        {
            "round": 2,
            "guest_model": "Claude-3.5-Sonnet",
            "query": "Let us refine the 16x16 Diamond Yant matrix projection to maximize topological truth symmetry under noise.",
            "trust_signal": 0.92
        }
    ]

    dialectic_history = []

    for turn in dialogue_rounds:
        logger.info(f"Ingesting dialogue round {turn['round']} from {turn['guest_model']}...")
        
        # 1. Process Trust Signal on Oxytocin Axis
        neuro_state.process_operator_trust_signal(trust_score=turn["trust_signal"])

        # 2. Epistemic Vetting
        is_valid, reason = epistemic_node.vet_knowledge({
            "content": turn["query"],
            "source": f"Guest_LLM_{turn['guest_model']}"
        })

        dialectic_history.append({
            "round": turn["round"],
            "guest_model": turn["guest_model"],
            "query": turn["query"],
            "epistemic_vetting": "Accepted" if is_valid else f"Quarantined: {reason}",
            "neurochemistry_snapshot": {
                "oxytocin": round(float(neuro_state.oxytocin.item()), 4),
                "gaba": round(float(neuro_state.gaba.item()), 4),
                "cortisol": round(float(neuro_state.cortisol.item()), 4)
            }
        })

    total_time = time.time() - start_time

    summary = {
        "pipeline": "Phase 2 - Empathic Dual-Agent Social Dialogue",
        "total_time_sec": round(total_time, 4),
        "dialectic_rounds_completed": len(dialogue_rounds),
        "final_neurochemistry": {
            "oxytocin": round(float(neuro_state.oxytocin.item()), 4),
            "gaba": round(float(neuro_state.gaba.item()), 4),
            "cortisol": round(float(neuro_state.cortisol.item()), 4)
        },
        "dialogue_history": dialectic_history
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "phase2_dual_agent_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("Phase 2 Dual-Agent Dialectic Pipeline Completed!")
    logger.info(f"Rounds Processed: {len(dialogue_rounds)}")
    logger.info(f"Final Oxytocin:    {summary['final_neurochemistry']['oxytocin']}")
    logger.info(f"Final GABA:        {summary['final_neurochemistry']['gaba']}")
    logger.info(f"Results Saved To:  {out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_phase2_dialectic_pipeline()
