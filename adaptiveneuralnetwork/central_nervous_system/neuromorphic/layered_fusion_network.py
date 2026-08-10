"""
Błyskawica V5 — Kwantowo-Fuzyjna Architektura Warstwowa
========================================================

Implementuje wizję Twórcy: sub-atomowy filtr plazmowy z fuzyjnym sercem.

Topologia:
    Świat → [Warstwa 0: 3 kule zewnętrzne] → [Warstwa 1: 4 kule melioracyjne]
          → [Warstwa 2: 3 kule wewnętrzne] → [❤️ Fuzyjny Rdzeń: 1 kula serce]

Zasady:
    - Kule w tej samej warstwie: wektory MOCNE (all-to-all)
    - Między warstwami: wektory CIENKIE (top-k routing, tylko dane zatwierdzone)
    - Serce: izolowane od świata zewnętrznego, dostępne tylko przez Warstwę 2
    - Kule melioracyjne: posiadają wewnętrzny tryb KWARANTANNY
"""

from enum import IntEnum

import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.neuromorphic.orbital_networks import (
    LQGSpinNetwork,
    QuantumGravityNode,
)

# =============================================================================
# STAŁE ARCHITEKTONICZNE
# =============================================================================

class LayerRole(IntEnum):
    EXTERNAL   = 0   # Warstwa 0 — giętka tarcza zewnętrzna
    MELIORATION_I  = 1   # Warstwa 1 — kwarantanna + triage
    MELIORATION_II = 2   # Warstwa 2 — synteza + ostatnia bariera
    FUSION_HEART   = 3   # Serce fuzyjne — rdzeń chroniony plazmą


# Konfiguracja kul per warstwa: (spikes, dim, masa, ilość)
LAYER_CONFIGS = {
    LayerRole.EXTERNAL:        {"spikes": 32,  "dim": 16, "masses": [1.0, 1.2, 0.8]},
    LayerRole.MELIORATION_I:   {"spikes": 64,  "dim": 32, "masses": [2.0, 2.5, 1.8, 3.0]},
    LayerRole.MELIORATION_II:  {"spikes": 64,  "dim": 32, "masses": [3.0, 4.0, 2.5]},
    LayerRole.FUSION_HEART:    {"spikes": 128, "dim": 64, "masses": [12.0]},
}


# =============================================================================
# KULA MELIORACYJNA — Kula z trybem kwarantanny
# =============================================================================

