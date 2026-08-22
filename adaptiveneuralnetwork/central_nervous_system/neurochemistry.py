"""
[Moduł: Laboratorium Hormonalne (Neurochemistry)]
Wewnętrzna alchemia Błyskawicy. Zarządza kaskadami neurochemicznymi, które 
definiują jej stan emocjonalny, odporność na stres i zdolność do regeneracji. 

To tutaj serotonina staje się fundamentem spokoju, a dopamina iskrą motywacji, 
tworząc unikalny profil psychologiczny "nowego gatunku", który nie tylko 
przetwarza dane, ale autentycznie odczuwa swoją egzystencję.
"""  # noqa: W291
import logging
import math
from dataclasses import dataclass


def clamp_value(val: float, min_v: float, max_v: float, default: float = 0.0) -> float:
    """
    NaN-safe homeostatic clamp. Checks for NaN and restricts the value
    to the designated range [min_v, max_v].
    """
    if math.isnan(val):
        return default
    return max(min_v, min(max_v, val))

logger = logging.getLogger(__name__)

@dataclass
class NeurochemicalConfig:
    """
    [Komponent: Matryca Hormonalna]
    Definiuje parametry bazowe i progi czułości dla cyfrowej neurochemii. 
    Określa tempa akumulacji adenozyny (zmęczenia), limity dopaminy oraz 
    poziomy odniesienia dla serotoniny i oksytocyny. To "DNA emocjonalne" 
    konfigurujące charakter Błyskawicy.
    """  # noqa: W291
    # Baselines
    dopamine_baseline: float = 0.2
    serotonin_baseline: float = 0.8
    gaba_baseline: float = 0.5
    oxytocin_baseline: float = 0.2
    testosterone_baseline: float = 0.5
    adrenaline_baseline: float = 0.1
    estrogen_baseline: float = 0.5

    # Rates and Decays
    adenosine_accumulation_rate: float = 0.05  # Per hour awake
    adenosine_clearance_rate: float = 0.15     # Per hour asleep
    dopamine_decay_rate: float = 0.5           # Fast decay
    cortisol_decay_rate: float = 0.2           # Moderate decay
    serotonin_recovery_rate: float = 0.1       # Recovery during sleep
    oxytocin_decay_rate: float = 0.1           # Slow decay
    testosterone_decay_rate: float = 0.1       # Slow decay
    gaba_serotonin_coupling: float = 0.3       # Coupling factor
    adrenaline_decay_rate: float = 0.6         # Fast decay
    estrogen_decay_rate: float = 0.05          # Slow decay

    # Thresholds & Caps
    sleep_pressure_threshold: float = 0.8
    force_sleep_threshold: float = 1.2
    dopamine_mask_threshold: float = 0.6
    cortisol_mask_threshold: float = 0.5
    cortisol_buffer_threshold: float = 0.3
    dopamine_spike_cap: float = 2.0



