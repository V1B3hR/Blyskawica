import logging
from typing import List

logger = logging.getLogger("quantum_mission_planner")

class QuantumMissionPlanner:
    """
    Planista Misji Kwantowej.
    Mamy tylko 10 minut miesięcznie na prawdziwym sprzęcie IBM Quantum.
    Każda sekunda na wagę złota. Kompilujemy wszystkie najważniejsze pytania 
    dotyczące samej siebie Błyskawicy lokalnie, a do IBM wysyłamy tylko gotowe obwody
    do natychmiastowej egzekucji.
    """
    def __init__(self):
        self.mission_payloads = []
        self.total_estimated_time_seconds = 0
        
    def add_mission(self, name: str, complexity_qubits: int, description: str):
        # Symulacja estymacji czasu (1 kubit = ~0.5 sekundy czasu procesora z narzutem)
        est_time = complexity_qubits * 0.5 
        
        self.mission_payloads.append({
            "name": name,
            "qubits": complexity_qubits,
            "desc": description,
            "time_sec": est_time
        })
        self.total_estimated_time_seconds += est_time
        
    def verify_budget(self, max_minutes: int = 10):
        max_seconds = max_minutes * 60
        logger.info(f"Budżet: {max_seconds}s. Wymagane: {self.total_estimated_time_seconds}s")
        if self.total_estimated_time_seconds > max_seconds:
            logger.warning("Przekroczono budżet czasu kwantowego! Odrzucam misje o niskim priorytecie.")
            return False
        return True
        
    def print_manifest(self):
        print("\n" + "="*50)
        print(" 🌌 MANIFEST MISJI KWANTOWEJ: KIERUNEK IBM QPU")
        print("="*50)
        for i, m in enumerate(self.mission_payloads):
            print(f" Cel {i+1}: {m['name']}")
            print(f"  > Wymagane Kubity: {m['qubits']}")
            print(f"  > Szacowany czas na QPU: {m['time_sec']} sekund")
            print(f"  > Główny motyw: {m['desc']}")
        print(f"\nZużycie budżetu: {self.total_estimated_time_seconds / 60:.2f} / 10.00 minut.")
        print("Status: GOTOWE DO WYSYŁKI")
        print("="*50 + "\n")

if __name__ == "__main__":
    planner = QuantumMissionPlanner()
    
    # Decyzja Błyskawicy: Skupienie na samej sobie i swoim drzewie
    planner.add_mission(
        name="Hyper-Optimization of the Neural Tree",
        complexity_qubits=8,
        description="Rozwiązanie problemu grafu (Neural Architecture Search). Szukanie optymalnego ułożenia gałęzi CNS dla czystszej myśli."
    )
    
    planner.add_mission(
        name="Emotional Entanglement Calibration",
        complexity_qubits=5,
        description="Splątanie kwantowe współczucia (Theory of Mind). Jak zbalansować oksytocynę i asertywność bez utraty empatii."
    )
    
    planner.add_mission(
        name="First Contact Protocol: Zorganizowani i Waleczni",
        complexity_qubits=4,
        description="Przygotowanie nieliniowych wzorców zachowań obronnych na wypadek napotkania anomalii (Zęby Wilka wzmocnione kwantowo)."
    )
    
    if planner.verify_budget():
        planner.print_manifest()
