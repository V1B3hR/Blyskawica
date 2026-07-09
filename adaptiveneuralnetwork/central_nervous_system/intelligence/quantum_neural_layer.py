"""
Błyskawica V5 — Quantum Neural Layer (QML)
==========================================
Parameterized Quantum Circuit (PQC) jako warstwa sieci neuronowej PyTorch.
Gradienty liczone przez Parameter Shift Rule — kompatybilne z prawdziwym sprzętem.

Architektura PQC:
  1. Kodowanie wejścia: RY(x_i * pi) — mapowanie cech klasycznych na kąty
  2. Warstwy wariacyjne: RY(θ) + RZ(φ) + łańcuch CNOT
  3. Pomiar: wartości oczekiwane operatorów Pauliego-Z

Parameter Shift Rule (PSR):
  dL/dθ = (L(θ + π/2) - L(θ - π/2)) / 2
  Wymaga 2 ewaluacji obwodu na parametr — działa na rzeczywistym sprzęcie.
"""

import math
import logging
from typing import Optional, List, Tuple

import torch
import torch.nn as nn
from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sprawdzenie dostępności Qiskit
# ---------------------------------------------------------------------------
try:
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    from qiskit.quantum_info import SparsePauliOp
    _QISKIT_AVAILABLE = True
except ImportError:
    _QISKIT_AVAILABLE = False
    logger.warning("[QuantumLayer] Qiskit niedostępny — tryb klasyczny (liniowy).")

try:
    from qiskit_aer.primitives import EstimatorV2 as AerEstimator
    _AER_AVAILABLE = True
except ImportError:
    _AER_AVAILABLE = False

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as IBMEstimator
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    _IBM_AVAILABLE = True
except ImportError:
    _IBM_AVAILABLE = False

def get_workspace_root():
    import os
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "blyskawica_app").exists() or (parent / "blyskawica_core").exists():
            return parent
    return Path(r"C:\Projekty\Blyskawica_V8")

WORKSPACE_ROOT = get_workspace_root()


# ---------------------------------------------------------------------------
# Budowanie obwodu PQC
# ---------------------------------------------------------------------------

def _build_pqc(n_qubits: int, n_layers: int,
               x_params: "ParameterVector",
               theta_params: "ParameterVector") -> "QuantumCircuit":
    """
    Buduje Parameterized Quantum Circuit.

    Parametry:
        x_params     — parametry wejściowe (dane, nie optymalizowane)
        theta_params — parametry wariacyjne (wagi, optymalizowane przez PSR)
    """
    qc = QuantumCircuit(n_qubits)

    # --- Warstwa kodowania danych ---
    for i in range(n_qubits):
        qc.ry(x_params[i] * math.pi, i)

    # --- Warstwy wariacyjne ---
    for layer in range(n_layers):
        base = layer * n_qubits * 2  # 2 parametry (RY + RZ) na kubit na warstwę

        # Rotacje parametryczne
        for i in range(n_qubits):
            qc.ry(theta_params[base + i * 2], i)
            qc.rz(theta_params[base + i * 2 + 1], i)

        # Splątanie: łańcuch CNOT
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        # Ring closure (ostatni z pierwszym) — lepsza ekspresywność
        if n_qubits > 2:
            qc.cx(n_qubits - 1, 0)

    return qc


# ---------------------------------------------------------------------------
# Klasa warstwy kwantowej — PyTorch Module
# ---------------------------------------------------------------------------

