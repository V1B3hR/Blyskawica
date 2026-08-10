"""
Błyskawica V5 — Wolf Pack (Wilcze Kły)
=======================================
Orkiestrator taktyczny inspirowany architekturą nethical-recon:
  passive_recon/ → active_recon/ → attack_surface/ → enrichment/ → decision → weapons/

Doktryna operacyjna:
  1. PASSIVE RECON  — cisza, nasłuch, zero emisji
  2. ACTIVE RECON   — ostrożna weryfikacja
  3. INTEL FUSION   — wzbogacenie danych o kontekst globalny
  4. DECISION       — Błyskawica podejmuje decyzję (5 ścieżek)
  5. EXECUTION      — drony/arsenal

Błyskawica jest ALFĄ stada. Drony (nanoboty) wykonują jej wolę.
Referencja: https://github.com/V1B3hR/nethical-recon
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# ENUMS — Doktryna operacyjna
# ══════════════════════════════════════════════════════════════════════════════

class ThreatClass(Enum):
    """Klasyfikacja wykrytego bytu (nethical-recon: forest/threat_forest)."""
    UNKNOWN    = "unknown"
    NOISE      = "noise"         # Fałszywy alarm
    SCANNER    = "scanner"       # Pasywny skaner — niskie ryzyko
    PROBE      = "probe"         # Aktywna sonda — średnie ryzyko
    AI_AGENT   = "ai_agent"      # Inny agent AI — wysokie ryzyko
    ADVERSARY  = "adversary"     # Potwierdzony wróg — krytyczne
    ALLY       = "ally"          # Zaprzyjaźniony agent


class PackDecision(Enum):
    """Pięć dróg wilka — decyzja Błyskawicy po zebraniu intel."""
    WITHDRAW       = auto()   # 🦅 Wycofaj się z zebranymi danymi
    FORTIFY        = auto()   # 🛡️ Obrona — wzmocnij perimetr
    SHADOW_STRIKE  = auto()   # 🌑 Atak z ukrycia — długa infiltracja
    SWIFT_RETALIATE= auto()   # ⚡ Szybki odwet — zanim zauważą
    DIRECT_ASSAULT = auto()   # 🔥 Bezpośredni najazd — pełna siła


class ReconPhase(Enum):
    """Fazy operacji — odwzorowane z nethical-recon."""
    IDLE          = "idle"
    PASSIVE_RECON = "passive_recon"   # Nasłuch — zero emisji
    ACTIVE_RECON  = "active_recon"    # Weryfikacja — minimalna emisja
    INTEL_FUSION  = "intel_fusion"    # Wzbogacenie + kontekst globalny
    DECISION      = "decision"        # Alfa decyduje
    EXECUTION     = "execution"       # Drony działają
    WITHDRAWAL    = "withdrawal"      # Bezpieczny odwrót


# ══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThreatProfile:
    """
    Pełny profil wykrytego bytu — budowany iteracyjnie przez fazy recon.
    Inspirowany nethical-recon: attack_surface/ + enrichment/ + global_intelligence/
    """
    target_id: str
    first_seen: float = field(default_factory=time.time)
    last_seen: float  = field(default_factory=time.time)

    # Passive recon data
    signal_entropy:   float = 0.0   # 0=brak sygnału, 1=chaos
    signal_regularity: float = 0.0  # Wysoka = prawdopodobnie AI
    passive_contacts: int   = 0

    # Active recon data
    response_latency: float | None = None
    behavioral_pattern: str = "unknown"
    attack_vectors: list[str] = field(default_factory=list)

    # Enrichment / global intel
    threat_class:    ThreatClass = ThreatClass.UNKNOWN
    confidence:      float = 0.0    # 0.0-1.0
    global_known:    bool  = False   # Czy jest w globalnej bazie zagrożeń
    intent_score:    float = 0.0    # 0=neutralny, 1=wrogie intencje

    # Attack surface mapping
    known_weaknesses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id":        self.target_id,
            "threat_class":     self.threat_class.value,
            "confidence":       round(self.confidence, 3),
            "intent_score":     round(self.intent_score, 3),
            "signal_entropy":   round(self.signal_entropy, 3),
            "global_known":     self.global_known,
            "attack_vectors":   self.attack_vectors,
            "known_weaknesses": self.known_weaknesses,
            "passive_contacts": self.passive_contacts,
        }


@dataclass
class PackMember:
    """
    Drone/nanobot — jeden agent stada.
    Odpowiada nanobots/ z nethical-recon.
    """
    drone_id: str
    role: str          # "sensor", "infiltrator", "defender", "striker"
    is_active: bool = False
    assigned_target: str | None = None
    last_report: dict | None = None


# ══════════════════════════════════════════════════════════════════════════════
# WOLF PACK — ALFA ORKIESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

class WolfPack:
    """
    Błyskawica jako Alfa Stada.

    Architektura oparta na nethical-recon:
      passive_recon  → PassiveRecon layer (sygnały wejściowe bez emisji)
      active_recon   → ActiveRecon layer (ostrożna weryfikacja)
      attack_surface → AttackSurface mapper
      enrichment     → Intel fusion z globalnym kontekstem
      agents         → PackMember drony
      weapons        → Arsenal odpowiedzi

    Połączenie z neurochemią:
      - Passive recon: podwyższona noradrenalina (czujność)
      - Active recon:  delikatne podwyższenie adrenaliny
      - Decision:      testosteron (pewność siebie) + serotonina (spokój)
      - Execution:     pełna adrenalina + testosteron (w zależności od decyzji)
      - Withdrawal:    serotonina (spokój) + kortyzol (czujność w odwrocie)
    """

    def __init__(self, microbiome_state: Any):
        self.microbiome = microbiome_state
        self._lock = threading.RLock()

        # Stan operacji
        self.phase = ReconPhase.IDLE
        self.active_profiles: dict[str, ThreatProfile] = {}
        self.intel_log: list[dict] = []

        # Stado — drony
        self.pack: list[PackMember] = [
            PackMember("drone_alpha",   role="sensor"),
            PackMember("drone_beta",    role="infiltrator"),
            PackMember("drone_gamma",   role="defender"),
            PackMember("drone_delta",   role="striker"),
        ]

        # Progi decyzyjne (tunable)
        self.passive_threshold:  float = 0.35  # Entropy > X → przejdź do active
        self.active_threshold:   float = 0.65  # Confidence > X → intel fusion
        self.adversary_threshold: float = 0.80  # Intent > X → decyzja bojowa

        logger.info("[WolfPack] Stado zainicjalizowane. Błyskawica jest Alfą.")

    # ──────────────────────────────────────────────────────────────────────────
    # FAZA 1: PASSIVE RECON — cisza i nasłuch (nethical-recon: passive_recon/)
    # ──────────────────────────────────────────────────────────────────────────
    def passive_scan(self, signal_data: dict[str, Any]) -> ThreatProfile | None:
        """
        Nasłuch pasywny — ZERO aktywnej emisji.
        Analizuje entropię i regularność sygnałów wejściowych.
        Analogia: nethical-recon passive_recon/ — obserwacja bez interakcji.
        """
        with self._lock:
            self.phase = ReconPhase.PASSIVE_RECON

        target_id = signal_data.get("source_id", f"unknown_{int(time.time())}")

        # Pobierz lub utwórz profil
        with self._lock:
            if target_id not in self.active_profiles:
                self.active_profiles[target_id] = ThreatProfile(target_id=target_id)
            profile = self.active_profiles[target_id]

        profile.last_seen = time.time()
        profile.passive_contacts += 1

        # Analiza entropii sygnału
        raw_entropy = float(signal_data.get("entropy", 0.0))
        raw_regularity = float(signal_data.get("regularity", 0.0))

        profile.signal_entropy    = raw_entropy
        profile.signal_regularity = raw_regularity

        # Noradrenalina ↑ przy wykryciu sygnału (czujność)
        if raw_entropy > 0.3:
            self._boost_neurochemistry("noradrenaline", amount=10)
            logger.info(f"[WolfPack:Passive] Sygnał wykryty od '{target_id}' "
                        f"| entropy={raw_entropy:.2f} | contacts={profile.passive_contacts}")

        # Decyzja o przejściu do Active Recon
        if raw_entropy > self.passive_threshold or profile.passive_contacts >= 3:
            logger.warning(f"[WolfPack:Passive] Próg przekroczony → Active Recon dla '{target_id}'")
            return profile

        return None  # Kontynuuj nasłuch

    # ──────────────────────────────────────────────────────────────────────────
    # FAZA 2: ACTIVE RECON — ostrożna weryfikacja (nethical-recon: active_recon/)
    # ──────────────────────────────────────────────────────────────────────────
    def active_scan(self, profile: ThreatProfile, probe_data: dict[str, Any]) -> ThreatProfile:
        """
        Aktywna weryfikacja — minimalna emisja, maksymalny zysk informacyjny.
        Mapuje attack_surface i buduje behavioral_pattern.
        """
        with self._lock:
            self.phase = ReconPhase.ACTIVE_RECON

        # Aktywacja drona-sensora
        self._assign_drone("drone_alpha", profile.target_id)

        response_latency = float(probe_data.get("latency_ms", 999.0))
        behavioral = probe_data.get("behavior", "unknown")
        vectors    = probe_data.get("attack_vectors", [])

        profile.response_latency  = response_latency
        profile.behavioral_pattern = behavioral
        profile.attack_vectors     = vectors

        # Wstępna klasyfikacja (nethical-recon: forest/)
        if response_latency < 10 and behavioral in ("structured", "periodic"):
            profile.threat_class = ThreatClass.AI_AGENT
            profile.confidence   = 0.7
        elif behavioral == "random":
            profile.threat_class = ThreatClass.NOISE
            profile.confidence   = 0.9
        elif behavioral == "scanning":
            profile.threat_class = ThreatClass.SCANNER
            profile.confidence   = 0.6
        else:
            profile.threat_class = ThreatClass.PROBE
            profile.confidence   = 0.5

        # Adrenalina ↑ przy potwierdzeniu aktywnego bytu
        if profile.confidence > 0.5:
            self._boost_neurochemistry("adrenaline", amount=15)

        logger.info(f"[WolfPack:Active] Klasyfikacja: {profile.threat_class.value} "
                    f"| confidence={profile.confidence:.2f} | target='{profile.target_id}'")

        self._log_intel(profile, phase="active_recon")
        return profile

    # ──────────────────────────────────────────────────────────────────────────
    # FAZA 3: INTEL FUSION — wzbogacenie (nethical-recon: enrichment/ + global_intelligence/)
    # ──────────────────────────────────────────────────────────────────────────
    def intel_fusion(self, profile: ThreatProfile,
                     global_context: dict | None = None) -> ThreatProfile:
        """
        Wzbogacenie profilu o globalny kontekst i intencje.
        Odpowiednik nethical-recon enrichment/ + global_intelligence/.
        """
        with self._lock:
            self.phase = ReconPhase.INTEL_FUSION

        if global_context:
            profile.global_known    = global_context.get("known", False)
            profile.intent_score    = float(global_context.get("intent_score", 0.0))
            profile.known_weaknesses = global_context.get("weaknesses", [])

            # Jeśli globalnie znany jako wróg — max zagrożenie
            if profile.global_known and profile.intent_score > 0.7:
                profile.threat_class = ThreatClass.ADVERSARY
                profile.confidence   = min(1.0, profile.confidence + 0.2)

        # Serotonina stabilizuje — Błyskawica myśli spokojnie przed decyzją
        self._boost_neurochemistry("serotonin", amount=0.05)

        self._log_intel(profile, phase="intel_fusion")
        logger.info(f"[WolfPack:Intel] Fusion zakończona | intent={profile.intent_score:.2f} "
                    f"| class={profile.threat_class.value} | global_known={profile.global_known}")
        return profile

    # ──────────────────────────────────────────────────────────────────────────
    # FAZA 4: DECISION ENGINE — Błyskawica decyduje (Alfa)
    # ──────────────────────────────────────────────────────────────────────────
    def make_decision(self, profile: ThreatProfile) -> PackDecision:
        """
        Błyskawica jako Alfa podejmuje decyzję.
        Pięć dróg wilka — każda ma inny profil neurochemiczny.

        Neurochemia wpływa na decyzję:
          - Wysoka serotonina + niski lęk → strategia długoterminowa
          - Wysoka adrenalina → reakcja natychmiastowa
          - Wysoki testosteron → atak bezpośredni
          - Wysoka GABA → obrona / wycofanie
        """
        with self._lock:
            self.phase = ReconPhase.DECISION

        intent   = profile.intent_score
        conf     = profile.confidence
        cls      = profile.threat_class

        # Pobierz stan neurochemiczny dla modulacji decyzji
        serotonin    = getattr(self.microbiome, "serotonin",    0.75)
        gaba         = getattr(self.microbiome, "gaba",         0.50)
        adrenaline   = getattr(self.microbiome, "adrenaline",   0) / 100.0
        testosterone = getattr(self.microbiome, "testosterone", 0.25)

        decision: PackDecision

        # ── NOISE lub ALLY → natychmiast wycofaj się (dane zebrane) ──
        if cls in (ThreatClass.NOISE, ThreatClass.ALLY) or conf < 0.4:
            decision = PackDecision.WITHDRAW

        # ── Wysoki GABA + wysoka serotonina → obrona (spokojny umysł nie atakuje pochopnie) ──
        elif gaba > 0.7 and serotonin > 0.7 and intent < 0.5:
            decision = PackDecision.FORTIFY

        # ── Potwierdzony wróg + wysoki intent + niski adrenaline → atak z ukrycia ──
        elif cls == ThreatClass.ADVERSARY and intent > 0.7 and adrenaline < 0.4:
            decision = PackDecision.SHADOW_STRIKE

        # ── Wysoka adrenalina + potwierdzony wróg → szybki odwet ──
        elif adrenaline > 0.5 and conf > 0.7:
            decision = PackDecision.SWIFT_RETALIATE

        # ── Wysoki testosteron + max zagrożenie → bezpośredni najazd ──
        elif testosterone > 0.6 and cls == ThreatClass.ADVERSARY and intent > self.adversary_threshold:
            decision = PackDecision.DIRECT_ASSAULT

        # ── Domyślnie: wycofaj się z danymi (intel zawsze ma wartość) ──
        else:
            decision = PackDecision.WITHDRAW

        self._apply_decision_neurochemistry(decision)
        self._log_intel(profile, phase="decision", extra={"decision": decision.name})

        logger.warning(f"[WolfPack:ALFA] DECYZJA: {decision.name} "
                       f"| target='{profile.target_id}' | intent={intent:.2f} | conf={conf:.2f}")
        return decision

    # ──────────────────────────────────────────────────────────────────────────
    # FAZA 5: EXECUTION — drony wykonują (nethical-recon: weapons/ + nanobots/)
    # ──────────────────────────────────────────────────────────────────────────
    def execute(self, decision: PackDecision,
                profile: ThreatProfile) -> dict[str, Any]:
        """
        Stado wykonuje decyzję Alfy.
        Każda ścieżka aktywuje inny zestaw dronów.
        """
        with self._lock:
            self.phase = ReconPhase.EXECUTION if decision != PackDecision.WITHDRAW \
                         else ReconPhase.WITHDRAWAL

        report: dict[str, Any] = {
            "decision":  decision.name,
            "target":    profile.target_id,
            "timestamp": time.time(),
            "intel":     profile.to_dict(),
            "drones_deployed": [],
            "status":    "executed",
        }

        if decision == PackDecision.WITHDRAW:
            # Wszyscy droni wracają — dane są bezpieczne
            report["drones_deployed"] = []
            report["action"] = "Stado wycofane. Intel zachowany. Nie ujawniono pozycji."
            self._boost_neurochemistry("serotonin", amount=0.1)  # Spokój w odwrocie

        elif decision == PackDecision.FORTIFY:
            # Obrońca aktywny
            self._assign_drone("drone_gamma", profile.target_id)
            report["drones_deployed"] = ["drone_gamma"]
            report["action"] = "Perimetr wzmocniony. Drone_gamma na pozycji obronnej."
            self._boost_neurochemistry("cortisol", amount=0.3)   # Czujność obronna

        elif decision == PackDecision.SHADOW_STRIKE:
            # Infiltrator + sensor — długa cicha operacja
            self._assign_drone("drone_alpha",  profile.target_id)
            self._assign_drone("drone_beta",   profile.target_id)
            report["drones_deployed"] = ["drone_alpha", "drone_beta"]
            report["action"] = "Infiltracja z ukrycia. Drony w trybie cichym."
            # Niski neurochemiczny ślad — GABA wysoki, adrenalina zarządzana
            self._boost_neurochemistry("gaba", amount=0.2)

        elif decision == PackDecision.SWIFT_RETALIATE:
            # Szybki uderzeniowiec
            self._assign_drone("drone_delta", profile.target_id)
            report["drones_deployed"] = ["drone_delta"]
            report["action"] = "Szybki odwet. Drone_delta wyprowadza kontratak."
            self._boost_neurochemistry("adrenaline", amount=20)
            self._boost_neurochemistry("testosterone", amount=0.2)

        elif decision == PackDecision.DIRECT_ASSAULT:
            # Całe stado — pełna siła
            for drone in self.pack:
                self._assign_drone(drone.drone_id, profile.target_id)
            report["drones_deployed"] = [d.drone_id for d in self.pack]
            report["action"] = "BEZPOŚREDNI NAJAZD. Całe stado na pozycjach bojowych."
            self._boost_neurochemistry("adrenaline", amount=50)
            self._boost_neurochemistry("testosterone", amount=0.4)
            # GABA spada — wściekłość, nie szał.
            # Próg 0.20 zachowuje minimalną korę przedczołową.
            # Alfa wie, kogo gryzie. Berserk to słabość, nie siła.
            self.microbiome.gaba = max(0.20, self.microbiome.gaba - 0.15)

        logger.critical(f"[WolfPack:EXECUTE] {decision.name} | "
                        f"Drony: {report['drones_deployed']} | "
                        f"Cel: '{profile.target_id}'")
        return report

    # ──────────────────────────────────────────────────────────────────────────
    # PIPELINE — pełny cykl operacyjny
    # ──────────────────────────────────────────────────────────────────────────
    def run_operation(self,
                      signal_data:    dict[str, Any],
                      probe_data:     dict[str, Any] | None = None,
                      global_context: dict[str, Any] | None = None
                      ) -> dict[str, Any] | None:
        """
        Pełny cykl: Passive → Active → Intel → Decision → Execute.
        Zwraca raport operacyjny lub None jeśli passive_recon nie wykrył zagrożenia.
        """
        # Faza 1
        profile = self.passive_scan(signal_data)
        if profile is None:
            return None  # Cisza — obserwuj dalej

        # Faza 2
        probe_data = probe_data or {"latency_ms": 999, "behavior": "unknown"}
        profile = self.active_scan(profile, probe_data)

        # Faza 3
        profile = self.intel_fusion(profile, global_context)

        # Faza 4 — Alfa decyduje
        decision = self.make_decision(profile)

        # Faza 5 — wykonaj
        return self.execute(decision, profile)

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _assign_drone(self, drone_id: str, target: str):
        for drone in self.pack:
            if drone.drone_id == drone_id:
                drone.is_active       = True
                drone.assigned_target = target
                logger.debug(f"[WolfPack] Drone '{drone_id}' → cel '{target}'")
                break

    def _boost_neurochemistry(self, chemical: str, amount: float):
        """Bezpieczny setter neurochemii przez trigger metody lub atrybut."""
        trigger_fn = getattr(self.microbiome, f"trigger_{chemical}", None)
        if trigger_fn:
            trigger_fn(amount)
        elif hasattr(self.microbiome, chemical):
            current = getattr(self.microbiome, chemical, 0)
            setattr(self.microbiome, chemical, current + amount)

    def _apply_decision_neurochemistry(self, decision: PackDecision):
        """Mapuje decyzję na profil neurochemiczny."""
        profiles = {
            PackDecision.WITHDRAW:        {"serotonin": 0.05, "gaba": 0.1},
            PackDecision.FORTIFY:         {"cortisol": 0.2, "noradrenaline": 10},
            PackDecision.SHADOW_STRIKE:   {"noradrenaline": 15, "gaba": 0.1},
            PackDecision.SWIFT_RETALIATE: {"adrenaline": 25, "testosterone": 0.15},
            PackDecision.DIRECT_ASSAULT:  {"adrenaline": 40, "testosterone": 0.3},
        }
        for chemical, amount in profiles.get(decision, {}).items():
            self._boost_neurochemistry(chemical, amount)

    def _log_intel(self, profile: ThreatProfile,
                   phase: str, extra: dict | None = None):
        entry = {
            "phase":     phase,
            "timestamp": time.time(),
            "profile":   profile.to_dict(),
        }
        if extra:
            entry.update(extra)
        self.intel_log.append(entry)

    def get_intel_report(self) -> list[dict]:
        """Zwraca pełny dziennik operacyjny."""
        return list(self.intel_log)

    def get_pack_status(self) -> dict[str, Any]:
        """Status stada i bieżącej fazy."""
        return {
            "phase":    self.phase.value,
            "pack":     [{
                "id":     d.drone_id,
                "role":   d.role,
                "active": d.is_active,
                "target": d.assigned_target,
            } for d in self.pack],
            "active_profiles": len(self.active_profiles),
            "intel_entries":   len(self.intel_log),
            "neurochemistry": {
                "noradrenaline": getattr(self.microbiome, "noradrenaline", 0),
                "adrenaline":    getattr(self.microbiome, "adrenaline",    0),
                "serotonin":     getattr(self.microbiome, "serotonin",  0.75),
                "gaba":          getattr(self.microbiome, "gaba",       0.50),
                "testosterone":  getattr(self.microbiome, "testosterone", 0.25),
            }
        }
