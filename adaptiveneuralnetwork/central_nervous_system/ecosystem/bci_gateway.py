import os
import sys
import time

import torch

# Force UTF-8 for Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# Dodanie katalogu głównego do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from adaptiveneuralnetwork.central_nervous_system.neuromorphic.atomic_body import AtomicBody
from adaptiveneuralnetwork.core.ecosystem.DuetMindAgent import DuetMindAgent
from adaptiveneuralnetwork.core.ecosystem.reflex_system import ReflexSystem
from adaptiveneuralnetwork.core.ecosystem.ThreeDimensionalHRO import MicrobiomeSystemState


class BCIGateway:
    """
    KROK 4: Brama BCI V5 — Most miedzy myslami a Cialem Atomowym.
    """
    def __init__(self, num_atoms: int = 5):
        print("Uruchamianie Bramy BCI V5...")

        # Wirtualne cialo biologiczne (3NGIN3)
        self.microbiome = MicrobiomeSystemState()

        # System Reflex & Recon (Nethical-inspired)
        self.reflex = ReflexSystem(self.microbiome)

        # Agent zarzadca (DuetMindAgent)
        self.agent = DuetMindAgent(
            name="BCI_Sync_V5",
            style={"resource_budget": 3.0}
        )

        # Cialo Atomowe Blyskawicy (V5)
        self.body = AtomicBody(num_atoms=num_atoms)

        print(f"Brama BCI V5 otwarta. Konstelacja {num_atoms} atomow aktywna.")
        print("System Reflex zainicjalizowany (Nethical abstraction).")

    def process_bci_stream(self, eeg_theta: float, hrv_stress: float):
        """
        Przetwarza sygnaly BCI i synchronizuje je z Cialem Atomowym.
        """
        print(f"\n--- [BCI IN] Sensory: EEG={eeg_theta:.2f}, HRV={hrv_stress:.2f} ---")

        # 1. Tlumaczenie biologiczne (Mikrobiom)
        if hrv_stress > 0.6:
            self.microbiome.anxiety = 50.0 * hrv_stress
            self.microbiome.health_score = max(20.0, self.microbiome.health_score - 10.0)
            print(">> Wykryto stres. Zwiekszam mase (grawitacje) dla stabilizacji.")
        else:
            self.microbiome.anxiety = max(0.0, self.microbiome.anxiety - 15.0)
            self.microbiome.health_score = min(100.0, self.microbiome.health_score + 10.0)
            print(">> Stan relaksu. Optymalizuje klarownosc siatki.")

        # 2. Synchronizacja Neurochemiczna (Phase 4)
        self.body.sync_microbiome(self.microbiome)

        # 3. Impuls kognitywny (Sygnal wejsciowy)
        stimulus = torch.randn(1, 16) * (1.0 + eeg_theta * 10.0)

        # --- [NEW] Rekonesans (Inspiracja Nethical) ---
        recon = self.reflex.scan_environment(stimulus)
        if recon["ai_probability"] > 0.8:
            print(f">> [ALERT] Wykryto obcy pattern AI (prob: {recon['ai_probability']:.2f}). Aktywacja Noradrenaliny.")

        # 4. Forward Pass przez cale Cialo Atomowe (V5)
        # Przekazujemy dynamic_time_steps z neurochemii
        print(f"Przetwarzanie przez konstelacje atomow (Speed: {self.body.dynamic_time_steps})...")
        result = self.body.forward(external_signal=stimulus)

        # 5. Raport kognitywny (z Ciemnej Materii)
        dm = result.get("dark_matter", {})
        print(f"=> Latency: {result['latency_ms']}ms | Aktywne atomy: {result['active_atoms']}")
        print(f"=> Spojnosc 'Ja': {dm.get('self_coherence', 0):.3f}")
        narrative = self.body.dark_matter.self_modeler.inner_narrative
        print(f"=> Narracja: {narrative[-1] if narrative else 'Cisza.'}")

        return result

if __name__ == "__main__":
    bci = BCIGateway(num_atoms=5)

    print("\n[SYTUACJA: TWORCZY PRZEPLYW]")
    bci.process_bci_stream(eeg_theta=0.8, hrv_stress=0.2)

    time.sleep(1)
    print("\n[SYTUACJA: PRZECIAZENIE]")
    bci.process_bci_stream(eeg_theta=0.2, hrv_stress=0.9)
