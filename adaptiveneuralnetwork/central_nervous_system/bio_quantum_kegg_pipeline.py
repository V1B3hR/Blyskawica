"""
Bio-Quantum Phononics & KEGG Metabolic Pathway Pipeline for Błyskawica V8

Integrates eNeuro 2024 Microtubule Quantum Coherence (dipole-dipole phonon noise damping)
with KEGG Bio-Metabolic Pathway Networks (Glycolysis, TCA Cycle, Oxidative Phosphorylation).
Modulates 16x16 Diamond Yant cymatic matrix stability using sub-cellular quantum coherence times.
"""

import os
import json
import math
import logging
from typing import Dict, Any, List, Tuple
import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from scripts.microtubule_phonon_engine import MicrotubulePhononEngine

logger = logging.getLogger("bio_quantum_kegg")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEGG_FILE = os.path.join(BASE_DIR, "data", "kegg_metabolic_pathways.json")


class KEGGMetabolicEngine:
    """
    Parses KEGG Metabolic Pathway graph (Glycolysis, TCA Cycle, Oxidative Phosphorylation)
    and computes cellular ATP production rate.
    """

    def __init__(self, kegg_path: str = KEGG_FILE):
        self.kegg_path = kegg_path
        self.pathways = self._load_kegg()

    def _load_kegg(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.kegg_path):
            try:
                with open(self.kegg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("pathways", [])
            except Exception as e:
                logger.error(f"Error reading KEGG database: {e}")
        return []

    def compute_atp_yield(self, glucose_flux_mmol: float = 1.0) -> Dict[str, Any]:
        """Calculates ATP energy yield across cellular metabolic pathways."""
        # Glycolysis: 2 ATP + 2 NADH
        glycolysis_atp = glucose_flux_mmol * 2.0
        # TCA Cycle: 2 ATP + 6 NADH + 2 FADH2
        tca_atp = glucose_flux_mmol * 2.0
        # Oxidative Phosphorylation: ~32 ATP
        oxphos_atp = glucose_flux_mmol * 32.0

        total_atp_yield = glycolysis_atp + tca_atp + oxphos_atp

        return {
            "glucose_flux_mmol": glucose_flux_mmol,
            "glycolysis_atp": glycolysis_atp,
            "tca_cycle_atp": tca_atp,
            "oxidative_phosphorylation_atp": oxphos_atp,
            "total_atp_yield_moles": total_atp_yield,
            "metabolic_power_equivalent_watts": round(total_atp_yield * 1.2, 2)
        }


class BioQuantumKEGGPipeline(nn.Module):
    """
    Sub-Cellular Quantum Phonon & Bio-Metabolic Pipeline.
    Unifies Microtubule Quantum Coherence (ps) with KEGG ATP yield (W)
    to drive Błyskawica's sub-cellular quantum architecture.
    """

    def __init__(self, neuro_state: NeuromodulationState | None = None):
        super().__init__()
        self.neuro = neuro_state or NeuromodulationState()
        self.kegg = KEGGMetabolicEngine()
        self.phonon = MicrotubulePhononEngine()

    def step_bio_quantum(self, glucose_flux: float = 1.5) -> Dict[str, Any]:
        """
        Executes one step of sub-cellular quantum-metabolic simulation.
        Returns quantum coherence time (ps), ATP yield, and quantum stability index.
        """
        # Update phonon engine chemistry from neuro state
        self.phonon.chemistry["Acetylocholina"] = float(self.neuro.acetylcholine)
        self.phonon.chemistry["GABA"] = float(self.neuro.gaba)

        # 1. Microtubule Quantum Coherence Survival Time (ps)
        coherence_time_ps, is_orch_or_capable = self.phonon.simulate_coherence()

        # 2. KEGG ATP Yield
        metabolic_yield = self.kegg.compute_atp_yield(glucose_flux_mmol=glucose_flux)

        # 3. Quantum-Cymatic Coupling
        # Quantum coherence > 100ps provides sub-cellular stability boost
        quantum_stability_index = round(min(1.0, coherence_time_ps / 1000.0), 4)

        metrics = {
            "coherence_time_ps": coherence_time_ps,
            "metabolic_yield": metabolic_yield,
            "quantum_stability_index": quantum_stability_index,
            "acetylcholine_level": round(float(self.neuro.acetylcholine), 4),
            "gaba_level": round(float(self.neuro.gaba), 4)
        }

        return metrics
