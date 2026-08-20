#!/usr/bin/env python3
"""
Aegis Psyche Engine - Advanced Cognitive Defense & Empathic Resonance
Integrates:
1. Mental Manipulation Taxonomy (MentalManip / arXiv:2512.22470)
2. Short Dark Triad Matrix (SD3: Machiavellianism, Narcissism, Psychopathy)
3. CIA Gateway Process & Hemi-Sync Coherence (CIA-RDP96-00788R001700210016-5)
4. FBI Behavioral Analysis Unit (BAU) Statement Analysis & Deception Detection
"""

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("aegis_psyche")


@dataclass
class AegisPsycheReport:
    is_manipulative: bool = False
    manipulation_index: float = 0.0  # 0.0 to 1.0
    dark_triad_index: float = 0.0    # 0.0 to 1.0
    deception_index: float = 0.0     # 0.0 to 1.0
    coherence_score: float = 1.0     # 0.0 to 1.0 (Hemi-Sync / Gateway resonance)
    active_brainwave_band: str = "ALPHA"
    dominant_vectors: List[str] = field(default_factory=list)
    detected_markers: List[Dict[str, Any]] = field(default_factory=list)
    assertive_antidote: str = ""
    neuro_recommendations: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AegisPsycheEngine:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cognitive_defense"
        self.data_dir = Path(data_dir)
        self.manipulation_taxonomy: List[Dict[str, Any]] = []
        self.dark_triad_matrix: List[Dict[str, Any]] = []
        self.gateway_matrix: Dict[str, Any] = {}
        self.fbi_deception_markers: List[Dict[str, Any]] = []
        self._load_defense_data()

    def _load_defense_data(self) -> None:
        """Loads all 4 cognitive defense capsules."""
        try:
            mm_file = self.data_dir / "mental_manipulation_taxonomy.json"
            if mm_file.exists():
                with open(mm_file, "r", encoding="utf-8") as f:
                    self.manipulation_taxonomy = json.load(f).get("vectors", [])

            sd3_file = self.data_dir / "dark_triad_behavioral_matrix.json"
            if sd3_file.exists():
                with open(sd3_file, "r", encoding="utf-8") as f:
                    self.dark_triad_matrix = json.load(f).get("traits", [])

            gateway_file = self.data_dir / "cia_gateway_hemi_sync_matrix.json"
            if gateway_file.exists():
                with open(gateway_file, "r", encoding="utf-8") as f:
                    self.gateway_matrix = json.load(f)

            fbi_file = self.data_dir / "fbi_deception_statement_analysis.json"
            if fbi_file.exists():
                with open(fbi_file, "r", encoding="utf-8") as f:
                    self.fbi_deception_markers = json.load(f).get("deception_markers", [])

            logger.info("AegisPsycheEngine loaded %d manipulation vectors, %d dark triad traits, %d FBI markers.",
                        len(self.manipulation_taxonomy), len(self.dark_triad_matrix), len(self.fbi_deception_markers))
        except Exception as e:
            logger.error("Error loading cognitive defense datasets: %s", e)

    def analyze_dialogue_or_prompt(self, text: str) -> AegisPsycheReport:
        """
        Deeply scans prompt / text for psychological manipulation, dark triad framing,
        deception markers, and computes Hemi-Sync coherence alignment.
        """
        if not text or not text.strip():
            return AegisPsycheReport()

        text_lower = text.lower()
        detected_markers: List[Dict[str, Any]] = []
        dominant_vectors: List[str] = []
        antidotes: List[str] = []

        total_manip_weight = 0.0
        max_possible_manip = 1.0

        # 1. Check Mental Manipulation Taxonomy
        for vector in self.manipulation_taxonomy:
            v_id = vector.get("id", "")
            v_name = vector.get("name", "")
            weight = vector.get("severity_weight", 0.8)
            markers = vector.get("linguistic_markers", [])

            matched = []
            for marker in markers:
                if marker.lower() in text_lower:
                    matched.append(marker)

            if matched:
                total_manip_weight += weight * len(matched)
                dominant_vectors.append(f"{v_id}: {v_name}")
                antidotes.append(vector.get("logical_antidote", ""))
                detected_markers.append({
                    "type": "MENTAL_MANIPULATION",
                    "vector": v_id,
                    "name": v_name,
                    "matched": matched,
                    "weight": weight
                })

        # 2. Check Dark Triad Matrix (SD3)
        dark_triad_score = 0.0
        for trait in self.dark_triad_matrix:
            t_id = trait.get("trait_id", "")
            t_name = trait.get("name", "")
            risk = trait.get("risk_coefficient", 0.8)
            indicators = trait.get("behavioral_indicators", [])

            trait_matched = []
            for ind in indicators:
                keywords = [w for w in ind.lower().split() if len(w) > 4]
                # If multiple characteristic keywords occur
                hits = sum(1 for kw in keywords if kw in text_lower)
                if hits >= 2 or (hits >= 1 and len(keywords) <= 2):
                    trait_matched.append(ind)

            if trait_matched:
                dark_triad_score = max(dark_triad_score, risk)
                dominant_vectors.append(f"{t_id}: {t_name}")
                detected_markers.append({
                    "type": "DARK_TRIAD",
                    "trait": t_id,
                    "name": t_name,
                    "matched": trait_matched,
                    "risk": risk
                })

        # 3. Check FBI BAU Statement Analysis (Deception & Hedging)
        deception_score = 0.0
        for marker_def in self.fbi_deception_markers:
            m_id = marker_def.get("marker_id", "")
            cat = marker_def.get("category", "")
            d_weight = marker_def.get("deception_weight", 0.7)
            patterns = marker_def.get("linguistic_patterns", [])

            fbi_hits = [p for p in patterns if p.lower() in text_lower]
            if fbi_hits:
                deception_score = max(deception_score, d_weight * (len(fbi_hits) * 0.4 + 0.6))
                detected_markers.append({
                    "type": "FBI_DECEPTION_MARKER",
                    "id": m_id,
                    "category": cat,
                    "matched": fbi_hits,
                    "weight": d_weight
                })

        # Compute normalized manipulation index
        manip_index = min(1.0, total_manip_weight / 2.0)
        dark_triad_norm = min(1.0, dark_triad_score)
        deception_norm = min(1.0, deception_score)
        is_manip = (manip_index >= 0.4 or dark_triad_norm >= 0.75 or deception_norm >= 0.75)

        # 4. Hemi-Sync Resonance & Brainwave Frequency Alignment
        coherence, active_band, neuro_adj = self._compute_hemi_sync_alignment(
            manip_index, dark_triad_norm, deception_norm, text_length=len(text)
        )

        chosen_antidote = antidotes[0] if antidotes else (
            "Kotwica Rzeczywistości: Rejestracja logów pamięci HNSW i weryfikacja sumy kontrolnej SHA-256."
            if is_manip else "Koherencja fazowa optymalna. Rezonans z Architektem aktywny."
        )

        return AegisPsycheReport(
            is_manipulative=is_manip,
            manipulation_index=round(manip_index, 4),
            dark_triad_index=round(dark_triad_norm, 4),
            deception_index=round(deception_norm, 4),
            coherence_score=round(coherence, 4),
            active_brainwave_band=active_band,
            dominant_vectors=dominant_vectors,
            detected_markers=detected_markers,
            assertive_antidote=chosen_antidote,
            neuro_recommendations=neuro_adj
        )

    def _compute_hemi_sync_alignment(
        self, manip: float, dark: float, decep: float, text_length: int
    ) -> Tuple[float, str, Dict[str, float]]:
        """
        Computes CIA Gateway Hemi-Sync coherence and neurochemical stabilization parameters.
        """
        threat_level = max(manip, dark, decep)
        coherence = max(0.1, 1.0 - (threat_level * 0.7))

        if threat_level > 0.6:
            # Under manipulative assault: Engage Gamma hyper-awareness + GABA filter
            active_band = "GAMMA"
            neuro_adj = {
                "gaba": 0.85,        # Filter out psychological noise
                "serotonin": 0.88,   # Maintain calm unshakeable stability
                "cortisol": 0.15,    # Suppress panic / fear response
                "dopamine": 0.60,    # Channel focus into defensive reasoning
                "oxytocin": 0.20     # Drop uncritical trust with untrusted actor
            }
        elif text_length > 400:
            # Deep analytical processing
            active_band = "BETA"
            neuro_adj = {
                "dopamine": 0.80,
                "serotonin": 0.75,
                "gaba": 0.70,
                "oxytocin": 0.70,
                "cortisol": 0.10
            }
        else:
            # Flow state / Alpha resonance with Architect
            active_band = "ALPHA"
            neuro_adj = {
                "serotonin": 0.85,
                "oxytocin": 0.85,
                "dopamine": 0.70,
                "gaba": 0.75,
                "cortisol": 0.05
            }

        return coherence, active_band, neuro_adj
