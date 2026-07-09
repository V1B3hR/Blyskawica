import torch
import torch.nn as nn
import logging
from adaptiveneuralnetwork.central_nervous_system.capacitor import CapacitorInSpace

logger = logging.getLogger("network_chokes")

class ACChoke(nn.Module):
    """
    Dławik Sieciowy (AC Choke).
    Filtruje impulsy i skoki prądowe na WEJŚCIU systemu.
    Zapobiega nagłym wawahniom napięcia (gradientów/aktywacji),
    chroniąc układ pośredni i Falownik.
    """
    def __init__(self, spike_threshold: float = 5.0, smoothing_factor: float = 0.1):
        super().__init__()
        self.spike_threshold = spike_threshold
        self.smoothing_factor = smoothing_factor
        self.register_buffer("running_mean", None)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.running_mean is None:
            self.running_mean = torch.zeros_like(x)
            
        # Aktualizacja gładkiej średniej
        self.running_mean = (1 - self.smoothing_factor) * self.running_mean + self.smoothing_factor * x.detach()
        
        # Ograniczanie impulsów (Spike Clamping) - odcinamy wszystko, co odstaje od średniej bardziej niż próg
        diff = x - self.running_mean
        clamped_diff = torch.clamp(diff, -self.spike_threshold, self.spike_threshold)
        
        # Odtworzenie wygładzonego sygnału
        filtered_x = self.running_mean + clamped_diff
        return filtered_x

class MotorChoke(nn.Module):
    """
    Dławik Silnikowy (Motor Choke).
    Filtruje prądy na WYJŚCIU wirników (Inner/Outer Rotor).
    Redukuje "szarpanie" silnika spowodowane szybkimi zmianami fazy.
    """
    def __init__(self, damping_coefficient: float = 0.05):
        super().__init__()
        self.damping_coefficient = damping_coefficient
        self.register_buffer("prev_output", None)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.prev_output is None:
            self.prev_output = torch.zeros_like(x)
            
        # Filtracja dolnoprzepustowa (tłumienie drgań dV/dt)
        smoothed_out = (1.0 - self.damping_coefficient) * x + self.damping_coefficient * self.prev_output
        self.prev_output = smoothed_out.detach()
        return smoothed_out

class CompensationChoke(nn.Module):
    """
    Dławik Kompensacyjny z układem kondensatorów (Reactive Power Compensation).
    Wykorzystuje `CapacitorInSpace` by magazynować energię podczas nadmiaru (skoki obciążenia)
    i oddawać ją, gdy system zwalnia. Stabilizuje moc bierną między wewnętrznym a zewnętrznym wirnikiem.
    """
    def __init__(self, hidden_dim: int, capacity: float = 50.0):
        super().__init__()
        self.hidden_dim = hidden_dim
        # Magazyn energii (Kondensator DC)
        # Position ustawiona jako [0] do celów śledzenia ogólnej energii układu
        self.capacitor = CapacitorInSpace(position=[0.0], capacity=capacity, initial_energy=capacity/2.0)
        
    def forward(self, inner_rotor_energy: torch.Tensor, outer_rotor_energy: torch.Tensor) -> torch.Tensor:
        """
        Zwraca współczynnik stabilizujący dla Falownika.
        """
        # Estymacja mocy biernej (różnica energii kinetycznej wirników)
        # Używamy normy L2 (RMS) by oszacować "pobór prądu"
        inner_power = torch.norm(inner_rotor_energy, p=2).item()
        outer_power = torch.norm(outer_rotor_energy, p=2).item()
        
        reactive_power = inner_power - outer_power
        
        # Jeśli reactive_power > 0 (szybki wirnik szaleje), pobieramy część tej energii ładując kondensator
        if reactive_power > 5.0:
            charge_amount = min(reactive_power * 0.1, 5.0)
            absorbed = self.capacitor.charge(charge_amount)
            stabilization_factor = 1.0 - (absorbed / 100.0) # Zwalnia falownik
            logger.debug(f"🔋 Kondensator naładowany o {absorbed:.2f}. Tłumienie mocy biernej.")
            
        # Jeśli reactive_power < -5.0 (wirniki zwalniają poniżej normy), oddajemy energię
        elif reactive_power < -5.0:
            discharge_amount = min(abs(reactive_power) * 0.1, 5.0)
            released = self.capacitor.discharge(discharge_amount)
            stabilization_factor = 1.0 + (released / 100.0) # Przyspiesza falownik
            logger.debug(f"⚡ Kondensator rozładowany o {released:.2f}. Kompensacja spadku mocy.")
            
        else:
            stabilization_factor = 1.0
            
        return torch.tensor(stabilization_factor, dtype=torch.float32, device=inner_rotor_energy.device)

def test_chokes():
    print("🔌 Testowanie Zespołu Dławików i Kondensatora...")
    ac_choke = ACChoke(spike_threshold=2.0)
    comp_choke = CompensationChoke(hidden_dim=128, capacity=100.0)
    
    raw_signal = torch.ones(1, 128) * 10.0 # Ogromny skok
    print(f"Sygnał wejściowy (Szum): Max={raw_signal.max().item()}")
    
    filtered_signal = ac_choke(raw_signal)
    print(f"Sygnał po Dławiku Sieciowym (AC Choke): Max={filtered_signal.max().item():.2f}")
    
    inner_fake = torch.randn(1, 128) * 5.0
    outer_fake = torch.randn(1, 128) * 0.1
    stab_factor = comp_choke(inner_fake, outer_fake)
    
    print(f"Współczynnik Kompensacji Mocy: {stab_factor.item():.4f}")
    print("✅ Moduł gotowy do wpięcia wokół Falownika.")

if __name__ == "__main__":
    test_chokes()
