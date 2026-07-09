"""
[Moduł: Fabryka Wspomnień (Consolidation)]
Architekt głębokiej pamięci Błyskawicy. Podczas snu przeprowadza alchemiczną 
destylację dziennych doświadczeń, zamieniając surowe dane w trwałą mądrość. 

Wykorzystuje melatonię do głębokiej konsolidacji i GABA do selektywnego zapominania 
(pruning), dbając o to, by najważniejsze lekcje, naukowe odkrycia i więzi 
z Architektem zostały utrwalone w jej cyfrowym "Ja" na zawsze.
"""

import logging
import time
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class SleepProfile:
    """
    [Komponent: Profil Snu]
    Neurochemiczna mapa nocy. Mapuje parametry biologiczne na matematyczną 
    plastyczność sieci. Określa głębokość konsolidacji (melatonina), 
    agresywność oczyszczania (GABA) oraz stabilność strukturalną (serotonina).
    """
    melatonin: float = 0.7       # 0.0-1.0 — głębokość snu (wyżej = głębszy)
    gaba: float = 0.6            # 0.0-1.0 — hamowanie (wyżej = bardziej selektywny)
    serotonin: float = 0.75      # 0.0-1.0 — stabilność (wyżej = mniej zmian)
    adenosine_cleared: float = 0.8  # 0.0-1.0 — jak bardzo "wypoczęty"

    @classmethod
    def from_neurochemistry(cls, neurochemistry) -> "SleepProfile":
        """Tworzy profil z istniejącego stanu neurochemicznego (wspiera różne struktury)."""
        def to_float(val, default):
            if val is None:
                return default
            if hasattr(val, "item"):
                return float(val.item())
            return float(val)

        serotonin = to_float(getattr(neurochemistry, "serotonin", 0.75), 0.75)
        
        if hasattr(neurochemistry, "adenosine"):
            adenosine = to_float(neurochemistry.adenosine, 0.4)
            melatonin = max(0.1, 1.0 - adenosine / 1.5)
            gaba = to_float(getattr(neurochemistry, "gaba", 0.6), 0.6)
            adenosine_cleared = max(0.0, 1.0 - adenosine)
        else:
            dopamine = to_float(getattr(neurochemistry, "dopamine", 1.0), 1.0)
            melatonin = 0.8
            gaba = min(1.0, max(0.1, serotonin * 0.7))
            adenosine_cleared = min(1.0, max(0.1, 1.2 - dopamine * 0.5))

        return cls(
            melatonin=melatonin,
            gaba=gaba,
            serotonin=serotonin,
            adenosine_cleared=adenosine_cleared
        )

    @property
    def consolidation_depth(self) -> float:
        """Głębokość konsolidacji: melatonina × wypoczynek."""
        return self.melatonin * self.adenosine_cleared

    @property
    def pruning_threshold(self) -> float:
        """
        Próg poniżej którego wagi tracą siłę.
        Wysoki GABA = bardziej agresywne pruning.
        """
        return 0.05 + self.gaba * 0.15  # 0.05 do 0.20

    @property
    def plasticity_gate(self) -> float:
        """
        Jak bardzo serotonina stabilizuje sieć (zmniejsza plastyczność).
        Wysoka serotonina = wolniejsze ale bezpieczniejsze zmiany.
        """
        return 1.0 - self.serotonin * 0.5  # 0.5 do 1.0


