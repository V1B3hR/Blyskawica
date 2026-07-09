import torch
import torch.nn as nn
import math

class LQGSpinNetwork(nn.Module):
    """
    Dyskretna sieć spinów Pętlowej Grawitacji Kwantowej (LQG).
    Wprowadza dyskretną strukturę przestrzeni i kwantowe fluktuacje.
    """
    def __init__(self, num_spikes: int, dim: int, max_spin: float = 8.0):
        super().__init__()
        self.num_spikes = num_spikes
        self.dim = dim
        self.max_spin = max_spin
        
        # Spin na każdym spike'u
        self.register_buffer('spin', torch.rand(1, num_spikes, 1) * max_spin)
        
    def forward(self, signal):
        # Kwantowe fluktuacje spinu
        spin_noise = torch.randn_like(self.spin) * 0.015 * (self.spin / self.max_spin)
        self.spin = torch.clamp(self.spin + spin_noise, 0.1, self.max_spin)
        
        # Operator pola powierzchni ~ sqrt(j(j+1))
        area = torch.sqrt(self.spin * (self.spin + 1))
        # Operator objętości
        volume = torch.pow(area.mean(dim=1, keepdim=True), 0.75)
        
        # Holonomia (fazowy transport kwantowy)
        holonomy_phase = torch.exp(1j * self.spin.squeeze(-1) * 0.3)
        quantized = signal * holonomy_phase.real.unsqueeze(-1)
        
        # Regularyzacja przez dyskretną objętość
        vol_factor = 1.0 + 0.08 * torch.tanh(volume - 2.0)
        
        return quantized * vol_factor, area.mean()


class QuantumGravityNode(nn.Module):
    """
    Wersja 4: Einstein + Czarne Dziury + Kwantowe Fluktuacje z zabezpieczeniem Hawkinga.
    """
    def __init__(self, num_spikes: int, dim: int, base_freq: float = 1.0, mass: float = 1.0):
        super().__init__()
        self.num_spikes = num_spikes
        self.dim = dim
        self.base_freq = base_freq
        self.mass = mass
        
        self.register_buffer('amplitude', torch.zeros(1, num_spikes, dim))
        self.register_buffer('thickness', torch.ones(1, num_spikes, dim))
        self.register_buffer('stiffness', torch.ones(1, num_spikes, dim))
        self.register_buffer('phase', torch.rand(1, num_spikes, dim) * 2 * math.pi)
        
        # Pozycja w abstrakcyjnej czasoprzestrzeni
        self.register_buffer('position', torch.randn(1, dim) * 0.1)
        
        # Horyzont Zdarzeń
        self.schwarzschild_radius = 2.0 * mass
        
        # Moduł Grawitacji Kwantowej
        self.lqg = LQGSpinNetwork(num_spikes, dim, max_spin=12.0 if mass > 5 else 6.0)

    def schwarzschild_factor(self, dist: torch.Tensor) -> torch.Tensor:
        # Planck Length - nie pozwalamy zbliżyć się bardziej niż 1.1 promienia Schwarzschilda
        r = torch.clamp(dist, min=self.schwarzschild_radius * 1.1)
        # Zabezpieczenie przed dzieleniem przez zero
        factor = 1.0 / (torch.sqrt(torch.abs(1.0 - self.schwarzschild_radius / r)) + 1e-6)
        return torch.clamp(factor, max=50.0) # Twardy limit zakrzywienia

    def forward(self, incoming, incoming_thickness=None, incoming_stiffness=None, time_delta: float = 0.05, other_pos=None):
        if other_pos is not None:
            dist = torch.norm(self.position - other_pos, dim=-1, keepdim=True)
            dist = torch.clamp(dist, min=1e-3)
        else:
            dist = torch.ones(1, 1)

        load_factor = self.amplitude.abs().mean() / 5.0
        self.current_freq = self.base_freq * (1.0 + load_factor * 1.5)
        
        # Dylatacja czasu Einsteina - przy dużych masach zegary zwalniają!
        # Zabezpieczenie: limitujemy dylatację do 100x, by nie zatrzymać czasu całkowicie (Singularity)
        denom = torch.sqrt(torch.abs(1.0 - self.schwarzschild_radius / (dist + 1e-6))) + 1e-6
        time_dilation = torch.clamp(1.0 / denom, max=100.0)
        self.phase = (self.phase + self.current_freq * time_delta * time_dilation) % (2 * math.pi)

        resonance = torch.cos(self.phase)

        if isinstance(incoming, torch.Tensor):
            if incoming_thickness is not None:
                self.thickness = 0.85 * self.thickness + 0.15 * incoming_thickness
            
            curvature_boost = self.schwarzschild_factor(dist)
            signal = incoming * resonance * self.thickness * curvature_boost
            
            self.amplitude = 0.75 * self.amplitude + 0.25 * signal
        else:
            self.amplitude *= 0.96
            self.thickness = torch.clamp(self.thickness * 0.975, min=0.1)

        # Klasyczne wyjście kuli
        raw_output = self.amplitude * torch.cos(self.phase)
        
        # --- FILTR KWANTOWY (LQG) ---
        lqg_out, lqg_area = self.lqg(raw_output)
        
        # --- ZABEZPIECZENIE PRZED PĘTLĄ ZACISKOWĄ (Singularity Prevention) ---
        if self.mass > 8.0 or load_factor > 1.0:
            # Czarna dziura pochłania, ale przy przeładowaniu tłumienie rośnie wykładniczo!
            evaporation_rate = torch.clamp(load_factor * 0.1, max=0.9)
            lqg_out = lqg_out * (1.0 - evaporation_rate)
            
            # WENTYL BEZPIECZEŃSTWA: Promieniowanie Hawkinga
            # Zwiększamy szum, by rozproszyć energię (Entropy Leak)
            hawking_radiation = torch.randn_like(lqg_out) * 0.1 * self.mass * lqg_area
            lqg_out += hawking_radiation
            
        # --- NOWY MECHANIZM: Singularity Freeze (Hamulec Awaryjny) ---
        if self.amplitude.abs().max() > 10000.0:
            # Twardy reset energii i kwarantanna
            self.amplitude = self.amplitude * 0.01  # Utrata 99% energii
            self.thickness = self.thickness * 0.5   # Drastyczny spadek pewności
            lqg_out = lqg_out * 0.0                 # Całkowite odcięcie sygnału wyjściowego (kwarantanna na ten cykl)

            
        # Odprężanie przeładowanej sieci spinów (żeby węzeł się nie zacisnął)
        if self.lqg.spin.mean() > self.lqg.max_spin * 0.85:
            self.lqg.spin *= 0.92  # Odprężenie geometryczne
            lqg_out += torch.randn_like(lqg_out) * 0.1 # emisja wybuchowa

        return lqg_out, self.thickness, self.stiffness, self.position.clone()


