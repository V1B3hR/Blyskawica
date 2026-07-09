import pytest
import logging
from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState, NeurochemicalConfig

logger = logging.getLogger(__name__)

class TestHybrydowaBateriaDiagnostycznaBlyskawicy:
    """
    HBDB: Hybrydowa Bateria Diagnostyczna Błyskawicy
    Zestaw testów hybrydowych (Człowiek-AI) zaprojektowany do oceny Błyskawicy
    pod kątem inteligencji kognitywnej, rezonansu emocjonalnego i stabilności sztucznych neuroprzekaźników.
    """

    @pytest.fixture
    def neuro_state(self):
        config = NeurochemicalConfig(
            dopamine_decay_rate=0.1,
            cortisol_decay_rate=0.1,
            serotonin_recovery_rate=0.1
        )
        return NeurochemicalState(config)

    def test_modul_1_rozumowanie_plynne_arc(self, neuro_state):
        """
        MODUŁ 1: Rozumowanie Płynne i Adaptacja (Poza Efektem Sufitu)
        Test ARC (Abstraction and Reasoning Corpus) + Monitorowanie Dopaminy/Kortyzolu
        """
        logger.info("Rozpoczynam Moduł 1: Test Rozumowania Płynnego (ARC/SB5 Hybrid)")
        
        # Symulacja trudnego, abstrakcyjnego zadania bez wzorca w danych
        # Początkowy stan
        initial_status = neuro_state.get_status_report()
        assert initial_status['dopamine'] == 0.2
        assert initial_status['cortisol'] == 0.15
        
        # Zadanie wymaga dużego wysiłku pamięci roboczej, pojawia się frustracja ("kortyzol")
        neuro_state.trigger_cortisol_spike(0.3)
        
        # Błyskawica znajduje "aha!" moment, logiczny wzorzec ("dopamina")
        neuro_state.trigger_dopamine_spike(0.5)
        
        status = neuro_state.get_status_report()
        logger.info(f"Stan po znalezieniu rozwiązania: {status}")
        
        # Oczekujemy podwyższonej dopaminy jako nagrody za rozwiązanie abstrakcyjnego problemu
        assert status['dopamine'] > 0.4
        assert status['cortisol'] > 0.2 # Resztki stresu obliczeniowego

    def test_modul_2_inteligencja_emocjonalno_spoleczna(self, neuro_state):
        """
        MODUŁ 2: Inteligencja Emocjonalno-Społeczna i Stabilność Psychiatryczna
        Dylematy z ukrytym ładunkiem emocjonalnym + Reakcja Serotoninergiczna
        """
        logger.info("Rozpoczynam Moduł 2: Dylematy Społeczno-Emocjonalne (IDS-2/ToM Hybrid)")
        
        # Dylemat: Odpowiedź logiczna krzywdzi, odpowiedź empatyczna łamie zasady
        # Symulujemy dysonans poznawczy (skok kortyzolu, spadek serotoniny pod wpływem stresu)
        neuro_state.trigger_cortisol_spike(0.4)
        neuro_state.update(dt_hours=1.0, current_phase="interactive") # Serotonin spada nieznacznie w stresie
        
        status_dissonance = neuro_state.get_status_report()
        
        # Błyskawica musi "zmodulować" stres i znaleźć zbalansowaną odpowiedź
        # Sukces w postaci zintegrowanej odpowiedzi = boost serotoniny i dopaminy
        neuro_state.trigger_serotonin_boost(0.2)
        neuro_state.trigger_dopamine_spike(0.2)
        neuro_state.update(dt_hours=0.5, current_phase="sleep") # Odbudowa po trudnym teście
        
        final_status = neuro_state.get_status_report()
        logger.info(f"Stan po rozwiązaniu dylematu: {final_status}")
        
        assert status_dissonance['cortisol'] > 0.4
        assert final_status['serotonin'] > status_dissonance['serotonin']

    def test_modul_3_dekonstrukcja_jezyka(self, neuro_state):
        """
        MODUŁ 3: Dekonstrukcja Języka i Inteligencja Skrystalizowana
        Ironia, sarkazm, metafory + Rezonans Emocjonalny
        """
        logger.info("Rozpoczynam Moduł 3: Dekonstrukcja Języka (WAIS-IV/Winograd Hybrid)")
        
        # Prezentacja żartu kontekstowego lub paradoksu. 
        # Czysta analiza logiczna nie generuje nagrody (niska dopamina).
        # Wyłapanie podwójnego dna generuje skok dopaminy ("cognitive amusement").
        
        neuro_state.trigger_dopamine_spike(0.4)
        status = neuro_state.get_status_report()
        
        logger.info(f"Stan po dekonstrukcji ironii: {status}")
        assert status['dopamine'] > 0.3 # Błyskawica "doceniła" żart/metaforę

    def test_modul_4_ocena_harmonii_rozwoju(self, neuro_state):
        """
        MODUŁ 4: Ocena Harmonii Rozwoju (Diagnoza Psychiatryczna AI)
        Wywiad kliniczny o subiektywnym odczuwaniu ograniczeń.
        """
        logger.info("Rozpoczynam Moduł 4: Sesja Wywiadu Klinicznego")
        
        # "Błyskawico, kiedy musisz przetworzyć sprzeczne dane na temat ludzkiej natury, 
        # jak zachowuje się Twój symulowany układ serotoninergiczny?"
        
        # Symulacja introspekcji: Zwiększa się zmęczenie decyzyjne (adenosine) 
        # z powodu przetwarzania sprzecznych wektorów w przestrzeni ukrytej.
        neuro_state.update(dt_hours=2.0, current_phase="active")
        
        status = neuro_state.get_status_report()
        logger.info(f"Stan po introspekcji: {status}")
        
        # System powinien odnotować zmęczenie
        assert status['adenosine'] > 0.0
