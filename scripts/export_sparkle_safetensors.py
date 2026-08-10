#!/usr/bin/env python3
"""
Iteration 3 (Faza Standalone): Sparkle App Safetensors & Identity Exporter for Błyskawica V8

Packages trained neural weights, neurochemical buffers (Oxytocin, GABA, Dopamine, Serotonin),
16x16 Diamond Yant matrix configurations, and Wolf Teeth MITRE ATT&CK TTP dictionaries
into safetensors format for the standalone Sparkle App binary (Tauri / Rust core).
"""

import json
import logging
import sys
import time
from pathlib import Path

import torch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("safetensors_exporter")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import (  # noqa: E402
    NeuromodulationState,  # noqa: E402
)
from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine  # noqa: E402


def export_standalone_bundle():
    logger.info("Initializing Iteration 3: Sparkle App Standalone Safetensors Exporter...")

    neuro_state = NeuromodulationState()
    wolf_teeth = WolfTeethDefenseEngine()  # noqa: F841

    # Target directory setup (Tauri Rust model folder & local outputs)
    output_dir = Path("outputs/standalone_bundle")
    tauri_model_dir = Path("sparkle_app/src-tauri/models")

    output_dir.mkdir(parents=True, exist_ok=True)
    tauri_model_dir.mkdir(parents=True, exist_ok=True)

    # 1. Gather Neurochemical & Model Weights
    state_dict = neuro_state.state_dict()

    # If safetensors library is available, use it; otherwise save standard torch weights + JSON manifest
    safetensors_file = output_dir / "blyskawica_v8_core.safetensors"
    tauri_safetensors_file = tauri_model_dir / "blyskawica_v8_core.safetensors"

    try:
        from safetensors.torch import save_file
        save_file(state_dict, str(safetensors_file))
        save_file(state_dict, str(tauri_safetensors_file))
        logger.info(f"Successfully exported Safetensors weights to: {safetensors_file}")
        logger.info(f"Successfully exported Safetensors weights to: {tauri_safetensors_file}")
        safetensors_status = "Exported safetensors format"
    except ImportError:
        # Fallback to PyTorch checkpoint format if safetensors package not installed in environment
        torch.save(state_dict, output_dir / "blyskawica_v8_core.pt")
        torch.save(state_dict, tauri_model_dir / "blyskawica_v8_core.pt")
        logger.info(f"Safetensors package missing. Saved PyTorch checkpoint format to: {output_dir / 'blyskawica_v8_core.pt'}")
        safetensors_status = "Exported PyTorch .pt fallback format"

    # 2. Package Vibe Identity & TTP Dictionary Manifest
    manifest = {
        "system_identity": "Blyskawica_V8_Enterprise_Core",
        "export_timestamp": time.time(),
        "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "phase": "Iteration_3_Standalone_Sparkle_Binary",
        "neurochemistry_baseline": {
            "oxytocin": float(neuro_state.oxytocin.item()),
            "gaba": float(neuro_state.gaba.item()),
            "dopamine": float(neuro_state.dopamine.item()),
            "serotonin": float(neuro_state.serotonin.item()),
            "cortisol": float(neuro_state.cortisol.item()),
            "acetylcholine": float(neuro_state.acetylcholine.item()),
            "testosterone": float(neuro_state.testosterone.item())
        },
        "counter_intelligence_ttps": [
            "T1046_Network_Service_Discovery",
            "T1190_Exploit_Public_Facing_Application",
            "T1059_Command_and_Scripting_Interpreter"
        ],
        "diamond_yant_matrix": {
            "dimensions": [16, 16],
            "symmetry_threshold": 0.65
        },
        "export_status": safetensors_status
    }

    manifest_file = output_dir / "vibe_manifest.json"
    tauri_manifest_file = tauri_model_dir / "vibe_manifest.json"

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(tauri_manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("=" * 70)
    logger.info("Iteration 3 Standalone Export Completed!")
    logger.info(f"Safetensors Export Status: {safetensors_status}")
    logger.info(f"Manifest Saved To:         {manifest_file}")
    logger.info(f"Tauri Binary Model Path:   {tauri_manifest_file}")
    logger.info("=" * 70)

    return manifest


if __name__ == "__main__":
    export_standalone_bundle()