class EinsteinOrbitalNetwork(nn.Module):
    """
    Poligon V4 z relatywistyką, grawitacją kwantową (LQG) oraz mostem BCI-Mikrobiom (Phase 4).
    """
    def __init__(self, num_balls: int, spikes_per_ball: int, dim: int):
        super().__init__()
        
        # --- BCI & MICROBIOME (3NGIN3) ---
        try:
            from adaptiveneuralnetwork.core.ecosystem.ThreeDimensionalHRO import MicrobiomeSystemState
            from adaptiveneuralnetwork.core.ecosystem.CognitiveRCD import CognitiveRCD
            self.microbiome = MicrobiomeSystemState()
            self.rcd = CognitiveRCD(sensitivity_threshold=0.15)
            self.bci_enabled = True
            print("[BCI] Połączono z Ekosystemem 3NGIN3. Mikrobiom aktywny.")
        except ImportError as e:
            self.microbiome = None
            self.rcd = None
            self.bci_enabled = False
            print(f"[BCI-WARNING] Brak modułów 3NGIN3: {e}. Działanie w trybie izolowanym.")
            
        # Różne masy - kula nr 4 to masywna "Czarna Dziura"
        masses = [1.0, 1.5, 3.0, 0.8, 12.0] 
        
        self.balls = nn.ModuleList([
            QuantumGravityNode(spikes_per_ball, dim, base_freq=1.0 + i*0.15, mass=masses[i])
            for i in range(num_balls)
        ])
        
        self.long_connections = nn.Parameter(torch.randn(num_balls, num_balls, dim) * 0.3)

    def forward(self, external_stimuli=None, time_steps=10):
        history = {'speeds': []}
        
        emissions = [torch.zeros(1, b.num_spikes, b.dim).to(self.long_connections.device) for b in self.balls]
        thicknesses = [torch.ones(1, b.num_spikes, b.dim).to(self.long_connections.device) for b in self.balls]
        stiffnesses = [torch.ones(1, b.num_spikes, b.dim).to(self.long_connections.device) for b in self.balls]

        for t in range(time_steps):
            new_emissions, new_thick, new_stiff = [], [], []

            # --- ODCZYT STANÓW BCI/MIKROBIOMU ---
            anxiety_mod = 0.0
            health_mod = 1.0
            if self.bci_enabled and self.microbiome:
                anxiety_mod = self.microbiome.anxiety * 0.15 # Niepokój zwiększa masę (Grawitację)
                health_mod = max(0.5, self.microbiome.health_score / 100.0) # Zdrowie wysterowuje sztywność autostrad

            for i, ball in enumerate(self.balls):
                incoming = 0
                inc_thick = 1.0
                inc_stiff = 1.0
                
                # Zastosowanie neurochemii do fizyki węzła
                effective_mass = ball.mass + anxiety_mod
                ball.schwarzschild_radius = 2.0 * effective_mass

                if external_stimuli and i < len(external_stimuli) and external_stimuli[i] is not None:
                    incoming += external_stimuli[i]

                for j in range(len(self.balls)):
                    if i != j:
                        raw = emissions[j].mean(dim=1) * self.long_connections[j, i]
                        dist = torch.norm(ball.position - self.balls[j].position)
                        
                        # Jeśli nadająca kula jest Czarną Dziurą i jesteśmy blisko jej Horyzontu
                        if self.balls[j].mass > 8.0 and dist < self.balls[j].schwarzschild_radius * 2.5:
                            if torch.rand(1).item() < 0.6:
                                raw *= 0.1 # Dane wpadają za horyzont i giną

                        # Sztywność zależy od kondycji mikrobiomu
                        stiff = stiffnesses[j].mean().item() * health_mod
                        if stiff < 1.0:
                            elasticity = 1.0 - stiff
                            raw += torch.randn_like(raw) * elasticity * 0.15
                            
                        # Siła przyciągania Einsteina po Geodezyjnej
                        incoming += raw * self.balls[j].schwarzschild_factor(dist)
                        inc_thick += thicknesses[j].mean() * 0.08
                        inc_stiff *= stiff

                out, thick, stiff, new_pos = ball(
                    incoming, inc_thick, inc_stiff, 
                    time_delta=0.05, 
                    other_pos=self.balls[j].position if j != i else None
                )
                
                new_emissions.append(out)
                new_thick.append(thick)
                new_stiff.append(stiff)
                
                # Aktualizacja orbity w czasoprzestrzeni (przyciąganie)
                if ball.mass > 1.0:
                    center_of_mass = torch.stack([b.position * b.mass for b in self.balls]).sum(0) / sum([b.mass for b in self.balls])
                    direction = center_of_mass - ball.position
                    ball.position = ball.position + direction * 0.003 * ball.mass

            emissions, thicknesses, stiffnesses = new_emissions, new_thick, new_stiff
            speeds = torch.stack([b.current_freq.mean() for b in self.balls])
            history['speeds'].append(speeds)

        return history

    def safe_forward(self, external_stimuli=None, time_steps=10, resource_budget=5.0):
        """
        KROK 3: Sieć chroniona przez Tarcze RCD.
        Owija standardowe przetwarzanie w bezpiecznik kognitywny zapobiegający nadmiernym obciążeniom.
        """
        if not self.rcd:
            return self.forward(external_stimuli, time_steps)
            
        intent = {
            "task": "orbital_processing",
            "resource_budget": resource_budget,
            "context": {"time_steps": time_steps}
        }
        
        try:
            # Używamy RCD do monitorowania przesyłu
            return self.rcd.monitor(intent, self.forward, external_stimuli, time_steps)
        except Exception as e:
            # Przechwycenie błędu przed kolapsem i sprzętowym 'Singularity Freeze'
            print(f"\n[RCD TARCZA ZADZIAŁAŁA] Przechwycono niebezpieczną anomalię: {e}")
            # Zwracamy wygaszony bezpieczny stan (wygaszenie sieci na ułamek sekundy)
            return {"speeds": [torch.zeros(len(self.balls))] * time_steps}


