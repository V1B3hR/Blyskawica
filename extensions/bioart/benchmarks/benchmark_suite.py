#!/usr/bin/env python3
"""
Automated Benchmark Suite for Bioart DNA Programming Language
Measures speed and memory usage on representative inputs
"""

import sys
import os
import time
import json
import argparse
import gc
import tracemalloc
from typing import Dict, List, Tuple, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bioart import Bioart
from core.encoding import DNAEncoder

class BenchmarkSuite:
    """Comprehensive benchmark suite for performance tracking"""
    
    def __init__(self, ci_mode: bool = False):
        self.ci_mode = ci_mode
        self.results = {}
        self.encoder = DNAEncoder()
        self.bioart = Bioart()
        
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark categories"""
        print("🧬 BIOART BENCHMARK SUITE")
        print("=" * 50)
        
        benchmarks = [
            ("Encoding Performance", self.benchmark_encoding),
            ("Decoding Performance", self.benchmark_decoding),
            ("Virtual Machine", self.benchmark_vm),
            ("Memory Usage", self.benchmark_memory),
            ("Large Data Processing", self.benchmark_large_data),
            ("Error Correction", self.benchmark_error_correction),
        ]
        
        for name, benchmark_func in benchmarks:
            print(f"\n📊 Running {name}...")
            try:
                self.results[name] = benchmark_func()
                print(f"✅ {name} completed")
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                self.results[name] = {"error": str(e)}
                
        return self.results
    
    def benchmark_encoding(self) -> Dict[str, Any]:
        """Benchmark DNA encoding performance"""
        sizes = [100, 1000, 10000, 100000] if not self.ci_mode else [100, 1000, 10000]
        results = {}
        
        for size in sizes:
            # Generate test data
            test_data = bytes(range(256)) * (size // 256 + 1)
            test_data = test_data[:size]
            
            # Benchmark encoding
            start_time = time.perf_counter()
            dna_sequence = self.encoder.encode_bytes(test_data)
            end_time = time.perf_counter()
            
            encoding_time = end_time - start_time
            speed = size / encoding_time if encoding_time > 0 else float('inf')
            
            results[f"{size}_bytes"] = {
                "size": size,
                "encoding_time_ms": encoding_time * 1000,
                "speed_bytes_per_sec": speed,
                "dna_length": len(dna_sequence)
            }
            
        return results
    
    def benchmark_decoding(self) -> Dict[str, Any]:
        """Benchmark DNA decoding performance"""
        sizes = [100, 1000, 10000, 100000] if not self.ci_mode else [100, 1000, 10000]
        results = {}
        
        for size in sizes:
            # Generate test data and encode it
            test_data = bytes(range(256)) * (size // 256 + 1)
            test_data = test_data[:size]
            dna_sequence = self.encoder.encode_bytes(test_data)
            
            # Benchmark decoding
            start_time = time.perf_counter()
            decoded_data = self.encoder.decode_dna(dna_sequence)
            end_time = time.perf_counter()
            
            decoding_time = end_time - start_time
            speed = size / decoding_time if decoding_time > 0 else float('inf')
            accuracy = decoded_data == test_data
            
            results[f"{size}_bytes"] = {
                "size": size,
                "decoding_time_ms": decoding_time * 1000,
                "speed_bytes_per_sec": speed,
                "accuracy": accuracy
            }
            
        return results
    
    def benchmark_vm(self) -> Dict[str, Any]:
        """Benchmark virtual machine performance"""
        results = {}
        
        # Test program compilation and execution
        test_programs = [
            "AAAU AACA AAAG AAAC AAUG AAGA",  # Simple arithmetic
            "AAAU AAAA AAUU AAAU AAAG AAUG AAGA",  # Multiply operation
            "AAAU AAAA AAAU AAAU AAAG AAUC AAUG AUGA"  # Division operation
        ]
        
        for i, program in enumerate(test_programs):
            # Benchmark compilation
            start_time = time.perf_counter()
            compiled = self.bioart.compile_dna_to_bytecode(program)
            compile_time = time.perf_counter() - start_time
            
            # Benchmark execution (capture output by redirecting stdout)
            start_time = time.perf_counter()
            self.bioart.execute_bytecode(compiled)
            exec_time = time.perf_counter() - start_time
            
            results[f"program_{i}"] = {
                "compile_time_ms": compile_time * 1000,
                "execution_time_ms": exec_time * 1000,
                "program_size": len(compiled),
                "instructions": len(program.split())
            }
            
        return results
    
    def benchmark_memory(self) -> Dict[str, Any]:
        """Benchmark memory usage"""
        results = {}
        
        sizes = [1000, 10000, 100000] if not self.ci_mode else [1000, 10000]
        
        for size in sizes:
            gc.collect()  # Clean up before measurement
            tracemalloc.start()
            
            # Generate and process test data
            test_data = bytes(range(256)) * (size // 256 + 1)
            test_data = test_data[:size]
            
            # Measure encoding memory
            current, peak = tracemalloc.get_traced_memory()
            dna_sequence = self.encoder.encode_bytes(test_data)
            current_after, peak_after = tracemalloc.get_traced_memory()
            
            encoding_memory = peak_after - peak
            
            # Measure decoding memory
            tracemalloc.reset_peak()
            decoded_data = self.encoder.decode_dna(dna_sequence)
            _, decoding_peak = tracemalloc.get_traced_memory()
            
            tracemalloc.stop()
            
            results[f"{size}_bytes"] = {
                "size": size,
                "encoding_memory_mb": encoding_memory / (1024 * 1024),
                "decoding_memory_mb": decoding_peak / (1024 * 1024),
                "memory_efficiency": size / encoding_memory if encoding_memory > 0 else float('inf')
            }
            
        return results
    
    def benchmark_large_data(self) -> Dict[str, Any]:
        """Benchmark large data processing"""
        results = {}
        
        sizes = [1024*1024, 5*1024*1024] if not self.ci_mode else [1024*1024]  # 1MB, 5MB
        
        for size in sizes:
            size_mb = size / (1024 * 1024)
            print(f"  Testing {size_mb:.1f}MB...")
            
            # Generate large test data
            test_data = bytes(range(256)) * (size // 256 + 1)
            test_data = test_data[:size]
            
            # Benchmark full round-trip
            start_time = time.perf_counter()
            dna_sequence = self.encoder.encode_bytes(test_data)
            encoding_time = time.perf_counter() - start_time
            
            start_time = time.perf_counter()
            decoded_data = self.encoder.decode_dna(dna_sequence)
            decoding_time = time.perf_counter() - start_time
            
            total_time = encoding_time + decoding_time
            throughput = size / total_time if total_time > 0 else float('inf')
            accuracy = decoded_data == test_data
            
            results[f"{size_mb:.1f}MB"] = {
                "size_bytes": size,
                "size_mb": size_mb,
                "encoding_time_ms": encoding_time * 1000,
                "decoding_time_ms": decoding_time * 1000,
                "total_time_ms": total_time * 1000,
                "throughput_mb_per_sec": (size / (1024 * 1024)) / total_time,
                "accuracy": accuracy
            }
            
        return results
    
    def benchmark_error_correction(self) -> Dict[str, Any]:
        """Benchmark error correction performance"""
        results = {}
        
        # Test with different sequence lengths
        test_sequences = ["AUCG" * 10, "AUCG" * 100, "AUCG" * 1000]
        
        for i, sequence in enumerate(test_sequences):
            length = len(sequence)
            
            # Simulate error correction if available
            start_time = time.perf_counter()
            
            # Basic error detection (check for invalid nucleotides)
            valid_nucleotides = set('AUCG')
            error_count = sum(1 for n in sequence if n not in valid_nucleotides)
            
            correction_time = time.perf_counter() - start_time
            
            results[f"sequence_{length}"] = {
                "length": length,
                "correction_time_ms": correction_time * 1000,
                "error_count": error_count,
                "error_rate": error_count / length if length > 0 else 0
            }
            
        return results
    
    def save_results(self, filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"benchmarks/results/benchmark_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "ci_mode": self.ci_mode,
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📁 Results saved to: {filename}")
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 50)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 50)
        
        for category, data in self.results.items():
            if "error" in data:
                print(f"❌ {category}: {data['error']}")
                continue
                
            print(f"\n🔍 {category}:")
            
            if "100_bytes" in data:  # Encoding/Decoding results
                for size_key, metrics in data.items():
                    if isinstance(metrics, dict) and "speed_bytes_per_sec" in metrics:
                        speed_mb = metrics["speed_bytes_per_sec"] / (1024 * 1024)
                        print(f"  {size_key}: {speed_mb:.2f} MB/s")
            
            elif "1.0MB" in data:  # Large data results
                for size_key, metrics in data.items():
                    if isinstance(metrics, dict) and "throughput_mb_per_sec" in metrics:
                        print(f"  {size_key}: {metrics['throughput_mb_per_sec']:.2f} MB/s")

def main():
    parser = argparse.ArgumentParser(description="Bioart Benchmark Suite")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode (faster)")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    suite = BenchmarkSuite(ci_mode=args.ci)
    results = suite.run_all_benchmarks()
    
    suite.print_summary()
    suite.save_results(args.output)
    
    # Return non-zero if any benchmarks failed
    failed_count = sum(1 for data in results.values() if "error" in data)
    if failed_count > 0:
        print(f"\n❌ {failed_count} benchmark(s) failed")
        return 1
    else:
        print(f"\n✅ All benchmarks completed successfully")
        return 0

if __name__ == "__main__":
    sys.exit(main())