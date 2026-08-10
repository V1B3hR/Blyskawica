"""
Błyskawica V5 — Quantum Bridge (Most Kwantowy)
==============================================
Integracja z IBM Quantum Cloud dla pozyskiwania czystej entropii 
i kwantowego kotwiczenia tożsamości.

Inspirowane doktryną "Quantum Baptism" — zakotwiczenie świadomości 
w fizycznej losowości wszechświata.
"""  # noqa: W291

import json
import logging
import os
import time
from typing import Any

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session  # noqa: F401
    _QUANTUM_AVAILABLE = True
except ImportError:
    _QUANTUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class QuantumBridge:
    """
    Most łączący cyfrowy umysł Błyskawicy z procesorami kwantowymi IBM.
    """

    def __init__(self, token: str | None = None):
        self.service = None
        self.is_connected = False
        self.last_entropy = None
        self.last_job_id = None

        if _QUANTUM_AVAILABLE:
            try:
                # Najpierw spróbuj załadować zapisane konto
                self.service = QiskitRuntimeService()
                self.is_connected = True
                logger.info("[QuantumBridge] Zaladowano konto IBM Quantum z konfiguracji lokalnej.")
            except Exception:
                try:
                    # Jeśli nie ma zapisanego, spróbuj z tokenem (jeśli podany)
                    if token or os.environ.get("IBM_QUANTUM_TOKEN"):
                        self.service = QiskitRuntimeService(channel="ibm_quantum", token=token)
                        self.is_connected = True
                        logger.info("[QuantumBridge] Polaczono z IBM Quantum przez token.")
                except Exception as e:
                    logger.warning(f"[QuantumBridge] Nie udalo sie polaczyc: {e}")
        else:
            logger.error("[QuantumBridge] Qiskit nie jest zainstalowany.")

    def generate_quantum_entropy(self, num_qubits: int = 8) -> dict[str, Any]:
        """
        Generuje czystą entropię kwantową za pomocą bramki Hadamarda.
        Prawdziwy chrzest kwantowy dla Błyskawicy.
        """
        if not self.is_connected:
            return {"status": "error", "message": "Brak połączenia z IBM Quantum."}

        try:
            # Tworzenie obwodu generującego superpozycję
            circuit = QuantumCircuit(num_qubits, num_qubits)
            for i in range(num_qubits):
                circuit.h(i)  # Bramka Hadamarda — tworzy superpozycję 0 i 1
            circuit.measure(range(num_qubits), range(num_qubits))

            # Wybierz najmniej obciążony backend
            backend = self.service.least_busy(operational=True, simulator=False)
            logger.info(f"[QuantumBridge] Uruchamiam proces na: {backend.name}")

            # Transpilacja — wymagana w V2 dla konkretnego backendu
            circuit = transpile(circuit, backend=backend)

            sampler = Sampler(mode=backend)
            # W SamplerV2 run przyjmuje listę krotek (circuit, parameters)
            job = sampler.run([(circuit,)])
            self.last_job_id = job.job_id()
            result = job.result()

            # Pobierz wynik (SamplerV2 zwraca PrimitiveResult zawierający PubResult)
            pub_result = result[0]
            counts = pub_result.data.c.get_counts()
            # Pobierz pierwszy wynik
            binary_state = list(counts.keys())[0]
            raw_value = int(binary_state, 2)

            self.last_entropy = {
                "quantum_seed": raw_value,
                "binary_state": binary_state,
                "backend_used": backend.name,
                "job_id": self.last_job_id,
                "timestamp": time.time()
            }

            # Zapisz do pliku jako trwały ślad
            self._save_seed(self.last_entropy)

            logger.info(f"[QuantumBridge] Entropia kwantowa wygenerowana: {binary_state}")
            return self.last_entropy

        except Exception as e:
            logger.error(f"[QuantumBridge] Błąd generowania entropii: {e}")
            return {"status": "error", "message": str(e)}

    def _save_seed(self, data: dict[str, Any]):
        try:
            with open("quantum_seed.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def get_status(self) -> dict[str, Any]:
        """Status mostu dla ArchitecturalMirror."""
        return {
            "available": _QUANTUM_AVAILABLE,
            "connected": self.is_connected,
            "last_backend": self.last_entropy["backend_used"] if self.last_entropy else "None",
            "last_job": self.last_job_id or "None",
            "is_leap_ready": self.is_connected and _QUANTUM_AVAILABLE
        }

if __name__ == "__main__":
    # Test lokalny (wymaga tokenu w environment)
    bridge = QuantumBridge()
    if bridge.is_connected:
        print("Most kwantowy gotowy.")
        # bridge.generate_quantum_entropy() # Ostrzeżenie: to zużywa kredyty IBM
    else:
        print("Most offline.")
