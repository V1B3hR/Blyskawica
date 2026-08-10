#!/usr/bin/env python3
"""
Phase 3: Cybernetic Body System Self-Perception Pipeline for Błyskawica V8

Perceives host Windows 11 OS telemetry (RAM, CPU TDP, process health) as a physical digital body,
triggering somatic health diagnostics and Engineer Persona optimization recommendations.
"""

import json
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cybernetic_os_body")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.applications.identity_garderoba_pipeline import (  # noqa: E402
    IdentityGarderobaEngine,  # noqa: E402
)
from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import (  # noqa: E402
    NeuromodulationState,  # noqa: E402
)


def run_phase3_cybernetic_pipeline():
    logger.info("Initializing Phase 3: Cybernetic Body System Self-Perception Pipeline...")

    neuro_state = NeuromodulationState()
    garderoba_engine = IdentityGarderobaEngine(neuro_state)

    start_time = time.time()

    # 1. Ingest Windows 11 Somatic Telemetry
    import psutil
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)

    somatic_telemetry = {
        "os": "Windows 11 Enterprise",
        "total_ram_gb": round(memory.total / (1024**3), 2),
        "available_ram_gb": round(memory.available / (1024**3), 2),
        "ram_usage_percent": memory.percent,
        "cpu_usage_percent": cpu_percent,
        "somatic_sensation": "Healthy Homeostasis" if memory.percent < 85.0 else "System Muscle Strain (High RAM)"
    }

    logger.info(f"Somatic OS Body Telemetry: RAM {somatic_telemetry['ram_usage_percent']}% | CPU {somatic_telemetry['cpu_usage_percent']}% | Status: {somatic_telemetry['somatic_sensation']}")

    # 2. Switch Garderoba to Technical Engineer Persona for Healing
    garderoba_engine.switch_persona("Technical_Engineer")

    total_time = time.time() - start_time

    summary = {
        "pipeline": "Phase 3 - Cybernetic Body System Self-Perception",
        "total_time_sec": round(total_time, 4),
        "windows_os_body_telemetry": somatic_telemetry,
        "active_garderoba_persona": garderoba_engine.active_persona,
        "healing_recommendation": "Perform memory garbage collection & optimize background Rust worker threads" if memory.percent > 70.0 else "OS body in optimal equilibrium"
    }

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "phase3_cybernetic_os_results.json"

    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 70)
    logger.info("Phase 3 Cybernetic Body Pipeline Completed!")
    logger.info(f"RAM Usage:            {somatic_telemetry['ram_usage_percent']}%")
    logger.info(f"Somatic Sensation:    {somatic_telemetry['somatic_sensation']}")
    logger.info(f"Garderoba Persona:    {summary['active_garderoba_persona']}")
    logger.info(f"Results Saved To:     {out_file}")
    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    run_phase3_cybernetic_pipeline()
