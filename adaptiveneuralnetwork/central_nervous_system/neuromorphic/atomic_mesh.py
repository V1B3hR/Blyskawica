"""
Błyskawica V5 — Faza 1: TransitNode + GrapheneMesh
===================================================
Siatka węzłów przelotowych w topologii grafenowej.

Węzły:
  - TransitNode:      routing z priorytetem (fast/normal/quarantine)
  - GrapheneMesh:     hexagonalna siatka węzłów między warstwami kul
  - RecyclerBall:     kula utylizacyjna dla anomalii
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, List, Dict, Tuple
from enum import IntEnum
from dataclasses import dataclass, field


# =============================================================================
# PRIORYTET PAKIETU
# =============================================================================

class DataPriority(IntEnum):
    CRITICAL   = 0   # Najszybsza sciezka, omija kolejke
    HIGH       = 1   # Fast-path
    NORMAL     = 2   # Standardowa siatka
    LOW        = 3   # Wolna sciezka, nie blokuje
    QUARANTINE = 4   # Skieruj do kuli utylizacyjnej


# =============================================================================
# TRANSIT NODE — Wegzel przelotowy
# =============================================================================

class TransitNode(nn.Module):
    """
    Wegzel przelotowy w siatce grafenowej.

    Odpowiedzialnosci:
    - Ocena priorytetu przychodzacego sygnalu
    - Wybor sciezki routingu (fast / normal / quarantine)
    - Przekazanie danych do sasiadow (max 3 w topologii grafenu)
    """

    MAX_NEIGHBORS = 3   # Grafen: kazdy wezzel ma max 3 sasiadow

    def __init__(self, dim: int, anomaly_threshold: float = 4.0,
                 node_id: int = 0):
        super().__init__()
        self.dim = dim
        self.node_id = node_id
        self.anomaly_threshold = anomaly_threshold

        # Scorer priorytetu (mala siec liniowa)
        self.priority_scorer = nn.Sequential(
            nn.Linear(dim, dim // 2, bias=False),
            nn.Tanh(),
            nn.Linear(dim // 2, 1, bias=False),
        )

        # Bramka routingu: [fast_weight, normal_weight, quarantine_weight]
        self.route_gate = nn.Linear(dim, 3, bias=False)

        # Bufor przepustowosci
        self.register_buffer('throughput', torch.zeros(1))
        self.register_buffer('quarantine_count', torch.zeros(1))

        # Statystyki
        self.routed_fast = 0
        self.routed_normal = 0
        self.routed_quarantine = 0

    def assess_priority(self, signal: torch.Tensor) -> DataPriority:
        """Ocenia priorytet sygnalu na podstawie jego energii i struktury."""
        energy = signal.abs().mean().item()

        if energy > self.anomaly_threshold * 10:
            return DataPriority.QUARANTINE
        elif energy > self.anomaly_threshold * 3:
            return DataPriority.CRITICAL
        elif energy > self.anomaly_threshold:
            return DataPriority.HIGH
        elif energy < 0.01:
            return DataPriority.LOW
        return DataPriority.NORMAL

    def forward(self, signal: torch.Tensor) -> Tuple[torch.Tensor, DataPriority, torch.Tensor]:
        """
        Przetwarza sygnal i zwraca:
        - przefiltrowany sygnal
        - priorytet
        - wagi routingu do sasiadow (3 wartosci)
        """
        # Upewnij sie ze sygnal jest 2D: (batch, dim)
        if signal.dim() == 3:
            sig_flat = signal.mean(dim=1)   # (batch, dim)
        else:
            sig_flat = signal

        # Pad lub przytnij do dim
        if sig_flat.shape[-1] != self.dim:
            sig_flat = F.adaptive_avg_pool1d(
                sig_flat.unsqueeze(1), self.dim
            ).squeeze(1)

        priority = self.assess_priority(sig_flat)

        # Wagi routingu do sasiadow
        route_weights = torch.softmax(self.route_gate(sig_flat), dim=-1)  # (batch, 3)

        # Filtrowanie sygnalu w zaleznosci od priorytetu
        if priority == DataPriority.QUARANTINE:
            filtered = sig_flat * 0.0   # Blokuj
            self.routed_quarantine += 1
            self.quarantine_count += 1
        elif priority in (DataPriority.CRITICAL, DataPriority.HIGH):
            filtered = sig_flat         # Przepusc pelny
            self.routed_fast += 1
        else:
            # Normalne/niskie: lekkie stlumienie
            filtered = sig_flat * (0.7 + 0.3 * route_weights[:, 1:2])
            self.routed_normal += 1

        self.throughput += filtered.abs().mean().detach()
        return filtered, priority, route_weights

    def get_stats(self) -> Dict:
        return {
            "node_id": self.node_id,
            "routed_fast": self.routed_fast,
            "routed_normal": self.routed_normal,
            "routed_quarantine": self.routed_quarantine,
            "throughput": self.throughput.item(),
        }


# =============================================================================
# GRAPHENE MESH — Heksagonalna siatka wezlow
# =============================================================================

class GrapheneMesh(nn.Module):
    """
    Siatka wezlow przelotowych w topologii grafenowej.

    W grafenie kazdy atom ma 3 sasiadow tworzac hexagonalna siec.
    Implementujemy uproszczona wersje: wezly w siatce rows x cols,
    gdzie kazdy ma max 3 polaczenia (jak w grafenie).

    Funkcje:
    - Routing priorytetowy (fast path dla CRITICAL/HIGH)
    - Routing normalny (przez siatke, nie blokuje fast path)
    - Przekierowanie QUARANTINE do RecyclerBall
    - Agregacja wyjsc do kuli docelowej
    """

    def __init__(self, num_nodes: int, dim: int,
                 anomaly_threshold: float = 4.0):
        super().__init__()
        self.num_nodes = num_nodes
        self.dim = dim

        # Wezly siatki
        self.nodes = nn.ModuleList([
            TransitNode(dim=dim, anomaly_threshold=anomaly_threshold,
                        node_id=i)
            for i in range(num_nodes)
        ])

        # Macierz sasiedztwa (hexagonalna, rzadka)
        adj = self._build_hexagonal_adjacency(num_nodes)
        self.register_buffer('adjacency', adj)

        # Fast-path: polaczenie bezposrednie dla CRITICAL
        self.fast_path = nn.Linear(dim, dim, bias=False)

        # Agregator wyjsc wezlow → sygnał do kuli docelowej
        self.aggregator = nn.Linear(dim, dim, bias=False)

        # Bufor anomalii (do RecyclerBall)
        self.anomaly_buffer: List[torch.Tensor] = []
        self.max_anomaly_buffer = 16

    def _build_hexagonal_adjacency(self, n: int) -> torch.Tensor:
        """
        Buduje rzadka macierz sasiedztwa inspirowana grafenem.
        Kazdy wezzel ma max 3 sasiadow.
        """
        adj = torch.zeros(n, n)
        for i in range(n):
            # Sasiedzi: i-1, i+1, i+cols (heksagonalna aproksymacja)
            cols = max(3, int(math.sqrt(n)))
            neighbors = []
            if i > 0:
                neighbors.append(i - 1)
            if i < n - 1:
                neighbors.append(i + 1)
            jump = i + cols
            if jump < n:
                neighbors.append(jump)
            # Max 3 sasiadow (grafen)
            for nb in neighbors[:3]:
                adj[i, nb] = 1.0
                adj[nb, i] = 1.0
        return adj

    def forward(self, signal: torch.Tensor) -> Tuple[torch.Tensor, Dict]:
        """
        Przepuszcza sygnal przez siatke grafenowa.

        Args:
            signal: (batch, dim) lub (batch, spikes, dim)

        Returns:
            (output, routing_stats)
        """
        # Normalizacja do 2D
        if signal.dim() == 3:
            sig = signal.mean(dim=1)   # (batch, dim)
        else:
            sig = signal

        if sig.shape[-1] != self.dim:
            sig = F.adaptive_avg_pool1d(
                sig.unsqueeze(1), self.dim
            ).squeeze(1)

        fast_outputs = []
        normal_outputs = []
        priorities = []

        # Kazdy wezzel przetwarza sygnal
        for node in self.nodes:
            filtered, priority, route_w = node(sig)
            priorities.append(priority)

            if priority in (DataPriority.CRITICAL, DataPriority.HIGH):
                fast_outputs.append(filtered)
            elif priority == DataPriority.QUARANTINE:
                # Bufor anomalii
                if len(self.anomaly_buffer) < self.max_anomaly_buffer:
                    self.anomaly_buffer.append(filtered.detach().clone())
            else:
                normal_outputs.append(filtered)

        # Agregacja: fast path priorytetowy
        if fast_outputs:
            fast_agg = torch.stack(fast_outputs).mean(dim=0)
            fast_out = self.fast_path(fast_agg)
        else:
            fast_out = torch.zeros_like(sig)

        # Normal path (srednia wezlow normalnych)
        if normal_outputs:
            normal_agg = torch.stack(normal_outputs).mean(dim=0)
        else:
            normal_agg = torch.zeros_like(sig)

        # Polaczenie: fast ma wiekszy wplyw
        combined = fast_out * 0.7 + normal_agg * 0.3
        output = self.aggregator(combined)

        stats = {
            "fast_count": len(fast_outputs),
            "normal_count": len(normal_outputs),
            "quarantine_count": sum(1 for p in priorities
                                    if p == DataPriority.QUARANTINE),
            "anomaly_buffer_size": len(self.anomaly_buffer),
        }

        return output, stats

    def flush_anomalies(self) -> Optional[torch.Tensor]:
        """Zwraca zebrane anomalie do RecyclerBall i czysci bufor."""
        if not self.anomaly_buffer:
            return None
        result = torch.stack(self.anomaly_buffer).mean(dim=0)
        self.anomaly_buffer.clear()
        return result


# =============================================================================
# RECYCLER BALL — Kula utylizacyjna
# =============================================================================

class RecyclerBall(nn.Module):
    """
    Kula utylizacyjna — przyjmuje anomalie z siatek,
    izoluje je, i produkuje bezpieczny sygnal diagnostyczny.

    Nie przekazuje danych dalej do jadura — tylko analizuje i niszczy.
    """

    def __init__(self, dim: int, capacity: int = 64):
        super().__init__()
        self.dim = dim
        self.capacity = capacity

        # Izolator anomalii
        self.isolator = nn.Sequential(
            nn.Linear(dim, dim, bias=False),
            nn.Sigmoid(),           # Normalizacja do [0,1]
        )

        # Kolekcja anomalii
        self.anomaly_log: List[Dict] = []
        self.total_recycled = 0

    def forward(self, anomaly_signal: torch.Tensor) -> Dict:
        """
        Przyjmuje anomalie, izoluje, loguje.
        Zwraca raport diagnostyczny (NIE sygnal do sieci).
        """
        if anomaly_signal.dim() == 3:
            sig = anomaly_signal.mean(dim=1)
        else:
            sig = anomaly_signal

        if sig.shape[-1] != self.dim:
            sig = F.adaptive_avg_pool1d(
                sig.unsqueeze(1), self.dim
            ).squeeze(1)

        isolated = self.isolator(sig)
        energy = sig.abs().mean().item()
        severity = min(1.0, energy / 100.0)

        report = {
            "energy": energy,
            "severity": severity,
            "isolated_norm": isolated.norm().item(),
            "action": "RECYCLED" if severity < 0.8 else "DESTROYED",
        }

        if len(self.anomaly_log) < self.capacity:
            self.anomaly_log.append(report)

        self.total_recycled += 1
        return report

    def get_summary(self) -> Dict:
        if not self.anomaly_log:
            return {"total_recycled": 0, "avg_severity": 0.0}
        avg_sev = sum(r["severity"] for r in self.anomaly_log) / len(self.anomaly_log)
        return {
            "total_recycled": self.total_recycled,
            "avg_severity": avg_sev,
            "log_size": len(self.anomaly_log),
        }


# =============================================================================
# NEURAL ATOM — Pelny atom (siatki + kule + serce)
# =============================================================================

class NeuralAtom(nn.Module):
    """
    Kompletna jednostka atomowa: siatki grafenowe + warstwy kul + serce.

    Integruje GrapheneMesh z LayeredFusionNetwork z V5.
    Kazda przestrzen miedzy warstwami ma wlasna siatke wezlow.
    """

    def __init__(self, atom_config: Dict):
        super().__init__()
        self.atom_id = atom_config.get("atom_id", "atom_0")
        self.dim = atom_config.get("dim", 16)

        # Import warstw z V5
        from adaptiveneuralnetwork.central_nervous_system.neuromorphic.layered_fusion_network import (
            LayeredFusionNetwork
        )

        # Fuzyjne jadro (serce + warstwy kul)
        self.fusion = LayeredFusionNetwork()

        # Siatki grafenowe miedzy warstwami
        mesh_nodes = atom_config.get("mesh_nodes", 6)
        anomaly_thr = atom_config.get("anomaly_threshold", 4.0)

        self.mesh_in   = GrapheneMesh(mesh_nodes, dim=16,
                                      anomaly_threshold=anomaly_thr)        # Wejscie
        self.mesh_w0w1 = GrapheneMesh(mesh_nodes, dim=32,
                                      anomaly_threshold=anomaly_thr * 1.5)  # W0→W1
        self.mesh_w1w2 = GrapheneMesh(mesh_nodes, dim=32,
                                      anomaly_threshold=anomaly_thr * 2.0)  # W1→Serce

        # Kula utylizacyjna
        self.recycler = RecyclerBall(dim=32)

    def forward(self, external_signal: Optional[torch.Tensor] = None,
                time_steps: int = 3) -> Dict:
        """Pelny przebieg przez atom."""
        stats = {"atom_id": self.atom_id, "mesh_stats": []}

        # 1. Siatka wejsciowa
        if external_signal is not None:
            sig_in, ms0 = self.mesh_in(external_signal)
            stats["mesh_stats"].append({"mesh": "input", **ms0})

            # Utylizacja anomalii z siatki wejsciowej
            anomalies = self.mesh_in.flush_anomalies()
            if anomalies is not None:
                report = self.recycler(anomalies)
                stats["recycler"] = report

            stimuli = [sig_in, None, None]
        else:
            stimuli = None

        # 2. Fuzyjne jadro (V5 LayeredFusionNetwork)
        history = self.fusion(
            external_stimuli=stimuli,
            time_steps=time_steps,
        )
        stats["heart_metrics"] = history.get("heart_metrics", [])

        # 3. Anomalie z siatek miedzy warstwami (przekaz do recyclera)
        for mesh, name in [(self.mesh_w0w1, "w0w1"), (self.mesh_w1w2, "w1w2")]:
            a = mesh.flush_anomalies()
            if a is not None:
                self.recycler(a)

        stats["recycler_summary"] = self.recycler.get_summary()
        return stats


# =============================================================================
# TEST INTEGRACYJNY
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TEST: TransitNode + GrapheneMesh + RecyclerBall + NeuralAtom")
    print("=" * 60)

    torch.manual_seed(42)

    # --- Test 1: Pojedynczy TransitNode ---
    print("\n[1] TransitNode — routing priorytetu")
    node = TransitNode(dim=16, anomaly_threshold=4.0, node_id=0)
    for label, energy in [("Normalny", 1.0), ("High", 15.0), ("Atak", 500.0)]:
        sig = torch.randn(1, 16) * energy
        out, priority, route_w = node(sig)
        print("  %-10s energia=%-8.1f priorytet=%-12s route=%s" % (
            label, energy, priority.name, route_w.detach().numpy().round(2)
        ))

    # --- Test 2: GrapheneMesh ---
    print("\n[2] GrapheneMesh (6 wezlow) — siatka grafenowa")
    mesh = GrapheneMesh(num_nodes=6, dim=16, anomaly_threshold=4.0)
    sig_normal = torch.randn(1, 16) * 1.0
    sig_attack = torch.randn(1, 16) * 500.0
    out_n, stats_n = mesh(sig_normal)
    out_a, stats_a = mesh(sig_attack)
    print("  Normalny: fast=%d, normal=%d, quarantine=%d" % (
        stats_n["fast_count"], stats_n["normal_count"], stats_n["quarantine_count"]))
    print("  Atak:     fast=%d, normal=%d, quarantine=%d, anomaly_buf=%d" % (
        stats_a["fast_count"], stats_a["normal_count"],
        stats_a["quarantine_count"], stats_a["anomaly_buffer_size"]))

    # --- Test 3: RecyclerBall ---
    print("\n[3] RecyclerBall — utylizacja anomalii")
    recycler = RecyclerBall(dim=16)
    anomaly = torch.randn(1, 16) * 200.0
    report = recycler(anomaly)
    print("  Energia: %.1f | Severity: %.3f | Akcja: %s" % (
        report["energy"], report["severity"], report["action"]))
    print("  Summary:", recycler.get_summary())

    # --- Test 4: Pelny NeuralAtom ---
    print("\n[4] NeuralAtom — pelny cykl atomowy")
    import sys, types

    # Patch dla brakujacych modulow ekosystemu
    for mod in ['adaptiveneuralnetwork', 'adaptiveneuralnetwork.core',
                'adaptiveneuralnetwork.central_nervous_system.neuromorphic',
                'adaptiveneuralnetwork.core.ecosystem']:
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)

    eco = sys.modules['adaptiveneuralnetwork.core.ecosystem']

    class FakeMicrobiome:
        anxiety = 0.0
        health_score = 100.0

    class FakeRCD:
        def monitor(self, intent, fn, *a, **kw):
            return fn(*a, **kw)

    eco.MicrobiomeSystemState = FakeMicrobiome
    eco.CognitiveRCD = FakeRCD

    # Patch layered_fusion_network
    import importlib.util, os
    base = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        'adaptiveneuralnetwork.central_nervous_system.neuromorphic.layered_fusion_network',
        os.path.join(base, 'layered_fusion_network.py')
    )
    lfn = importlib.util.module_from_spec(spec)
    sys.modules['adaptiveneuralnetwork.central_nervous_system.neuromorphic.layered_fusion_network'] = lfn
    spec.loader.exec_module(lfn)

    config = {"atom_id": "alpha_01", "dim": 16, "mesh_nodes": 6,
              "anomaly_threshold": 3.0}
    atom = NeuralAtom(config)

    # Spokojny sygnal
    sig = torch.randn(1, 16) * 0.8
    result = atom(external_signal=sig, time_steps=2)
    print("  Atom: %s" % result["atom_id"])
    print("  Recycler:", result["recycler_summary"])
    if result["heart_metrics"]:
        hm = result["heart_metrics"][-1]
        print("  Serce energia: %.4f" % hm["heart_amplitude"])
        print("  Fuzja:         %.4f" % hm["fusion_energy"])