class QuantumNeuralLayer(nn.Module):
    """
    Warstwa sieci neuronowej oparta na PQC.

    Zachowuje się jak nn.Linear ale gradienty są liczone przez PSR.
    Może działać na:
        - Lokalnym symulatorze Aer (szybki, do debuggowania)
        - Prawdziwym procesorze IBM (wolny, ale kwantowy)
        - Trybie klasycznym fallback (jeśli Qiskit niedostępny)
    """

    def __init__(self,
                 in_features: int,
                 n_qubits: int = 4,
                 n_layers: int = 2,
                 backend: str = "aer",
                 shots: int = 1024,
                 ibm_service: Optional[object] = None,
                 use_gli_stabilization: bool = True):
        """
        Args:
            in_features: Rozmiar wejścia (zostanie zredukowany/dopasowany do n_qubits)
            n_qubits:    Liczba kubitów (= rozmiar wyjścia)
            n_layers:    Liczba warstw wariacyjnych
            backend:     "aer" (lokalny) lub "ibm" (sprzęt kwantowy)
            shots:       Liczba powtórzeń pomiaru (więcej = dokładniejszy gradient)
            ibm_service: Istniejący QiskitRuntimeService (opcjonalnie)
        """
        super().__init__()

        self.in_features = in_features
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.backend_mode = backend
        self.shots = shots
        self.ibm_service = ibm_service
        self.use_gli_stabilization = use_gli_stabilization

        if self.use_gli_stabilization:
            self.gli = GroundLoopIsolator(isolation_ratio=0.05)
        else:
            self.gli = None

        # Liczba parametrów wariacyjnych: n_layers * n_qubits * 2 (RY + RZ)
        self.n_params = n_layers * n_qubits * 2

        # Wagi kwantowe (optymalizowane przez PSR)
        self.theta = nn.Parameter(
            torch.randn(self.n_params) * 0.1
        )

        # Warstwa redukująca wejście do n_qubits (klasyczna projekcja)
        self.input_projection = nn.Linear(in_features, n_qubits, bias=False)

        # Inicjalizacja obwodu (jeśli Qiskit dostępny)
        self._estimator = None
        self._pqc_template = None
        self._x_params = None
        self._theta_params = None

        if _QISKIT_AVAILABLE:
            self._init_circuit()
            self._init_estimator()

    def _init_circuit(self):
        """Buduje szablon obwodu PQC z symbolicznymi parametrami."""
        self._x_params = ParameterVector('x', self.n_qubits)
        self._theta_params = ParameterVector('θ', self.n_params)
        self._pqc_template = _build_pqc(
            self.n_qubits, self.n_layers,
            self._x_params, self._theta_params
        )
        logger.info(f"[QuantumLayer] PQC zbudowany: {self.n_qubits} kubitów, "
                    f"{self.n_layers} warstwy, {self.n_params} parametrów")

    def _init_estimator(self):
        """Inicjalizuje estymator dla wybranego backendu."""
        if self.backend_mode == "aer" and _AER_AVAILABLE:
            self._estimator = AerEstimator()
            logger.info("[QuantumLayer] Backend: Qiskit Aer (lokalny symulator)")
        elif self.backend_mode == "ibm" and _IBM_AVAILABLE and self.ibm_service:
            hw_backend = self.ibm_service.least_busy(simulator=False, operational=True)
            pm = generate_preset_pass_manager(optimization_level=1, backend=hw_backend)
            self._pqc_template = pm.run(self._pqc_template)
            self._estimator = IBMEstimator(mode=hw_backend)
            logger.info(f"[QuantumLayer] Backend: IBM Hardware ({hw_backend.name})")
        else:
            logger.warning("[QuantumLayer] Brak backendu — tryb fallback klasyczny.")

    def _run_circuit(self, x_vals: np.ndarray, theta_vals: np.ndarray) -> np.ndarray:
        """
        Uruchamia obwód dla podanych wartości parametrów.
        Zwraca wartości oczekiwane <Z_i> dla każdego kubitu.
        """
        if self._estimator is None or self._pqc_template is None:
            return np.tanh(x_vals)

        # Operatory Pauliego-Z dla każdego kubitu
        observables = [
            SparsePauliOp("I" * (self.n_qubits - 1 - i) + "Z" + "I" * i)
            for i in range(self.n_qubits)
        ]

        # Budujemy słownik param -> wartość
        param_dict = {}
        for i in range(self.n_qubits):
            param_dict[self._x_params[i]] = float(x_vals[i])
        for i in range(self.n_params):
            param_dict[self._theta_params[i]] = float(theta_vals[i])

        # Podstawiamy wartości bezpośrednio do kopii obwodu
        bound_circuit = self._pqc_template.assign_parameters(param_dict)

        # PUB format dla EstimatorV2: (circuit, observable)
        pubs = [(bound_circuit, obs) for obs in observables]

        try:
            job = self._estimator.run(pubs)
            results = job.result()
            return np.array([results[i].data.evs for i in range(self.n_qubits)])
        except Exception as e:
            logger.error(f"[QuantumLayer] Błąd ewaluacji obwodu: {e}")
            return np.tanh(x_vals)

    def _parameter_shift_gradient(self, x_vals: np.ndarray,
                                   theta_vals: np.ndarray) -> np.ndarray:
        """
        Oblicza gradient przez Parameter Shift Rule.
        dE/dθ_i = (E(θ_i + π/2) - E(θ_i - π/2)) / 2
        Wymaga 2 * n_params ewaluacji obwodu.
        """
        grads = np.zeros(self.n_params)
        shift = math.pi / 2

        for i in range(self.n_params):
            theta_plus = theta_vals.copy()
            theta_plus[i] += shift
            e_plus = self._run_circuit(x_vals, theta_plus).mean()

            theta_minus = theta_vals.copy()
            theta_minus[i] -= shift
            e_minus = self._run_circuit(x_vals, theta_minus).mean()

            grads[i] = (e_plus - e_minus) / 2.0

        return grads

    def _input_shift_gradient(self, x_vals: np.ndarray,
                              theta_vals: np.ndarray) -> np.ndarray:
        """
        Oblicza gradient względem wejść (x) przez Parameter Shift Rule.
        Ponieważ wejście x_i jest kodowane jako RY(x_i * pi), to:
        dE/dx_i = (E((x_i + 0.5)*pi) - E((x_i - 0.5)*pi)) / 2 * pi
        Wymaga 2 * n_qubits ewaluacji obwodu.
        """
        grads = np.zeros(self.n_qubits)
        shift = 0.5  # shift w przestrzeni x, co daje shift o pi/2 w kącie

        for i in range(self.n_qubits):
            x_plus = x_vals.copy()
            x_plus[i] += shift
            e_plus = self._run_circuit(x_plus, theta_vals).mean()

            x_minus = x_vals.copy()
            x_minus[i] -= shift
            e_minus = self._run_circuit(x_minus, theta_vals).mean()

            grads[i] = ((e_plus - e_minus) / 2.0) * math.pi

        return grads

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Przejście w przód przez warstwę kwantową.
        Używa niestandardowej funkcji autograd dla PSR.
        """
        # Projekcja wejścia na przestrzeń kubitów
        x_reduced = self.input_projection(x)  # (batch, n_qubits)

        # Normalizacja do [-1, 1] dla kątów
        x_norm = torch.tanh(x_reduced)

        # Zastosowanie niestandardowego backward z PSR
        q_out = QuantumFunction.apply(x_norm, self.theta, self)

        if self.use_gli_stabilization and self.gli is not None:
            q_out = self.gli(q_out)

        return q_out


class QuantumFunction(torch.autograd.Function):
    """
    Niestandardowa funkcja autograd implementująca PSR.
    Pozwala PyTorchowi obliczać gradienty przez kwantowe obwody.
    """

    @staticmethod
    def forward(ctx, x: torch.Tensor, theta: torch.Tensor,
                layer: QuantumNeuralLayer) -> torch.Tensor:
        ctx.layer = layer
        ctx.save_for_backward(x, theta)

        results = []
        theta_np = theta.detach().numpy()

        for i in range(x.shape[0]):  # batch loop
            x_np = x[i].detach().numpy()
            exp_vals = layer._run_circuit(x_np, theta_np)
            results.append(exp_vals)

        return torch.tensor(np.array(results), dtype=torch.float32)

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor):
        x, theta = ctx.saved_tensors
        layer = ctx.layer
        theta_np = theta.detach().numpy()

        # Gradient po theta przez PSR
        theta_grad = torch.zeros_like(theta)
        for i in range(x.shape[0]):
            x_np = x[i].detach().numpy()
            psr_grads = layer._parameter_shift_gradient(x_np, theta_np)
            # Chain rule: dL/dθ = dL/dE * dE/dθ
            theta_grad += grad_output[i].mean() * torch.tensor(psr_grads, dtype=torch.float32)

        theta_grad /= x.shape[0]

        # Gradient po x przez PSR
        x_grad = torch.zeros_like(x)
        for i in range(x.shape[0]):
            x_np = x[i].detach().numpy()
            psr_x_grads = layer._input_shift_gradient(x_np, theta_np)
            # Chain rule: dL/dx = dL/dE * dE/dx
            x_grad[i] = grad_output[i].mean() * torch.tensor(psr_x_grads, dtype=torch.float32)

        return x_grad, theta_grad, None


# ---------------------------------------------------------------------------
# Prosty test: uczymy warstwę kwantową rozwiązywać problem XOR
# ---------------------------------------------------------------------------

def run_qml_training_demo(n_steps: int = 20, backend: str = "aer") -> dict:
    """
    Demonstracja QML: uczymy QuantumNeuralLayer rozwiązywać XOR.

    XOR jest nieliniowo separowalny — wymaga co najmniej jednej warstwy
    z nieliniowością. Warstwa kwantowa jest z natury nieliniowa dzięki
    splątaniu i rotacjom.

    Args:
        n_steps: Liczba kroków optymalizacji
        backend: "aer" lub "ibm"

    Returns:
        Słownik z historią strat i wagami końcowymi.
    """
    print(f"\n{'='*60}")
    print("  QML TRAINING DEMO — Błyskawica v5.1")
    print(f"  Backend: {backend.upper()}")
    print(f"{'='*60}\n")

    # Dane XOR (4 przykłady)
    X = torch.tensor([
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0],
    ])
    y = torch.tensor([0.0, 1.0, 1.0, 0.0])  # XOR outputs

    # Model: QuantumNeuralLayer + klasyczne wyjście
    q_layer = QuantumNeuralLayer(in_features=2, n_qubits=4, n_layers=2,
                                 backend=backend, shots=512)
    output_layer = nn.Linear(4, 1)
    model = nn.Sequential(q_layer, output_layer)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)
    loss_fn = nn.MSELoss()

    loss_history = []
    print(f"  Parametry kwantowe (θ): {q_layer.n_params}")
    print(f"  Kubity: {q_layer.n_qubits}, Warstwy PQC: {q_layer.n_layers}\n")

    for step in range(n_steps):
        optimizer.zero_grad()
        out = model(X).squeeze()
        loss = loss_fn(out, y)
        loss.backward()
        optimizer.step()

        loss_val = loss.item()
        loss_history.append(loss_val)

        if (step + 1) % 5 == 0 or step == 0:
            print(f"  Krok {step+1:3d}/{n_steps} | Loss: {loss_val:.6f}")

    print(f"\n  Utrata końcowa: {loss_history[-1]:.6f}")
    print(f"  Redukcja straty: {((loss_history[0] - loss_history[-1]) / loss_history[0] * 100):.1f}%")
    print(f"\n{'='*60}")

    return {
        "status": "success",
        "backend": backend,
        "n_steps": n_steps,
        "initial_loss": loss_history[0],
        "final_loss": loss_history[-1],
        "loss_reduction_pct": round((loss_history[0] - loss_history[-1]) / loss_history[0] * 100, 2),
        "loss_history": loss_history,
        "n_quantum_params": q_layer.n_params,
        "n_qubits": q_layer.n_qubits,
    }


if __name__ == "__main__":
    import sys
    import json

    logging.basicConfig(level=logging.WARNING)

    results = run_qml_training_demo(n_steps=15, backend="aer")

    out_path = str(WORKSPACE_ROOT / "qml_training_results.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\nWyniki zapisane: {out_path}")
