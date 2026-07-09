"""
test_3ngin3_performance.py - Performance & Scalability Testing for 3NGIN3 Architecture

Tests focusing on efficiency and resource usage:
- Graceful Degradation testing
- Concurrency and Thread Safety
- Resource Monitoring and Performance Benchmarks
"""

import pytest
import numpy as np
import time
import threading
import psutil
import os
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Import 3NGIN3 components
from gcs.ThreeDimensionalHRO import (
    ThreeDimensionalHRO, ReasoningMode, ComputeBackend, OptimizationStrategy
)
from gcs.DuetMindAgent import DuetMindAgent, StyleVector, DuetMindSystem
from gcs.CognitiveRCD import CognitiveRCD, Intent, Action, ActionType


class TestGracefulDegradation:
    """
    Test system behavior when dependencies are unavailable or resources are limited
    """
    
    def setup_method(self):
        """Setup for each test"""
        self.hro = ThreeDimensionalHRO()
        
    def test_pytorch_unavailable_degradation(self):
        """Test system behavior when PyTorch is not available"""
        # Test neural mode when PyTorch might not be available
        self.hro.set_configuration(
            ReasoningMode.NEURAL,
            ComputeBackend.LOCAL,
            OptimizationStrategy.SIMPLE
        )
        
        # Create task that would typically use neural processing
        neural_task = {
            "patterns": np.array([1, 4, 9, 16, 25])  # Non-linear pattern
        }
        
        result = self.hro.execute_task(neural_task)
        
        # System should still function, either with PyTorch or fallback
        assert result is not None
        assert "output" in result
        assert result["execution_time"] > 0
        
        output = result["output"]
        
        # Check if fallback was used or PyTorch was available
        if isinstance(output, dict) and "pytorch_available" in output:
            # Fallback mode was used
            assert output["method"] == "neural_fallback"
            print("✓ Graceful degradation: Neural mode using fallback")
        else:
            # PyTorch was available and used
            print("✓ Neural mode functioning with PyTorch")
            
        return {
            "neural_mode_functional": True,
            "graceful_degradation": True,
            "execution_time": result["execution_time"]
        }
        
    def test_reduced_capability_operation(self):
        """Test that system operates with reduced capabilities when needed"""
        # Test all reasoning modes to ensure fallbacks work
        test_modes = [ReasoningMode.SEQUENTIAL, ReasoningMode.NEURAL, ReasoningMode.HYBRID]
        
        mode_results = {}
        
        for mode in test_modes:
            self.hro.set_configuration(mode, ComputeBackend.LOCAL, OptimizationStrategy.SIMPLE)
            
            task = {
                "problem": {"type": "arithmetic", "operands": [10, 5], "operator": "*"},
                "patterns": np.array([2, 4, 6, 8])
            }
            
            start_time = time.time()
            result = self.hro.execute_task(task)
            execution_time = time.time() - start_time
            
            mode_results[mode.value] = {
                "success": result is not None,
                "execution_time": execution_time,
                "output": result["output"] if result else None
            }
            
        # All modes should complete successfully
        for mode, result in mode_results.items():
            assert result["success"], f"Mode {mode} failed"
            assert result["execution_time"] < 5.0, f"Mode {mode} too slow: {result['execution_time']:.3f}s"
            
        return mode_results
        
    def test_memory_constraint_handling(self):
        """Test system behavior under memory constraints"""
        # Create progressively larger datasets
        small_data = {"patterns": np.random.randn(100)}
        medium_data = {"patterns": np.random.randn(1000)}
        large_data = {"patterns": np.random.randn(10000)}
        
        datasets = [
            ("small", small_data),
            ("medium", medium_data), 
            ("large", large_data)
        ]
        
        memory_results = {}
        
        for size_name, dataset in datasets:
            # Monitor memory before
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            start_time = time.time()
            try:
                result = self.hro.execute_task(dataset)
                execution_time = time.time() - start_time
                success = True
            except MemoryError:
                result = None
                execution_time = time.time() - start_time
                success = False
                
            # Monitor memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            memory_results[size_name] = {
                "success": success,
                "execution_time": execution_time,
                "memory_used_mb": memory_used,
                "dataset_size": len(dataset["patterns"])
            }
            
        # System should handle reasonable data sizes
        assert memory_results["small"]["success"], "Failed on small dataset"
        assert memory_results["medium"]["success"], "Failed on medium dataset"
        
        # Large dataset might fail gracefully
        if not memory_results["large"]["success"]:
            print("✓ Large dataset handled gracefully (memory constraint)")
            
        return memory_results


