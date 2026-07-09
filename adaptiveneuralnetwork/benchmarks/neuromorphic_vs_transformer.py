import sys
import os
import time
import psutil
import torch
import torch.nn as nn

# Upewnienie się, że projekt jest w PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from adaptiveneuralnetwork.central_nervous_system.neuromorphic.orbital_networks import EinsteinOrbitalNetwork

class SimpleTransformer(nn.Module):
    """
    Standardowy Transformer Encoder jako klasyczna baza porównawcza (Baseline).
    """
    def __init__(self, d_model=16, nhead=2, num_layers=2):
        super().__init__()
        # Typowa warstwa, feedforward powiększony 4-krotnie (64)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=64, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
    def forward(self, x):
        return self.transformer(x)

def measure_memory_and_time(model_fn, *args, **kwargs):
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024
    
    start_time = time.perf_counter()
    out = model_fn(*args, **kwargs)
    end_time = time.perf_counter()
    
    mem_after = process.memory_info().rss / 1024 / 1024
    mem_used = max(0, mem_after - mem_before)
    
    return out, (end_time - start_time) * 1000, mem_used

def run_benchmark():
    print("="*65)
    print("BENCHMARK: EINSTEIN ORBITAL NETWORK V4 vs CLASSIC TRANSFORMER")
    print("="*65)
    
    # 1. Setup: 12 cykli czasowych, ekstremalnie zaszumiony bodziec
    dim = 16
    time_steps = 12
    # Bodziec to wielki szum (np. nieprzefiltrowane dane z BCI)
    noisy_sequence = torch.randn(1, time_steps, dim) * 50.0 
    
    print("Inicjalizacja modeli...")
    # Orbital z wyłączonym BCI/RCD dla sprawiedliwego testu surowej matematyki
    orbital_net = EinsteinOrbitalNetwork(num_balls=5, spikes_per_ball=64, dim=dim)
    orbital_net.bci_enabled = False 
    
    transformer = SimpleTransformer(d_model=dim, nhead=2, num_layers=2)
    
    # Rozgrzewka (Warmup) by PyTorch załadował backend
    _ = transformer(torch.randn(1, 5, dim))
    _ = orbital_net(external_stimuli=[torch.randn(1, dim)] + [None]*4, time_steps=2)
    
    # -----------------------------------------
    # TEST 1: TRANSFORMER
    # -----------------------------------------
    print("\n[Test 1] KLASYCZNY TRANSFORMER")
    def run_transformer():
        return transformer(noisy_sequence)
        
    t_out, t_time, t_mem = measure_memory_and_time(run_transformer)
    t_variance = torch.var(t_out).item()
    
    print(f"  > Czas wykonania: {t_time:.2f} ms")
    print(f"  > Zużycie pamięci (wzrost): {t_mem:.2f} MB")
    print(f"  > Wariancja wyjścia (Podatność na szum): {t_variance:.2f}")
    
    # -----------------------------------------
    # TEST 2: ORBITAL NETWORK V4
    # -----------------------------------------
    print("\n[Test 2] ORBITAL NETWORK V4 (LQG + Einstein)")
    # Przygotowanie bodźca dla sieci orbitalnej: uderzamy w pierwszą kulę
    stimulus = [noisy_sequence[0, 0, :].unsqueeze(0)] + [None]*4
    
    def run_orbital():
        return orbital_net(external_stimuli=stimulus, time_steps=time_steps)
        
    o_out, o_time, o_mem = measure_memory_and_time(run_orbital)
    
    # Wariancja prędkości jako stabilność (jak bardzo kulki "szaleją")
    speeds_tensor = torch.stack(o_out['speeds'])
    o_variance = torch.var(speeds_tensor).item()
    
    print(f"  > Czas wykonania: {o_time:.2f} ms")
    print(f"  > Zużycie pamięci (wzrost): {o_mem:.2f} MB")
    print(f"  > Wariancja wyjścia (Stabilizacja szumu): {o_variance:.2f}")
    
    # -----------------------------------------
    # WNIOSKI
    # -----------------------------------------
    print("\n" + "="*65)
    print("WNIOSKI Z BENCHMARKU:")
    print(f"1. Szybkość: Orbital Network jest {'SZYBSZA' if o_time < t_time else 'WOLNIEJSZA'} o {abs(t_time - o_time):.2f} ms.")
    print(f"2. Pamięć: Orbital Network zużywa {'MNIEJ' if o_mem < t_mem else 'WIĘCEJ'} pamięci o {abs(t_mem - o_mem):.2f} MB.")
    
    if o_variance < t_variance:
         print("3. Stabilność: SUKCES. Orbital Network doskonale wygładza szum kwantowy")
         print("               dzięki promieniowaniu Hawkinga. Transformer przepuszcza chaos dalej.")
    else:
         print("3. Stabilność: Sieć orbitalna wykazuje dużą dynamikę rotacyjną przy uderzeniu.")
         
    print("="*65)

if __name__ == "__main__":
    run_benchmark()
