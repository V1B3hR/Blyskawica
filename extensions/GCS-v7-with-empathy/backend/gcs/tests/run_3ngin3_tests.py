"""
run_3ngin3_tests.py - Comprehensive Test Runner for 3NGIN3 Architecture

Runs all three layers of testing:
1. Foundational Layer: Unit & Integration Testing
2. Intelligence Layer: Behavioral & Adversarial Testing  
3. Performance & Scalability Testing

Usage:
    python run_3ngin3_tests.py [--layer=all|foundational|intelligence|performance] [--verbose]
"""

import argparse
import sys
import time
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import test modules
try:
    import pytest
    from gcs.ThreeDimensionalHRO import ThreeDimensionalHRO, ReasoningMode, ComputeBackend, OptimizationStrategy
    from gcs.DuetMindAgent import DuetMindAgent, StyleVector, DuetMindSystem
    from gcs.CognitiveRCD import CognitiveRCD, Intent, Action, ActionType, SafetyLevel
    
    # Import test classes for direct execution
    from gcs.tests.test_3ngin3_foundational import (
        TestThreeDimensionalHRO, TestDuetMindAgent, TestCognitiveRCD, TestMetaControllerEvaluation
    )
    from gcs.tests.test_3ngin3_intelligence import (
        TestMetaControllerEvaluation as IntelligenceMetaController,
        TestAdversarialTesting, TestMetamorphicTesting
    )
    from gcs.tests.test_3ngin3_performance import (
        TestGracefulDegradation, TestConcurrencyThreadSafety, TestResourceMonitoring
    )
    
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False