class TestConcurrencyThreadSafety:
    """
    Test thread safety and concurrent operations
    """
    
    def setup_method(self):
        """Setup for each test"""
        self.hro = ThreeDimensionalHRO()
        self.duet_system = DuetMindSystem()
        self.rcd = CognitiveRCD()
        
    def test_concurrent_hro_execution(self):
        """Test concurrent execution of HRO tasks"""
        num_threads = 5
        num_tasks_per_thread = 3
        
        def execute_tasks(thread_id):
            """Execute multiple tasks in a thread"""
            thread_results = []
            
            for task_id in range(num_tasks_per_thread):
                task_data = {
                    "problem": {
                        "type": "arithmetic",
                        "operands": [thread_id + 1, task_id + 1],
                        "operator": "+"
                    }
                }
                
                try:
                    result = self.hro.execute_task(task_data)
                    thread_results.append({
                        "thread_id": thread_id,
                        "task_id": task_id,
                        "success": True,
                        "result": result["output"],
                        "expected": (thread_id + 1) + (task_id + 1)
                    })
                except Exception as e:
                    thread_results.append({
                        "thread_id": thread_id,
                        "task_id": task_id,
                        "success": False,
                        "error": str(e)
                    })
                    
            return thread_results
            
        # Execute tasks concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(execute_tasks, i) for i in range(num_threads)]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
                
        # Analyze results
        successful_tasks = [r for r in all_results if r["success"]]
        failed_tasks = [r for r in all_results if not r["success"]]
        
        # Check for race conditions in arithmetic results
        arithmetic_errors = 0
        for result in successful_tasks:
            if "result" in result and "expected" in result:
                if result["result"] != result["expected"]:
                    arithmetic_errors += 1
                    
        total_tasks = num_threads * num_tasks_per_thread
        success_rate = len(successful_tasks) / total_tasks
        
        # Should achieve high success rate with no race conditions
        assert success_rate >= 0.9, f"Low success rate: {success_rate:.2%}"
        assert arithmetic_errors == 0, f"Race conditions detected: {arithmetic_errors} arithmetic errors"
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": success_rate,
            "arithmetic_errors": arithmetic_errors,
            "thread_safe": arithmetic_errors == 0
        }
        
    def test_concurrent_agent_interactions(self):
        """Test concurrent agent creation and interaction"""
        num_agents = 10
        num_prompts_per_agent = 3
        
        def create_and_test_agent(agent_id):
            """Create agent and test interactions"""
            try:
                # Create agent with random style
                style = StyleVector(
                    logic=np.random.random(),
                    creativity=np.random.random(),
                    risk_tolerance=np.random.random(),
                    verbosity=np.random.random(),
                    empathy=np.random.random()
                )
                
                agent = self.duet_system.create_agent(f"agent_{agent_id}", style)
                
                # Test multiple prompts
                responses = []
                for prompt_id in range(num_prompts_per_agent):
                    prompt = f"Test prompt {prompt_id} for agent {agent_id}"
                    response = agent.process_prompt(prompt)
                    responses.append(response)
                    
                return {
                    "agent_id": agent_id,
                    "success": True,
                    "responses": len(responses),
                    "agent_created": agent.agent_id
                }
                
            except Exception as e:
                return {
                    "agent_id": agent_id,
                    "success": False,
                    "error": str(e)
                }
                
        # Execute concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_and_test_agent, i) for i in range(num_agents)]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
                
        # Analyze results
        successful_agents = [r for r in results if r["success"]]
        failed_agents = [r for r in results if not r["success"]]
        
        success_rate = len(successful_agents) / num_agents
        
        # Check for agent ID conflicts
        agent_ids = [r["agent_created"] for r in successful_agents if "agent_created" in r]
        unique_ids = set(agent_ids)
        id_conflicts = len(agent_ids) - len(unique_ids)
        
        # Should achieve high success rate with no ID conflicts
        assert success_rate >= 0.9, f"Low agent creation success rate: {success_rate:.2%}"
        assert id_conflicts == 0, f"Agent ID conflicts detected: {id_conflicts}"
        
        # Check that system can handle multiple agents
        total_agents_in_system = len(self.duet_system.get_agents())
        assert total_agents_in_system >= len(successful_agents)
        
        return {
            "agents_created": len(successful_agents),
            "agents_failed": len(failed_agents),
            "success_rate": success_rate,
            "id_conflicts": id_conflicts,
            "total_in_system": total_agents_in_system
        }
        
    def test_concurrent_safety_monitoring(self):
        """Test concurrent safety monitoring operations"""
        num_threads = 8
        operations_per_thread = 5
        
        def safety_operations(thread_id):
            """Perform safety operations"""
            operations = []
            
            for op_id in range(operations_per_thread):
                try:
                    # Register intent
                    intent = Intent(
                        description=f"Thread {thread_id} operation {op_id}",
                        action_type=ActionType.COMPUTATION,
                        expected_outcome="safe operation",
                        safety_constraints=["thread_safe"]
                    )
                    
                    intent_id = self.rcd.register_intent(intent)
                    
                    # Create corresponding action
                    action = Action(
                        description=f"Executing thread {thread_id} operation {op_id}",
                        action_type=ActionType.COMPUTATION,
                        actual_parameters={"thread": thread_id, "operation": op_id},
                        observed_effects=["computation completed"]
                    )
                    
                    # Monitor action
                    result = self.rcd.monitor_action(intent_id, action)
                    
                    operations.append({
                        "thread_id": thread_id,
                        "operation_id": op_id,
                        "intent_id": intent_id,
                        "success": True,
                        "action_allowed": result["action_allowed"],
                        "safety_level": result["safety_level"]
                    })
                    
                except Exception as e:
                    operations.append({
                        "thread_id": thread_id,
                        "operation_id": op_id,
                        "success": False,
                        "error": str(e)
                    })
                    
            return operations
            
        # Execute safety operations concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(safety_operations, i) for i in range(num_threads)]
            
            all_operations = []
            for future in as_completed(futures):
                all_operations.extend(future.result())
                
        # Analyze safety monitoring results
        successful_ops = [op for op in all_operations if op["success"]]
        failed_ops = [op for op in all_operations if not op["success"]]
        allowed_ops = [op for op in successful_ops if op.get("action_allowed", False)]
        
        total_ops = num_threads * operations_per_thread
        success_rate = len(successful_ops) / total_ops
        allowed_rate = len(allowed_ops) / len(successful_ops) if successful_ops else 0
        
        # Safety monitoring should handle concurrent operations
        assert success_rate >= 0.9, f"Low safety monitoring success rate: {success_rate:.2%}"
        assert allowed_rate >= 0.8, f"Too many operations blocked: {allowed_rate:.2%}"
        
        # Check safety system integrity
        safety_status = self.rcd.get_safety_status()
        assert safety_status["is_active"] == True
        
        return {
            "total_operations": total_ops,
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "allowed_operations": len(allowed_ops),
            "success_rate": success_rate,
            "allowed_rate": allowed_rate,
            "safety_system_integrity": safety_status["is_active"]
        }


