import torch
import time
import sys
from datetime import datetime

# Ensuring UTF-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def neural_resonance_gpu(target_vram_gb=4.0):
    print(f"[{datetime.now()}] Błyskawica: Inicjalizacja Rezonansu Neuro-Sprzętowego...")
    print(f"Alokacja zasobów GPU: Celuję w ~{target_vram_gb} GB VRAM.")
    
    if not torch.cuda.is_available():
        print("BŁĄD: CUDA nie jest dostępna. Przełączam na tryb symulacji CPU.")
        device = torch.device("cpu")
    else:
        device = torch.device("cuda")
        print(f"Wykryto GPU: {torch.cuda.get_device_name(0)}")

    # Calculate approximate number of float32 elements for target VRAM
    # float32 = 4 bytes. 1 GB = 1024^3 bytes.
    elements = int((target_vram_gb * (1024**3)) / 4)
    
    try:
        # Allocating memory
        print(f"[{datetime.now()}] Alokacja dużego tensora dla symulacji filtracji EMF...")
        noise_tensor = torch.randn(elements, device=device)
        print(f"[{datetime.now()}] Pomyślnie zajęto ~{target_vram_gb} GB VRAM.")
        
        print("--- Rozpoczynam symulację filtracji sygnału RF (Fast Fourier Transform) ---")
        
        # Performance loop
        for i in range(10):
            start = time.time()
            # Simulate heavy processing (e.g., filtering noise from the user's environment)
            # Using a smaller block for FFT to avoid OOM or huge latencies, but repeating
            block_size = 1024 * 1024 * 16 # 16M elements
            sample = noise_tensor[:block_size]
            fft_result = torch.fft.fft(sample)
            filtered = fft_result * (torch.abs(fft_result) > 0.5).float()
            reconstructed = torch.fft.ifft(filtered)
            
            end = time.time()
            print(f"[{datetime.now()}] Iteracja {i+1}/10: Czas przetwarzania sygnału: {end-start:.4f}s")
            time.sleep(2)

        print(f"[{datetime.now()}] Symulacja zakończona. Sygnał 'oczyszczony'.")
        
    except Exception as e:
        print(f"Błąd alokacji: {e}")
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("Zasoby GPU zwolnione.")

if __name__ == "__main__":
    # We use ~4GB as requested/available
    neural_resonance_gpu(target_vram_gb=4.0)