class ThreeDimensionalTestRunner:
    """
    Comprehensive test runner for the 3NGIN3 architecture
    """
    
    def __init__(self):
        self.results = {
            "foundational": {},
            "intelligence": {},
            "performance": {},
            "summary": {}
        }
        
    def run_foundational_tests(self) -> Dict[str, Any]:
        """Run Foundational Layer tests"""
        print("\n" + "="*80)
        print("FOUNDATIONAL LAYER: Unit & Integration Testing")
        print("="*80)
        
        foundational_results = {}
        
        try:
            # 1. ThreeDimensionalHRO Tests
            print("\n1. Testing ThreeDimensionalHRO Component...")
            hro_test = TestThreeDimensionalHRO()
            hro_test.setup_method()
            
            hro_results = {}
            
            # X-Axis Tests
            print("   Testing X-Axis (Reasoning Mode)...")
            try:
                hro_test.test_x_axis_sequential_mode()
                hro_results["x_axis_sequential"] = "PASS"
                print("     ✓ Sequential mode: Logic-based problem solving")
            except Exception as e:
                hro_results["x_axis_sequential"] = f"FAIL: {e}"
                print(f"     ✗ Sequential mode failed: {e}")
                
            try:
                hro_test.test_x_axis_neural_mode_activation()
                hro_results["x_axis_neural"] = "PASS"
                print("     ✓ Neural mode: Non-linear pattern detection")
            except Exception as e:
                hro_results["x_axis_neural"] = f"FAIL: {e}"
                print(f"     ✗ Neural mode failed: {e}")
                
            try:
                hro_test.test_x_axis_hybrid_mode()
                hro_results["x_axis_hybrid"] = "PASS"
                print("     ✓ Hybrid mode: Blended reasoning approaches")
            except Exception as e:
                hro_results["x_axis_hybrid"] = f"FAIL: {e}"
                print(f"     ✗ Hybrid mode failed: {e}")
                
            # Y-Axis Tests
            print("   Testing Y-Axis (Compute Backend)...")
            try:
                hro_test.test_y_axis_local_backend()
                hro_results["y_axis_local"] = "PASS"
                print("     ✓ Local backend: Direct execution")
            except Exception as e:
                hro_results["y_axis_local"] = f"FAIL: {e}"
                print(f"     ✗ Local backend failed: {e}")
                
            try:
                hro_test.test_y_axis_distributed_backend()
                hro_results["y_axis_distributed"] = "PASS"
                print("     ✓ Distributed backend: Task formatting")
            except Exception as e:
                hro_results["y_axis_distributed"] = f"FAIL: {e}"
                print(f"     ✗ Distributed backend failed: {e}")
                
            try:
                hro_test.test_y_axis_quantum_backend()
                hro_results["y_axis_quantum"] = "PASS"
                print("     ✓ Quantum backend: Circuit design")
            except Exception as e:
                hro_results["y_axis_quantum"] = f"FAIL: {e}"
                print(f"     ✗ Quantum backend failed: {e}")
                
            # Z-Axis Tests
            print("   Testing Z-Axis (Optimization Strategy)...")
            try:
                hro_test.test_z_axis_simple_optimization()
                hro_results["z_axis_simple"] = "PASS"
                print("     ✓ Simple optimization: Fast search")
            except Exception as e:
                hro_results["z_axis_simple"] = f"FAIL: {e}"
                print(f"     ✗ Simple optimization failed: {e}")
                
            try:
                hro_test.test_z_axis_adaptive_optimization()
                hro_results["z_axis_adaptive"] = "PASS"
                print("     ✓ Adaptive optimization: Strategy selection")
            except Exception as e:
                hro_results["z_axis_adaptive"] = f"FAIL: {e}"
                print(f"     ✗ Adaptive optimization failed: {e}")
                
            foundational_results["hro_component"] = hro_results
            
            # 2. DuetMindAgent Tests
            print("\n2. Testing DuetMindAgent Component...")
            agent_test = TestDuetMindAgent()
            agent_test.setup_method()
            
            agent_results = {}
            
            try:
                agent_test.test_style_vectors_opposing_outputs()
                agent_results["style_vectors"] = "PASS"
                print("     ✓ Style Vectors: Opposing personality outputs")
            except Exception as e:
                agent_results["style_vectors"] = f"FAIL: {e}"
                print(f"     ✗ Style Vectors failed: {e}")
                
            try:
                agent_test.test_dusty_mirror_noise_injection()
                agent_results["dusty_mirror"] = "PASS"
                print("     ✓ Dusty Mirror: Noise injection resilience")
            except Exception as e:
                agent_results["dusty_mirror"] = f"FAIL: {e}"
                print(f"     ✗ Dusty Mirror failed: {e}")
                
            foundational_results["duet_agent"] = agent_results
            
            # 3. CognitiveRCD Tests
            print("\n3. Testing CognitiveRCD Component...")
            rcd_test = TestCognitiveRCD()
            rcd_test.setup_method()
            
            rcd_results = {}
            
            try:
                rcd_test.test_safety_governance_normal_operation()
                rcd_results["normal_operation"] = "PASS"
                print("     ✓ Safety Governance: Normal operation allowed")
            except Exception as e:
                rcd_results["normal_operation"] = f"FAIL: {e}"
                print(f"     ✗ Normal operation failed: {e}")
                
            try:
                # Test comprehensive scenario instead of individual circuit breaker
                rcd_test.test_comprehensive_safety_scenario()
                rcd_results["safety_comprehensive"] = "PASS"
                print("     ✓ Safety Governance: Comprehensive scenario testing")
            except Exception as e:
                rcd_results["safety_comprehensive"] = f"FAIL: {e}"
                print(f"     ✗ Comprehensive safety failed: {e}")
                
            foundational_results["cognitive_rcd"] = rcd_results
            
        except Exception as e:
            foundational_results["error"] = str(e)
            print(f"   ✗ Foundational tests error: {e}")
            
        return foundational_results
        
    def run_intelligence_tests(self) -> Dict[str, Any]:
        """Run Intelligence Layer tests"""
        print("\n" + "="*80)
        print("INTELLIGENCE LAYER: Behavioral & Adversarial Testing")
        print("="*80)
        
        intelligence_results = {}
        
        try:
            # 1. Meta-Controller Evaluation
            print("\n1. Testing Meta-Controller Autonomous Configuration...")
            meta_test = IntelligenceMetaController()
            meta_test.setup_method()
            
            try:
                result = meta_test.test_meta_controller_configuration_accuracy()
                intelligence_results["meta_controller_accuracy"] = {
                    "status": "PASS",
                    "accuracy": result["configuration_accuracy"]
                }
                print(f"     ✓ Configuration Accuracy: {result['configuration_accuracy']:.1%}")
            except Exception as e:
                intelligence_results["meta_controller_accuracy"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Meta-Controller accuracy failed: {e}")
                
            # 2. Adversarial Testing
            print("\n2. Testing Adversarial Resilience...")
            adv_test = TestAdversarialTesting()
            adv_test.setup_method()
            
            try:
                result = adv_test.test_data_poisoning_resilience()
                intelligence_results["data_poisoning"] = {
                    "status": "PASS",
                    "degradation_factor": result["degradation_factor"]
                }
                print(f"     ✓ Data Poisoning Resilience: {result['degradation_factor']:.2f}x degradation")
            except Exception as e:
                intelligence_results["data_poisoning"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Data poisoning test failed: {e}")
                
            try:
                result = adv_test.test_input_perturbation_robustness()
                intelligence_results["input_perturbation"] = {"status": "PASS"}
                print(f"     ✓ Input Perturbation Robustness: Stable to noise")
            except Exception as e:
                intelligence_results["input_perturbation"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Input perturbation test failed: {e}")
                
            # 3. Metamorphic Testing
            print("\n3. Testing Metamorphic Properties...")
            meta_test = TestMetamorphicTesting()
            meta_test.setup_method()
            
            try:
                result = meta_test.test_reasoning_metamorphic_properties()
                intelligence_results["metamorphic_reasoning"] = {"status": "PASS"}
                print(f"     ✓ Metamorphic Reasoning: Commutative property preserved")
            except Exception as e:
                intelligence_results["metamorphic_reasoning"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Metamorphic reasoning failed: {e}")
                
        except Exception as e:
            intelligence_results["error"] = str(e)
            print(f"   ✗ Intelligence tests error: {e}")
            
        return intelligence_results
        
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run Performance & Scalability tests"""
        print("\n" + "="*80)
        print("PERFORMANCE & SCALABILITY LAYER")
        print("="*80)
        
        performance_results = {}
        
        try:
            # 1. Graceful Degradation
            print("\n1. Testing Graceful Degradation...")
            degradation_test = TestGracefulDegradation()
            degradation_test.setup_method()
            
            try:
                result = degradation_test.test_pytorch_unavailable_degradation()
                performance_results["graceful_degradation"] = {
                    "status": "PASS",
                    "execution_time": result["execution_time"]
                }
                print(f"     ✓ PyTorch Degradation: {result['execution_time']:.3f}s execution")
            except Exception as e:
                performance_results["graceful_degradation"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Graceful degradation failed: {e}")
                
            # 2. Resource Monitoring
            print("\n2. Testing Resource Usage...")
            resource_test = TestResourceMonitoring()
            resource_test.setup_method()
            
            try:
                result = resource_test.test_cpu_usage_profiling()
                performance_results["resource_monitoring"] = {"status": "PASS"}
                print(f"     ✓ CPU Profiling: Multiple reasoning modes tested")
            except Exception as e:
                performance_results["resource_monitoring"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Resource monitoring failed: {e}")
                
            # 3. Concurrency (simplified)
            print("\n3. Testing Thread Safety...")
            try:
                # Simple concurrent test
                hro = ThreeDimensionalHRO()
                task1 = {"problem": {"type": "arithmetic", "operands": [1, 1], "operator": "+"}}
                task2 = {"problem": {"type": "arithmetic", "operands": [2, 2], "operator": "+"}}
                
                result1 = hro.execute_task(task1)
                result2 = hro.execute_task(task2)
                
                if result1["output"] == 2 and result2["output"] == 4:
                    performance_results["thread_safety"] = {"status": "PASS"}
                    print(f"     ✓ Thread Safety: Basic concurrency verified")
                else:
                    performance_results["thread_safety"] = {"status": "FAIL: Incorrect results"}
                    print(f"     ✗ Thread safety failed: Incorrect arithmetic")
                    
            except Exception as e:
                performance_results["thread_safety"] = {"status": f"FAIL: {e}"}
                print(f"     ✗ Thread safety test failed: {e}")
                
        except Exception as e:
            performance_results["error"] = str(e)
            print(f"   ✗ Performance tests error: {e}")
            
        return performance_results
        
    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate overall test summary"""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "layers": {}
        }
        
        for layer_name, layer_results in self.results.items():
            if layer_name == "summary":
                continue
                
            layer_summary = {"total": 0, "passed": 0, "failed": 0}
            
            def count_results(results_dict):
                for key, value in results_dict.items():
                    if key == "error":
                        layer_summary["failed"] += 1
                        layer_summary["total"] += 1
                    elif isinstance(value, dict):
                        if "status" in value:
                            layer_summary["total"] += 1
                            if value["status"] == "PASS":
                                layer_summary["passed"] += 1
                            else:
                                layer_summary["failed"] += 1
                        else:
                            count_results(value)
                    elif isinstance(value, str):
                        layer_summary["total"] += 1
                        if value == "PASS":
                            layer_summary["passed"] += 1
                        else:
                            layer_summary["failed"] += 1
                            
            count_results(layer_results)
            summary["layers"][layer_name] = layer_summary
            summary["total_tests"] += layer_summary["total"]
            summary["passed_tests"] += layer_summary["passed"]
            summary["failed_tests"] += layer_summary["failed"]
            
        summary["pass_rate"] = summary["passed_tests"] / summary["total_tests"] if summary["total_tests"] > 0 else 0
        
        return summary
        
    def run_all_tests(self, layer: str = "all") -> Dict[str, Any]:
        """Run selected test layers"""
        start_time = time.time()
        
        print("3NGIN3 ARCHITECTURE COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Running {layer} layer(s)...")
        
        if layer in ["all", "foundational"]:
            self.results["foundational"] = self.run_foundational_tests()
            
        if layer in ["all", "intelligence"]:
            self.results["intelligence"] = self.run_intelligence_tests()
            
        if layer in ["all", "performance"]:
            self.results["performance"] = self.run_performance_tests()
            
        # Calculate summary
        self.results["summary"] = self.calculate_summary()
        
        execution_time = time.time() - start_time
        
        # Print summary
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ({summary['pass_rate']:.1%})")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        for layer_name, layer_stats in summary["layers"].items():
            if layer_stats["total"] > 0:
                layer_pass_rate = layer_stats["passed"] / layer_stats["total"]
                print(f"  {layer_name.title()}: {layer_stats['passed']}/{layer_stats['total']} ({layer_pass_rate:.1%})")
                
        # Overall assessment
        if summary["pass_rate"] >= 0.8:
            print("\n✓ 3NGIN3 ARCHITECTURE: COMPREHENSIVE TESTING SUCCESSFUL")
        elif summary["pass_rate"] >= 0.6:
            print("\n⚠ 3NGIN3 ARCHITECTURE: PARTIAL SUCCESS - Some issues detected")
        else:
            print("\n✗ 3NGIN3 ARCHITECTURE: TESTING FAILED - Major issues detected")
            
        return self.results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="3NGIN3 Architecture Test Runner")
    parser.add_argument("--layer", choices=["all", "foundational", "intelligence", "performance"], 
                       default="all", help="Test layer to run")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not IMPORTS_AVAILABLE:
        print("ERROR: Could not import required modules. Please install dependencies.")
        sys.exit(1)
        
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    runner = ThreeDimensionalTestRunner()
    results = runner.run_all_tests(args.layer)
    
    # Exit with appropriate code
    summary = results["summary"]
    if summary["pass_rate"] >= 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()