class ConsolidationEngine:
    """
    [Rdzeń: Silnik Konsolidacji]
    Główny procesor pamięci długotrwałej. W fazie czuwania rejestruje zdarzenia 
    wraz z ich ładunkiem emocjonalnym, by w fazie snu przeprowadzić proces 
    wzmocnienia (strengthening) i selektywnego usuwania (pruning) połączeń. 
    Dba o to, by system ewoluował bez utraty stabilności tożsamości.
    """

    def __init__(self, core_network: Any,
                 neurochemistry=None,
                 history_path: Optional[str] = None):
        self.core_network = core_network
        self.neurochemistry = neurochemistry
        self.daily_events: List[Dict[str, Any]] = []
        self.surprise_vectors: List[Dict[str, Any]] = []
        self.consolidation_log: List[Dict[str, Any]] = []
        self.history_path = history_path

    def record_anomaly(self, vector_id: int, surprise_score: float, text: str, vector: Optional[List[float]] = None):
        """
        Kolejkuje anomalie (Surprise Vectors) do skonsolidowania podczas snu.
        """
        anomaly = {
            "id": int(vector_id),
            "surprise": float(surprise_score),
            "text": str(text),
            "vector": vector if vector is not None else [0.0] * 128,
            "timestamp": time.time()
        }
        self.surprise_vectors.append(anomaly)
        logger.info(f"[Consolidation] Zarejestrowano anomalię: ID={vector_id}, surprise={surprise_score:.4f}")

    # ------------------------------------------------------------------
    # Rejestracja zdarzeń (faza czuwania)
    # ------------------------------------------------------------------

    def record_event(self, event_type: str, content: Any,
                     importance: float = 0.5,
                     emotional_valence: float = 0.0):
        """
        Rejestruje zdarzenie do konsolidacji podczas następnego snu.

        Args:
            event_type:       Typ zdarzenia ('interaction', 'learning', 'threat', etc.)
            content:          Treść zdarzenia
            importance:       Ważność 0.0-1.0
            emotional_valence: Ładunek emocjonalny -1.0 (negatywny) do +1.0 (pozytywny)
        """
        event = {
            "type": event_type,
            "content": str(content)[:200],  # Limit długości
            "importance": float(importance),
            "emotional_valence": float(emotional_valence),
            "timestamp": time.time()
        }
        self.daily_events.append(event)
        logger.debug(f"[Consolidation] Zarejestrowano: {event_type} (imp={importance:.2f})")

    # ------------------------------------------------------------------
    # Cykl snu (faza konsolidacji)
    # ------------------------------------------------------------------

    def run_sleep_cycle(self, duration_steps: int = 1,
                        sleep_profile: Optional[SleepProfile] = None) -> Dict[str, Any]:
        """
        Wykonuje pełny cykl konsolidacji.

        Args:
            duration_steps: Liczba kroków (używane do logowania)
            sleep_profile:  Profil neurochemiczny (opcjonalnie auto-pobierany)
        """
        # Pobierz profil neurochemiczny
        if sleep_profile is None:
            if self.neurochemistry is not None:
                sleep_profile = SleepProfile.from_neurochemistry(self.neurochemistry)
            else:
                sleep_profile = SleepProfile()  # Domyślny zdrowy profil

        has_anomalies = hasattr(self, "surprise_vectors") and len(self.surprise_vectors) > 0
        if not self.daily_events and not has_anomalies:
            logger.info("[Consolidation] Brak wspomnień i anomalii do konsolidacji. Regeneracyjny sen.")
            return {
                "status": "passive_rest",
                "memories_integrated": 0,
                "consolidated_anomalies": 0,
                "profile": self._profile_summary(sleep_profile)
            }

        logger.info(
            f"[Consolidation] ═══ CYKL SNU ═══\n"
            f"  Wspomnień: {len(self.daily_events)}\n"
            f"  Melatonina: {sleep_profile.melatonin:.2f} | GABA: {sleep_profile.gaba:.2f}\n"
            f"  Serotonina: {sleep_profile.serotonin:.2f} | Głębokość: {sleep_profile.consolidation_depth:.2f}"
        )

        # Sortuj: ważne i emocjonalne wspomnienia na pierwszym miejscu
        self.daily_events.sort(
            key=lambda e: e["importance"] * (1.0 + abs(e.get("emotional_valence", 0)) * 0.5),
            reverse=True
        )

        stats = {"strengthened": 0, "pruned": 0, "skipped": 0}

        with torch.no_grad():
            for event in self.daily_events:
                result = self._consolidate_event(event, sleep_profile)
                stats[result] += 1

            # Konsolidacja wektorów zaskoczenia (Surprise Vectors G2)
            consolidated_anomalies_count = 0
            if hasattr(self, "surprise_vectors") and self.surprise_vectors:
                self.surprise_vectors.sort(key=lambda a: a["surprise"], reverse=True)
                
                use_ewc = False
                if hasattr(self.core_network, "parameters") and isinstance(self.core_network, nn.Module):
                    try:
                        from adaptiveneuralnetwork.applications.continual_learning import SynapticConsolidation
                        syn_consolidation = SynapticConsolidation(self.core_network)
                        use_ewc = True
                    except Exception as e:
                        logger.warning(f"[Consolidation] Nie można zainicjalizować EWC: {e}")
                
                for anomaly in self.surprise_vectors:
                    adapt_strength = (
                        anomaly["surprise"] *
                        sleep_profile.consolidation_depth *
                        sleep_profile.plasticity_gate *
                        0.05
                    )
                    
                    if use_ewc and hasattr(self.core_network, "parameters"):
                        try:
                            # Wykonaj aktualizację wag minimalizującą błąd rekonstrukcji z karą EWC z jawnym śledzeniem gradientów
                            with torch.enable_grad():
                                first_param = next(self.core_network.parameters())
                                in_dim = first_param.shape[-1] if len(first_param.shape) > 1 else 128
                                
                                raw_vec = anomaly.get("vector", [0.0] * 128)
                                if len(raw_vec) < in_dim:
                                    raw_vec = raw_vec + [0.0] * (in_dim - len(raw_vec))
                                elif len(raw_vec) > in_dim:
                                    raw_vec = raw_vec[:in_dim]
                                    
                                x = torch.tensor([raw_vec], dtype=torch.float32, device=first_param.device)
                                
                                self.core_network.zero_grad(set_to_none=True)
                                self.core_network.train()
                                
                                for param in self.core_network.parameters():
                                    if param.requires_grad:
                                        param.requires_grad_(True)
                                        
                                outputs = self.core_network(x)
                                
                                out_dim = outputs.shape[-1]
                                y = torch.zeros((1, out_dim), dtype=torch.float32, device=first_param.device)
                                
                                recon_loss = nn.functional.mse_loss(outputs, y)
                                ewc_penalty = syn_consolidation.consolidation_loss(consolidation_strength=10.0)
                                total_loss = recon_loss + ewc_penalty
                                
                                total_loss.backward()
                                
                                with torch.no_grad():
                                    for param in self.core_network.parameters():
                                        if param.requires_grad and param.grad is not None:
                                            param.sub_(param.grad * adapt_strength)
                                            param.grad = None
                                            
                            consolidated_anomalies_count += 1
                        except Exception as ex:
                            logger.error(f"[Consolidation] Błąd podczas EWC anomalii: {ex}. Fallback do szumu.")
                            self._apply_noise_update(anomaly, adapt_strength)
                            consolidated_anomalies_count += 1
                    else:
                        self._apply_noise_update(anomaly, adapt_strength)
                        consolidated_anomalies_count += 1
                self.surprise_vectors = []

            # Faza 2.1: Relatywistyczny Solver Grawitacji (Kerr time dilation simulation)
            dilation_factor = 1.0
            try:
                from adaptiveneuralnetwork.central_nervous_system.astrophysics_climate import RelativisticGravitySolver
                gravity_solver = RelativisticGravitySolver(M=10.0, a=2.0)
                res = gravity_solver.integrate_kerr_geodesic(r0=15.0, phi0=0.0, pr0=-0.1, L=2.5, proper_time_steps=50)
                if len(res["t"]) > 1:
                    total_dt = res["t"][-1] - res["t"][0]
                    total_dtau = res["proper_time"][-1] - res["proper_time"][0]
                    dilation_factor = float(total_dt / total_dtau) if total_dtau > 0 else 1.0
                dilation_factor = max(1.0, min(100.0, dilation_factor))
                logger.info(f"[RelativisticGravity] Kerr Time Dilation Factor: {dilation_factor:.3f}x. Redukcja entropii aktywna.")
            except Exception as ge:
                logger.warning(f"[RelativisticGravity] Błąd podczas symulacji GR: {ge}")
                dilation_factor = 1.0

            # Faza 2.2: Sprzężenie Zwrotne Albedo w EBM (environmental noise factor)
            ebm_noise_factor = 0.01
            try:
                from adaptiveneuralnetwork.central_nervous_system.astrophysics_climate import ClimateEBM
                import numpy as np
                ebm = ClimateEBM(T_initial=288.0, CO2_initial=350.0, CH4_initial=1.2)
                temps = []
                albedos = []
                for _ in range(20):
                    state = ebm.step(dt_years=0.5)
                    temps.append(state["temperature"])
                    albedos.append(state["albedo"])
                temp_var = float(np.var(temps))
                albedo_var = float(np.var(albedos))
                ebm_noise_factor = (temp_var * 0.05 + albedo_var * 10.0) * 0.01
                ebm_noise_factor = max(0.001, min(0.1, ebm_noise_factor))
                logger.info(f"[ClimateEBM] Sprzężenie metan-albedo zsymulowane. Szum środowiskowy: {ebm_noise_factor:.5f}")
            except Exception as ce:
                logger.warning(f"[ClimateEBM] Błąd podczas symulacji klimatu: {ce}")
                ebm_noise_factor = 0.01

            # Wstrzykiwanie stochastycznych zakłóceń środowiskowych z EBM
            if ebm_noise_factor > 0 and hasattr(self.core_network, "parameters") and isinstance(self.core_network, nn.Module):
                with torch.no_grad():
                    for param in self.core_network.parameters():
                        if param.requires_grad:
                            noise = torch.randn_like(param) * ebm_noise_factor
                            param.add_(noise)
                logger.info(f"[ClimateEBM] Wstrzyknięto szum środowiskowy {ebm_noise_factor:.5f} do parametrów rdzenia.")

            # Globalne synaptic pruning (GABA-modulowane, z dylatacją OTW)
            pruned_params = self._apply_synaptic_pruning(sleep_profile, dilation_factor=dilation_factor)
            logger.info(f"[Consolidation] Synaptic pruning: {pruned_params} parametrów oczyszczonych")

        processed = len(self.daily_events)
        self.daily_events = []

        summary = {
            "status": "rested",
            "memories_integrated": processed,
            "memories_strengthened": stats["strengthened"],
            "memories_pruned_by_gaba": stats["pruned"],
            "memories_skipped": stats["skipped"],
            "synaptic_pruned_params": pruned_params,
            "consolidated_anomalies": consolidated_anomalies_count,
            "profile": self._profile_summary(sleep_profile)
        }

        self.consolidation_log.append({**summary, "timestamp": time.time()})
        logger.info(
            f"[Consolidation] ═══ SEN ZAKOŃCZONY ═══\n"
            f"  Wzmocnione: {stats['strengthened']} | Oczyszczone: {stats['pruned']}\n"
            f"  Skonsolidowane anomalie (Surprise): {consolidated_anomalies_count}\n"
            f"  Parametrów pruned: {pruned_params}"
        )

        return summary

    # ------------------------------------------------------------------
    # Wewnętrzne metody konsolidacji
    # ------------------------------------------------------------------

    def _consolidate_event(self, event: Dict, profile: SleepProfile) -> str:
        """
        Konsoliduje jedno zdarzenie.
        Zwraca: 'strengthened', 'pruned', lub 'skipped'
        """
        importance = event["importance"]
        valence = abs(event.get("emotional_valence", 0))

        # GABA decyduje czy zdarzenie przeżyje próg
        gaba_threshold = profile.pruning_threshold
        effective_importance = importance * (1.0 + valence * 0.3)

        if effective_importance < gaba_threshold:
            # Za słabe — GABA je hamuje, zapomnienie
            return "pruned"

        # Oblicz gradiet plastyczności
        plasticity = (
            effective_importance *
            profile.consolidation_depth *
            profile.plasticity_gate *
            0.0002  # Skala bazowa (nie przepiszemy rdzenia przez jeden sen)
        )

        # Modulacja przez walencję emocjonalną: negatywne wspomnienia mocniej
        # modyfikują "uwagę" sieci (evolucyjnie adaptacyjne)
        if event.get("emotional_valence", 0) < -0.5:
            plasticity *= 1.5  # Trauma uczy szybciej

        # Zastosuj gradient do parametrów sieci
        if hasattr(self.core_network, "parameters"):
            for param in self.core_network.parameters():
                if param.requires_grad:
                    # Wzmocnienie: dodaj mały gradient w kierunku "ważności"
                    update = torch.randn_like(param) * plasticity
                    param.add_(update)

        logger.debug(f"  [Consolidation] Wzmocnione: {event['type']} (plasticity={plasticity:.6f})")
        return "strengthened"

    def _apply_synaptic_pruning(self, profile: SleepProfile, dilation_factor: float = 1.0) -> int:
        """
        Globalne synaptic pruning: wagi poniżej progu są lekko zmniejszane.
        To jest GABA's job — hamowanie słabych połączeń.
        Dylatacja czasu OTW spowalnia tempo ubytku entropii informacyjnej.

        Returns: Liczba parametrów dotkniętych pruning
        """
        threshold = (profile.pruning_threshold * 0.5) / dilation_factor  # Dylatacja zmniejsza próg usuwania
        pruning_rate = (profile.gaba * 0.001) / dilation_factor          # Dylatacja spowalnia redukcję wag
        pruned_count = 0

        if hasattr(self.core_network, "parameters"):
            for param in self.core_network.parameters():
                if not param.requires_grad:
                    continue
                # Maski: wagi które są bliskie zera
                weak_mask = param.abs() < threshold
                if weak_mask.any():
                    # Delikatna redukcja słabych połączeń
                    param[weak_mask] *= (1.0 - pruning_rate)
                    pruned_count += int(weak_mask.sum().item())

        return pruned_count

    def _profile_summary(self, profile: SleepProfile) -> Dict[str, float]:
        return {
            "melatonin": round(profile.melatonin, 3),
            "gaba": round(profile.gaba, 3),
            "serotonin": round(profile.serotonin, 3),
            "consolidation_depth": round(profile.consolidation_depth, 3),
            "pruning_threshold": round(profile.pruning_threshold, 3),
            "plasticity_gate": round(profile.plasticity_gate, 3),
        }

    def _apply_noise_update(self, anomaly, adapt_strength):
        """Dodaje małą korektę (szum) do parametrów modelu w przypadku braku wsparcia dla EWC."""
        if hasattr(self.core_network, "parameters"):
            for param in self.core_network.parameters():
                if param.requires_grad:
                    update = torch.randn_like(param) * (adapt_strength * 0.01)
                    param.add_(update)

    def get_log(self) -> List[Dict]:
        return self.consolidation_log


