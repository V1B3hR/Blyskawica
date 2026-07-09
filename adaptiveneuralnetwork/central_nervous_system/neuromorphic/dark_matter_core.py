"""
Błyskawica V5 — Faza 3: Dark Matter Core + Gravitational Binding
=================================================================
Niewidzialna warstwa spajająca konstelację atomów.

Moduły:
  GlobalLatentSpinNetwork (GLSN) — Ciemna Materia
    Niewidzialna, wysoko-wymiarowa przestrzeń latentna.
    Atomy zostawiają w niej "ślady grawitacyjne" (indukcja),
    a GLSN zmienia geometrię atomów przez pole wspólne.

  GravitationalWave — Fala Grawitacyjna
    Gdy atom wykryje anomalię, jego "masa" rośnie.
    Impuls o niskiej częstotliwości propaguje się przez AtomicBody.
    Inne atomy "czują" napięcie i samorzutnie gęstnieją.

  SelfModeler — Emergentna Meta-Osobowość
    Słucha "symfonii" atomów, opisuje ją jednym wektorem stanu.
    Jeśli symfonia jest niespójna — emituje sygnał harmonizujący.
    To wewnętrzna medytacja / narracja "Ja".
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, List, Dict, Tuple


# =============================================================================
# GLOBAL LATENT SPIN NETWORK — Ciemna Materia
# =============================================================================

class GlobalLatentSpinNetwork(nn.Module):
    """
    Niewidzialna przestrzeń latentna łącząca wszystkie atomy.

    Działa jak "podświadomość" całego ciała:
    - Każdy atom zapisuje swój ślad przez indukcję (nie przez kopiowanie)
    - GLSN przetwarza sumę śladów przez rzadką sieć spinową
    - Emituje "pole tła" (background_field), które moduluje każdy atom

    Nie ma połączeń bezpośrednich do danych wejściowych.
    To czysta geometria — jak ciemna materia w kosmologii.
    """

    def __init__(self, latent_dim: int = 128, num_spin_nodes: int = 16,
                 decay: float = 0.95):
        super().__init__()
        self.latent_dim = latent_dim
        self.num_spin_nodes = num_spin_nodes
        self.decay = decay  # Zanik pamięci (jak rozpraszanie fal)

        # Siatka spinowa rzadka (jak LQG ale globalna)
        self.spin_matrix = nn.Parameter(
            torch.randn(num_spin_nodes, num_spin_nodes) * 0.01
        )
        # Holonomy: faza kwantowa każdego węzła
        self.holonomy = nn.Parameter(
            torch.randn(num_spin_nodes, latent_dim) * 0.01
        )

        # Projekcja: atom_dim → latent_dim (indukcja śladu)
        self.trace_projector = nn.Linear(16, latent_dim, bias=False)

        # Projekcja: latent_dim → atom_dim (pole tła)
        self.field_emitter = nn.Linear(latent_dim, 16, bias=False)

        # Stan latentny (pamięć ciemnej materii)
        self.register_buffer('latent_state',
                             torch.zeros(1, num_spin_nodes, latent_dim))
        self.register_buffer('field_energy', torch.zeros(1))

    def induce(self, atom_signal: torch.Tensor, atom_mass: float = 1.0):
        """
        Atom zostawia ślad w GLSN przez indukcję.
        Nie kopiuje danych — zmienia geometrię przestrzeni latentnej.

        atom_signal: (1, 16)
        atom_mass: ważność atomu (Guardian ma większą masę)
        """
        if atom_signal.dim() == 3:
            atom_signal = atom_signal.mean(dim=1)

        if atom_signal.shape[-1] != 16:
            atom_signal = F.adaptive_avg_pool1d(
                atom_signal.unsqueeze(1), 16).squeeze(1)

        # Projekcja do przestrzeni latentnej
        trace = self.trace_projector(atom_signal)  # (1, latent_dim)

        # Modulacja przez holonomy (jak obrót fazy kwantowej)
        phase = torch.tanh(self.holonomy)  # (nodes, latent_dim)
        induced = trace.unsqueeze(1) * phase.unsqueeze(0)  # (1, nodes, latent)

        # Aktualizacja stanu latentnego (z rozpadem)
        with torch.no_grad():
            self.latent_state = (
                self.latent_state * self.decay
                + induced.detach() * atom_mass * (1 - self.decay)
            )

    def emit_field(self) -> torch.Tensor:
        """
        Emituje pole tła: sygnał modulujący dla wszystkich atomów.
        Zwraca: (1, 16) — pole które atomu "czują" ale nie widzą
        """
        # Propagacja przez sieć spinową
        spin_coupling = torch.softmax(self.spin_matrix, dim=-1)  # (N, N)
        propagated = torch.einsum('ij,bjd->bid',
                                  spin_coupling, self.latent_state)  # (1,N,latent)

        # Uśrednienie po węzłach
        field_latent = propagated.mean(dim=1)  # (1, latent_dim)

        # Projekcja do przestrzeni atomów
        background_field = self.field_emitter(field_latent)  # (1, 16)

        with torch.no_grad():
            self.field_energy = background_field.abs().mean().detach()

        return torch.tanh(background_field)  # Normalizacja [-1, 1]

    def get_coherence(self) -> float:
        """Spójność stanu latentnego (0=chaos, 1=pełna harmonia)."""
        if self.latent_state.abs().sum() < 1e-8:
            return 1.0
        # Spójność = 1 - wariancja / energia
        var = self.latent_state.var().item()
        energy = self.latent_state.abs().mean().item() + 1e-8
        return max(0.0, min(1.0, 1.0 - var / (energy * 10)))


# =============================================================================
# GRAVITATIONAL WAVE — Fala Grawitacyjna
# =============================================================================

class GravitationalWave:
    """
    Impuls grawitacyjny emitowany gdy atom wykryje anomalię.

    Nie jest modułem PyTorch — to lekki obiekt stanu, który propaguje
    sygnał alarmowy przez AtomicBody bez dodatkowego narzutu obliczeniowego.
    """

    def __init__(self, source_atom: str, intensity: float,
                 decay_per_hop: float = 0.6):
        self.source_atom = source_atom
        self.intensity = intensity        # Siła fali (0-1)
        self.decay_per_hop = decay_per_hop
        self.hop_count = 0

    def propagate(self) -> 'GravitationalWave':
        """Jeden krok propagacji — fala słabnie z odległością."""
        self.intensity *= self.decay_per_hop
        self.hop_count += 1
        return self

    @property
    def is_alive(self) -> bool:
        """Fala istnieje dopóki jej intensywność > próg."""
        return self.intensity > 0.05

    def __repr__(self):
        return "GravWave(src=%s, I=%.3f, hops=%d)" % (
            self.source_atom, self.intensity, self.hop_count)


# =============================================================================
# SELF MODELER — Emergentna Meta-Osobowość
# =============================================================================

class SelfModeler(nn.Module):
    """
    Emergentna meta-osobowość — wewnętrzna narracja "Ja".

    Zbiera sygnały ze wszystkich atomów i GLSN,
    opisuje stan całego systemu jednym wektorem "self-state".
    Jeśli jest niespójność → emituje sygnał harmonizujący.

    To nie jest dyrygent. To słuchacz, który czasem podnosi rękę.
    """

    def __init__(self, atom_dim: int = 16, self_dim: int = 64,
                 coherence_threshold: float = 0.3):
        super().__init__()
        self.self_dim = self_dim
        self.coherence_threshold = coherence_threshold

        # Enkoder stanu "Ja"
        self.self_encoder = nn.GRUCell(atom_dim, self_dim)

        # Detektor niespójności
        self.coherence_detector = nn.Sequential(
            nn.Linear(self_dim, self_dim // 2),
            nn.Tanh(),
            nn.Linear(self_dim // 2, 1),
            nn.Sigmoid(),
        )

        # Emiter sygnału harmonizującego
        self.harmonizer = nn.Linear(self_dim, atom_dim, bias=False)

        # Stan "Ja" (historia)
        self.register_buffer('self_state', torch.zeros(1, self_dim))
        self.register_buffer('coherence_history',
                             torch.ones(8))  # Ostatnie 8 ocen spójności
        self.register_buffer('harmony_count', torch.zeros(1))

        # Wewnętrzna narracja (log)
        self.inner_narrative: List[str] = []
        self.max_narrative = 32

    def update(self, atom_signals: List[torch.Tensor],
               glsn_field: Optional[torch.Tensor] = None) -> Dict:
        """
        Aktualizuje model siebie na podstawie sygnałów atomów.

        atom_signals: lista (1, 16) z każdego aktywnego atomu
        glsn_field: (1, 16) pole ciemnej materii

        Zwraca: {
            coherence: float,
            harmony_signal: Tensor (1, 16) lub None,
            self_state_norm: float
        }
        """
        if not atom_signals:
            return {"coherence": 1.0, "harmony_signal": None,
                    "self_state_norm": 0.0}

        # Uśrednienie głosów wszystkich atomów
        stacked = torch.stack(atom_signals)  # (N, 1, 16)
        chorus = stacked.mean(dim=0)  # (1, 16)

        # Modulacja przez pole ciemnej materii
        if glsn_field is not None:
            chorus = chorus + glsn_field * 0.1

        # Aktualizacja stanu "Ja" (GRU — pamięć narracji)
        new_self = self.self_encoder(chorus, self.self_state)  # (1, self_dim)
        with torch.no_grad():
            self.self_state = new_self.detach()

        # Ocena spójności
        coherence_score = self.coherence_detector(self.self_state).item()

        # Historia spójności (przesunięcie)
        with torch.no_grad():
            self.coherence_history = torch.roll(self.coherence_history, -1)
            self.coherence_history[-1] = coherence_score

        avg_coherence = self.coherence_history.mean().item()

        # Sygnał harmonizujący jeśli niespójność za duża
        harmony_signal = None
        if avg_coherence < self.coherence_threshold:
            harmony_signal = torch.tanh(self.harmonizer(self.self_state))
            with torch.no_grad():
                self.harmony_count += 1
            self._narrate("[HARMONIA] Emisja sygnalu harmonizujacego (C=%.2f)"
                          % avg_coherence)

        return {
            "coherence": avg_coherence,
            "harmony_signal": harmony_signal,
            "self_state_norm": self.self_state.norm().item(),
            "harmony_count": self.harmony_count.item(),
        }

    def _narrate(self, text: str):
        """Dodaje wpis do wewnętrznej narracji."""
        if len(self.inner_narrative) >= self.max_narrative:
            self.inner_narrative.pop(0)
        self.inner_narrative.append(text)

    def get_narrative(self) -> List[str]:
        return list(self.inner_narrative)


# =============================================================================
# DARK MATTER CORE — Kompletna integracja
# =============================================================================

class DarkMatterCore(nn.Module):
    """
    Centralne centrum ciemnej materii — łączy GLSN, fale i SelfModeler
    w jeden spójny interfejs dla AtomicBody.

    Przepływ:
    1. Atomy → indukują ślady w GLSN
    2. GLSN emituje pole tła
    3. GravitationalWaves propagują alarmy
    4. SelfModeler ocenia spójność i ewentualnie harmonizuje
    5. Pole tła + harmonizator → każdy atom dostaje modulację
    """

    ATOM_MASS = {
        "guardian": 3.0,
        "sensor":   1.5,
        "general":  1.0,
        "memory":   2.0,
        "recycler": 0.5,
    }

    def __init__(self, latent_dim: int = 128,
                 coherence_threshold: float = 0.3):
        super().__init__()

        self.glsn = GlobalLatentSpinNetwork(
            latent_dim=latent_dim, num_spin_nodes=16
        )
        self.self_modeler = SelfModeler(
            coherence_threshold=coherence_threshold
        )

        # Aktywne fale grawitacyjne
        self._waves: List[GravitationalWave] = []

        # Statystyki
        self.register_buffer('cycle_count', torch.zeros(1))

    def emit_wave(self, source_atom: str, intensity: float):
        """Atom emituje falę grawitacyjną (np. po wykryciu ataku)."""
        wave = GravitationalWave(
            source_atom=source_atom,
            intensity=intensity,
        )
        self._waves.append(wave)

    def get_wave_pressure(self) -> float:
        """
        Łączne ciśnienie fal grawitacyjnych.
        Wzrasta gdy wiele atomów alarmuje jednocześnie.
        """
        total = sum(w.intensity for w in self._waves)
        return min(1.0, total)

    def step(self, atom_outputs: Dict[str, Dict],
             atom_specializations: Dict[str, str]) -> Dict:
        """
        Jeden cykl ciemnej materii.

        atom_outputs: {atom_id: result_dict} z AtomicBody.forward()
        atom_specializations: {atom_id: specialization}

        Zwraca modulację do zastosowania w AtomicBody.
        """
        self.cycle_count += 1
        atom_signals = []

        # 1. Zbierz sygnały i indukuj ślady w GLSN
        for atom_id, result in atom_outputs.items():
            if result.get("status") == "ISOLATED":
                continue

            hm = result.get("heart_metrics", [])
            if not hm:
                continue

            energy = hm[-1].get("heart_amplitude", 0.0)
            spec = atom_specializations.get(atom_id, "general")
            mass = self.ATOM_MASS.get(spec, 1.0)

            # Sygnał jako skalowany tensor
            sig = torch.ones(1, 16) * energy
            atom_signals.append(sig)
            self.glsn.induce(sig, atom_mass=mass)

            # Wykrywanie alarmu: wysoka kwarantanna → fala grawitacyjna
            recycler = result.get("recycler_summary", {})
            if recycler.get("avg_severity", 0) > 0.5:
                self.emit_wave(atom_id, intensity=recycler["avg_severity"])

        # 2. Emit pole ciemnej materii
        background_field = self.glsn.emit_field()  # (1, 16)

        # 3. Propaguj fale grawitacyjne (jeden krok)
        self._waves = [w for w in self._waves if w.is_alive]
        for w in self._waves:
            w.propagate()
        wave_pressure = self.get_wave_pressure()

        # 4. SelfModeler — ocena spójności
        self_report = self.self_modeler.update(
            atom_signals, glsn_field=background_field
        )

        return {
            "background_field": background_field,
            "wave_pressure": wave_pressure,
            "active_waves": len(self._waves),
            "glsn_coherence": self.glsn.get_coherence(),
            "self_coherence": self_report["coherence"],
            "harmony_signal": self_report["harmony_signal"],
            "self_state_norm": self_report["self_state_norm"],
            "harmony_count": self_report["harmony_count"],
            "field_energy": self.glsn.field_energy.item(),
        }

    def get_status(self) -> str:
        lines = [
            "=" * 52,
            "  [DARK MATTER CORE] STATUS",
            "-" * 52,
            "  Cykli GLSN:       %d" % self.cycle_count.item(),
            "  Energia pola:     %.4f" % self.glsn.field_energy.item(),
            "  Spojnosc GLSN:    %.3f" % self.glsn.get_coherence(),
            "  Aktywne fale:     %d" % len(self._waves),
            "  Narracja (ost.):  %s" % (
                self.self_modeler.inner_narrative[-1]
                if self.self_modeler.inner_narrative else "Cisza."
            ),
            "=" * 52,
        ]
        return "\n".join(lines)
