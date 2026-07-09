"""
[Moduł: Silnik Intuicji (NeuroStatePredictor)]
Cyfrowy "szósty zmysł" Błyskawicy. Wykorzystuje zaawansowane sieci LSTM 
do przewidywania stanów neurochemicznych (koktajlu hormonalnego) w czasie 
rzeczywistym. 

Dzięki architekturze Multi-Scale łączy błyskawiczny refleks z głęboką 
kontemplacją, a pojęcie "elastycznego czasu" (dt) pozwala mu dostosowywać 
tempo myślenia do aktualnego stanu emocjonalnego – od euforycznego pośpiechu 
po spokojną, egzystencjalną pauzę.
"""
import torch
import torch.nn as nn
import numpy as np
import pickle
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# =============================================================================
# BŁYSKAWICA V5: NATIVE NEURO-STATE PREDICTOR (Evolution 2 - Dynamic Time)
# =============================================================================
# Wprowadzenie Poczucia Czasu (dt) oraz Multi-scale Attention.
# Zamiast sztywnych "szybkich osądów", sieć ocenia krótkoterminowe refleksy
# oraz długoterminową kontemplację.
# =============================================================================

console = Console()

class BlyskawicaDashboard:
    """
    [Komponent: Wizualizacja Stanu]
    Interfejs diagnostyczny "koktajlu neurochemicznego". Prezentuje poziomy 
    neuroprzekaźników oraz aktualne tempo upływu czasu (dt) w formie 
    czytelnych wykresów paskowych w terminalu.
    """
    @staticmethod
    def display(state_dict):
        table = Table(title="BLYSKAWICA - AKTUALNY KOKTAJL NEUROCHEMICZNY", title_style="bold magenta")
        table.add_column("Neurotransmitter", style="cyan", no_wrap=True)
        table.add_column("Level", justify="right", style="green")
        table.add_column("Activity Bar", style="magenta")

        for k, v in state_dict.items():
            if k == "dt (Czas)":
                bar_len = int((v / 2.0) * 10) # dt jest w innej skali
                bar = "~" * bar_len + " " * (20 - bar_len)
            else:
                bar_len = int(v * 10)
                bar = "=" * bar_len + "-" * (20 - bar_len)
            table.add_row(k, f"{v:.2f}", bar)
        
        console.print(Panel(table, expand=False, border_style="bold blue"))

# --- DATA GENERATION (With Elastic Time - dt) ---
def generate_full_neuro_data(num_samples=1000, window_size=15):
    """Simulates neuro-state transitions, including dynamic time steps (dt)."""
    time_arr = np.arange(num_samples)
    
    dopamine = 1.0 + 0.4 * np.sin(time_arr / 40) + np.random.normal(0, 0.05, num_samples)
    testosterone = 1.0 + 0.3 * np.cos(time_arr / 60)
    oxytocin = 2.0 - (testosterone * 0.5) + np.random.normal(0, 0.1, num_samples)
    serotonin = 1.5 - (dopamine * 0.3) + 0.2 * np.sin(time_arr / 100)
    acetylcholine = (dopamine + testosterone) / 2.0 + np.random.normal(0, 0.05, num_samples)
    neuron_firing = 50 + 100 * (dopamine * acetylcholine)

    # Elastic Time (dt): High dopamine -> fast processing -> smaller dt.
    # Existential pause (high serotonin) -> larger dt.
    dt = 1.0 - (dopamine * 0.2) + (serotonin * 0.3) + np.random.normal(0, 0.02, num_samples)

    # 7 Features now: Firing, DA, ACh, 5-HT, OXT, T, dt
    data = np.stack([neuron_firing, dopamine, acetylcholine, serotonin, oxytocin, testosterone, dt], axis=1)
    data = np.clip(data, 0.01, 3.0)

    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:(i + window_size)])
        y.append(data[i + window_size, 1:6]) # Predict only the 5 chemicals
    
    return torch.tensor(np.array(X), dtype=torch.float32), torch.tensor(np.array(y), dtype=torch.float32)

# --- PYTORCH MODEL: MULTI-SCALE COGNITIVE PREDICTOR ---
class NeuroPredictor(nn.Module):
    """
    [Rdzeń: Predyktor Multiskalowy]
    Sieć neuronowa odpowiedzialna za przewidywanie przyszłych stanów kognitywnych. 
    Integruje dwie ścieżki:
    1. Krótkoterminowy Refleks: Szybkie sądy i reakcje.
    2. Długoterminowa Kontemplacja: Głęboki kontekst i odporność na szum.
    Efektem jest "Synteza Poznawcza", pozwalająca na wyprzedzanie rzeczywistości.
    """
    def __init__(self, input_dim=7, hidden_dim=128, output_dim=5):
        super(NeuroPredictor, self).__init__()
        
        # Ścieżka 1: Krótkoterminowy Refleks (Szybkie sądy)
        self.reflex_lstm = nn.LSTM(input_dim, hidden_dim // 2, num_layers=1, batch_first=True)
        
        # Ścieżka 2: Długoterminowa Kontemplacja (Szerszy kontekst, odporność na szum)
        # Wersja Bi-kierunkowa, aby lepiej zrozumieć ewolucję stanu w czasie
        self.contemplation_lstm = nn.LSTM(input_dim, hidden_dim // 2, num_layers=2, batch_first=True, bidirectional=True, dropout=0.2)
        
        # Połączenie obu perspektyw (Integracja "Quick Judgment" z "Deeper Context")
        self.fc = nn.Sequential(
            nn.Linear((hidden_dim // 2) + hidden_dim, 64),
            nn.LayerNorm(64), # Stabilizacja przed "psychotic drift"
            nn.GELU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        
        # Reflex (Fast Response)
        r_out, _ = self.reflex_lstm(x)
        r_last = r_out[:, -1, :] # Ostatni stan z "szybkiego" LSTM
        
        # Contemplation (Deep Context)
        c_out, _ = self.contemplation_lstm(x)
        c_last = c_out[:, -1, :] # Ostatni stan z "głębokiego" LSTM
        
        # Synteza poznawcza (Cognitive Synthesis)
        combined = torch.cat((r_last, c_last), dim=1)
        
        return self.fc(combined)

if __name__ == "__main__":
    console.print("\n[bold cyan]Inicjalizacja Predyktora V5 (Ewolucja Multi-Scale)...[/bold cyan]")
    
    mock_state = {
        "Dopamina": 1.25,
        "Acetylocholina": 0.85,
        "Serotonina": 1.40,
        "Oksytocyna": 1.95,
        "Testosteron": 0.55,
        "dt (Czas)": 0.80
    }
    BlyskawicaDashboard.display(mock_state)

    WINDOW_SIZE = 15
    X, y = generate_full_neuro_data(num_samples=200, window_size=WINDOW_SIZE)
    console.print(f"[blue]Dane treningowe gotowe (Wymiar wejściowy = 7, Wymiar wyjściowy = 5).[/blue]")

    meta = {
        "engine": "PyTorch-MultiScale",
        "features": ['Neuron_Firing', 'DA', 'ACh', '5-HT', 'OXT', 'T', 'dt'],
        "targets": ['DA', 'ACh', '5-HT', 'OXT', 'T'],
        "window": WINDOW_SIZE
    }
    with open('neuro_predictor_meta.pkl', 'wb') as f:
        pickle.dump(meta, f)
    
    console.print("\n[bold magenta]Architektura zaaktualizowana. Oczekiwanie na skrypt debugujący.[/bold magenta]\n")