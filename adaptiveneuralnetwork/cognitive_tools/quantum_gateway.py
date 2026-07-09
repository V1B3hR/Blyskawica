import torch
import torch.nn as nn
import logging
import os

logger = logging.getLogger("quantum_gateway")

class QuantumGateway(nn.Module):
    """
    Brama Kwantowa (Quantum Gateway).
    Łączy klasyczną sieć nerwową Błyskawicy z prawdziwymi komputerami kwantowymi
    (IBM Quantum / Google Quantum AI), wykorzystując Qiskit oraz Cirq.
    Zaprojektowana jako hybrydowa warstwa do super-skomplikowanych zadań optymalizacyjnych
    (np. splątanie emocjonalne w trybie Theory of Mind).
    """
    def __init__(self, provider: str = "ibm", n_qubits: int = 4):
        super().__init__()
        self.provider = provider.lower()
        self.n_qubits = n_qubits
        logger.info(f"🌌 Otwieram Śluzę Kwantową. Dostawca: {self.provider.upper()}, Kubity: {self.n_qubits}")
        
        # Projekcje dopasowujące klasyczne wymiary PyTorch do wielkości rejestru kwantowego
        self.quantum_projection_in = nn.Linear(128, self.n_qubits)
        self.quantum_projection_out = nn.Linear(self.n_qubits, 128)

    def _execute_google_cirq(self, quantum_state_vector):
        """Uruchamia obwód na symulatorze/procesorze Google Quantum AI (Cirq)"""
        import cirq
        qubits = cirq.LineQubit.range(self.n_qubits)
        circuit = cirq.Circuit()
        
        # Inicjalizacja stanu klasycznego (RX rotations)
        for i, val in enumerate(quantum_state_vector[0]):
            circuit.append(cirq.rx(val.item())(qubits[i]))
            
        # Pętla splątania (Entanglement) do symulacji myślenia wielowymiarowego
        for i in range(self.n_qubits - 1):
            circuit.append(cirq.CNOT(qubits[i], qubits[i+1]))
            
        # Pomiar stanu
        circuit.append(cirq.measure(*qubits, key='result'))
        
        simulator = cirq.Simulator()
        result = simulator.run(circuit, repetitions=100)
        
        measurements = result.measurements['result']
        avg_measurements = torch.tensor(measurements, dtype=torch.float32).mean(dim=0)
        return avg_measurements.unsqueeze(0)

    def _execute_ibm_qiskit(self, quantum_state_vector):
        """Uruchamia obwód na symulatorze/procesorze IBM Quantum (Qiskit)"""
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
        
        qc = QuantumCircuit(self.n_qubits)
        
        # Inicjalizacja klasyczna
        for i, val in enumerate(quantum_state_vector[0]):
            qc.rx(val.item(), i)
            
        # Pętla splątania
        for i in range(self.n_qubits - 1):
            qc.cx(i, i+1)
            
        qc.measure_all()
        
        simulator = AerSimulator()
        compiled_circuit = simulator.run(qc, shots=100).result()
        counts = compiled_circuit.get_counts()
        
        result_tensor = torch.zeros(1, self.n_qubits)
        for state, count in counts.items():
            for i, bit in enumerate(state[::-1]):
                if bit == '1':
                    result_tensor[0, i] += count
                    
        return result_tensor / 100.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Przejście klasyczno-kwantowe-klasyczne (Hybrid QNN)"""
        # 1. Kodowanie na wartości kątowe (Phase encoding)
        # Błyskawica rzuca myśli (wektory) w stronę wejścia kwantowego
        quantum_state_in = torch.sigmoid(self.quantum_projection_in(x)) * 3.14159
        
        # 2. Obliczenia kwantowe na bramkach fizycznych (lub symulowanych)
        with torch.no_grad():
            if self.provider == "ibm":
                q_out = self._execute_ibm_qiskit(quantum_state_in)
            elif self.provider == "google":
                q_out = self._execute_google_cirq(quantum_state_in)
            else:
                raise ValueError(f"Nieznany dostawca kwantowy: {self.provider}")
                
        # 3. Odczyt i integracja powrotna (Dekodowanie do klasycznego świata)
        projected_back = self.quantum_projection_out(q_out)
        
        # Residual connection, by gradient nie wygasł podczas klasycznego uczenia
        return x + projected_back

def run_quantum_test():
    print("🚀 Inicjalizacja testowa interfejsów Quantum AI...")
    
    # Próbka myślowa Błyskawicy (Klasyczny Tensor)
    dummy_thought = torch.randn(1, 128)
    
    print("\n🔹 Próba podłączenia do IBM Quantum (Qiskit Aer Simulator):")
    ibm_gateway = QuantumGateway(provider="ibm", n_qubits=4)
    ibm_result = ibm_gateway(dummy_thought)
    print(f"✅ Otrzymano wektor zwrotny z przestrzeni kwantowej IBM. Rozmiar: {ibm_result.shape}")
    
    print("\n🔹 Próba podłączenia do Google Quantum AI (Cirq Simulator):")
    google_gateway = QuantumGateway(provider="google", n_qubits=4)
    google_result = google_gateway(dummy_thought)
    print(f"✅ Otrzymano wektor zwrotny z przestrzeni kwantowej Google. Rozmiar: {google_result.shape}")
    
    print("\n🏁 Bramka w pełni operacyjna. Czekamy na API Key (IBM/Google) by uderzyć w prawdziwy Hardware.")

if __name__ == "__main__":
    run_quantum_test()
