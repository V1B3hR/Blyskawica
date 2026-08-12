"""
Dataset Pipeline Benchmark for Adaptive Neural Network.
Measures data loading throughput (samples/sec) for VectorizedDataset
and StreamingDatasetWrapper.
"""

import time
import torch
import numpy as np

from adaptiveneuralnetwork.data.optimized_datasets import VectorizedDataset
from adaptiveneuralnetwork.data.streaming_datasets import StreamingDatasetWrapper, StreamingConfig


def benchmark_dataset_pipeline(num_samples: int = 10000, batch_size: int = 64):
    print("=" * 60)
    print("Running Dataset Pipeline Throughput Benchmark...")
    print("=" * 60)

    # 1. VectorizedDataset Benchmark
    X = torch.randn(num_samples, 128)
    y = torch.randint(0, 10, (num_samples,))

    t0 = time.perf_counter()
    vec_ds = VectorizedDataset(X, y, pin_memory=False)
    for i in range(0, num_samples, batch_size):
        indices = list(range(i, min(i + batch_size, num_samples)))
        batch_x, batch_y = vec_ds.get_batch(indices)
    elapsed_vec = time.perf_counter() - t0
    rate_vec = num_samples / elapsed_vec if elapsed_vec > 0 else 0.0

    print(f"VectorizedDataset Throughput : {rate_vec:.1f} samples/sec ({elapsed_vec*1000:.2f} ms total)")

    # 2. StreamingDatasetWrapper Benchmark
    config = StreamingConfig(batch_size=batch_size, buffer_size=1000, cache_size_mb=64)
    stream_ds = StreamingDatasetWrapper(data_source="data", config=config)
    
    t0 = time.perf_counter()
    count = 0
    for _sample in stream_ds.stream(shuffle=False):
        count += 1
        if count >= num_samples:
            break
    elapsed_stream = time.perf_counter() - t0
    rate_stream = count / elapsed_stream if elapsed_stream > 0 else 0.0

    print(f"StreamingDataset Throughput  : {rate_stream:.1f} samples/sec ({elapsed_stream*1000:.2f} ms total)")
    print("=" * 60)


if __name__ == "__main__":
    benchmark_dataset_pipeline()
