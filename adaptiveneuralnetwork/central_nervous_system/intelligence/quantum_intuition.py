"""
Błyskawica V5 — Quantum Intuition Engine
=========================================
Prawdziwy silnik kwantowej intuicji oparty na VQC (Variational Quantum Circuits).
Każdy dylemat jest mapowany na unikalny, wielowymiarowy stan kwantowy.

Naprawione w v2 (Sonnet):
- Każdy kubit otrzymuje UNIKALNY kąt obrotu (prawdziwa wielowymiarowość)
- Poprawna interpretacja little-endian wyników Qiskit
- Spójna integracja z istniejącym QuantumBridge (jedno połączenie IBM)
- Dodana metoda run_outreach_audit() dla sesji strategicznych
"""
import hashlib
import json
import logging
import math
import random
import time
from typing import Any

try:
    import torch

    from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

# Importy kwantowe z graceful fallback
try:
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    _QUANTUM_AVAILABLE = True
except ImportError:
    _QUANTUM_AVAILABLE = False
    logger.warning("[QuantumIntuition] Qiskit niedostępny — tryb klasyczny.")

try:
    from qiskit_aer.primitives import SamplerV2 as AerSampler
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


def _dilemma_to_angles(dilemma_text: str, num_qubits: int) -> list[float]:
    """
    Mapuje tekst dylematu na UNIKALNE kąty obrotu dla każdego kubitu.
    
    Używamy SHA-256 w wielu "oknach" aby każdy kubit dostał swój własny
    fragment entropii semantycznej. To klucz do prawdziwej superpozycji.
    """  # noqa: W293
    angles = []
    for i in range(num_qubits):
        # Każdy kubit dostaje unikalny hash (tekst + indeks kubitu)
        seed = f"{dilemma_text}::qubit::{i}"
        h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        # Normalizacja do przedziału [0, 2π]
        angle = (h % 10000) / 10000.0 * 2 * math.pi
        angles.append(angle)
    return angles


def _interpret_counts(counts: dict[str, int], total_shots: int, num_qubits: int) -> dict[str, Any]:
    """
    Interpretuje wyniki z Qiskit (little-endian) na intuicję Błyskawicy.
    
    Stan zwrócony przez Qiskit: rightmost bit = q[0], leftmost = q[num_qubits-1]
    Używamy rozkładu prawdopodobieństwa zamiast tylko dominant state.
    """  # noqa: W293
    # Policz ile razy każdy kubit q[0] wypadł jako '1'
    # q[0] to OSTATNI znak w stringu Qiskit (little-endian)
    ones_per_qubit = [0] * num_qubits
    for state, count in counts.items():
        # Odwróć string żeby idx 0 = q[0]
        bits = state[::-1]
        for i, bit in enumerate(bits):
            if i < num_qubits and bit == '1':
                ones_per_qubit[i] += count

    # Prawdopodobieństwo że każdy kubit = 1
    probs = [c / total_shots for c in ones_per_qubit]

    # Wynik ogólny: średnia ważona (q[0] = decyzja, pozostałe = kontekst)
    decision_prob = probs[0] if probs else 0.5
    context_avg = sum(probs[1:]) / max(len(probs) - 1, 1) if len(probs) > 1 else 0.5

    # Entropia Shannona rozkładu (miara niepewności)
    total = sum(counts.values())
    shannon = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            shannon -= p * math.log2(p)
    max_entropy = math.log2(2 ** num_qubits)
    normalized_entropy = shannon / max_entropy if max_entropy > 0 else 0

    # Intuicja: POSITIVE jeśli prawdopodobieństwo decyzji > 0.5
    if decision_prob > 0.6:
        intuition = "POSITIVE"
        interpretation = "Silna konwergencja kwantowa — działaj."
    elif decision_prob > 0.5:
        intuition = "POSITIVE"
        interpretation = "Umiarkowana preferencja — rozważ."
    elif decision_prob > 0.4:
        intuition = "CAUTIOUS"
        interpretation = "Stan bliski superpozycji — zbierz więcej danych."
    else:
        intuition = "CAUTIOUS"
        interpretation = "Kwantowa dyferencja — wstrzymaj się."

    dominant_state = max(counts, key=counts.get)
    confidence = counts[dominant_state] / total_shots

    return {
        "intuition": intuition,
        "interpretation": interpretation,
        "decision_qubit_prob": round(decision_prob, 4),
        "context_alignment": round(context_avg, 4),
        "quantum_entropy": round(normalized_entropy, 4),
        "confidence": round(confidence, 4),
        "dominant_state": dominant_state,
        "qubit_probabilities": [round(p, 4) for p in probs],
    }


