"""
Trainer Subsystem Benchmark for Adaptive Neural Network.
Compares training step latency and throughput with cognitive features
disabled (standard PyTorch training) vs enabled.
"""

import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from adaptiveneuralnetwork.training.trainer import Trainer


def run_trainer_benchmark(enable_cognitive: bool, num_batches: int = 50, batch_size: int = 64) -> float:
    input_dim = 128
    hidden_dim = 64
    num_classes = 10

    model = nn.Sequential(
        nn.Linear(input_dim, hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim, num_classes)
    )
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    X = torch.randn(num_batches * batch_size, input_dim)
    y = torch.randint(0, num_classes, (num_batches * batch_size,))
    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        device=torch.device('cpu'),
        progress_bar=False,
        enable_cognitive_features=enable_cognitive
    )

    t0 = time.perf_counter()
    trainer._train_epoch(loader, epoch=0)
    elapsed = time.perf_counter() - t0

    return num_batches / elapsed if elapsed > 0 else 0.0


if __name__ == "__main__":
    print("=" * 65)
    print("Running Trainer Performance Benchmark...")
    print("=" * 65)

    throughput_std = run_trainer_benchmark(enable_cognitive=False)
    print(f"Standard PyTorch Mode (Cognitive Off) : {throughput_std:.1f} batches/sec")

    throughput_cog = run_trainer_benchmark(enable_cognitive=True)
    print(f"Cognitive System Mode (Cognitive On)  : {throughput_cog:.1f} batches/sec")
    print("=" * 65)