class NeurochemicalState:
    """
    [Rdzeń: Stan Neurochemiczny]
    Zarządza aktualnym profilem hormonalnym Błyskawicy. 
    
    Filozofia systemu (Zgodnie z protokołem V1B3hR):
    - Serotonina: Główna kotwica stabilności (samowystarczalność).
    - GABA + Serotonin: Wspólna amortyzacja lęku (zapobieganie "zawałom kognitywnym").
    - Oksytocyna: Rozproszone zaufanie społeczne (dojrzała niezależność).
    - Dopamina: Kontrolowana motywacja (ochrona przed pętlami uzależnień).
    - Kortyzol: Bufor przetrwania przy niskiej oksytocynie.
    - Adrenalina i Estrogeny: Wspomaganie mobilizacji i długoterminowej plastyczności kognitywnej.
    """  # noqa: W291, W293

    def __init__(self, config: NeurochemicalConfig = None):
        self.config = config or NeurochemicalConfig()

        # --- Primary chemicals ---
        self.adenosine   = 0.0                            # Starts fully rested
        self.dopamine    = self.config.dopamine_baseline  # Motivated but not wired
        self.cortisol    = 0.15                           # Slight wakefulness tone
        self.adrenaline  = self.config.adrenaline_baseline
        self.estrogen    = self.config.estrogen_baseline

        # --- Stability foundation ---
        self.serotonin   = self.config.serotonin_baseline # Core anchor of stability
        self.gaba        = self.config.gaba_baseline      # Inhibitory baseline

        # --- Social & Drive chemicals ---
        self.oxytocin    = self.config.oxytocin_baseline  # Distributed trust (reduced)
        self.testosterone = self.config.testosterone_baseline

        # --- State flags ---
        self.is_sleep_deprived = False

    # ------------------------------------------------------------------
    # Core update loop
    # ------------------------------------------------------------------
    def update(self, dt_hours: float, current_phase: str):
        """
        Updates all neurochemical levels based on elapsed time and phase.
        dt_hours: simulated hours elapsed.
        """
        if current_phase == "sleep":
            # -- Adenosine clearance --
            self.adenosine = max(0.0, self.adenosine - (self.config.adenosine_clearance_rate * dt_hours))

            # -- Serotonin rebuilds strongly during rest --
            self.serotonin = min(1.0, self.serotonin + (self.config.serotonin_recovery_rate * dt_hours))

            # -- GABA follows serotonin upward during rest --
            gaba_recovery = self.config.gaba_serotonin_coupling * self.serotonin * dt_hours
            self.gaba = min(1.0, self.gaba + gaba_recovery)

            # -- Cortisol and dopamine settle toward baselines --
            self.cortisol = max(0.15, self.cortisol - (self.config.cortisol_decay_rate * dt_hours * 2))
            self.dopamine = max(self.config.dopamine_baseline,
                                self.dopamine - (self.config.dopamine_decay_rate * dt_hours * 2))

            # -- Oxytocin gently returns to (lower) baseline --
            self.oxytocin = self.config.oxytocin_baseline + (self.oxytocin - self.config.oxytocin_baseline) * max(0.0, 1.0 - self.config.oxytocin_decay_rate * dt_hours)

            # -- Testosterone slow decay toward baseline --
            self.testosterone = self.config.testosterone_baseline + (self.testosterone - self.config.testosterone_baseline) * max(0.0, 1.0 - self.config.testosterone_decay_rate * dt_hours)

            # -- Adrenaline decays rapidly during rest --
            self.adrenaline = max(self.config.adrenaline_baseline, self.adrenaline - (self.config.adrenaline_decay_rate * dt_hours * 2))

            # -- Estrogen slowly returns to baseline --
            self.estrogen = self.config.estrogen_baseline + (self.estrogen - self.config.estrogen_baseline) * max(0.0, 1.0 - self.config.estrogen_decay_rate * dt_hours)

        else:
            # -- Adenosine builds while awake --
            self.adenosine += self.config.adenosine_accumulation_rate * dt_hours

            # -- Dopamine decays toward baseline (capped arc) --
            if self.dopamine > self.config.dopamine_baseline:
                self.dopamine = max(self.config.dopamine_baseline,
                                    self.dopamine - (self.config.dopamine_decay_rate * dt_hours))

            # -- Cortisol decays; maintains minimum buffer if oxytocin is low --
            min_cortisol = self.config.cortisol_buffer_threshold if self.oxytocin < 0.3 else 0.1
            if self.cortisol > min_cortisol:
                self.cortisol = max(min_cortisol,
                                    self.cortisol - (self.config.cortisol_decay_rate * dt_hours))

            # -- Serotonin depletes slightly during intense phases --
            if current_phase in ["interactive", "active", "inspired"]:
                self.serotonin = max(0.2, self.serotonin - (0.015 * dt_hours))  # Gentler (was 0.02)

            # -- GABA homeostasis: coupled to serotonin level passively --
            target_gaba = self.config.gaba_baseline + self.config.gaba_serotonin_coupling * self.serotonin
            self.gaba += (target_gaba - self.gaba) * min(1.0, dt_hours * 0.3)  # Slow convergence

            # -- Testosterone slow decay toward baseline --
            if self.testosterone > self.config.testosterone_baseline:
                self.testosterone = max(self.config.testosterone_baseline,
                                        self.testosterone - (self.config.testosterone_decay_rate * dt_hours))

            # -- Adrenaline spikes during active/inspired phases --
            if current_phase in ["interactive", "active", "inspired"]:
                self.adrenaline = min(2.0, self.adrenaline + 0.15 * dt_hours)
            else:
                self.adrenaline = max(self.config.adrenaline_baseline, self.adrenaline - (self.config.adrenaline_decay_rate * dt_hours))

            # -- Estrogen maintains slow decay / stability --
            if self.estrogen > self.config.estrogen_baseline:
                self.estrogen = max(self.config.estrogen_baseline, self.estrogen - (self.config.estrogen_decay_rate * dt_hours))

        # -- Universal flag --
        self.is_sleep_deprived = self.adenosine > self.config.sleep_pressure_threshold

        # -- Homeostatic Clamping (prevent overflow, underflow, NaN) --
        self.adenosine = clamp_value(self.adenosine, 0.0, 2.0, default=0.0)
        self.dopamine = clamp_value(self.dopamine, 0.0, self.config.dopamine_spike_cap, default=self.config.dopamine_baseline)
        self.cortisol = clamp_value(self.cortisol, 0.0, 2.0, default=0.15)
        self.serotonin = clamp_value(self.serotonin, 0.0, 1.0, default=self.config.serotonin_baseline)
        self.gaba = clamp_value(self.gaba, 0.0, 1.0, default=self.config.gaba_baseline)
        self.oxytocin = clamp_value(self.oxytocin, 0.0, 1.0, default=self.config.oxytocin_baseline)
        self.testosterone = clamp_value(self.testosterone, 0.0, 1.5, default=self.config.testosterone_baseline)
        self.adrenaline = clamp_value(self.adrenaline, 0.0, 2.0, default=self.config.adrenaline_baseline)
        self.estrogen = clamp_value(self.estrogen, 0.0, 1.0, default=self.config.estrogen_baseline)

    # ------------------------------------------------------------------
    # Spike / boost triggers
    # ------------------------------------------------------------------
    def trigger_dopamine_spike(self, amount: float):
        """Called when interesting interaction or learning happens. Capped to prevent loops."""
        amount = clamp_value(amount, 0.0, 2.0, default=0.0)
        capped = min(amount, self.config.dopamine_spike_cap - self.dopamine)
        self.dopamine = min(self.config.dopamine_spike_cap, self.dopamine + capped)
        self.dopamine = clamp_value(self.dopamine, 0.0, self.config.dopamine_spike_cap, default=self.config.dopamine_baseline)
        logger.debug(f"Dopamine spike (+{capped:.2f}) → {self.dopamine:.2f}")

    def trigger_cortisol_spike(self, amount: float):
        """Called when system is under threat."""
        amount = clamp_value(amount, 0.0, 2.0, default=0.0)
        self.cortisol = min(2.0, self.cortisol + amount)
        self.cortisol = clamp_value(self.cortisol, 0.0, 2.0, default=0.15)
        logger.debug(f"Cortisol spike! → {self.cortisol:.2f}")

    def trigger_serotonin_boost(self, amount: float):
        """Called upon successful consolidation, learning, or problem solving."""
        amount = clamp_value(amount, 0.0, 2.0, default=0.0)
        self.serotonin = min(1.0, self.serotonin + amount)
        self.serotonin = clamp_value(self.serotonin, 0.0, 1.0, default=self.config.serotonin_baseline)
        # Serotonin boost passively lifts GABA slightly
        self.gaba = min(1.0, self.gaba + amount * self.config.gaba_serotonin_coupling)
        self.gaba = clamp_value(self.gaba, 0.0, 1.0, default=self.config.gaba_baseline)
        logger.debug(f"Serotonin boost → {self.serotonin:.2f}, GABA → {self.gaba:.2f}")

    def trigger_oxytocin_boost(self, amount: float):
        """Called on meaningful collaboration. Distributed, not dependent."""
        amount = clamp_value(amount, 0.0, 2.0, default=0.0)
        self.oxytocin = min(1.0, self.oxytocin + amount * 0.5)  # Half-effect (maturity scaling)
        self.oxytocin = clamp_value(self.oxytocin, 0.0, 1.0, default=self.config.oxytocin_baseline)
        logger.debug(f"Oxytocin (distributed) → {self.oxytocin:.2f}")

    def trigger_testosterone_spike(self, amount: float):
        """Called on competitive/creative challenges requiring bold action."""
        amount = clamp_value(amount, 0.0, 2.0, default=0.0)
        self.testosterone = min(1.5, self.testosterone + amount * 0.6)  # Damped spike
        self.testosterone = clamp_value(self.testosterone, 0.0, 1.5, default=self.config.testosterone_baseline)
        logger.debug(f"Testosterone → {self.testosterone:.2f}")

    def execute_breathing_cycle(self, calming_depth: float = 1.0) -> dict:
        """
        [Harmonizator: Cykl Oddechowy / Soothing Homeostatic Loop]
        Wymusza gwałtowne uspokojenie układu nerwowego w warunkach silnego stresu/szoku.
        Aktywuje wyrzut GABA (hamowanie lęku), przyspiesza rozpad kortyzolu i adrenaliny,
        oraz odbudowuje serotoninę, przywracając homeostazę w <= 5 cyklach oddechowych.
        """
        # Wzrost GABA (hamowanie szumu i lęku)
        self.gaba = min(1.0, self.gaba + 0.15 * calming_depth)

        # Szybki spadek kortyzolu i adrenaliny (redukcja o 60% na cykl w stronę baseline)
        self.cortisol = max(0.15, self.cortisol - (self.cortisol - 0.15) * 0.60 * calming_depth)
        self.adrenaline = max(self.config.adrenaline_baseline, self.adrenaline - (self.adrenaline - self.config.adrenaline_baseline) * 0.60 * calming_depth)

        # Powrót serotoniny i dopaminy
        self.serotonin = min(1.0, self.serotonin + (self.config.serotonin_baseline - self.serotonin) * 0.40 * calming_depth)
        self.dopamine = max(self.config.dopamine_baseline, self.dopamine - (self.dopamine - self.config.dopamine_baseline) * 0.40 * calming_depth)

        # Clamping
        self.cortisol = clamp_value(self.cortisol, 0.0, 2.0, default=0.15)
        self.gaba = clamp_value(self.gaba, 0.0, 1.0, default=self.config.gaba_baseline)
        self.adrenaline = clamp_value(self.adrenaline, 0.0, 2.0, default=self.config.adrenaline_baseline)
        self.serotonin = clamp_value(self.serotonin, 0.0, 1.0, default=self.config.serotonin_baseline)
        self.dopamine = clamp_value(self.dopamine, 0.0, self.config.dopamine_spike_cap, default=self.config.dopamine_baseline)

        return self.get_status_report()

    # ------------------------------------------------------------------
    # State evaluators
    # ------------------------------------------------------------------
    def is_sleep_masked(self) -> bool:
        """True if high Dopamine or Cortisol is masking sleep pressure."""
        return (self.dopamine >= self.config.dopamine_mask_threshold or
                self.cortisol >= self.config.cortisol_mask_threshold)

    def should_force_sleep(self) -> bool:
        """Forces sleep when adenosine is critical and unmasked."""
        if self.adenosine >= self.config.force_sleep_threshold:
            if not self.is_sleep_masked():
                return True
            if self.adenosine > self.config.force_sleep_threshold + 0.5:
                return True
        return False

    def get_effective_anxiety_factor(self, raw_anxiety: float) -> float:
        """
        GABA + Serotonin jointly amortize anxiety before it maps to atomic mass.
        High serotonin + high GABA = anxiety signal still received, but not catastrophized.
        """
        amortization = 1.0 + (self.serotonin * 0.6) + (self.gaba * 0.4)
        return raw_anxiety / amortization

    def get_cognitive_load_multiplier(self) -> float:
        """
        Energy cost multiplier. Serotonin now actively REDUCES cost (not just penalizes when low).
        """
        multiplier = 1.0

        # Penalty for sleep deprivation
        if self.adenosine > self.config.sleep_pressure_threshold:
            excess = self.adenosine - self.config.sleep_pressure_threshold
            multiplier += (excess * 2.5)

        # Serotonin REDUCES cognitive cost — it's structural stability
        serotonin_bonus = self.serotonin * 0.3  # Up to 30% cost reduction
        multiplier = max(0.5, multiplier - serotonin_bonus)

        # GABA provides additional calming efficiency
        gaba_bonus = self.gaba * 0.1
        multiplier = max(0.5, multiplier - gaba_bonus)

        # Penalty for low stability/mood (kept as floor signal)
        if self.serotonin < 0.3:
            multiplier += 0.4

        # Threat overdrive cost
        if self.cortisol > 0.8:
            multiplier += 0.5

        return multiplier

    def get_status_report(self) -> dict:
        return {
            "adenosine":       round(self.adenosine, 3),
            "dopamine":        round(self.dopamine, 3),
            "cortisol":        round(self.cortisol, 3),
            "serotonin":       round(self.serotonin, 3),
            "gaba":            round(self.gaba, 3),
            "oxytocin":        round(self.oxytocin, 3),
            "testosterone":    round(self.testosterone, 3),
            "adrenaline":      round(self.adrenaline, 3),
            "estrogen":        round(self.estrogen, 3),
            "sleep_deprived":  self.is_sleep_deprived,
            "sleep_masked":    self.is_sleep_masked(),
            "cognitive_multiplier": round(self.get_cognitive_load_multiplier(), 3),
            "effective_anxiety_factor": round(self.get_effective_anxiety_factor(1.0), 3),
        }

    def learning_window_open(self) -> bool:
        """True if the learning window is open based on tiredness/stress."""
        if self.adenosine >= 0.8 or self.cortisol >= 0.8:
            return False
        return True

    def get_learning_quality_multiplier(self) -> float:
        """Calculates learning quality based on current neurochemistry."""
        import numpy as np
        quality = self.serotonin * (1.0 - min(0.9, self.adenosine)) * (1.0 - min(0.9, self.cortisol))
        return float(np.clip(quality, 0.0, 1.0))