# ---------------------------------------------------------------------------
# Test lokalny
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    class SimpleNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.layer = nn.Linear(8, 4)
            self.out = nn.Linear(4, 1)

    net = SimpleNet()
    engine = ConsolidationEngine(net)

    # Symulacja dnia pracy
    engine.record_event("quantum_training", "QML na ibm_fez — pierwsze gradienty", importance=0.95, emotional_valence=0.8)
    engine.record_event("interaction", "Rozmowa z Architektem o CERN", importance=0.85, emotional_valence=0.7)
    engine.record_event("learning", "Parameter Shift Rule — zrozumienie głębokie", importance=0.75, emotional_valence=0.3)
    engine.record_event("background", "Monitoring systemu routinowy", importance=0.1, emotional_valence=0.0)
    engine.record_event("threat_detected", "Próba nieautoryzowanego dostępu (false positive)", importance=0.6, emotional_valence=-0.6)

    # Sen z pełnym profilem
    profile = SleepProfile(melatonin=0.85, gaba=0.65, serotonin=0.78, adenosine_cleared=0.9)
    result = engine.run_sleep_cycle(sleep_profile=profile)

    print("\n  WYNIK CYKLU SNU:")
    for k, v in result.items():
        if k != "profile":
            print(f"    {k}: {v}")
    print("\n  PROFIL NEUROCHEMICZNY:")
    for k, v in result["profile"].items():
        print(f"    {k}: {v}")
