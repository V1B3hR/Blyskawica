"""
Serving Infrastructure Benchmark for Adaptive Neural Network.
Measures latency distribution (p50, p95, p99), throughput (RPS),
and concurrent request handling for ModelServer.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any

from adaptiveneuralnetwork.production.serving import ModelServer, ServingConfig
from adaptiveneuralnetwork.api.model import AdaptiveModel
from adaptiveneuralnetwork.api.config import AdaptiveConfig


class ServingBenchmark:
    """Benchmark harness for ModelServer under load."""

    def __init__(self, batch_size: int = 16, max_workers: int = 4):
        self.config = ServingConfig(
            model_path="models/adaptive",
            batch_size=batch_size,
            max_workers=max_workers,
            enable_batching=True,
            enable_caching=True,
            max_batch_delay_ms=10
        )
        self.server = ModelServer(self.config)
        self.server.model = AdaptiveModel(AdaptiveConfig(input_dim=128, hidden_dim=64, output_dim=10))
        self.server.model.eval()

    async def run_concurrent_load(self, num_requests: int = 100, concurrency: int = 10) -> Dict[str, Any]:
        """Run concurrent prediction requests and compute performance statistics."""
        semaphore = asyncio.Semaphore(concurrency)
        latencies: List[float] = []

        async def worker():
            async with semaphore:
                sample_input = [[0.1 * i for i in range(128)]]
                t0 = time.perf_counter()
                try:
                    await self.server.predict(sample_input)
                    latencies.append((time.perf_counter() - t0) * 1000.0)
                except Exception as e:
                    print(f"Request failed: {e}")

        t_start = time.perf_counter()
        tasks = [asyncio.create_task(worker()) for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - t_start

        latencies.sort()
        rps = num_requests / total_time if total_time > 0 else 0.0

        return {
            "num_requests": num_requests,
            "concurrency": concurrency,
            "total_time_sec": total_time,
            "throughput_rps": rps,
            "latency_p50_ms": statistics.median(latencies) if latencies else 0.0,
            "latency_p95_ms": latencies[int(len(latencies) * 0.95)] if latencies else 0.0,
            "latency_p99_ms": latencies[int(len(latencies) * 0.99)] if latencies else 0.0,
            "min_ms": min(latencies) if latencies else 0.0,
            "max_ms": max(latencies) if latencies else 0.0,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Running ModelServer Concurrent Load Benchmark...")
    print("=" * 60)

    bench = ServingBenchmark()
    results = asyncio.run(bench.run_concurrent_load(num_requests=200, concurrency=20))

    print(f"Total Requests : {results['num_requests']}")
    print(f"Concurrency    : {results['concurrency']}")
    print(f"Total Time     : {results['total_time_sec']:.3f} s")
    print(f"Throughput     : {results['throughput_rps']:.1f} RPS")
    print(f"Latency P50    : {results['latency_p50_ms']:.2f} ms")
    print(f"Latency P95    : {results['latency_p95_ms']:.2f} ms")
    print(f"Latency P99    : {results['latency_p99_ms']:.2f} ms")
    print("=" * 60)