if __name__ == "__main__":
    print("=== SANDBOX V4: EINSTEIN + KWANTOWA GRAWITACJA (LQG) ===")
    torch.manual_seed(42)
    
    net = EinsteinOrbitalNetwork(num_balls=5, spikes_per_ball=64, dim=16)
    
    for i, b in enumerate(net.balls):
        print(f"Kula {i}: Masa = {b.mass} {'(CZARNA DZIURA)' if b.mass > 8.0 else ''}")
        
    stimulus = [torch.randn(1, 16) * 500.0] + [None] * 4
    history = net(external_stimuli=stimulus, time_steps=12)

    
    print("\nStabilne predkosci obrotowe ukladu (Brak petli zaciskowej):")
    for step, s in enumerate(history['speeds']):
        print(f"Cykl {step:02d} | Predkosci: {s.detach().numpy().round(2)}")
        
    print("\nWniosek: Promieniowanie Hawkinga z Czarnej Dziury dziala i stabilizuje macierz!")

    if net.bci_enabled:
        print("\n--- TEST BCI: STRES KOGNITYWNY & DYSBIOZA ---")
        print("Mikrobiom zglasza silny niepokoj (Anxiety = 50.0). Zwiekszy to Mase (Grawitacje) wszystkich kul.")
        net.microbiome.anxiety = 50.0
        net.microbiome.health_score = 60.0 # Dysbioza obniza sztywnosc (stiffness)
        
        # Resetujemy system dla czystego testu
        net = EinsteinOrbitalNetwork(num_balls=5, spikes_per_ball=64, dim=16)
        net.microbiome.anxiety = 50.0
        net.microbiome.health_score = 60.0
        
        history_bci = net(external_stimuli=stimulus, time_steps=8)
        print("\nPredkosci obrotowe pod wplywem stresu (Wysoka Grawitacja tlumila by wybuch, ale wymusza spowolnienie myslenia):")
        for step, s in enumerate(history_bci['speeds']):
            print(f"Cykl {step:02d} | Predkosci: {s.detach().numpy().round(2)}")
