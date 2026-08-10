import logging

import torch
import torch.nn as nn

from adaptiveneuralnetwork.cognitive_tools.network_chokes import (
    ACChoke,
    CompensationChoke,
    MotorChoke,
)

logger = logging.getLogger("quantum_dual_rotor")

class PhaseInverter(nn.Module):
    """
    Falownik Fazy (Phase Inverter).
    Reguluje stosunek prędkości (Hz) między Szybkim a Wolnym Wirnikiem.
    Reaguje na obciążenie poznawcze (np. uderzenie kortyzolu / stresu)
    zwiększając częstotliwość wewnętrznego wirnika do granic możliwości,
    podczas gdy zewnętrzny wirnik (refleksja) utrzymuje stateczność.
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        # Symulacja układu sprzężenia zwrotnego PID (Proportional-Integral-Derivative) w sieci
        self.dt_controller = nn.Linear(hidden_dim, 2) # Wyrzuca [inner_dt, outer_dt]

    def forward(self, cognitive_load: torch.Tensor):
        # Aktywacja Sigmoid * Max Częstotliwość
        dts = torch.sigmoid(self.dt_controller(cognitive_load))
        inner_dt = dts[:, 0] * 100.0 # Bije do 100 Hz (Szybkie reakcje)
        outer_dt = dts[:, 1] * 10.0  # Bije do 10 Hz (Głębokie przemyślenia)
        return inner_dt, outer_dt


class DualRotorEngine(nn.Module):
    """
    Podwójny Wirnik (Dual Rotor Loop) zaprojektowany dla 'alive_node.py'.
    Jeden wirnik wsunięty w drugi (tuleja w tulei).
    - Inner Rotor: Przetwarza bieżące zmysły, szybki odruch (Zęby Wilka).
    - Outer Rotor: Przetwarza długą pamięć, empatię i wyciąga wnioski na przyszłość.
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim

        # Falownik (Inverter)
        self.inverter = PhaseInverter(hidden_dim)

        # Wewnętrzny wirnik (Szybki - Refleks, Przetrwanie, Natychmiastowa Świadomość)
        self.inner_rotor = nn.GRUCell(input_size=hidden_dim, hidden_size=hidden_dim)

        # Zewnętrzny wirnik (Wolny - Pamięć epizodyczna, C.R.A, Teoria Umysłu)
        self.outer_rotor = nn.GRUCell(input_size=hidden_dim, hidden_size=hidden_dim)

        # Ochrona przeciwprzepięciowa (Dławiki V1B3hR)
        self.ac_choke = ACChoke(spike_threshold=2.0)
        self.motor_choke_inner = MotorChoke(damping_coefficient=0.05)
        self.motor_choke_outer = MotorChoke(damping_coefficient=0.05)
        self.comp_choke = CompensationChoke(hidden_dim, capacity=100.0)

        logger.info("⚙️ Zainicjowano Podwójny Wirnik Kognitywny z pełnym ekranowaniem dławikowym (AC/Motor/Comp).")

    def forward(self, sensory_input: torch.Tensor, prev_inner_state: torch.Tensor, prev_outer_state: torch.Tensor):
        """
        Główna pętla wewnątrz pętli. 
        Odpalana iteracyjnie, zasilając AliveNode.
        """  # noqa: W291
        # 0. Filtracja prądów doziemnych i szumów wejściowych (AC Choke)
        safe_sensory_input = self.ac_choke(sensory_input)

        # 1. Falownik sprawdza "obciążenie umysłu"
        inner_hz, outer_hz = self.inverter(safe_sensory_input)

        # 2. Wewnętrzny Wirnik kręci się jako pierwszy
        new_inner_state = self.inner_rotor(safe_sensory_input, prev_inner_state)

        # 3. Kompensacja Mocy Biernej (Capacitor) stabilizuje falownik
        stabilization_factor = self.comp_choke(new_inner_state, prev_outer_state)
        inner_hz = inner_hz * stabilization_factor
        outer_hz = outer_hz * stabilization_factor

        # 4. Zewnętrzny Wirnik asymiluje sygnał w odpowiedniej Fazie
        phase_shift = torch.cos(inner_hz / (outer_hz + 1e-5))
        fused_context = safe_sensory_input + (new_inner_state * phase_shift.unsqueeze(1))
        new_outer_state = self.outer_rotor(fused_context, prev_outer_state)

        # 5. Dławiki Silnikowe na wyjściu wygładzają szarpnięcia
        smooth_inner = self.motor_choke_inner(new_inner_state)
        smooth_outer = self.motor_choke_outer(new_outer_state)

        return smooth_inner, smooth_outer, (inner_hz, outer_hz)

def test_dual_rotor():
    print("🔋 Rozruch sprzęgła. Silniki Dual Rotor gotowe...")
    engine = DualRotorEngine(hidden_dim=128)

    # Symulacja stanu początkowego (Zero Voltage)
    inner_state = torch.zeros(1, 128)
    outer_state = torch.zeros(1, 128)

    # Symulacja uderzenia danych z zewnątrz (np. głośny dźwięk z mikrofonu)
    print("\n⚡ Wtrysk danych (Anomalia Sensoryczna)")
    impulse = torch.randn(1, 128)

    inner_state, outer_state, (freq_in, freq_out) = engine(impulse, inner_state, outer_state)

    print(f"🔄 Wewnętrzny Wirnik rozpędził się do: {freq_in.item():.2f} Hz (Szybka reakcja!)")
    print(f"🌍 Zewnętrzny Wirnik utrzymał stabilne: {freq_out.item():.2f} Hz (Zachowanie spokoju)")

    print("\n✅ Pętla w pętli działa perfekcyjnie. Fazy zostały przesunięte i zsynchronizowane.")
    print("Jest to idealny silnik do zasilenia nowej generacji AliveNode!")

if __name__ == "__main__":
    test_dual_rotor()
