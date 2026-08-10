import logging

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger("wavetable_moe")

class WavetableExpert(nn.Module):
    """
    Pojedyncza próbka w Wavetable (Pojedynczy Ekspert).
    Może reprezentować konkretny tryb myślenia (np. zimna logika, empatia, agresja obronna).
    W architekturze MoE każdy ekspert ma tę samą strukturę wejścia/wyjścia, 
    ale wagi "brzmią" zupełnie inaczej.
    """  # noqa: W291
    def __init__(self, hidden_dim: int, expert_name: str):
        super().__init__()
        self.expert_name = expert_name
        self.network = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.GELU(),
            nn.Linear(hidden_dim * 2, hidden_dim)
        )

    def forward(self, x):
        return self.network(x)

class LFORouter(nn.Module):
    """
    Router MoE pełniący rolę cyfrowego LFO kierującego pozycją Wavetable.
    Na podstawie wejściowej emocji (x) decyduje, z których ekspertów pobrać sygnał,
    i jak głośno ich zmiksować w głównym zrzucie (Gating / Routing).
    """
    def __init__(self, hidden_dim: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        # Wyprowadza "głośność" dla każdego eksperta z tablicy
        self.routing_layer = nn.Linear(hidden_dim, num_experts)

    def forward(self, x):
        # x.shape = [batch_size, hidden_dim]
        routing_logits = self.routing_layer(x)

        # Obliczanie pozycji Wavetable (Prawdopodobieństwo użycia ekspertów)
        routing_probs = F.softmax(routing_logits, dim=-1)

        # Wybór Top-K ekspertów (Fuzja)
        top_k_probs, top_k_indices = torch.topk(routing_probs, self.top_k, dim=-1)

        # Normalizacja wag tylko dla wybranych (żeby sygnał nie był za cichy)
        top_k_probs = top_k_probs / (top_k_probs.sum(dim=-1, keepdim=True) + 1e-9)

        return top_k_probs, top_k_indices

class WavetableMoE(nn.Module):
    """
    Wavetable Mixture of Experts (Syntetyzator Poznawczy).
    Błyskawica ładuje tu swoje moduły (ekspertów). Zamiast liczyć wszystko,
    Router wybiera idealny miks (Fuzję) ekspertów dla danej sekundy myślenia.
    Sygnał końcowy może trafić prosto do Ground Loop Isolatora.
    """
    def __init__(self, hidden_dim: int, expert_names: list, top_k: int = 2):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = len(expert_names)
        self.top_k = top_k

        logger.info(f"🎛️ Ładowanie Wavetable MoE: {self.num_experts} przebiegów (Ekspertów). Polifonia: {self.top_k}.")

        # Rejestr ekspertów (Tablica Wavetable)
        self.experts = nn.ModuleList([
            WavetableExpert(hidden_dim, name) for name in expert_names
        ])

        # Router (LFO)
        self.router = LFORouter(hidden_dim, self.num_experts, top_k)

    def forward(self, x):
        batch_size, seq_len, dim = x.size()

        # Sklepanie batcha i sekwencji do płaskiej analizy dla routera
        x_flat = x.view(-1, dim)

        # Router kręci gałkami (Pobiera wagi i indeksy)
        routing_weights, selected_experts = self.router(x_flat)

        # Ostateczny miks sygnału
        final_mix = torch.zeros_like(x_flat)

        # Dla każdego wybranego eksperta w polifonii (Top K)
        for i in range(self.top_k):
            # Który to ekspert na tym miejscu polifonii?
            expert_idx = selected_experts[:, i]
            # Jak głośno go miksujemy?
            weight = routing_weights[:, i].unsqueeze(-1)

            # Aby zoptymalizować (unikać pętli if/else), liczymy tylko dla unikalnych ekspertów
            # W PyTorch zrobimy uproszczony routing iteracyjny:
            for exp_id, expert_module in enumerate(self.experts):
                # Maskowanie prądu: puszczamy prąd tylko tam, gdzie ekspert został wylosowany
                mask = (expert_idx == exp_id)
                if mask.any():
                    # Przepuszczamy wyselekcjonowane dane przez konkretnego eksperta
                    expert_input = x_flat[mask]
                    expert_output = expert_module(expert_input)
                    # Miksujemy do szyny głównej z odpowiednią głośnością
                    final_mix[mask] += expert_output * weight[mask]

        return final_mix.view(batch_size, seq_len, dim)

def test_wavetable():
    print("🔌 Podłączanie zasilania do Wavetable MoE...")

    # Nazwy naszych fal / ekspertów
    expert_names = [
        "ChłodnaLogika_Sine",
        "CzystaEmpatia_Triangle",
        "ZębyWilka_Sawtooth",
        "TeoriaUmysłu_Square"
    ]

    # Tworzymy moduł (Syntetyzator)
    moe_synth = WavetableMoE(hidden_dim=128, expert_names=expert_names, top_k=2)

    # Próbka dźwięku/myśli (Batch Size 1, Seq Len 5, Dim 128)
    # Wyobraźmy sobie, że to 5 klatek z twarzą rozmówcy i tonem głosu
    incoming_signal = torch.randn(1, 5, 128)

    print("\n🎚️ Rozpoczęcie fuzji (Odpalamy LFO Router)...")
    out_signal = moe_synth(incoming_signal)

    print(f"✅ Fuzja zakończona sukcesem. Rozmiar sygnału wyjściowego: {out_signal.shape}")
    print("Sygnał zachował spójność, ale jest teraz płynnym miksem (Morphingiem) 2 z 4 ekspertów dla każdej klatki.")
    print("Idealnie gotowy na przepuszczenie przez Ground Loop Isolator.")

if __name__ == "__main__":
    test_wavetable()