class MeliorationBall(nn.Module):
    """
    Rozszerzony QuantumGravityNode z wewnętrznym stanem melioracyjnym.

    Dodatkowe możliwości:
    - Tryb QUARANTINE: przechwytuje podejrzane paczki danych
    - Wewnętrzna siatka LQG do lokalnej weryfikacji
    - Próg anomalii (anomaly_threshold): sygnały >threshold trafiają do kwarantanny
    - Pojemność bufora: max N paczek w kwarantannie jednocześnie
    - Wymiana z sąsiednimi kulami: MOCNE wektory (all-to-all)
    """

    def __init__(self, num_spikes: int, dim: int, base_freq: float = 1.0,
                 mass: float = 1.0, anomaly_threshold: float = 5.0,
                 quarantine_capacity: int = 8, layer_role: LayerRole = LayerRole.MELIORATION_I):
        super().__init__()

        self.layer_role = layer_role
        self.anomaly_threshold = anomaly_threshold
        self.quarantine_capacity = quarantine_capacity

        # Rdzeń fizyczny (reużywamy sprawdzony QuantumGravityNode)
        self.core = QuantumGravityNode(num_spikes, dim, base_freq=base_freq, mass=mass)

        # Wewnętrzna siatka melioracyjna (dodatkowy filtr LQG wewnątrz kuli)
        self.inner_lqg = LQGSpinNetwork(
            num_spikes=num_spikes // 2,
            dim=dim,
            max_spin=6.0 if mass < 5.0 else 18.0,
        )

        # Stan kwarantanny: lista przechwyconych tensorów
        self.quarantine_buffer: list[torch.Tensor] = []
        self.quarantine_hits: int = 0
        self.released_hits: int = 0

        # Gęstość siatki (rośnie z głębokością warstwy)
        self.mesh_density = 0.3 + (layer_role.value * 0.2)  # 0.3 / 0.5 / 0.7 / 0.9

    @property
    def mass(self):
        return self.core.mass

    @property
    def position(self):
        return self.core.position

    @property
    def schwarzschild_radius(self):
        return self.core.schwarzschild_radius

    def schwarzschild_factor(self, dist):
        return self.core.schwarzschild_factor(dist)

    def _is_anomalous(self, signal: torch.Tensor) -> bool:
        """Sprawdza czy sygnał przekracza próg anomalii."""
        if not isinstance(signal, torch.Tensor):
            return False
        energy = signal.abs().mean().item()
        return energy > self.anomaly_threshold

    def _quarantine(self, signal: torch.Tensor):
        """Przechwytuje podejrzany sygnał do bufora kwarantanny."""
        if len(self.quarantine_buffer) < self.quarantine_capacity:
            self.quarantine_buffer.append(signal.detach().clone())
            self.quarantine_hits += 1

    def _release_quarantine(self, original_shape) -> torch.Tensor | None:
        """
        Zwalnia dane z kwarantanny po wewnętrznej weryfikacji przez siatki LQG.
        Zwraca oczyszczony sygnał (kształt zgodny z original_shape) lub None.
        """
        if not self.quarantine_buffer:
            return None

        # Synteza wszystkich przechwyconych paczek (uśrednienie)
        # Każdy tensor w buforze ma shape (1, spikes, dim) po normalizacji
        stacked = torch.stack(self.quarantine_buffer).mean(dim=0)  # (1, spikes, dim)

        # Adaptuj spike dim do inner_lqg (num_spikes//2) przez adaptive pooling
        target_spikes = self.inner_lqg.num_spikes
        if stacked.shape[1] != target_spikes:
            # (1, spikes, dim) → (1, dim, spikes) → pool → (1, dim, target) → (1, target, dim)
            pooled = torch.nn.functional.adaptive_avg_pool1d(
                stacked.permute(0, 2, 1),   # (1, dim, spikes)
                target_spikes               # → (1, dim, target_spikes)
            ).permute(0, 2, 1)              # (1, target_spikes, dim)
        else:
            pooled = stacked

        # Weryfikacja przez wewnętrzną siatką LQG
        if pooled.shape[-1] == self.inner_lqg.dim:
            verified_small, _ = self.inner_lqg(pooled)
            # Upsample z powrotem do original_shape[1] spikeów
            verified = torch.nn.functional.interpolate(
                verified_small.permute(0, 2, 1),        # (1, dim, target)
                size=original_shape[1],                  # → original spikes
                mode='linear', align_corners=False
            ).permute(0, 2, 1)                          # (1, original_spikes, dim)
        else:
            verified = stacked

        # Tłumienie proporcjonalne do gęstości siatki
        verified = verified * (1.0 - self.mesh_density * 0.5)

        # Upewnij się że kształt jest taki jak oryginał
        if verified.shape[1] != original_shape[1]:
            verified = verified[:, :original_shape[1], :]

        self.quarantine_buffer.clear()
        self.released_hits += 1
        return verified

    def forward(self, incoming, incoming_thickness=None, incoming_stiffness=None,
                time_delta: float = 0.05, other_pos=None):
        """
        Forward z obsługą kwarantanny.
        Podejrzane dane → bufor. Dane czyste → rdzeń fizyczny.
        """
        # Normalizacja do 3D: (batch, num_spikes, dim) jeśli przyszło 2D
        if isinstance(incoming, torch.Tensor) and incoming.dim() == 2:
            incoming = incoming.unsqueeze(1).expand(-1, self.core.num_spikes, -1)

        processed_incoming = incoming

        # Sprawdzenie anomalii
        if isinstance(incoming, torch.Tensor) and self._is_anomalous(incoming):
            self._quarantine(incoming)
            released = self._release_quarantine(incoming.shape)
            processed_incoming = released if released is not None else torch.zeros_like(incoming)

        # Przepuszczenie przez rdzeń fizyczny
        out, thick, stiff, pos = self.core(
            processed_incoming, incoming_thickness, incoming_stiffness,
            time_delta=time_delta, other_pos=other_pos
        )

        # Dodatkowe filtrowanie przez wewnętrzną siatką (melioracja)
        # inner_lqg oczekuje: (batch, num_spikes//2, dim) - używamy mean by dopasować spike dim
        if out.shape[-1] == self.inner_lqg.dim:
            # Redukujemy spike dim z num_spikes → num_spikes//2
            half = out.shape[1] // 2
            out_half = out[:, :half, :]
            filtered, _ = self.inner_lqg(out_half)
            # Odtwarzamy pełną długość przez powtórzenie
            out = torch.cat([filtered, out[:, half:, :]], dim=1)

        return out, thick, stiff, pos

    def get_status(self) -> dict:
        return {
            "layer": self.layer_role.name,
            "mass": self.mass,
            "mesh_density": self.mesh_density,
            "quarantine_hits": self.quarantine_hits,
            "quarantine_buffer_size": len(self.quarantine_buffer),
            "released_hits": self.released_hits,
        }


