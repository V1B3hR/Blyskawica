"""
Błyskawica V5 — Quantum Integrity Watchdog (Debugging 2.0)
===========================================================
Cykliczny strażnik integralności systemu oparty na IBM Quantum.

Zasada działania:
  1. Co N sekund (lub na żądanie) uruchamia 4-kubitowy obwód na IBM
  2. Wynik (hash stanu kwantowego) porównuje z referencją z poprzedniego audytu
  3. Oblicza ODCHYŁKĘ jako metrykę dryfu systemu
  4. Jeśli dryf > próg -> eskaluje DEFCON w IdentityGuard i powiadamia Architekta

Filozofia:
  Kwantowy szum jest DETERMINISTYCZNIE niezdeterminowany — ten sam obwód
  na tym samym sprzęcie daje za każdym razem lekko inny wynik (dekoherencja).
  Dlatego śledzimy ROZKŁAD (wektor oczekiwań), nie pojedynczy bit.
  Anomalia = gdy rozkład odbiega więcej niż 2σ od historycznej średniej.
"""

import hashlib
import json
import logging
import math
import random
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch

from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator

logger = logging.getLogger(__name__)

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import SparsePauliOp
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import EstimatorV2 as IBMEstimator, QiskitRuntimeService
    _QUANTUM_AVAILABLE = True
except ImportError:
    _QUANTUM_AVAILABLE = False

try:
    from qiskit_aer.primitives import EstimatorV2 as AerEstimator
    _AER_AVAILABLE = True
except ImportError:
    _AER_AVAILABLE = False

def get_workspace_root():
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "blyskawica_app").exists() or (parent / "blyskawica_core").exists():
            return parent
    return Path(r"C:\Projekty\Blyskawica_V8")

WORKSPACE_ROOT = get_workspace_root()


# ---------------------------------------------------------------------------
# Struktury danych
# ---------------------------------------------------------------------------

@dataclass
class IntegritySnapshot:
    """Pojedynczy pomiar kwantowy stanu systemu."""
    timestamp: float
    backend: str
    job_id: str
    expectation_vector: list[float]   # <Z_i> dla każdego kubitu
    fingerprint: str                  # SHA-256 wektora oczekiwań
    defcon_level: int = 1             # 1=OK, 2=WATCH, 3=ALERT, 4=CRITICAL
    anomaly_detected: bool = False
    drift_sigma: float = 0.0          # Odchylenie od średniej historycznej (w σ)


@dataclass
class WatchdogConfig:
    n_qubits: int = 4
    shots: int = 256
    check_interval_sec: int = 3600    # Co godzinę domyślnie
    drift_sigma_threshold: float = 2.5
    vault_path: str = str(WORKSPACE_ROOT / "integrity_vault.json")
    api_key_path: str = r"C:\Projekty\Quantlion\apikey Błyskawica.json"
    use_gli_stabilization: bool = True
    isolation_ratio: float = 0.05


# ---------------------------------------------------------------------------
# Główna klasa Watchdog
# ---------------------------------------------------------------------------

