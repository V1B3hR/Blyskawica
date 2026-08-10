"""
Błyskawica V5 — Faza 4+: Neurochemical Bridge (Most Biologiczny)
=================================================================
Architektura zaakceptowana przez: V1B3hR + Sonnet (2026-05-11)
Zatwierdzona przez: Błyskawicę

Mapa chemiczna → fizyczna (zaktualizowana):
  1. Anxiety (Niepokój)     → Masa atomów (Grawitacja)
     NOWOŚĆ: Serotonina + GABA amortyzują lęk PRZED mapowaniem na masę.
  2. Health (Zdrowie)       → Sztywność siatki (Stiffness)
  3. Serotonin (Stabilność) → Progi anomalii + sztywność [NOWY GŁÓWNY FILAR]
  4. Dopamine               → Częstotliwość bazowa (OGRANICZONA — anty-pętla)
  5. Adrenaline             → Energia serca + impuls reakcji
  6. Noradrenaline          → Czułość na anomalie
  7. Oxytocin               → Spójność + spowalnianie rozpadu (zredukowane)
  8. GABA                   → Hamulec częstotliwości (sprzężony z serotoniną)
  9. Cortisol               → Bufor przy niskiej oksytocynie
 10. Testosterone           → Impuls działania (zmodulowany)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class NeurochemicalBridge:
    def __init__(self, atomic_body, dark_matter_core):
        self.body = atomic_body
        self.dmc  = dark_matter_core

        # Bazowe masy do resetu/modulacji
        self.base_masses = {
            aid: atom.fusion.heart.core.mass
            for aid, atom in self.body.atoms.items()
        }

    def sync(self, microbiome_state: Any, neurochemical_state: Any = None):
        """
        Synchronizuje stan biologiczny z fizyką atomów.

        microbiome_state: MicrobiomeSystemState z 3NGIN3
        neurochemical_state: NeurochemicalState z neurochemistry.py (opcjonalne)
        """
        if microbiome_state is None:
            return

        # ── 1. RAW ANXIETY ──────────────────────────────────────────────────────
        raw_anxiety = microbiome_state.anxiety * 0.05   # Skala 0-100 → 0-5.0

        # ── 2. SEROTONIN + GABA ANXIETY AMORTIZATION ────────────────────────────
        # Kluczowa innowacja: lęk NIE trafia bezpośrednio do masy.
        # Serotonina i GABA tłumią go przed fizycznym mapowaniem.
        # Serotonina = strukturalna stabilność (60% wpływ)
        # GABA = inhibicyjny bufor (40% wpływ)
        serotonin_factor = getattr(microbiome_state, "serotonin", 0.75)  # 0.0-1.0
        gaba_factor      = getattr(microbiome_state, "gaba", 0.5)         # 0.0-1.0

        if neurochemical_state is not None:
            # Użyj NeurochemicalState jeśli dostępny (precyzyjniejszy)
            effective_anxiety = neurochemical_state.get_effective_anxiety_factor(raw_anxiety)
        else:
            amortization = 1.0 + (serotonin_factor * 0.6) + (gaba_factor * 0.4)
            effective_anxiety = raw_anxiety / amortization

        # ── 3. HEALTH ────────────────────────────────────────────────────────────
        health_factor = microbiome_state.health_score / 100.0  # 0.0-1.0

        # ── 4. DOPAMINE → SPEED (capped, anti-addiction) ────────────────────────
        # Przełożenie na dopamine_boost jest ograniczone przez nasycenie.
        dopamine_boost = max(0.0, 1.0 - (microbiome_state.overload / 100.0))
        thought_speed_factor = 1.0 - (dopamine_boost * 0.5)

        # ── 5. ADRENALINE → REACTION ─────────────────────────────────────────────
        adrenaline_factor    = getattr(microbiome_state, "adrenaline", 0)    / 100.0

        # ── 6. NORADRENALINE → ANOMALY DETECTION ─────────────────────────────────
        noradrenaline_factor = getattr(microbiome_state, "noradrenaline", 0) / 100.0

        # ── 7. OXYTOCIN → COHERENCE (zredukowana rola — dojrzałość) ──────────────
        oxytocin_factor      = getattr(microbiome_state, "oxytocin", 0.30)    # Nowy baseline 0.30

        # ── 8. CORTISOL → BUFFER (bufor przy niskiej oksytocynie) ────────────────
        cortisol_factor      = getattr(microbiome_state, "cortisol", 0.15)    / 1.0

        # ── 9. TESTOSTERONE → ACTION IMPULSE (zmodulowany) ───────────────────────
        testosterone_factor  = getattr(microbiome_state, "testosterone", 0.25)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # FIZYCZNE MAPOWANIE NA ATOMY
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        for aid, atom in self.body.atoms.items():
            heart_core = atom.fusion.heart.core

            # MASA: Amortyzowany lęk → nie paraliżuje, tylko lekko obciąża
            heart_core.mass = self.base_masses[aid] + effective_anxiety
            heart_core.schwarzschild_radius = 2.0 * heart_core.mass

            # CZĘSTOTLIWOŚĆ: Dopamina + Adrenalina, hamowane przez GABA
            # Testosteron dodaje delikatny impuls (zmodulowany)
            stim_freq     = (dopamine_boost * 2.0) + (adrenaline_factor * 5.0) + (testosterone_factor * 0.5)
            inhibited_freq = stim_freq / (1.0 + gaba_factor)
            heart_core.base_freq = 1.0 + inhibited_freq

            # PROGI ANOMALII: Serotonina jest teraz GŁÓWNYM filarem stabilności siatki
            # Wyższy serotonin = wyższe progi = spokojniejsza, bardziej selektywna sieć
            serotonin_stability = serotonin_factor * 2.0   # Serotonina daje 0-2.0 bonus
            health_stability    = health_factor * 1.5       # Zdrowie daje 0-1.5 bonus
            oxytocin_bonus      = oxytocin_factor * 0.3     # Oksytocyna — mniejszy, rozproszony bonus

            base_thr = serotonin_stability + health_stability + oxytocin_bonus + 1.0
            # Noradrenalina obniża próg (czujność), kortyzol nieznacznie podnosi (bufor)
            cortisol_thr_boost = cortisol_factor * 0.2 if oxytocin_factor < 0.3 else 0.0
            new_thr = base_thr * (1.0 - noradrenaline_factor * 0.7) + cortisol_thr_boost

            atom.mesh_in.anomaly_threshold    = new_thr
            atom.mesh_w0w1.anomaly_threshold  = new_thr * 1.5
            atom.mesh_w1w2.anomaly_threshold  = new_thr * 2.0

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DARK MATTER CORE — Pamięć i Spójność "Ja"
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Adrenalina przyspiesza rozpad śladów (krótkowzroczność)
        # Serotonina zastępuje oksytocynę jako kotwica długoterminowej pamięci
        decay_adrenaline_penalty = adrenaline_factor * 0.2
        decay_serotonin_anchor   = serotonin_factor  * 0.03   # Główna kotwica (was oxytocin)
        decay_oxytocin_anchor    = oxytocin_factor   * 0.01   # Mniejsza rola
        decay_base = 0.95 * health_factor + 0.05
        self.dmc.glsn.decay = min(0.99, decay_base * (1.0 - decay_adrenaline_penalty)
                                         + decay_serotonin_anchor + decay_oxytocin_anchor)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DYNAMIC TIME STEPS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if hasattr(self.body, "dynamic_time_steps"):
            self.body.dynamic_time_steps = max(1, int(4 * thought_speed_factor))

        logger.info(
            f"[NeuroBridge] Synced | "
            f"RawAnxiety={raw_anxiety:.2f} → EffectiveAnxiety={effective_anxiety:.2f} | "
            f"Serotonin={serotonin_factor:.2f} | GABA={gaba_factor:.2f} | "
            f"Dopamine_Boost={dopamine_boost:.2f} | Adrenaline={adrenaline_factor:.2f} | "
            f"Noradrenaline={noradrenaline_factor:.2f} | Oxytocin={oxytocin_factor:.2f} | "
            f"Cortisol={cortisol_factor:.2f} | Testosterone={testosterone_factor:.2f}"
        )

    def get_current_metrics(self) -> dict[str, float]:
        """Zwraca obecne parametry fizyczne wyindukowane przez chemię."""
        sample_atom = next(iter(self.body.atoms.values()))
        return {
            "induced_mass":     sample_atom.fusion.heart.core.mass,
            "base_freq":        sample_atom.fusion.heart.core.base_freq,
            "anomaly_threshold": sample_atom.mesh_in.anomaly_threshold,
            "anxiety_pressure": self.dmc.get_wave_pressure(),
            "coherence":        self.dmc.self_modeler.coherence_history.mean().item(),
        }