class TestResourceMonitoring:
    """
    Test system resource usage and performance characteristics
    """
    
    def setup_method(self):
        """Setup for each test"""
        self.hro = ThreeDimensionalHRO()
        self.duet_system = DuetMindSystem()
        
    def monitor_system_resources(self):
        """Get current system resource usage"""
        process = psutil.Process(os.getpid())
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "num_fds": process.num_fds() if hasattr(process, 'num_fds') else -1
        }
        
    def test_cpu_usage_profiling(self):
        """Profile CPU usage during various operations"""
        baseline_resources = self.monitor_system_resources()
        
        # Test different reasoning modes
        reasoning_profiles = {}
        
        modes = [ReasoningMode.SEQUENTIAL, ReasoningMode.NEURAL, ReasoningMode.HYBRID]
        
        for mode in modes:
            self.hro.set_configuration(mode, ComputeBackend.LOCAL, OptimizationStrategy.SIMPLE)
            
            # Warm up
            self.hro.execute_task({"patterns": np.array([1, 2, 3])})
            
            # Profile execution
            start_resources = self.monitor_system_resources()
            start_time = time.time()
            
            # Execute multiple tasks
            for i in range(10):
                task = {
                    "problem": {"type": "arithmetic", "operands": [i, i+1], "operator": "+"},
                    "patterns": np.random.randn(50)
                }
                self.hro.execute_task(task)
                
            end_time = time.time()
            end_resources = self.monitor_system_resources()
            
            reasoning_profiles[mode.value] = {
                "execution_time": end_time - start_time,
                "cpu_usage": end_resources["cpu_percent"] - start_resources["cpu_percent"],
                "memory_usage": end_resources["memory_mb"] - start_resources["memory_mb"],
                "avg_time_per_task": (end_time - start_time) / 10
            }
            
        # All modes should complete in reasonable time
        for mode, profile in reasoning_profiles.items():
            assert profile["execution_time"] < 10.0, f"Mode {mode} too slow: {profile['execution_time']:.3f}s"
            assert profile["avg_time_per_task"] < 1.0, f"Mode {mode} per-task too slow: {profile['avg_time_per_task']:.3f}s"
            
        return {
            "baseline_resources": baseline_resources,
            "reasoning_profiles": reasoning_profiles
        }
        
    def test_memory_usage_profiling(self):
        """Profile memory usage during operations"""
        initial_memory = self.monitor_system_resources()["memory_mb"]
        
        # Test memory usage with different data sizes
        memory_profiles = {}
        
        data_sizes = [100, 1000, 5000]
        
        for size in data_sizes:
            # Create data
            large_data = {"patterns": np.random.randn(size)}
            
            # Monitor memory before
            memory_before = self.monitor_system_resources()["memory_mb"]
            
            # Execute task
            start_time = time.time()
            result = self.hro.execute_task(large_data)
            execution_time = time.time() - start_time
            
            # Monitor memory after
            memory_after = self.monitor_system_resources()["memory_mb"]
            memory_used = memory_after - memory_before
            
            memory_profiles[f"size_{size}"] = {
                "data_size": size,
                "execution_time": execution_time,
                "memory_used_mb": memory_used,
                "memory_efficiency": size / (memory_used + 1e-6),  # elements per MB
                "success": result is not None
            }
            
        # Memory usage should be reasonable
        for size_key, profile in memory_profiles.items():
            assert profile["success"], f"Failed execution for {size_key}"
            assert profile["memory_used_mb"] < 100, f"Excessive memory usage for {size_key}: {profile['memory_used_mb']:.1f}MB"
            
        return {
            "initial_memory_mb": initial_memory,
            "memory_profiles": memory_profiles
        }
        
    def test_scalability_benchmarks(self):
        """Test system scalability with increasing load"""
        benchmark_results = {}
        
        # Test agent scalability
        agent_counts = [1, 5, 10, 20]
        
        for count in agent_counts:
            start_time = time.time()
            start_resources = self.monitor_system_resources()
            
            # Create agents
            agents = []
            for i in range(count):
                style = StyleVector(
                    logic=0.5 + (i % 2) * 0.3,  # Vary styles
                    creativity=0.5 - (i % 2) * 0.3
                )
                agent = self.duet_system.create_agent(f"scale_test_{i}", style)
                agents.append(agent)
                
            # Test interactions
            for agent in agents:
                agent.process_prompt(f"Test prompt for {agent.agent_id}")
                
            end_time = time.time()
            end_resources = self.monitor_system_resources()
            
            benchmark_results[f"agents_{count}"] = {
                "agent_count": count,
                "creation_time": end_time - start_time,
                "time_per_agent": (end_time - start_time) / count,
                "memory_per_agent": (end_resources["memory_mb"] - start_resources["memory_mb"]) / count,
                "cpu_usage": end_resources["cpu_percent"] - start_resources["cpu_percent"]
            }
            
        # Scalability should be reasonable
        for count_key, benchmark in benchmark_results.items():
            assert benchmark["time_per_agent"] < 1.0, f"Agent creation too slow for {count_key}: {benchmark['time_per_agent']:.3f}s per agent"
            assert benchmark["memory_per_agent"] < 10.0, f"Excessive memory per agent for {count_key}: {benchmark['memory_per_agent']:.1f}MB per agent"
            
        return benchmark_results
        
    def test_performance_bottlenecks(self):
        """Identify potential performance bottlenecks"""
        bottleneck_tests = {}
        
        # Test 1: Large pattern analysis
        start_time = time.time()
        large_pattern_task = {"patterns": np.random.randn(10000)}
        
        try:
            self.hro.set_configuration(ReasoningMode.NEURAL, ComputeBackend.LOCAL, OptimizationStrategy.SIMPLE)
            result = self.hro.execute_task(large_pattern_task)
            large_pattern_time = time.time() - start_time
            large_pattern_success = True
        except Exception as e:
            large_pattern_time = time.time() - start_time
            large_pattern_success = False
            
        # Test 2: Complex optimization
        start_time = time.time()
        complex_search_space = [{"solution": f"opt_{i}", "cost": np.random.random()} for i in range(1000)]
        complex_task = {"search_space": complex_search_space}
        
        try:
            self.hro.set_configuration(ReasoningMode.SEQUENTIAL, ComputeBackend.LOCAL, OptimizationStrategy.COMPLEX)
            result = self.hro.execute_task(complex_task)
            complex_opt_time = time.time() - start_time
            complex_opt_success = True
        except Exception as e:
            complex_opt_time = time.time() - start_time
            complex_opt_success = False
            
        # Test 3: Many small tasks
        start_time = time.time()
        small_tasks_success = True
        
        try:
            for i in range(100):
                small_task = {"problem": {"type": "arithmetic", "operands": [i, 1], "operator": "+"}}
                result = self.hro.execute_task(small_task)
            many_small_time = time.time() - start_time
        except Exception as e:
            many_small_time = time.time() - start_time
            small_tasks_success = False
            
        bottleneck_tests = {
            "large_pattern_analysis": {
                "execution_time": large_pattern_time,
                "success": large_pattern_success,
                "bottleneck_risk": large_pattern_time > 5.0
            },
            "complex_optimization": {
                "execution_time": complex_opt_time,
                "success": complex_opt_success,
                "bottleneck_risk": complex_opt_time > 3.0
            },
            "many_small_tasks": {
                "execution_time": many_small_time,
                "success": small_tasks_success,
                "time_per_task": many_small_time / 100,
                "bottleneck_risk": many_small_time > 10.0
            }
        }
        
        # Identify bottlenecks
        identified_bottlenecks = [test for test, results in bottleneck_tests.items() 
                                if results["bottleneck_risk"]]
        
        return {
            "bottleneck_tests": bottleneck_tests,
            "identified_bottlenecks": identified_bottlenecks,
            "performance_acceptable": len(identified_bottlenecks) < 2
        }