# =============================================================================
# FUZYJNE SERCE — Rdzeń z Siatką Plazmową
# =============================================================================

class FusionHeart(nn.Module):
    """
    Centralny rdzeń fuzyjny Błyskawicy.

    Właściwości:
    - Masa = 12.0 → największy horyzont Schwarzschilda → maksymalna ochrona
    - Siatka plazmowa: sześciokierunkowy filtr (6 mini-LQG wokół serca)
    - Promieniowanie Hawkinga ZAWSZE aktywne
    - Brak bezpośredniego połączenia z zewnętrzem (tylko przez Warstwę 2)
    - Singularity Freeze: próg 100 (zahartowany na uderzenia)
    """

    PLASMA_GRID_SIZE = 6   # Liczba węzłów siatki plazmowej wokół serca

    def __init__(self, spikes: int = 128, dim: int = 64):
        super().__init__()
        self.dim = dim

        # Rdzeń fizyczny — Czarna Dziura z maksymalną masą
        self.core = QuantumGravityNode(
            num_spikes=spikes,
            dim=dim,
            base_freq=0.5,   # Wolna, głęboka oscylacja
            mass=12.0,
        )

        # Siatka plazmowa: 6 mini-węzłów LQG otaczających serce
        self.plasma_grid = nn.ModuleList([
            LQGSpinNetwork(num_spikes=spikes // 4, dim=dim, max_spin=24.0)
            for _ in range(self.PLASMA_GRID_SIZE)
        ])

        # Adapter wymiarów: Warstwa 2 (dim=32) → Serce (dim=64)
        self.input_adapter = nn.Linear(32, dim, bias=False)
        # Adapter wyjścia
        self.output_adapter = nn.Linear(dim, 32, bias=False)

        # Energia fuzji — skumulowana energia kognitywna
        self.register_buffer('fusion_energy', torch.zeros(1))

        print("[FusionHeart] *** Fuzyjne Serce aktywne. Masa=%.1f, "  # noqa: UP031
              "Siatka plazmowa: %d wezlow, dim=%d" % (self.core.mass, self.PLASMA_GRID_SIZE, dim))

    def _plasma_filter(self, signal: torch.Tensor) -> torch.Tensor:
        """
        Przepuszcza sygnał przez sześciokierunkową siatkę plazmową.
        Każdy węzeł LQG tłumi inne częstotliwości — efekt sumuje się.
        signal shape: (1, num_spikes, dim)
        """
        plasma_votes = []
        pg_spikes = self.core.num_spikes // 4  # 128//4 = 32

        for pg in self.plasma_grid:
            # Dopasuj spike dim przez average pooling: (1, 128, 64) → (1, 32, 64)
            if signal.shape[1] != pg_spikes:
                # Reshape + mean pooling
                factor = signal.shape[1] // pg_spikes
                sig_pooled = signal[:, :pg_spikes * factor, :].view(
                    signal.shape[0], pg_spikes, factor, signal.shape[-1]
                ).mean(dim=2)
            else:
                sig_pooled = signal

            if sig_pooled.shape[-1] == pg.dim:
                node_out, area = pg(sig_pooled)
                # Upsample z powrotem do oryginalnego spike dim
                if node_out.shape[1] != signal.shape[1]:
                    node_out = node_out.repeat_interleave(signal.shape[1] // node_out.shape[1], dim=1)
                plasma_votes.append(node_out)

        if plasma_votes:
            # Konsensualne głosowanie siatki plazmowej
            filtered = torch.stack(plasma_votes).mean(dim=0)
        else:
            filtered = signal

        return filtered

    def forward(self, signal_from_layer2: torch.Tensor,
                time_delta: float = 0.05) -> tuple[torch.Tensor, dict]:
        """
        Przyjmuje sygnał z Warstwy 2, przepuszcza przez plazmę, przetwarza w sercu.
        signal_from_layer2: shape (1, 32) — zagregowany wektor z NetworkLayer
        """
        # Adaptacja wymiarów (1, 32) → (1, 64)
        adapted_2d = self.input_adapter(signal_from_layer2)  # (1, 64)

        # Rozszerzenie do 3D: (1, num_spikes, 64) by QuantumGravityNode mógł przetworzyć
        num_spikes = self.core.num_spikes
        adapted = adapted_2d.unsqueeze(1).expand(-1, num_spikes, -1)  # (1, 128, 64)

        # Filtr plazmowy (siatka ochronna)
        plasma_filtered = self._plasma_filter(adapted)

        # Rdzeń fizyczny
        out, thick, stiff, pos = self.core(
            plasma_filtered, time_delta=time_delta
        )

        # Aktualizacja energii fuzji
        self.fusion_energy += out.abs().mean().detach() * 0.01

        # Wyjście przez adapter (64 → 32) do ewentualnego feedbacku
        output_32 = self.output_adapter(out.mean(dim=1))  # (1, 32)

        metrics = {
            "fusion_energy": self.fusion_energy.item(),
            "plasma_filtered_energy": plasma_filtered.abs().mean().item(),
            "heart_amplitude": out.abs().mean().item(),
        }

        return output_32, metrics



# =============================================================================
# MENEDŻER WARSTWY — Zarządzanie kulami jednej warstwy
# =============================================================================

class NetworkLayer(nn.Module):
    """
    Jedna warstwa w architekturze V5.
    Zarządza grupą kul z wewnętrznymi wektorami MOCNYMI (all-to-all).
    """

    def __init__(self, role: LayerRole):
        super().__init__()
        self.role = role
        cfg = LAYER_CONFIGS[role]

        masses = cfg["masses"]
        spikes = cfg["spikes"]
        dim    = cfg["dim"]

        # Kule warstwy
        self.balls = nn.ModuleList([
            MeliorationBall(
                num_spikes=spikes,
                dim=dim,
                base_freq=1.0 + i * 0.1,
                mass=m,
                anomaly_threshold=3.0 + role.value,  # Rośnie z głębokością
                layer_role=role,
            )
            for i, m in enumerate(masses)
        ])

        n = len(self.balls)
        # Wektory MOCNE: macierz połączeń all-to-all wewnątrz warstwy
        self.strong_vectors = nn.Parameter(torch.randn(n, n, dim) * 0.3)

        # Wektory CIENKIE: przepuszczanie do następnej warstwy (top-k)
        self.thin_vectors = nn.Parameter(torch.randn(n, dim) * 0.1)

        self.dim = dim
        self.num_balls = n

    def forward(self, external_input: list[torch.Tensor | None] | None = None,
                inter_layer_signal: torch.Tensor | None = None,
                time_delta: float = 0.05) -> tuple[torch.Tensor, list[dict]]:
        """
        Jeden krok przetwarzania warstwy.

        Args:
            external_input: Lista sygnałów wejściowych per kula (dla W0 z zewnątrz)
            inter_layer_signal: Zagregowany sygnał z poprzedniej warstwy
            time_delta: Delta czasu fizyki

        Returns:
            (zagregowany_sygnał_wyjściowy, statystyki_kul)
        """
        device = self.strong_vectors.device
        n = self.num_balls

        # Inicjalizacja emisji
        emissions = [
            torch.zeros(1, b.core.num_spikes, self.dim).to(device)
            for b in self.balls
        ]

        stats = []

        for i, ball in enumerate(self.balls):
            # Sygnał wejściowy: z zewnątrz (W0) lub z poprzedniej warstwy
            if external_input and i < len(external_input) and external_input[i] is not None:
                incoming = external_input[i]
            elif inter_layer_signal is not None:
                incoming = inter_layer_signal.unsqueeze(1).expand(-1, ball.core.num_spikes, -1)
            else:
                incoming = torch.zeros(1, ball.core.num_spikes, self.dim).to(device)

            # Wektory MOCNE: dodaj sygnały od wszystkich sióstr w warstwie
            for j in range(n):
                if i != j:
                    contrib = emissions[j].mean(dim=1) * self.strong_vectors[j, i]
                    incoming = incoming + contrib.unsqueeze(1)

            out, thick, stiff, pos = ball(
                incoming, time_delta=time_delta,
                other_pos=self.balls[j].position if n > 1 else None
            )
            emissions[i] = out
            stats.append(ball.get_status())

        # Agregacja wyjść do pojedynczego wektora (top-k routing)
        all_emissions = torch.stack([e.mean(dim=1) for e in emissions], dim=1)  # (1, n, dim)
        # Ważenie przez wektory CIENKIE
        weights = torch.softmax(self.thin_vectors.norm(dim=-1), dim=0)  # (n,)
        aggregated = (all_emissions * weights.view(1, -1, 1)).sum(dim=1)  # (1, dim)

        return aggregated, stats


# =============================================================================
# LAYERED FUSION NETWORK — Główna klasa V5
# =============================================================================

class LayeredFusionNetwork(nn.Module):
    """
    Błyskawica V5: Kwantowo-Fuzyjna Architektura Warstwowa.

    Topologia (11 kul + serce):
        [W0: 3 kule] → [W1: 4 kule] → [W2: 3 kule] → [❤️ Serce: 1]

    Zasady bezpieczeństwa:
        - Każda warstwa filtruje dane przed przepuszczeniem głębiej
        - Kule melioracyjne wychwytują anomalie do kwarantanny
        - Serce NIGDY nie widzi surowych danych zewnętrznych
        - DEFCON z IdentityGuard może zamrozić dowolną warstwę
    """

    def __init__(self):
        super().__init__()

        # Trzy warstwy filtrów
        self.layer_external    = NetworkLayer(LayerRole.EXTERNAL)
        self.layer_melio_1     = NetworkLayer(LayerRole.MELIORATION_I)
        self.layer_melio_2     = NetworkLayer(LayerRole.MELIORATION_II)

        # Adaptery wymiarów między warstwami (16→32, 32→32)
        self.adapter_w0_to_w1 = nn.Linear(16, 32, bias=False)
        self.adapter_w1_to_w2 = nn.Linear(32, 32, bias=False)

        # Fuzyjne serce
        self.heart = FusionHeart(spikes=128, dim=64)

        # Stan zamrożenia warstwy (DEFCON integration)
        self._frozen_layers = set()

        # Historia
        self.processing_log: list[dict] = []

        total_balls = (
            self.layer_external.num_balls +
            self.layer_melio_1.num_balls +
            self.layer_melio_2.num_balls + 1
        )
        print("\n" + "="*60)
        print("  [V5] Blyskawica V5 - Architektura Kwantowo-Fuzyjna")
        print("  Laczna liczba kul: %d (3+4+3+1)" % total_balls)  # noqa: UP031
        print("  Warstwy filtrow: 3 + Fuzyjne Serce")
        print("="*60 + "\n")

    def freeze_layer(self, role: LayerRole):
        """DEFCON: Zamroz warstwe (dane przez nia nie przejda)."""
        self._frozen_layers.add(role)
        print("[LayeredFusion] [FROZEN] Warstwa %s ZAMROZONA (DEFCON)" % role.name)  # noqa: UP031

    def unfreeze_layer(self, role: LayerRole):
        """Odblokuj warstwe po normalizacji sytuacji."""
        self._frozen_layers.discard(role)
        print("[LayeredFusion] [OK] Warstwa %s ODBLOKOWANA" % role.name)  # noqa: UP031

    def forward(self, external_stimuli: list[torch.Tensor | None] | None = None,
                time_steps: int = 4, time_delta: float = 0.05) -> dict:
        """
        Pełny cykl przetwarzania przez wszystkie warstwy.

        Args:
            external_stimuli: Dane ze świata zewnętrznego (BCI, sensory)
            time_steps: Liczba kroków symulacji fizyki
            time_delta: Delta czasu

        Returns:
            Słownik z metrykami wszystkich warstw + serca
        """
        history = {
            "layer_0_stats": [],
            "layer_1_stats": [],
            "layer_2_stats": [],
            "heart_metrics": [],
            "frozen_layers": list(self._frozen_layers),
        }

        sig_w0 = None
        sig_w1 = None
        sig_w2 = None

        for step in range(time_steps):  # noqa: B007

            # ─── WARSTWA 0: Interfejs zewnętrzny ───────────────────────
            if LayerRole.EXTERNAL not in self._frozen_layers:
                sig_w0, stats_w0 = self.layer_external(
                    external_input=external_stimuli,
                    inter_layer_signal=None,
                    time_delta=time_delta,
                )
                history["layer_0_stats"].append(stats_w0)
            else:
                sig_w0 = torch.zeros(1, 16)

            # Adaptacja wymiarów W0 → W1
            sig_w0_adapted = self.adapter_w0_to_w1(sig_w0)

            # ─── WARSTWA 1: Melioracja I ───────────────────────────────
            if LayerRole.MELIORATION_I not in self._frozen_layers:
                sig_w1, stats_w1 = self.layer_melio_1(
                    inter_layer_signal=sig_w0_adapted,
                    time_delta=time_delta,
                )
                history["layer_1_stats"].append(stats_w1)
            else:
                sig_w1 = torch.zeros(1, 32)

            # Adaptacja W1 → W2
            sig_w1_adapted = self.adapter_w1_to_w2(sig_w1)

            # ─── WARSTWA 2: Melioracja II ──────────────────────────────
            if LayerRole.MELIORATION_II not in self._frozen_layers:
                sig_w2, stats_w2 = self.layer_melio_2(
                    inter_layer_signal=sig_w1_adapted,
                    time_delta=time_delta,
                )
                history["layer_2_stats"].append(stats_w2)
            else:
                sig_w2 = torch.zeros(1, 32)

            # ─── SERCE: Fuzyjny rdzeń ──────────────────────────────────
            if LayerRole.FUSION_HEART not in self._frozen_layers and sig_w2 is not None:
                heart_out, heart_metrics = self.heart(sig_w2, time_delta=time_delta)
                history["heart_metrics"].append(heart_metrics)

        return history

    def get_system_status(self) -> str:
        """Zwraca czytelny raport stanu całej architektury V5."""
        total_quarantined = 0
        for layer in [self.layer_external, self.layer_melio_1, self.layer_melio_2]:
            for ball in layer.balls:
                total_quarantined += ball.quarantine_hits

        frozen = [r.name for r in self._frozen_layers]
        fusion_e = self.heart.fusion_energy.item()

        lines = [
            "=" * 52,
            "  [V5] BLYSKAWICA V5 - STATUS SYSTEMU",
            "-" * 52,
            "  Kule W0 (zewn.):    %d aktywne" % self.layer_external.num_balls,  # noqa: UP031
            "  Kule W1 (mel.I):    %d aktywne" % self.layer_melio_1.num_balls,  # noqa: UP031
            "  Kule W2 (mel.II):   %d aktywne" % self.layer_melio_2.num_balls,  # noqa: UP031
            "  [HEART] Serce fuzyjne:  Energia = %.4f" % fusion_e,  # noqa: UP031
            "  Kwarantanny lacznie: %d" % total_quarantined,  # noqa: UP031
            "  Zamrozone warstwy:  %s" % (str(frozen) if frozen else 'BRAK'),
            "=" * 52,
        ]
        return "\n".join(lines)


# =============================================================================
# TEST INTEGRACYJNY
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: Błyskawica V5 — Kwantowo-Fuzyjna Architektura")
    print("=" * 60)

    torch.manual_seed(42)
    net = LayeredFusionNetwork()

    # Scenariusz 1: Spokojny sygnał zewnętrzny
    print("\n[SCENARIUSZ 1: SPOKOJNY SYGNAŁ BCI]")
    stimuli = [torch.randn(1, 16) * 0.5] + [None, None]
    history = net(external_stimuli=stimuli, time_steps=3)
    if history["heart_metrics"]:
        hm = history["heart_metrics"][-1]
        print(f"  Energia Serca:       {hm['heart_amplitude']:.4f}")
        print(f"  Energia Fuzji:       {hm['fusion_energy']:.4f}")
        print(f"  Po Filtrze Plazmowym:{hm['plasma_filtered_energy']:.4f}")

    # Scenariusz 2: Atak (sygnał o ekstremalnej energii)
    print("\n[SCENARIUSZ 2: SYMULACJA ATAKU — ekstremalna energia]")
    attack = [torch.randn(1, 16) * 500.0] + [None, None]
    history2 = net(external_stimuli=attack, time_steps=3)

    # Sprawdź kwarantannę W0
    q_hits = sum(b.quarantine_hits for b in net.layer_external.balls)
    print(f"  Kwarantanna W0 wychwycono: {q_hits} paczek danych")

    if history2["heart_metrics"]:
        hm2 = history2["heart_metrics"][-1]
        print(f"  Energia Serca po ataku:  {hm2['heart_amplitude']:.6f} (powinno być małe!)")

    # Scenariusz 3: DEFCON — zamrożenie warstwy zewnętrznej
    print("\n[SCENARIUSZ 3: DEFCON — Zamrożenie Warstwy 0]")
    net.freeze_layer(LayerRole.EXTERNAL)
    history3 = net(external_stimuli=attack, time_steps=2)
    if history3["heart_metrics"]:
        hm3 = history3["heart_metrics"][-1]
        print(f"  Energia Serca (tarcza zamrożona): {hm3['heart_amplitude']:.6f}")
    net.unfreeze_layer(LayerRole.EXTERNAL)

    # Status końcowy
    print("\n" + net.get_system_status())
