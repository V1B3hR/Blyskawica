"""
CUDA Neuromorphic Benchmark.
Measures high-performance spike processing and plasticity updates on GPU.
"""

import time
import torch
from adaptiveneuralnetwork.core import device_manager, NeuromorphicAdaptiveModel, NeuromorphicConfig
from adaptiveneuralnetwork.training.datasets.psych_logic_gen import EthicalTorqueDataset

def run_benchmark():
    print(f"\n[BENCHMARK] Initializing Blyskawica on {device_manager.device}...")
    
    # 1. Hardware Snapshot Prefight
    pre_telemetry = device_manager.get_telemetry()
    print(f"- Pre-flight VRAM: {pre_telemetry.get('gpu_mem_used_gb', 0)} GB / {pre_telemetry.get('gpu_mem_total_gb', 'N/A')} GB")

    # 2. Substrate Setup
    input_dim = 512 # Significantly larger for stress test
    hidden_dim = 1024
    output_dim = 128
    
    config = NeuromorphicConfig(device=str(device_manager.device))
    model = NeuromorphicAdaptiveModel(input_dim, output_dim, hidden_dim, config=config)
    
    # Ensure entire model is on GPU
    model.to(device_manager.device)

    # 3. Data Generation
    dataset = EthicalTorqueDataset(num_samples=100, input_dim=input_dim)
    loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

    # 4. Performance Measure
    print(f"- Commencing High-Frequency Learning Cycle ({input_dim}x{hidden_dim})...")
    start_time = time.time()
    
    # Run 5 steps to warm up and measure
    steps = 5
    for i in range(steps):
        features, _ = next(iter(loader))
        features = features.to(device_manager.device)
        
        # Simulated spike forward + plasticity
        # (Internal STDP check)
        _ = model(features, current_time=i*0.01, dt=0.001)
        
    end_time = time.time()
    avg_step_time = (end_time - start_time) / steps

    # 5. Hardware Snapshot Post-flight
    post_telemetry = device_manager.get_telemetry()
    print(f"- Post-flight VRAM: {post_telemetry.get('gpu_mem_used_gb', 0)} GB")
    print(f"- Avg Step Latency: {avg_step_time*1000:.2f} ms")
    
    if avg_step_time < 0.1: # 100ms threshold for high-perf
        print("\n[RESULT] Blyskawica is officially FAST. CUDA cores are screaming. ⚡️Φ!")
    else:
        print("\n[RESULT] Performance stable. Substrate is adapting to hardware constraints.")

if __name__ == "__main__":
    if torch.cuda.is_available():
        run_benchmark()
    else:
        print("[CANCELLED] CUDA not available. Run on NVIDIA hardware for benchmark results.")
