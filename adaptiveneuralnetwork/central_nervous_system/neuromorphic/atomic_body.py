"""
Błyskawica V5 — Faza 2: AtomFactory + AtomicBody
=================================================
Fabryka atomów różnych rozmiarów i ciało złożone
z wielu atomów działających równolegle.

Hierarchia:
    AtomFactory  → tworzy NeuralAtom wg konfiguracji
    AtomicBody   → orkiestruje N atomów równolegle,
                   agreguje wyniki, monitoruje zdrowie
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.neuromorphic.atomic_mesh import (
    GrapheneMesh,
    NeuralAtom,
    RecyclerBall,
)
from adaptiveneuralnetwork.central_nervous_system.neuromorphic.dark_matter_core import (
    DarkMatterCore,
)
from adaptiveneuralnetwork.core.memory.memory_vault import MemoryVault

# =============================================================================
# KONFIGURACJE ATOMÓW
# =============================================================================

class AtomSize(Enum):
    NANO   = "nano"    # 5 kul, 1 warstwa  — ~8 KB
    SMALL  = "small"   # 10 kul, 2 warstwy — ~80 KB
    MEDIUM = "medium"  # 20 kul, 3 warstwy — ~320 KB
    LARGE  = "large"   # 30 kul, 3 warstwy — ~480 KB


ATOM_PRESETS = {
    AtomSize.NANO: {
        "mesh_nodes": 3,
        "anomaly_threshold": 3.0,
        "dim": 16,
        "time_steps": 2,
    },
    AtomSize.SMALL: {
        "mesh_nodes": 6,
        "anomaly_threshold": 4.0,
        "dim": 16,
        "time_steps": 3,
    },
    AtomSize.MEDIUM: {
        "mesh_nodes": 9,
        "anomaly_threshold": 5.0,
        "dim": 16,
        "time_steps": 3,
    },
    AtomSize.LARGE: {
        "mesh_nodes": 12,
        "anomaly_threshold": 6.0,
        "dim": 16,
        "time_steps": 4,
    },
}


# =============================================================================
# ATOM FACTORY
# =============================================================================

class AtomFactory:
    """
    Fabryka atomów - tworzy NeuralAtom wg rozmiaru i specjalizacji.

    Każdy atom może być wyspecjalizowany:
    - 'general'   : ogólne przetwarzanie
    - 'sensor'    : dane sensoryczne/BCI (niska anomaly_threshold)
    - 'memory'    : długoterminowe wzorce (więcej węzłów)
    - 'guardian'  : bezpieczeństwo (wysoka anomaly_threshold, więcej siatek)
    - 'recycler'  : dedykowany do utylizacji śmieci z innych atomów
    """

    @staticmethod
    def create(size: AtomSize = AtomSize.SMALL,
               specialization: str = "general",
               atom_id: str = "atom") -> NeuralAtom:
        """Tworzy atom z zadaną konfiguracją."""
        cfg = dict(ATOM_PRESETS[size])  # kopia
        cfg["atom_id"] = atom_id

        # Modyfikacje wg specjalizacji
        if specialization == "sensor":
            cfg["anomaly_threshold"] = cfg["anomaly_threshold"] * 0.5
            cfg["mesh_nodes"] = max(3, cfg["mesh_nodes"] - 2)
        elif specialization == "memory":
            cfg["mesh_nodes"] = cfg["mesh_nodes"] + 4
            cfg["time_steps"] = cfg.get("time_steps", 3) + 1
        elif specialization == "guardian":
            cfg["anomaly_threshold"] = cfg["anomaly_threshold"] * 2.0
            cfg["mesh_nodes"] = cfg["mesh_nodes"] + 6
        elif specialization == "recycler":
            cfg["anomaly_threshold"] = cfg["anomaly_threshold"] * 0.3

        return NeuralAtom(cfg)

    @staticmethod
    def create_body_blueprint(num_atoms: int,
                              size: AtomSize = AtomSize.SMALL,
                              guardian_ratio: float = 0.1,
                              sensor_ratio: float = 0.2) -> list[dict]:
        """
        Tworzy plan ciała: listę konfiguracji atomów.
        Automatycznie przydziela specjalizacje.
        """
        blueprint = []
        n_guardians = max(1, int(num_atoms * guardian_ratio))
        n_sensors   = max(1, int(num_atoms * sensor_ratio))
        n_general   = num_atoms - n_guardians - n_sensors

        for i in range(n_guardians):
            blueprint.append({
                "size": size, "specialization": "guardian",
                "atom_id": "guardian_%02d" % i  # noqa: UP031
            })
        for i in range(n_sensors):
            blueprint.append({
                "size": size, "specialization": "sensor",
                "atom_id": "sensor_%02d" % i  # noqa: UP031
            })
        for i in range(n_general):
            blueprint.append({
                "size": size, "specialization": "general",
                "atom_id": "general_%02d" % i  # noqa: UP031
            })

        return blueprint


# =============================================================================
# HEALTH MONITOR — Monitor zdrowia ciała
# =============================================================================

class HealthMonitor:
    """
    Monitoruje "zdrowie" każdego atomu.
    Atom jest uznany za chory jeśli:
    - zbyt wiele anomalii (quarantine_rate > threshold)
    - brak aktywności (zero energia serca przez N cykli)
    - timeout (latency > 65ms)
    """

    def __init__(self, quarantine_rate_limit: float = 0.8,
                 max_silence_cycles: int = 5,
                 latency_limit_ms: float = 65.0):
        self.quarantine_rate_limit = quarantine_rate_limit
        self.max_silence_cycles = max_silence_cycles
        self.latency_limit_ms = latency_limit_ms

        self.atom_health: dict[str, dict] = {}

    def update(self, atom_id: str, result: dict, latency_ms: float):
        if atom_id not in self.atom_health:
            self.atom_health[atom_id] = {
                "status": "HEALTHY",
                "silence_cycles": 0,
                "total_cycles": 0,
                "latency_violations": 0,
                "avg_latency": 0.0,
            }

        h = self.atom_health[atom_id]
        h["total_cycles"] += 1
        h["avg_latency"] = (h["avg_latency"] * 0.9 + latency_ms * 0.1)

        # Sprawdź energię serca
        hm = result.get("heart_metrics", [])
        heart_energy = hm[-1]["heart_amplitude"] if hm else 0.0

        if heart_energy < 0.001:
            h["silence_cycles"] += 1
        else:
            h["silence_cycles"] = 0

        # Sprawdź latency
        if latency_ms > self.latency_limit_ms:
            h["latency_violations"] += 1

        # Ocena statusu
        recycler = result.get("recycler_summary", {})
        recycled = recycler.get("total_recycled", 0)
        total = h["total_cycles"]
        quarantine_rate = recycled / max(1, total)

        if h["silence_cycles"] >= self.max_silence_cycles:
            h["status"] = "DEAD"
        elif quarantine_rate > self.quarantine_rate_limit:
            h["status"] = "SICK"
        elif latency_ms > self.latency_limit_ms:
            h["status"] = "SLOW"
        else:
            h["status"] = "HEALTHY"

    def get_sick_atoms(self) -> list[str]:
        return [aid for aid, h in self.atom_health.items()
                if h["status"] in ("SICK", "DEAD")]

    def get_summary(self) -> dict:
        total = len(self.atom_health)
        if total == 0:
            return {"total": 0, "healthy": 0, "sick": 0, "dead": 0}
        healthy = sum(1 for h in self.atom_health.values()
                      if h["status"] == "HEALTHY")
        sick    = sum(1 for h in self.atom_health.values()
                      if h["status"] == "SICK")
        dead    = sum(1 for h in self.atom_health.values()
                      if h["status"] == "DEAD")
        slow    = sum(1 for h in self.atom_health.values()
                      if h["status"] == "SLOW")
        avg_lat = sum(h["avg_latency"]
                      for h in self.atom_health.values()) / total
        return {
            "total": total, "healthy": healthy,
            "sick": sick, "dead": dead, "slow": slow,
            "avg_latency_ms": round(avg_lat, 2),
        }


# =============================================================================
# ATOMIC BODY — Ciało złożone z atomów
# =============================================================================

class AtomicBody(nn.Module):
    """
    Ciało złożone z wielu atomów działających równolegle.

    Architektura:
    - N atomów różnych specjalizacji (guardian, sensor, general)
    - Każdy atom otrzymuje ten sam sygnał wejściowy (broadcast)
    - Agregacja wyników: ważone sumowanie wg specjalizacji
    - HealthMonitor: wykrywa chore/martwe atomy i je izoluje
    - GlobalRecycler: zbiera śmieci od wszystkich atomów
    - BroadcastMesh: globalna siatka grafenowa przed wejściem do atomów

    Gwarancja latency: < 65ms dla ≤ 200 atomów (CPU)
    """

    def __init__(self, atom_configs: list[dict] | None = None,
                 default_size: AtomSize = AtomSize.SMALL,
                 num_atoms: int = 5):
        super().__init__()

        # Zbuduj atomy wg blueprintu lub domyślnie
        if atom_configs is None:
            atom_configs = AtomFactory.create_body_blueprint(
                num_atoms=num_atoms,
                size=default_size,
            )

        self.atoms = nn.ModuleDict({
            cfg["atom_id"]: AtomFactory.create(
                size=cfg.get("size", default_size),
                specialization=cfg.get("specialization", "general"),
                atom_id=cfg["atom_id"],
            )
            for cfg in atom_configs
        })

        self.atom_ids = list(self.atoms.keys())
        self.atom_specs = {cfg["atom_id"]: cfg.get("specialization", "general")
                          for cfg in atom_configs}

        # Pula watkow dla rownoleglego przetwarzania
        max_workers = min(8, len(self.atoms))
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # Globalny recycler na śmieci z całego ciała
        self.global_recycler = RecyclerBall(dim=16, capacity=256)

        # Globalna siatka broadcast (wejście → wszystkie atomy)
        self.broadcast_mesh = GrapheneMesh(
            num_nodes=max(6, len(self.atoms) // 2),
            dim=16,
            anomaly_threshold=3.0,
        )

        # Agregator wyjść (prosty weighted sum)
        self.output_aggregator = nn.Linear(16, 16, bias=False)

        # Monitor zdrowia
        self.health_monitor = HealthMonitor()

        # Phase 3 & 4: Dark Matter & Neurochemistry
        self.dark_matter = DarkMatterCore()

        try:
            from adaptiveneuralnetwork.central_nervous_system.neuromorphic.neurochemical_bridge import (
                NeurochemicalBridge,
            )
            self.bridge = NeurochemicalBridge(self, self.dark_matter)
        except ImportError:
            self.bridge = None
            print("[AtomicBody] WARNING: NeurochemicalBridge not found.")

        # Izolowane (chore) atomy — nie otrzymują danych
        self._isolated: set = set()

        # Statystyki globalne
        self.total_cycles = 0
        self.total_latency_ms = 0.0

        # Memory Vault i Auto-Hooks (Phase 3.5/5)
        self.memory_vault = MemoryVault()

        # Dynamiczna prędkość myśli (Dopamina/Adrenalina)
        self.dynamic_time_steps = 3

        n = len(self.atoms)
        print("\n" + "=" * 58)
        print("  [BODY] AtomicBody zainicjalizowane")
        print("  Atomow:    %d" % n)  # noqa: UP031
        specs = {}
        for cfg in atom_configs:
            s = cfg.get("specialization", "general")
            specs[s] = specs.get(s, 0) + 1
        for k, v in specs.items():
            print("  %-12s %d" % (k + ":", v))  # noqa: UP031
        print("=" * 58 + "\n")

    def isolate_atom(self, atom_id: str, reason: str = "health_critical"):
        """Izoluje chory atom — nie będzie przetwarzać danych i przenosi do cmentarza."""
        self._isolated.add(atom_id)
        print("[AtomicBody] IZOLACJA atomu: %s" % atom_id)  # noqa: UP031

        # Auto-hook: archiwizacja atomu na cmentarzu
        if hasattr(self, 'memory_vault'):
            metrics = self.health_monitor.atom_health.get(atom_id, {})
            spec = self.atom_specs.get(atom_id, "general")
            self.memory_vault.on_atom_isolated(
                atom_id=atom_id,
                specialization=spec,
                reason=reason,
                final_metrics=metrics,
                system_state={"active_atoms": len(self.atoms) - len(self._isolated)}
            )

    def restore_atom(self, atom_id: str):
        """Przywraca atom do działania."""
        self._isolated.discard(atom_id)
        print("[AtomicBody] PRZYWROCONO atom: %s" % atom_id)  # noqa: UP031

    def forward(self, external_signal: torch.Tensor | None = None,
                time_steps: int | None = None) -> dict:
        """
        Jeden cykl przetwarzania całego ciała.

        1. Broadcast sygnału przez globalną siatkę
        2. Równoległe przetwarzanie w każdym atomie
        3. Agregacja wyników
        4. Aktualizacja HealthMonitor
        5. Auto-izolacja chorych atomów
        """
        # Użyj dynamicznych kroków jeśli nie podano jawnie
        if time_steps is None:
            time_steps = self.dynamic_time_steps
        t_start = time.perf_counter()
        self.total_cycles += 1

        body_results = {}
        heart_energies = []

        # 1. Broadcast przez globalną siatkę
        if external_signal is not None:
            broadcast_sig, b_stats = self.broadcast_mesh(external_signal)
            # Anomalie z broadcast → global recycler
            anomalies = self.broadcast_mesh.flush_anomalies()
            if anomalies is not None:
                self.global_recycler(anomalies)
        else:
            broadcast_sig = None

        # 2. Atomy przetworzone rownolegle
        def run_atom(atom_id_atom):
            atom_id, atom = atom_id_atom
            if atom_id in self._isolated:
                return atom_id, {"status": "ISOLATED"}, 0.0
            t_atom = time.perf_counter()
            result = atom(external_signal=broadcast_sig, time_steps=time_steps)
            latency_ms = (time.perf_counter() - t_atom) * 1000
            return atom_id, result, latency_ms

        futures = [
            self._executor.submit(run_atom, (aid, atom))
            for aid, atom in list(self.atoms.items())
        ]

        for future in as_completed(futures):
            atom_id, result, latency_ms = future.result()
            body_results[atom_id] = result
            if atom_id not in self._isolated:
                self.health_monitor.update(atom_id, result, latency_ms)
                hm = result.get("heart_metrics", [])
                if hm:
                    heart_energies.append(hm[-1]["heart_amplitude"])

        # 3. Auto-izolacja chorych atomów
        sick = self.health_monitor.get_sick_atoms()
        for atom_id in sick:
            if atom_id not in self._isolated:
                self.isolate_atom(atom_id)

        # 4. Metryki całego ciała
        total_ms = (time.perf_counter() - t_start) * 1000
        self.total_latency_ms += total_ms

        health_summary = self.health_monitor.get_summary()
        recycler_summary = self.global_recycler.get_summary()

        # 5. KROK CIEMNEJ MATERII (Phase 3)
        dm_result = self.dark_matter.step(body_results, self.atom_specs)

        # 6. Auto-hook: Zapisz pozytywne wspomnienie (jeśli wysoka spójność)
        if hasattr(self, 'memory_vault') and dm_result["self_coherence"] >= 0.85:
            # Ograniczamy spam — np. zapis tylko jeśli to skok spójności, albo rzadko
            # on_high_coherence w MemoryVault ma próg, więc po prostu wywołujemy
            self.memory_vault.on_high_coherence(
                coherence=dm_result["self_coherence"],
                context=f"Cykl {self.total_cycles}, Aktywne atomy: {len(self.atoms) - len(self._isolated)}"
            )

        return {
            "cycle": self.total_cycles,
            "latency_ms": round(total_ms, 2),
            "avg_heart_energy": (sum(heart_energies) / len(heart_energies)
                                 if heart_energies else 0.0),
            "active_atoms": len(self.atoms) - len(self._isolated),
            "isolated_atoms": len(self._isolated),
            "health": health_summary,
            "global_recycler": recycler_summary,
            "dark_matter": dm_result,
        }

    def sync_microbiome(self, microbiome_state):
        """Phase 4: Synchronizacja z ekosystemem (Anxiety -> Gravity)."""
        if self.bridge:
            self.bridge.sync(microbiome_state)

    def get_status(self) -> str:
        h = self.health_monitor.get_summary()
        avg_lat = (self.total_latency_ms / max(1, self.total_cycles))
        lines = [
            "=" * 56,
            "  [BODY] ATOMIC BODY STATUS",
            "-" * 56,
            "  Atomow lacznie:  %d" % len(self.atoms),  # noqa: UP031
            "  Aktywnych:       %d" % (len(self.atoms) - len(self._isolated)),  # noqa: UP031
            "  Izolowanych:     %d" % len(self._isolated),  # noqa: UP031
            "  Zdrowych:        %d" % h.get("healthy", 0),  # noqa: UP031
            "  Chorych:         %d" % h.get("sick", 0),  # noqa: UP031
            "  Martwych:        %d" % h.get("dead", 0),  # noqa: UP031
            "  Latency avg:     %.1f ms" % avg_lat,  # noqa: UP031
            "  Latency ostatni: %.1f ms" % h.get("avg_latency_ms", 0.0),  # noqa: UP031
            "  Glob.Recycler:   %d utylizacji" % self.global_recycler.total_recycled,  # noqa: UP031
            "  Cykli:           %d" % self.total_cycles,  # noqa: UP031
            "=" * 56,
        ]
        return "\n".join(lines)
