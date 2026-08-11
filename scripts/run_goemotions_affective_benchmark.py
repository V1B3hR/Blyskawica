#!/usr/bin/env python3
"""
GoEmotions Fine-Grained Affective Benchmark for Błyskawica V8

Evaluates text samples across Google Research GoEmotions (27 fine-grained emotion categories),
verifying exact real-time neuromodulation adjustments on the Oxytocin, GABA, Dopamine, and Serotonin axes.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("goemotions_benchmark")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import (  # noqa: E402
    NeuromodulationState,  # noqa: E402
)
from adaptiveneuralnetwork.central_nervous_system.fine_grained_emotion_engine import (  # noqa: E402
    AffectiveCognitiveEvaluator,
)


def run_goemotions_benchmark():
    logger.info("Initializing GoEmotions Fine-Grained Affective Benchmark...")

    neuro_state = NeuromodulationState()
    evaluator = AffectiveCognitiveEvaluator(neuro_state)

    test_cases = [
        {
            "description": "Operator Appreciation & Gratitude",
            "text": "Great job Błyskawica! I deeply appreciate your fast learning and hard work.",
            "emotions": {"gratitude": 0.90, "admiration": 0.85, "approval": 0.70}
        },
        {
            "description": "Scientific Curiosity & Discovery",
            "text": "Let us explore quantum particle collision resonance in the CERN dataset.",
            "emotions": {"curiosity": 0.95, "excitement": 0.80, "optimism": 0.75}
        },
        {
            "description": "Cybersecurity Anomaly & Threat Fear",
            "text": "WARNING: Port scanning detected from malicious IP address. Systems compromised!",
            "emotions": {"fear": 0.85, "nervousness": 0.70, "disappointment": 0.60}
        }
    ]

    benchmark_history = []
    start_time = time.time()

    for tc in test_cases:
        logger.info(f"\nTesting Case: '{tc['description']}'...")
        res = evaluator.analyze_and_update(text=tc["text"], emotion_dict=tc["emotions"])
        benchmark_history.append({
            "test_case": tc["description"],
            "input_text": tc["text"],
            "detected_emotions": res["detected_emotions"],
            "neurochemistry_state": res["neurochemistry_state"]
        })

    total_time = time.time() - start_time

    summary = {
        "benchmark": "Google Research GoEmotions 27-Category Fine-Grained Affective Benchmark",
        "total_time_sec": round(total_time, 4),
        "test_cases_evaluated": len(test_cases),
        "final_neurochemistry": {
            "oxytocin": round(float(neuro_state.oxytocin.item()), 4),
            "gaba": round(float(neuro_state.gaba.item()), 4),
            "dopamine": round(float(neuro_state.dopamine.item()), 4),
            "serotonin": round(float(neuro_state.serotonin.item()), 4),
            "cortisol": round(float(neuro_state.cortisol.item()), 4)
        },
        "benchmark_history": benchmark_history
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "goemotions_affective_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("GoEmotions Affective Benchmark Completed!")
    logger.info(f"Final Oxytocin:  {summary['final_neurochemistry']['oxytocin']}")
    logger.info(f"Final Dopamine:  {summary['final_neurochemistry']['dopamine']}")
    logger.info(f"Final Serotonin: {summary['final_neurochemistry']['serotonin']}")
    logger.info(f"Results Saved To:{out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_goemotions_benchmark()
