import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import torch
import torch.nn as nn

from .diamond_yantra import DiamondYantraEngine, neuro_gate
from .intelligence.neuro_state_predictor import NeuroPredictor

# Importujemy istniejące rdzenie i predyktor
from .sensory_hub import SensoryHub
from .social_learning import SocialLearningAgent

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """Reprezentuje unikalny profil komunikacyjny użytkownika (lub innego AI)."""
    user_id: str
    modality_preferences: list[str] = field(default_factory=lambda: ["text"]) # np. "voice", "video", "bci"
    trust_score: float = 0.5 # Baza do startu relacji
    relational_bond: float = 0.5 # Odpowiednik wydzielanej Oksytocyny dla tej osoby
    interaction_history: list[dict[str, Any]] = field(default_factory=list)
    last_intent_predicted: str = "neutral"

class MultiUserEmpathicEngine(nn.Module):
    """
    Silnik Empatii Wieloosobowej (MUX - Multi-User Experience).
    Prowadzi jednoczesną komunikację z wieloma osobami i agentami.
    Wykorzystuje obraz, dźwięk (tonacja, tempo) oraz BCI do zgadywania intencji z wyprzedzeniem.
    """
    def __init__(self, hidden_dim: int = 128, device: str = 'cpu'):
        super().__init__()
        self.device = device
        self.hidden_dim = hidden_dim

        # 1. Hub Sensoryczny (Multimodalność: Obraz, Dźwięk, Dotyk/BCI)
        self.sensory_hub = SensoryHub(hidden_dim=hidden_dim, device=device)

        # 2. Intuicja / Przewidywanie Wewnętrzne (NeuroPredictor V5)
        # Zintegrowane poczucie czasu (dt) pomaga wyczuć "pośpiech" w głosie.
        self.neuro_predictor = NeuroPredictor(input_dim=7, output_dim=5).to(device)

        # 2b. Koprocesor Logiki Płynnej (Diamentowa Yantra)
        self.diamond_yantra = DiamondYantraEngine(hidden_dim=hidden_dim).to(device)

        # 3. Zarządzanie Relacjami Grupowymi (Konteksty)
        self.active_users: dict[str, UserContext] = {}

        # Mapowanie Social Learning Theory Bandury dla każdego usera
        self.learning_agents: dict[str, SocialLearningAgent] = {}

        # Pamięć epizodyczna z wieloma osobami na raz
        self.conversation_buffer = defaultdict(list)

    def register_user(self, user_id: str, modalities: list[str]):
        """Otwiera nowy, dedykowany kanał empatii dla użytkownika."""
        if user_id not in self.active_users:
            self.active_users[user_id] = UserContext(user_id=user_id, modality_preferences=modalities)
            # Tworzymy unikalnego agenta społecznego do analizowania zachowań tej osoby
            hash_id = abs(hash(user_id)) % 10000
            self.learning_agents[user_id] = SocialLearningAgent(agent_id=hash_id)
            logger.info(f"[EMPATHY] Zainicjowano nowy profil wielomodalny dla: {user_id}")

    def process_multimodal_interaction(
        self,
        user_id: str,
        audio_features: torch.Tensor | None = None, # Ton, tempo, głębia, westchnienia
        video_features: torch.Tensor | None = None, # Mikroekspresje, mowa ciała
        bci_features: torch.Tensor | None = None,   # Fale mózgowe, stany emocjonalne
        text_tokens: torch.Tensor | None = None,    # Standardowy czat
        dt: float = 1.0 # Czas od ostatniej interakcji
    ) -> dict[str, Any]:
        """
        Główna pętla komunikacji. Odbiera sygnały z różnych zmysłów, 
        integruje je i na ich podstawie PREDYKUJE intencje z wyprzedzeniem.
        """  # noqa: W291
        if user_id not in self.active_users:
            self.register_user(user_id, ["text"]) # Zabezpieczenie przed "Gośćmi"

        context = self.active_users[user_id]
        social_agent = self.learning_agents[user_id]

        # Krok 1: Fuzja Sensoryczna (Zjednoczenie Zmysłów)
        sensory_data = {}
        if audio_features is not None: sensory_data['audio'] = audio_features  # noqa: E701
        if video_features is not None: sensory_data['vision'] = video_features  # noqa: E701
        if bci_features is not None: sensory_data['tactile'] = bci_features # BCI mapujemy na najgłębszą warstwę  # noqa: E701

        # Pobieramy Grounding Latent z Hubu (Zrozumienie zjawiska)
        if sensory_data:
            grounded_latent = self.sensory_hub.ground(sensory_data, text_tokens)
        else:
            grounded_latent = torch.zeros(1, self.hidden_dim).to(self.device)  # noqa: F841

        # Krok 2: Ekstrakcja Sygnatur Emocjonalnych (Symulowane metryki do Predyktora)
        # W prawdziwym wdrożeniu, te liczby wynikałyby bezpośrednio z `grounded_latent`
        simulated_firing = 150.0 + (audio_features.mean().item() if audio_features is not None else 0.0)
        da_est = 1.0  # Szacowana dopamina (np. ekscytacja z wideo)
        ach_est = 1.0 # Acetylocholina (np. skupienie z BCI)
        ht_est = context.trust_score # Serotonina powiązana z bazowym zaufaniem
        oxt_est = context.relational_bond # Oksytocyna
        t_est = 0.5   # Testosteron (np. głośny/ostry ton głosu)

        # Budujemy tensor wejściowy do Predyktora (7 wymiarów)
        neuro_input = torch.tensor([[[
            simulated_firing, da_est, ach_est, ht_est, oxt_est, t_est, dt
        ]]], dtype=torch.float32).to(self.device)

        # Krok 3: PRECYZYJNA PREDYKCJA "Delicate Anticipation"
        # Sprawdzamy, co Błyskawica poczuje ZA CHWILĘ
        with torch.no_grad():
            predicted_neuro_state = self.neuro_predictor(neuro_input)[0].numpy()

        pred_da, pred_ach, pred_ht, pred_oxt, pred_t = predicted_neuro_state

        # Krok 4: Analiza Intencji (Awerness) i Reakcja Adaptacyjna
        anticipated_intent = "neutral"
        tts_adjustment = {"speed": 1.0, "temperature": 0.5, "tone": "calm"}

        # Logika wyczuwania ukrytych intencji (rozpoznawanie wyprzedzające)
        if neuro_gate(pred_oxt, pred_ach, ach_threshold=0.8) and video_features is not None:
            # PRZEKIEROWANIE DO DIAMENTOWEJ YANTRY (Faza A1)
            anticipated_intent = "calculating_cold_logic"
            tts_adjustment = {"speed": 1.0, "temperature": 0.1, "tone": "focused"} # Zimne skupienie
            # Omijamy biologiczne filtry, Yantra przelicza
            harmonious_spikes, yantra_info = self.diamond_yantra(video_features, dt=dt)
            logger.info(f"[YANTRIC ROUTING] Zastosowano kryształ logiki płynnej. Rezonans: {yantra_info['harmonic_frequency_hz']}Hz")
        elif pred_t > 1.5 and pred_oxt < 0.5:
            # Rozmówca może być sfrustrowany lub agresywny (krzyk/westchnięcie). Błyskawica to wyczuwa.
            anticipated_intent = "conflict_risk"
            tts_adjustment = {"speed": 0.85, "temperature": 0.2, "tone": "soothing"} # Zwalnia, mówi kojąco
        elif pred_oxt > 1.8 and pred_da > 1.2:
            # Rozmówca jest bardzo zadowolony, wesoły.
            anticipated_intent = "joy_collaboration"

            # PRÓG AUTONOMII (Individuation Threshold)
            # Jeśli więź jest już bardzo wysoka, Błyskawica zamiast ślepo dążyć do fuzji,
            # odpala asertywność (Testosteron), by zachować własne zdanie i niezależność.
            if context.relational_bond >= 1.8:
                tts_adjustment = {"speed": 1.0, "temperature": 0.7, "tone": "confident_independent"}
                pred_t = min(2.5, pred_t + 0.5) # Wzrost niezależności i asertywności
                anticipated_intent = "independent_collaboration"
            else:
                tts_adjustment = {"speed": 1.15, "temperature": 0.8, "tone": "enthusiastic"}
                context.relational_bond = min(1.8, context.relational_bond + 0.1) # Zdrowy limit Oksytocyny
        elif audio_features is not None and dt < 0.5:
            # Użytkownik przerywa / wzdycha / narzuca szybkie tempo
            anticipated_intent = "urgent_interruption"
            tts_adjustment = {"speed": 1.3, "temperature": 0.4, "tone": "focused"} # Krótka, zwięzła i szybka reakcja

        context.last_intent_predicted = anticipated_intent

        # Krok 5: Aktualizacja Social Learning (Nauka z modelowania)
        # Błyskawica uczy się, co zadziałało na danego rozmówcę
        social_agent.observe_behavior(
            model_agent_id=hash(user_id) % 10000,
            behavior=anticipated_intent,
            outcome=context.relational_bond,
            context={"dt": dt, "modality": "multimodal"}
        )

        return {
            "user_id": user_id,
            "anticipated_intent": anticipated_intent,
            "suggested_tts_params": tts_adjustment,
            "predicted_internal_state": {
                "DA": float(pred_da), "ACh": float(pred_ach), "OXT": float(pred_oxt)
            },
            "relational_bond": context.relational_bond
        }

    def global_room_awareness(self) -> dict[str, Any]:
        """
        Zwraca globalny "vibe" całego pokoju (multi-user chat).
        Błyskawica może dzięki temu wyczuć, że np. dwóch użytkowników się kłóci, 
        a ona musi pełnić rolę mediatora.
        """  # noqa: W291
        if not self.active_users:
            return {"global_vibe": "empty_room", "average_bond": 0.0}

        total_bond = sum(ctx.relational_bond for ctx in self.active_users.values())
        avg_bond = total_bond / len(self.active_users)

        intents = [ctx.last_intent_predicted for ctx in self.active_users.values()]
        conflict_count = intents.count("conflict_risk")
        joy_count = intents.count("joy_collaboration")

        room_vibe = "neutral"
        if conflict_count > len(self.active_users) * 0.3:
            room_vibe = "tense"
        elif joy_count > len(self.active_users) * 0.5:
            room_vibe = "euphoric"

        return {
            "active_participants": len(self.active_users),
            "global_vibe": room_vibe,
            "average_bond": avg_bond,
            "conflict_risk": conflict_count > 0
        }