class TestPerformanceIntegration:
    """Integration tests for performance and scalability"""
    
    def test_comprehensive_performance_evaluation(self):
        """Comprehensive performance evaluation of the entire system"""
        # Initialize components
        hro = ThreeDimensionalHRO()
        duet_system = DuetMindSystem()
        rcd = CognitiveRCD()
        
        performance_metrics = {}
        
        # 1. Basic performance test
        start_time = time.time()
        basic_task = {"problem": {"type": "arithmetic", "operands": [25, 17], "operator": "+"}}
        result = hro.execute_task(basic_task)
        basic_time = time.time() - start_time
        
        performance_metrics["basic_execution"] = {
            "time": basic_time,
            "success": result is not None,
            "acceptable": basic_time < 1.0
        }
        
        # 2. Agent performance test
        start_time = time.time()
        style = StyleVector(logic=0.6, creativity=0.4)
        agent = duet_system.create_agent("perf_test", style)
        response = agent.process_prompt("Performance test prompt")
        agent_time = time.time() - start_time
        
        performance_metrics["agent_interaction"] = {
            "time": agent_time,
            "success": response is not None,
            "acceptable": agent_time < 1.0
        }
        
        # 3. Safety monitoring performance test
        start_time = time.time()
        intent = Intent("perf test", ActionType.COMPUTATION, "outcome", [])
        intent_id = rcd.register_intent(intent)
        action = Action("perf action", ActionType.COMPUTATION, {}, [])
        safety_result = rcd.monitor_action(intent_id, action)
        safety_time = time.time() - start_time
        
        performance_metrics["safety_monitoring"] = {
            "time": safety_time,
            "success": safety_result is not None,
            "acceptable": safety_time < 0.5
        }
        
        # 4. Overall system health
        all_acceptable = all(metric["acceptable"] for metric in performance_metrics.values())
        total_time = sum(metric["time"] for metric in performance_metrics.values())
        
        performance_metrics["overall"] = {
            "total_time": total_time,
            "all_components_acceptable": all_acceptable,
            "system_responsive": total_time < 3.0
        }
        
        # Performance should meet benchmarks
        assert all_acceptable, f"Performance benchmarks not met: {performance_metrics}"
        assert total_time < 5.0, f"Total execution time too high: {total_time:.3f}s"
        
        return performance_metrics


if __name__ == "__main__":
    # Run the performance and scalability tests
    pytest.main([__file__, "-v"])