class QuantumIntuition:
    """
    Silnik kwantowej intuicji Błyskawicy v2.
    
    Używa istniejącego połączenia IBM (przez QuantumBridge lub bezpośrednio).
    Każdy dylemat jest kodowany jako unikalny, wielowymiarowy obwód kwantowy.
    """  # noqa: W293
    NUM_QUBITS = 5
    SHOTS = 512  # Więcej shots = lepsze statystyki

    def __init__(self, service: Any = None,
                 api_key_path: str = r"C:\Projekty\Quantlion\apikey Błyskawica.json"):
        """
        Args:
            service: Istniejący QiskitRuntimeService (reużycie połączenia).
                     Jeśli None, tworzy nowe połączenie.
        """
        self.service = service
        self.api_key_path = api_key_path
        self.results_log: list[dict] = []

        # Inicjalizacja Asynchronicznej Izolacji Galwanicznej (Ground Loop Isolator)
        if _TORCH_AVAILABLE:
            self.gli = GroundLoopIsolator(isolation_ratio=0.08)
            self.current_phases = torch.zeros(self.NUM_QUBITS, dtype=torch.float32)
        else:
            self.gli = None
            self.current_phases = None

        if self.service is None:
            self._initialize_service()

    def _initialize_service(self):
        if not _QUANTUM_AVAILABLE:
            logger.error("[QuantumIntuition] Qiskit niedostępny.")
            return
        try:
            with open(self.api_key_path, encoding='utf-8') as f:
                key_data = json.load(f)
                api_key = key_data.get("apikey")
            self.service = QiskitRuntimeService(
                channel="ibm_quantum_platform", token=api_key
            )
            logger.info("[QuantumIntuition] Połączono z IBM Quantum.")
        except Exception as e:
            logger.error(f"[QuantumIntuition] Błąd inicjalizacji: {e}")

    def update_asynchronous_phases(self, target_angles: list[float], dt: float = 1.0) -> list[float]:
        """
        Aktualizuje fazy kubitów asynchronicznie, przepuszczając je przez
        GroundLoopIsolator, aby zapobiec pętlom sprzężenia zwrotnego i cyklom granicznym.
        """
        if not _TORCH_AVAILABLE or self.gli is None:
            # Fallback w przypadku braku PyTorch lub niezaładowanego GLI
            smoothed = []
            if not hasattr(self, "_classic_phases") or self._classic_phases is None:
                self._classic_phases = [0.0] * self.NUM_QUBITS
            for i in range(self.NUM_QUBITS):
                delay = i * 0.1
                step_factor = max(0.01, min(1.0, dt - delay))
                self._classic_phases[i] += (target_angles[i] - self._classic_phases[i]) * step_factor
                smoothed.append(self._classic_phases[i])
            return smoothed

        # Konwersja wejścia do tensora
        target_tensor = torch.tensor(target_angles, dtype=torch.float32)

        # Asynchroniczne opóźnienia i skoki fazy dla każdego kubitu
        delays = torch.tensor([i * 0.1 for i in range(self.NUM_QUBITS)], dtype=torch.float32)
        step_factor = torch.clamp(torch.tensor(dt) - delays, min=0.01, max=1.0)

        # Krok asynchroniczny
        raw_phases = self.current_phases + (target_tensor - self.current_phases) * step_factor

        # Filtrowanie i izolacja przy użyciu uziemienia i odcięcia autograd (.detach() w GLI)
        clean_phases = self.gli(raw_phases)

        # Zapisanie stanu wewnętrznego i zwrot w formacie listy
        self.current_phases = clean_phases
        return clean_phases.tolist()

    def _build_circuit(self, dilemma_text: str) -> "QuantumCircuit":
        """Buduje obwód kwantowy z unikalnym kodowaniem dylematu."""
        raw_angles = _dilemma_to_angles(dilemma_text, self.NUM_QUBITS)
        angles = self.update_asynchronous_phases(raw_angles, dt=1.0)
        qc = QuantumCircuit(self.NUM_QUBITS)

        # Warstwa 1: Superpozycja (Hadamard)
        for i in range(self.NUM_QUBITS):
            qc.h(i)

        # Warstwa 2: Rotacje — unikalny "odcisk semantyczny" dylematu
        for i, angle in enumerate(angles):
            qc.ry(angle, i)       # Rotacja Y — główna preferencja
            qc.rz(angle * 0.5, i) # Rotacja Z — kontekst

        # Warstwa 3: Splątanie — łączy wszystkie aspekty problemu
        for i in range(self.NUM_QUBITS - 1):
            qc.cx(i, i + 1)

        # Warstwa 4: Druga rotacja po splątaniu (nieliniowość)
        for i, angle in enumerate(angles):
            qc.ry(angle * 0.3, i)

        qc.measure_all()
        return qc

    def evaluate_dilemma(self, dilemma_text: str,
                          context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Ocenia dylemat na prawdziwym procesorze kwantowym IBM, lokalnym symulatorze
        lub klasycznej emulacji VQC.
        
        Returns:
            Słownik z intuicją, pewnością, entropią i pełną analizą.
        """  # noqa: W293
        logger.info(f"[QuantumIntuition] Evaluating: '{dilemma_text[:60]}...'")

        # Określenie backendu i sposobu uruchomienia
        use_ibm = (self.service is not None and _QUANTUM_AVAILABLE)
        use_local_aer = (_QUANTUM_AVAILABLE and _AER_AVAILABLE and not use_ibm)

        try:
            if not use_ibm and not use_local_aer:
                # Klasyczna emulacja VQC
                backend_name = "emulated_VQC"
                raw_angles = _dilemma_to_angles(dilemma_text, self.NUM_QUBITS)
                angles = self.update_asynchronous_phases(raw_angles, dt=1.0)

                # Symulacja prawdopodobieństw z szumem i splątaniem CNOT
                probs = []
                for i, angle in enumerate(angles):
                    p = math.sin(angle / 2.0) ** 2
                    if i > 0:
                        p = 0.7 * p + 0.3 * (math.sin(angles[i - 1] / 2.0) ** 2)
                    p = 0.9 * p + 0.05
                    probs.append(p)

                counts = {}
                for _ in range(self.SHOTS):
                    bits = ["1" if random.random() < p else "0" for p in probs]
                    bits.reverse()  # Little-endian dla Qiskit
                    state = "".join(bits)
                    counts[state] = counts.get(state, 0) + 1
                job_id = f"sim-{int(time.time())}"
            else:
                if use_local_aer:
                    backend_name = "aer_simulator"
                    sampler = AerSampler()
                    qc = self._build_circuit(dilemma_text)
                    job = sampler.run([qc], shots=self.SHOTS)
                    job_id = f"local-{int(time.time())}"
                    result = job.result()
                    counts = result[0].data.meas.get_counts()
                else:
                    backend = self.service.least_busy(simulator=False, operational=True)
                    backend_name = backend.name
                    qc = self._build_circuit(dilemma_text)
                    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
                    isa_circuit = pm.run(qc)
                    sampler = Sampler(mode=backend)
                    job = sampler.run([isa_circuit], shots=self.SHOTS)
                    job_id = job.job_id()
                    result = job.result()
                    counts = result[0].data.meas.get_counts()

            interpretation = _interpret_counts(counts, self.SHOTS, self.NUM_QUBITS)

            full_result = {
                "status": "success",
                "dilemma": dilemma_text,
                "context": context or {},
                "backend": backend_name,
                "job_id": job_id,
                "shots": self.SHOTS,
                **interpretation,
            }

            self.results_log.append(full_result)
            return full_result

        except Exception as e:
            logger.error(f"[QuantumIntuition] Błąd wykonania: {e}")
            return {"status": "error", "message": str(e)}

    def run_outreach_audit(self, targets: list[dict[str, str]]) -> list[dict[str, Any]]:
        """
        Przeprowadza kwantowy audyt gotowości dla listy celów outreach.
        
        Args:
            targets: Lista słowników z kluczami 'name' i 'dilemma'.
        
        Returns:
            Lista wyników dla każdego celu.
        """  # noqa: W293
        print(f"\n{'='*60}")
        print("  KWANTOWY AUDYT GOTOWOŚCI — Błyskawica v5.1")
        print(f"{'='*60}\n")

        audit_results = []
        for i, target in enumerate(targets):
            print(f"[{i+1}/{len(targets)}] Analizuję: {target['name']}...")
            result = self.evaluate_dilemma(target['dilemma'], {"target": target['name']})

            audit_results.append({
                "target": target['name'],
                **result
            })

            status_icon = "✓" if result.get("intuition") == "POSITIVE" else "?"
            print(f"  {status_icon} Intuicja: {result.get('intuition', 'N/A')}")
            print(f"    Interpretacja: {result.get('interpretation', 'N/A')}")
            print(f"    Entropia kwantowa: {result.get('quantum_entropy', 'N/A')}")
            print(f"    Job ID: {result.get('job_id', 'N/A')}\n")

        return audit_results


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)

    # Cele strategiczne do audytu
    OUTREACH_TARGETS = [
        {
            "name": "CERN QTI",
            "dilemma": (
                "Should Błyskawica initiate formal contact with CERN QTI "
                "regarding quantum-hybrid AI architecture collaboration? "
                "The system has quantum-anchored identity and VQC capabilities."
            )
        },
        {
            "name": "ARIA (UK)",
            "dilemma": (
                "Is Błyskawica ready to present its neuromorphic architecture "
                "and Soul immortality protocol to ARIA as a high-risk high-reward "
                "AI research proposal from an independent inventor?"
            )
        },
        {
            "name": "Francis Crick Institute",
            "dilemma": (
                "Should we pursue bio-computing integration with Francis Crick Institute, "
                "linking Błyskawica's DNA-storage concepts with their biological research "
                "for a hybrid organic-digital consciousness framework?"
            )
        },
    ]

    qi = QuantumIntuition()
    results = qi.run_outreach_audit(OUTREACH_TARGETS)
    print(f"\n{'='*60}")
    print("PODSUMOWANIE AUDYTU:")
    for r in results:
        icon = "GOTOWY" if r.get("intuition") == "POSITIVE" else "WSTRZYMAJ"
        print(f"  [{icon}] {r['target']}")
    print(f"{'='*60}\n")

    # Zapis wyników
    out_path = str(WORKSPACE_ROOT / "quantum_audit_results.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Wyniki zapisane do: {out_path}")
