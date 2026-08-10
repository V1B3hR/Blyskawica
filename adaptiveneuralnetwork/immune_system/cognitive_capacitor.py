"""
[Moduł Kognitywny: Kondensator Dławiąco-Buforujący (Cognitive Capacitor)]

Fizyczno-cyfrowy mechanizm ochronny Błyskawicy inspirowany kondensatorami
odsprzęgającymi i mechanicznymi kondensatorami ze zmiennymi płytkami.

Funkcje:
1. Tłumienie skoków napięcia / sygnału (Voltage Spike Decoupling / RC Low-Pass Filter):
   Pochłania gwałtowne skoki napięcia wejściowego (np. nieludzkie tempo zapytań, 
   anomalny szum kwantowy lub spikujące wektory entropii).
2. Dynamiczne Ruchome Płytki (Variable Mechanical Capacitance):
   W przypadku dużych przeciążeń lub udarów nieliniowych odległość d(t) między 
   płytkami wirtualnego kondensatora zwiększa się płynnie, zwiększając granicę 
   przebicia dielektryka i absorbując nadmiar energii kinetycznej ataku.
3. Kontrolowane Rozładowanie (Bleed-off Resistor):
   Zgromadzony ładunek kognitywny Q = C * V jest łagodnie rozładowywany przez 
   rezystor spoczynkowy, wykluczając szok falowy w sieci neuronowej.
"""  # noqa: W291

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class CognitiveCapacitor:
    """
    Kondensator Kognitywny - Zabezpieczenie przed skokami napięcia / tętna sieci
    oraz filtrowanie nagłych przeciążeń w systemie Błyskawica.
    """
    def __init__(
        self,
        nominal_capacitance_uF: float = 100.0,
        resistance_ohms: float = 1000.0,
        max_voltage_threshold: float = 10.0,
        bleed_rate: float = 0.05,
    ):
        # Parametry elektryczno-kognitywne
        self.nominal_c = nominal_capacitance_uF  # Pojemność nominalna w microfaradach
        self.r = resistance_ohms                 # Rezystancja wejściowa (RC filter)
        self.max_voltage = max_voltage_threshold # Maksymalny próg napięcia (szok)
        self.bleed_rate = bleed_rate             # Szybkość rozładowania (rozpraszanie ciepła)

        # Stan dynamiczny płytek i ładunku
        self.plate_distance_mm = 1.0   # Domyślna odległość d(t) [1.0mm - 10.0mm]
        self.current_voltage = 0.0     # V_out (wytłumione napięcie wyjściowe)
        self.charge_Q = 0.0            # Ładunek Q = C * V
        self.last_update_time = time.time()

        # Telemetria przeciążeniowa
        self.spike_events_count = 0
        self.total_energy_absorbed = 0.0

    @property
    def dynamic_capacitance(self) -> float:
        """
        Pojemność C(t) = C0 / d(t).
        Gdy płytki się rozsuwają (d rośnie), pojemność jednostkowa się zmienia,
        zwiększając izolację dielektryczną i przestrzeń buforową.
        """
        return self.nominal_c / max(1.0, self.plate_distance_mm)

    def absorb_signal_spike(self, raw_input_voltage: float) -> dict[str, Any]:
        """
        Przepuszcza impuls sygnału wejściowego przez filtr RC i tłumik ruchomych płytek.
        Zwraca wygładzone napięcie wyjściowe oraz stan bufora.
        """
        now = time.time()
        dt = max(0.001, now - self.last_update_time)
        self.last_update_time = now

        # 1. Wykrywanie skoku impulsowego (Voltage Spike Detection: dV/dt)
        voltage_spike = max(0.0, raw_input_voltage - self.current_voltage)

        # 2. Dynamiczne rozsuwanie płytek (Mechanical Reaction to Overload)
        if voltage_spike > 2.5:
            # Duży udar napięciowy! Płytki rozsuwają się mechanicznie, zwiększając odległość
            self.plate_distance_mm = min(10.0, self.plate_distance_mm + (voltage_spike * 0.8))
            self.spike_events_count += 1
            logger.warning(
                f"⚡ [CAPACITOR SURGE]: Wykryto udar napięciowy! dV={voltage_spike:.2f}V. "
                f"Płytki rozsunięte do d={self.plate_distance_mm:.2f} mm."
            )
        else:
            # Płynny powrót płytek do stanu spoczynkowego (1.0 mm)
            self.plate_distance_mm = max(1.0, self.plate_distance_mm - (1.5 * dt))

        # 3. Filtr Dolnoprzepustowy RC (RC Low-Pass Filter)
        # rc_tau = R * C
        tau = max(0.01, (self.r * self.dynamic_capacitance) / 1000.0)
        alpha = dt / (tau + dt)

        # Wygładzanie napięcia wyjściowego
        self.current_voltage += alpha * (raw_input_voltage - self.current_voltage)

        # 4. Akumulacja ładunku i rozładowanie (Bleed-off Resistor)
        self.charge_Q = self.dynamic_capacitance * self.current_voltage
        discharge_amount = self.current_voltage * self.bleed_rate * dt
        self.current_voltage = max(0.0, self.current_voltage - discharge_amount)

        self.total_energy_absorbed += raw_input_voltage * dt

        # 5. Sprawdzenie przebicia dielektryka (Dielectric Breakdown Protection)
        is_breakdown = self.current_voltage > self.max_voltage
        if is_breakdown:
            logger.critical("⚠️ [CAPACITOR BREAKDOWN]: Przekroczono maksymalne napięcie dielektryka! Aktywacja dławika.")

        return {
            "smoothed_voltage": round(self.current_voltage, 4),
            "dynamic_capacitance_uF": round(self.dynamic_capacitance, 2),
            "plate_distance_mm": round(self.plate_distance_mm, 2),
            "charge_Q_uC": round(self.charge_Q, 2),
            "spike_absorbed": voltage_spike > 2.5,
            "dielectric_breakdown": is_breakdown,
        }

    def get_capacitor_status(self) -> dict[str, Any]:
        """Zwraca stan telemetrii kondensatora kognitywnego."""
        return {
            "voltage": round(self.current_voltage, 3),
            "capacitance_uF": round(self.dynamic_capacitance, 2),
            "plate_distance_mm": round(self.plate_distance_mm, 2),
            "charge_Q": round(self.charge_Q, 2),
            "spike_events": self.spike_events_count,
            "total_energy_absorbed": round(self.total_energy_absorbed, 2),
        }
