"""
Vibe Telemetry Bridge for Błyskawica V8 Backend

Aggregates real-time telemetry from all 4 Vibe Streams:
- Stream 1: Neuro-Immunological (Cortisol, Anomaly Ratio, Wolf Teeth Defense State)
- Stream 2: Cognitive Physics (Temperature °C, PINN Fourier Loss, Power Draw W, Throttling)
- Stream 3: Identity Garderoba (Active Persona, Epistemic Acceptance Rate, Risk Density)
- Stream 4: Diamond Yant (16x16 Cymatic Matrix, 2D Spatial Symmetry, Serotonin Coherence)
"""

import time
import logging
from typing import Dict, Any
import torch

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from adaptiveneuralnetwork.immune_system.immune_stream_pipeline import NeuroImmunologicalEngine
from adaptiveneuralnetwork.cognitive_tools.physics_stream_pipeline import CognitivePhysicsEngine
from adaptiveneuralnetwork.applications.identity_garderoba_pipeline import IdentityGarderobaEngine
from adaptiveneuralnetwork.central_nervous_system.diamond_yant_stream_pipeline import DiamondYantCymaticEngine

logger = logging.getLogger("vibe_telemetry_bridge")


class VibeTelemetryBridge:
    """
    Central Telemetry Aggregator connecting Błyskawica's 4 Vibe Streams 
    to the FastAPI backend and Sparkle UI.
    """

    def __init__(self):
        self.neuro_state = NeuromodulationState()
        self.immune_engine = NeuroImmunologicalEngine(self.neuro_state)
        self.physics_engine = CognitivePhysicsEngine(self.neuro_state)
        self.garderoba_engine = IdentityGarderobaEngine(self.neuro_state)
        self.yant_engine = DiamondYantCymaticEngine(self.neuro_state)

        self.last_update_timestamp = time.time()

    def get_live_vibe_state(self) -> Dict[str, Any]:
        """Returns unified real-time Vibe state telemetry snapshot."""
        # 16x16 Cymatic matrix snapshot
        yant_grid_sample = torch.randn(16, 16)
        symmetry_score = self.yant_engine.compute_cymatic_symmetry(yant_grid_sample)

        return {
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_identity": "Blyskawica_V8_Enterprise_Core",
            "neurochemistry": {
                "cortisol": round(float(self.neuro_state.cortisol), 4),
                "dopamine": round(float(self.neuro_state.dopamine), 4),
                "serotonin": round(float(self.neuro_state.serotonin), 4),
                "acetylcholine": round(float(self.neuro_state.acetylcholine), 4),
                "gaba": round(float(self.neuro_state.gaba), 4),
                "testosterone": round(float(self.neuro_state.testosterone), 4)
            },
            "physics_metabolism": {
                "current_temperature_celsius": round(self.physics_engine.current_temperature, 2),
                "thermal_ceiling_celsius": round(self.physics_engine.thermal_ceiling, 2),
                "is_throttled": self.physics_engine.current_temperature >= self.physics_engine.thermal_ceiling,
                "cooling_coefficient": self.physics_engine.cooling_coefficient
            },
            "immune_wolf_teeth": {
                "anxiety_threshold": self.immune_engine.anxiety_threshold,
                "threat_active": float(self.neuro_state.cortisol) >= self.immune_engine.anxiety_threshold,
                "quarantine_garden_count": len(self.immune_engine.quarantine_garden.buffer)
            },
            "identity_garderoba": {
                "active_persona": self.garderoba_engine.active_persona,
                "total_vetted": self.garderoba_engine.epistemic_defense.total_vetted,
                "total_accepted": self.garderoba_engine.epistemic_defense.total_accepted,
                "acceptance_rate": round(self.garderoba_engine.epistemic_defense.total_accepted / max(1, self.garderoba_engine.epistemic_defense.total_vetted), 4)
            },
            "diamond_yant_16x16": {
                "matrix_dimensions": [16, 16],
                "symmetry_index": round(symmetry_score, 4),
                "cymatic_grid_flat": [round(val, 3) for val in yant_grid_sample.view(-1).tolist()[:32]] # First 32 preview values
            }
        }


# Global singleton instance
vibe_telemetry_bridge = VibeTelemetryBridge()