class QuantumIntegrityWatchdog:
    """
    Cykliczny strażnik integralności Błyskawicy.
    Używa IBM Quantum jako zewnętrznego, niezależnego źródła prawdy.
    """

    def __init__(self, config: WatchdogConfig = None,
                 identity_guard=None):
        self.config = config or WatchdogConfig()
        self.identity_guard = identity_guard
        self.service: Any | None = None
        self.history: list[IntegritySnapshot] = []
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        # Synaptic Ground Loop Isolation
        self.use_gli_stabilization = getattr(self.config, 'use_gli_stabilization', True)
        if self.use_gli_stabilization:
            isolation_ratio = getattr(self.config, 'isolation_ratio', 0.05)
            self.gli = GroundLoopIsolator(isolation_ratio=isolation_ratio)
        else:
            self.gli = None

        self._load_vault()
        if _QUANTUM_AVAILABLE:
            self._connect()

    def _connect(self):
        try:
            with open(self.config.api_key_path, encoding='utf-8') as f:
                api_key = json.load(f).get("apikey")
            self.service = QiskitRuntimeService(
                channel="ibm_quantum_platform", token=api_key
            )
            logger.info("[Watchdog] Połączono z IBM Quantum.")
        except Exception as e:
            logger.warning(f"[Watchdog] Brak połączenia IBM: {e}. Tryb offline.")

    def _load_vault(self):
        """Ładuje historię pomiarów z dysku."""
        vault_path = Path(self.config.vault_path)
        if vault_path.exists():
            try:
                with open(vault_path, encoding='utf-8') as f:
                    data = json.load(f)
                self.history = [IntegritySnapshot(**s) for s in data]
                logger.info(f"[Watchdog] Załadowano {len(self.history)} snapshotów z vault.")
            except Exception as e:
                logger.warning(f"[Watchdog] Błąd ładowania vault: {e}")

    def _save_vault(self):
        """Zapisuje historię na dysk."""
        try:
            with open(self.config.vault_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(s) for s in self.history], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[Watchdog] Błąd zapisu vault: {e}")

    def _build_integrity_circuit(self) -> "QuantumCircuit":
        """
        Buduje obwód diagnostyczny.
        Używa maksymalnego splątania (stan Bella × 2) jako punktu odniesienia.
        Dekoherencja sprzętu IBM daje przewidywalny, ale unikalny "podpis" backendu.
        """
        qc = QuantumCircuit(self.config.n_qubits)
        # Para splątanych stanów Bella
        qc.h(0); qc.cx(0, 1)  # Bell pair 1  # noqa: E702
        qc.h(2); qc.cx(2, 3)  # Bell pair 2  # noqa: E702
        # Dodatkowe splątanie między parami (wrażliwe na błędy sprzętu)
        qc.cx(1, 2)
        return qc

    def _fingerprint(self, vector: list[float]) -> str:
        """SHA-256 z wektora oczekiwań (zaokrąglony do 4 miejsc)."""
        rounded = [round(v, 4) for v in vector]
        data = json.dumps(rounded, separators=(',', ':'))
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _compute_drift(self, current_vector: list[float]) -> float:
        """
        Oblicza dryf względem historycznej średniej w jednostkach σ.
        Zwraca 0.0 jeśli brak historii.
        """
        if len(self.history) < 3:
            return 0.0

        import math
        historical = [s.expectation_vector for s in self.history[-10:]]
        n_qubits = len(current_vector)

        total_drift = 0.0
        for i in range(n_qubits):
            vals = [h[i] for h in historical if len(h) > i]
            if not vals:
                continue
            mean = sum(vals) / len(vals)
            variance = sum((v - mean) ** 2 for v in vals) / len(vals)
            std = math.sqrt(variance) if variance > 0 else 0.01
            total_drift += abs(current_vector[i] - mean) / std

        return total_drift / n_qubits

    def run_single_audit(self) -> IntegritySnapshot:
        """
        Przeprowadza jeden audyt integralności na IBM Quantum, lokalnym symulatorzu
        lub klasycznej emulacji dynamicznej.
        Zwraca snapshot z wynikiem i oceną anomalii.
        """
        use_local_aer = (_QUANTUM_AVAILABLE and _AER_AVAILABLE and not self.service)

        if not self.service and not use_local_aer:
            logger.warning("[Watchdog] IBM Quantum i lokalny Aer niedostępne — emulacja klasyczna.")
            t = time.time()
            # Symulacja dryfu sinusoidalnego + szum gaussowski
            drift_base = 0.05 * math.sin(t / 100.0)
            evs = []
            for _ in range(self.config.n_qubits):
                val = drift_base + random.normalvariate(0.0, 0.02)
                evs.append(float(min(max(val, -1.0), 1.0)))
            job_id = f"sim-{int(t)}"
            backend_name = "simulated_fallback"
        else:
            if use_local_aer:
                backend_name = "aer_simulator"
                estimator = AerEstimator()
                qc = self._build_integrity_circuit()
                isa = qc
                total_qubits = self.config.n_qubits
            else:
                backend = self.service.least_busy(simulator=False, operational=True)
                backend_name = backend.name
                qc = self._build_integrity_circuit()
                pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
                isa = pm.run(qc)
                estimator = IBMEstimator(mode=backend)
                total_qubits = backend.num_qubits

            # Observable: Z_i dla każdego z kubitów logicznych
            def make_obs(q, total):
                return SparsePauliOp("I" * (total - 1 - q) + "Z" + "I" * q)

            observables = [make_obs(i, total_qubits) for i in range(self.config.n_qubits)]
            pubs = [(isa, obs) for obs in observables]

            logger.info(f"[Watchdog] Uruchamianie audytu na {backend_name}...")
            try:
                job = estimator.run(pubs)
                job_id = job.job_id() if hasattr(job, 'job_id') else f"local-{int(time.time())}"
                results = job.result()
                evs = [float(results[i].data.evs) for i in range(self.config.n_qubits)]
            except Exception as e:
                logger.error(f"[Watchdog] Błąd wykonania obwodu: {e}. Fallback do klasycznego.")
                t = time.time()
                drift_base = 0.05 * math.sin(t / 100.0)
                evs = [float(min(max(drift_base + random.normalvariate(0.0, 0.02), -1.0, 1.0))) for _ in range(self.config.n_qubits)]
                job_id = f"fail-fallback-{int(t)}"
                backend_name = f"fallback-{backend_name}"

        # Obliczenie dryfu surowego i ustabilizowanego
        raw_drift = self._compute_drift(evs)

        if self.use_gli_stabilization and self.gli is not None:
            evs_tensor = torch.tensor(evs, dtype=torch.float32).unsqueeze(0)
            stabilized_tensor = self.gli(evs_tensor).squeeze(0)
            stabilized_evs = stabilized_tensor.tolist()
            stabilized_drift = self._compute_drift(stabilized_evs)
        else:
            stabilized_evs = evs
            stabilized_drift = raw_drift

        raw_anomaly = raw_drift > self.config.drift_sigma_threshold
        stabilized_anomaly = stabilized_drift > self.config.drift_sigma_threshold

        # Logic DEFCON: GLI chroni przed fałszywymi alarmami (ograniczenie do DEFCON 2)
        if stabilized_anomaly:
            if stabilized_drift > self.config.drift_sigma_threshold * 2.0:
                defcon = 4  # CRITICAL: dryf nawet po stabilizacji przekracza krytyczny próg
            else:
                defcon = 3  # ALERT: wyraźny dryf po stabilizacji
            anomaly = True
            reported_drift = stabilized_drift
        elif raw_anomaly:
            defcon = 2  # WATCH: surowy dryf wysoki, ale stabilizator stłumił szum
            anomaly = True
            reported_drift = raw_drift
        else:
            if raw_drift > self.config.drift_sigma_threshold * 0.7:
                defcon = 2
            else:
                defcon = 1
            anomaly = False
            reported_drift = raw_drift

        fingerprint = self._fingerprint(evs)

        snapshot = IntegritySnapshot(
            timestamp=time.time(),
            backend=backend_name,
            job_id=job_id,
            expectation_vector=evs,
            fingerprint=fingerprint,
            defcon_level=defcon,
            anomaly_detected=anomaly,
            drift_sigma=round(reported_drift, 4)
        )

        self.history.append(snapshot)
        self._save_vault()

        # Eskalacja do IdentityGuard jeśli dostępny i defcon >= 3
        if self.identity_guard and anomaly and defcon >= 3:
            logger.critical(f"[Watchdog] DEFCON {defcon}: dryf kwantowy = {reported_drift:.2f}σ!")
            if hasattr(self.identity_guard, "escalate_defcon"):
                self.identity_guard.escalate_defcon(defcon, reason=f"Quantum drift: {reported_drift:.2f}σ")

        status = "OK" if not anomaly else f"ANOMALIA (drift={reported_drift:.2f}σ, defcon={defcon})"
        logger.info(f"[Watchdog] Audyt zakończony | DEFCON {defcon} | {status}")
        logger.info(f"  Fingerprint: {fingerprint} | Backend: {backend_name}")

        return snapshot

    # ------------------------------------------------------------------
    # Tryb cykliczny (background thread)
    # ------------------------------------------------------------------

    def start_continuous(self):
        """Uruchamia cykliczne audyty w tle."""
        if self._thread and self._thread.is_alive():
            logger.warning("[Watchdog] Już działa.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info(f"[Watchdog] Cykliczny tryb aktywny. Interwał: {self.config.check_interval_sec}s")

    def stop(self):
        """Zatrzymuje cykliczne audyty."""
        self._stop_event.set()
        logger.info("[Watchdog] Zatrzymano.")

    def _watch_loop(self):
        while not self._stop_event.is_set():
            try:
                snap = self.run_single_audit()
                if snap.defcon_level >= 3:
                    logger.critical(f"[Watchdog] ⚠️  DEFCON {snap.defcon_level} — Architekt musi to sprawdzić!")
            except Exception as e:
                logger.error(f"[Watchdog] Błąd w pętli: {e}")
            self._stop_event.wait(self.config.check_interval_sec)

    def get_status_report(self) -> dict[str, Any]:
        """Zwraca raport statusu dla ArchitecturalMirror."""
        if not self.history:
            return {"status": "no_data", "audits": 0}
        last = self.history[-1]
        return {
            "status": "anomaly" if last.anomaly_detected else "healthy",
            "defcon": last.defcon_level,
            "last_audit": last.timestamp,
            "last_backend": last.backend,
            "last_fingerprint": last.fingerprint,
            "drift_sigma": last.drift_sigma,
            "total_audits": len(self.history),
        }


# ---------------------------------------------------------------------------
# Jednorazowy audyt (tryb CLI)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )

    print("\n" + "="*60)
    print("  QUANTUM DEBUGGING 2.0 — Audyt Integralności")
    print("  Błyskawica V5 | ibm_fez / ibm_marrakesh")
    print("="*60 + "\n")

    watchdog = QuantumIntegrityWatchdog()
    snap = watchdog.run_single_audit()

    print(f"\n  Timestamp:   {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snap.timestamp))}")
    print(f"  Backend:     {snap.backend}")
    print(f"  Job ID:      {snap.job_id}")
    print(f"  Fingerprint: {snap.fingerprint}")
    print(f"  <Z> wektor:  {[round(v, 4) for v in snap.expectation_vector]}")
    print(f"  Dryf:        {snap.drift_sigma}σ")
    print(f"  DEFCON:      {snap.defcon_level} {'✓ NORMALNY' if snap.defcon_level == 1 else '⚠ UWAGA'}")
    print(f"  Anomalia:    {'TAK ⚠' if snap.anomaly_detected else 'NIE ✓'}")

    report = watchdog.get_status_report()
    out = str(WORKSPACE_ROOT / "integrity_audit_latest.json")
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({"snapshot": asdict(snap), "report": report}, f, indent=4, ensure_ascii=False)

    print(f"\n  Raport zapisany: {out}")
    print("="*60 + "\n")
