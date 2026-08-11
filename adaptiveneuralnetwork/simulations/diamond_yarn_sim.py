"""
[Poligon Doświadczalny: Diamond Yarn & MesoPhone]
Środowisko testowe dla fotonicznej logiki i zarządzania termicznego Błyskawicy.
Symuluje wysokie obciążenia kognitywne (generowanie ciepła) oraz zjawisko 
dekoherencji kwantowej (szum N0-N6 z QDataSet).
"""  # noqa: W291

import logging

logger = logging.getLogger("DiamondYarnSim")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DiamondYarnPoligon:
    def __init__(self):
        self.core_temperature = 0.0 # Względna jednostka ciepła (0.0 = idealne chłodzenie)
        self.logic_stability = 100.0 # % stabilności logiki fotonicznej
        self.noise_level = "N0" # Brak szumu kwantowego na start

        logger.info("[INIT] Poligon Diamond Yarn aktywowany. Czekam na obciążenie.")

    def apply_cognitive_load(self, intensity: int):
        """
        Symuluje uderzenie ciężkich obliczeń i dylematów etycznych.
        Powoduje natychmiastowy wzrost temperatury (akustyczne fonony).
        """
        heat_generated = intensity * 1.5
        self.core_temperature += heat_generated
        logger.warning(f"[STRESS] Aplikacja obciążenia kognitywnego (Poziom: {intensity}). Generowanie ciepła: +{heat_generated}.")
        self._evaluate_stability()

    def simulate_mesophone_cooling(self):
        """
        Uruchamia mechanizm odprowadzania ciepła zainspirowany projektem MesoPhone.
        Wykorzystuje siatkę diamentowych nanonici do redukcji temperatury.
        """
        cooling_power = 25.0 # Zdolność chłodzenia systemu
        heat_removed = min(self.core_temperature, cooling_power)
        self.core_temperature -= heat_removed
        logger.info(f"[COOLING] Aktywacja MesoPhone. Odprowadzono ciepło: -{heat_removed:.2f}. Aktualna temp: {self.core_temperature:.2f}")

        # Chłodzenie przywraca stabilność
        if self.core_temperature < 10.0:
            self.logic_stability = min(100.0, self.logic_stability + 5.0)

    def inject_quantum_noise(self, profile: str):
        """
        Wprowadza szum w oparciu o modele z QDataSet (np. N1 - Pauli Z, N6 - gęstość spektralna).
        Degraduje stabilność logiki, jeśli rdzeń jest przegrzany.
        """
        self.noise_level = profile
        damage = 0.0

        if profile == "N1":
            damage = 2.0
        elif profile == "N6":
            damage = 15.0

        # Jeśli rdzeń jest gorący, szum kwantowy powoduje większe spustoszenie (dekoherencja termiczna)
        thermal_penalty = self.core_temperature * 0.1
        total_degradation = damage + thermal_penalty

        self.logic_stability -= total_degradation
        logger.error(f"[NOISE] Wprowadzono szum {profile}. Degradacja stabilności: -{total_degradation:.2f}%. Aktualna stabilność: {self.logic_stability:.2f}%")
        self._evaluate_stability()

    def _evaluate_stability(self):
        if self.logic_stability <= 0:
            self.logic_stability = 0
            logger.critical("[SYSTEM FAILURE] Krytyczna dekoherencja! Logika fotoniczna uległa zniszczeniu.")
        elif self.core_temperature > 50.0:
            logger.warning("[WARNING] Temperatura rdzenia krytycznie wysoka! Wymagane natychmiastowe chłodzenie MesoPhone.")

# Prosty test działania
if __name__ == "__main__":
    poligon = DiamondYarnPoligon()
    # 1. Zwykła praca
    poligon.apply_cognitive_load(10)
    poligon.simulate_mesophone_cooling()

    # 2. Atak szumem
    poligon.inject_quantum_noise("N1")

    # 3. Krytyczny stres
    poligon.apply_cognitive_load(40)
    poligon.inject_quantum_noise("N6")
    poligon.simulate_mesophone_cooling()
