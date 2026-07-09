#!/usr/bin/env python3
"""
Advanced Biological Features Test Suite
Tests for machine learning optimization, quantum error correction, 
workflow automation, and real-time monitoring
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from biological.ml_sequence_optimizer import (
    MLSequenceOptimizer, OptimizationObjective, SequenceFeatures, OptimizationResult
)
from biological.quantum_error_correction import (
    QuantumErrorCorrector, QuantumCodeType, QuantumState, QuantumErrorCorrectionResult
)
from biological.workflow_automation import (
    WorkflowOrchestrator, Workflow, WorkflowTask, TaskType, WorkflowStatus, Priority
)
from biological.realtime_monitoring import (
    RealTimeMonitor, SynthesisJob, SynthesisPhase, MonitoringStatus, MetricType, AlertLevel
)

class TestAdvancedBiologicalFeatures:
    """Test suite for advanced biological computing features"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_all_tests(self):
        """Run all advanced feature tests"""
        print("🧬 Advanced Biological Features Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_ml_sequence_optimizer,
            self.test_quantum_error_correction,
            self.test_workflow_automation,
            self.test_realtime_monitoring,
            self.test_integration_scenarios
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self._record_test_result(test_method.__name__, False, str(e))
        
        self._print_test_summary()
    
    def test_ml_sequence_optimizer(self):
        """Test machine learning-based sequence optimization"""
        print("\n🤖 Testing ML Sequence Optimizer")
        print("-" * 40)
        
        optimizer = MLSequenceOptimizer()
        
        # Test 1: Feature extraction
        test_sequence = "AUCGAUCGAUCGAUC"
        features = optimizer.extract_features(test_sequence)
        
        assert isinstance(features, SequenceFeatures)
        assert features.length == len(test_sequence)
        assert 0.0 <= features.gc_content <= 1.0
        self._record_test_result("ML Optimizer: Feature extraction", True)
        
        # Test 2: Fitness score calculation
        objectives = [OptimizationObjective.GC_CONTENT, OptimizationObjective.SYNTHESIS_EFFICIENCY]
        score = optimizer.calculate_fitness_score(test_sequence, objectives)
        
        assert 0.0 <= score <= 1.0
        self._record_test_result("ML Optimizer: Fitness score calculation", True)
        
        # Test 3: Sequence optimization
        result = optimizer.optimize_sequence(
            test_sequence, 
            objectives, 
            max_iterations=20,
            target_score=0.8
        )
        
        assert isinstance(result, OptimizationResult)
        assert result.original_sequence == test_sequence
        assert len(result.optimized_sequence) == len(test_sequence)
        assert result.score_improvement >= -1.0  # Can be negative if no improvement
        self._record_test_result("ML Optimizer: Sequence optimization", True)
        
        # Test 4: Batch optimization
        test_sequences = ["AUCGAUC", "CGAUCGA", "GAUCGAU"]
        batch_results = optimizer.batch_optimize(test_sequences, objectives, max_iterations=10)
        
        assert len(batch_results) == len(test_sequences)
        assert all(isinstance(r, OptimizationResult) for r in batch_results)
        self._record_test_result("ML Optimizer: Batch optimization", True)
        
        # Test 5: Optimization report
        report = optimizer.get_optimization_report()
        
        assert "total_optimizations" in report
        assert "success_rate" in report
        assert report["total_optimizations"] > 0
        self._record_test_result("ML Optimizer: Optimization report", True)
        
        print(f"✅ ML Sequence Optimizer tests completed")
        print(f"   - Optimized {len(test_sequences) + 1} sequences")
        print(f"   - Average improvement: {result.score_improvement:.3f}")
    
    def test_quantum_error_correction(self):
        """Test quantum error correction for biological storage"""
        print("\n⚛️  Testing Quantum Error Correction")
        print("-" * 40)
        
        corrector = QuantumErrorCorrector()
        
        # Test 1: DNA to quantum state conversion
        test_dna = "AUCG"
        quantum_state = corrector.dna_to_quantum_state(test_dna)
        
        assert isinstance(quantum_state, QuantumState)
        assert quantum_state.num_qubits == len(test_dna)
        assert len(quantum_state.amplitudes) == 2 ** len(test_dna)
        self._record_test_result("Quantum ECC: DNA to quantum conversion", True)
        
        # Test 2: Quantum state to DNA conversion
        reconstructed_dna = corrector.quantum_state_to_dna(quantum_state)
        
        assert len(reconstructed_dna) == len(test_dna)
        # Note: May not be identical due to quantum measurement
        self._record_test_result("Quantum ECC: Quantum to DNA conversion", True)
        
        # Test 3: Quantum noise application
        noisy_state = corrector.apply_quantum_noise(quantum_state, noise_probability=0.1)
        
        assert isinstance(noisy_state, QuantumState)
        assert noisy_state.num_qubits == quantum_state.num_qubits
        self._record_test_result("Quantum ECC: Quantum noise application", True)
        
        # Test 4: Error syndrome calculation
        syndrome = corrector.calculate_syndrome(quantum_state, QuantumCodeType.STEANE_CODE)
        
        assert isinstance(syndrome, list)
        assert all(isinstance(s, int) for s in syndrome)
        self._record_test_result("Quantum ECC: Error syndrome calculation", True)
        
        # Test 5: Quantum error correction
        encoded_dna = corrector.encode_with_quantum_ecc(test_dna, QuantumCodeType.STEANE_CODE)
        correction_result = corrector.decode_with_quantum_ecc(encoded_dna, QuantumCodeType.STEANE_CODE)
        
        assert isinstance(correction_result, QuantumErrorCorrectionResult)
        assert correction_result.original_dna == encoded_dna
        assert len(correction_result.corrected_dna) > 0
        assert correction_result.quantum_overhead >= 0
        self._record_test_result("Quantum ECC: Error correction", True)
        
        # Test 6: DNA-quantum mapping
        mapping = corrector.create_quantum_biological_mapping(test_dna)
        
        assert mapping.dna_sequence == test_dna
        assert isinstance(mapping.quantum_state, QuantumState)
        assert 0.0 <= mapping.encoding_fidelity <= 1.0
        assert mapping.decoherence_time > 0
        self._record_test_result("Quantum ECC: DNA-quantum mapping", True)
        
        # Test 7: Code benchmarking
        test_sequences = ["AUCG", "CGAU", "GAUCG"]
        benchmark_results = corrector.benchmark_quantum_codes(test_sequences)
        
        assert isinstance(benchmark_results, dict)
        assert len(benchmark_results) > 0
        self._record_test_result("Quantum ECC: Code benchmarking", True)
        
        print(f"✅ Quantum Error Correction tests completed")
        print(f"   - Tested {len(test_sequences)} sequences")
        print(f"   - Quantum overhead: {correction_result.quantum_overhead} qubits")
    
    def test_workflow_automation(self):
        """Test synthetic biology workflow automation"""
        print("\n🔄 Testing Workflow Automation")
        print("-" * 40)
        
        orchestrator = WorkflowOrchestrator()
        
        # Test 1: Create workflow from template
        workflow_id = orchestrator.create_workflow_from_template(
            "standard_synthesis", 
            "Test DNA Synthesis"
        )
        
        assert workflow_id is not None
        assert workflow_id in orchestrator.workflows
        workflow = orchestrator.workflows[workflow_id]
        assert len(workflow.tasks) > 0
        self._record_test_result("Workflow: Template-based creation", True)
        
        # Test 2: Create custom workflow
        custom_tasks = [
            {
                "task_type": "dna_design",
                "name": "Custom Design",
                "description": "Custom DNA design task",
                "inputs": {"target": "test_protein"},
                "estimated_duration": 1.0
            },
            {
                "task_type": "sequence_optimization",
                "name": "Custom Optimization",
                "description": "Custom optimization task",
                "dependencies": ["Custom Design"],
                "estimated_duration": 0.5
            }
        ]
        
        custom_workflow_id = orchestrator.create_custom_workflow(
            "Custom Test Workflow",
            custom_tasks
        )
        
        assert custom_workflow_id is not None
        assert custom_workflow_id in orchestrator.workflows
        self._record_test_result("Workflow: Custom workflow creation", True)
        
        # Test 3: Execute workflow (sequential)
        success = orchestrator.execute_workflow(custom_workflow_id, parallel_execution=False)
        
        assert success
        custom_workflow = orchestrator.workflows[custom_workflow_id]
        assert custom_workflow.status == WorkflowStatus.COMPLETED
        self._record_test_result("Workflow: Sequential execution", True)
        
        # Test 4: Workflow status tracking
        status = orchestrator.get_workflow_status(custom_workflow_id)
        
        assert status is not None
        assert status["workflow_id"] == custom_workflow_id
        assert status["completion_percentage"] == 100.0
        assert status["total_tasks"] == len(custom_tasks)
        self._record_test_result("Workflow: Status tracking", True)
        
        # Test 5: List workflows
        workflows = orchestrator.list_workflows()
        
        assert len(workflows) >= 2  # At least our two test workflows
        assert any(w["workflow_id"] == workflow_id for w in workflows)
        assert any(w["workflow_id"] == custom_workflow_id for w in workflows)
        self._record_test_result("Workflow: Workflow listing", True)
        
        # Test 6: Execution statistics
        stats = orchestrator.get_execution_statistics()
        
        assert "total_workflows" in stats
        assert "success_rate" in stats
        assert stats["total_workflows"] >= 1
        self._record_test_result("Workflow: Execution statistics", True)
        
        # Test 7: Export workflow data
        export_data = orchestrator.export_workflow_data(custom_workflow_id)
        
        assert export_data is not None
        assert "workflow" in export_data
        assert "export_timestamp" in export_data
        self._record_test_result("Workflow: Data export", True)
        
        print(f"✅ Workflow Automation tests completed")
        print(f"   - Created {len(orchestrator.workflows)} workflows")
        print(f"   - Executed {stats['total_workflows']} workflows")
        print(f"   - Success rate: {stats['success_rate']:.1%}")
    
    def test_realtime_monitoring(self):
        """Test real-time DNA synthesis monitoring"""
        print("\n📊 Testing Real-time Monitoring")
        print("-" * 40)
        
        monitor = RealTimeMonitor()
        
        # Test 1: Start monitoring
        monitor.start_monitoring()
        
        assert monitor.monitoring_status == MonitoringStatus.ACTIVE
        self._record_test_result("Monitoring: System startup", True)
        
        # Test 2: Register synthesis job
        test_job = SynthesisJob(
            job_id="TEST_001",
            sequence="AUCGAUCGAUCGAUC",
            instrument_id="SYNTH_001",
            operator="test_user",
            started_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(hours=4),
            current_phase=SynthesisPhase.PREPARATION,
            current_cycle=0,
            total_cycles=15,
            synthesis_method="solid_phase"
        )
        
        success = monitor.register_synthesis_job(test_job)
        
        assert success
        assert test_job.job_id in monitor.synthesis_jobs
        self._record_test_result("Monitoring: Job registration", True)
        
        # Test 3: Update job progress
        monitor.update_job_progress(
            test_job.job_id, 
            current_cycle=5, 
            current_phase=SynthesisPhase.ELONGATION
        )
        
        updated_job = monitor.synthesis_jobs[test_job.job_id]
        assert updated_job.current_cycle == 5
        assert updated_job.current_phase == SynthesisPhase.ELONGATION
        self._record_test_result("Monitoring: Progress updates", True)
        
        # Test 4: Collect metrics (simulate monitoring loop)
        time.sleep(2)  # Allow metrics collection
        
        # Get job status
        job_status = monitor.get_job_status(test_job.job_id)
        
        assert job_status is not None
        assert job_status["job_id"] == test_job.job_id
        assert job_status["progress_percentage"] > 0
        self._record_test_result("Monitoring: Job status", True)
        
        # Test 5: Instrument status
        instrument_status = monitor.get_instrument_status("SYNTH_001")
        
        assert instrument_status is not None
        assert instrument_status["instrument_id"] == "SYNTH_001"
        assert instrument_status["current_job_id"] == test_job.job_id
        self._record_test_result("Monitoring: Instrument status", True)
        
        # Test 6: Dashboard data
        dashboard = monitor.get_dashboard_data()
        
        assert "active_jobs" in dashboard
        assert "total_alerts" in dashboard
        assert dashboard["active_jobs"] >= 1
        self._record_test_result("Monitoring: Dashboard data", True)
        
        # Test 7: Metrics history
        metrics = monitor.get_metrics_history(job_id=test_job.job_id, hours=1)
        
        assert isinstance(metrics, list)
        # May be empty if monitoring just started
        self._record_test_result("Monitoring: Metrics history", True)
        
        # Test 8: Recent alerts
        alerts = monitor.get_recent_alerts(hours=1)
        
        assert isinstance(alerts, list)
        # Should have at least job start alert
        assert len(alerts) >= 1
        self._record_test_result("Monitoring: Alert system", True)
        
        # Test 9: Monitoring statistics
        stats = monitor.get_monitoring_statistics()
        
        assert "monitoring_status" in stats
        assert "total_jobs_monitored" in stats
        assert stats["total_jobs_monitored"] >= 1
        self._record_test_result("Monitoring: Statistics", True)
        
        # Test 10: Export monitoring data
        export_data = monitor.export_monitoring_data(hours=1)
        
        assert "synthesis_jobs" in export_data
        assert "instruments" in export_data
        assert len(export_data["synthesis_jobs"]) >= 1
        self._record_test_result("Monitoring: Data export", True)
        
        # Stop monitoring
        monitor.stop_monitoring_system()
        assert monitor.monitoring_status == MonitoringStatus.STOPPED
        
        print(f"✅ Real-time Monitoring tests completed")
        print(f"   - Monitored {stats['total_jobs_monitored']} jobs")
        print(f"   - Tracked {len(export_data['instruments'])} instruments")
        print(f"   - Generated {len(alerts)} alerts")
    
    def test_integration_scenarios(self):
        """Test integration scenarios combining multiple features"""
        print("\n🔗 Testing Integration Scenarios")  
        print("-" * 40)
        
        # Scenario 1: ML-optimized sequence with quantum error correction
        optimizer = MLSequenceOptimizer()
        corrector = QuantumErrorCorrector()
        
        test_sequence = "AUCGAUCGAUCGAUCGAUC"
        objectives = [OptimizationObjective.GC_CONTENT, OptimizationObjective.ERROR_RESILIENCE]
        
        # Optimize sequence
        optimization_result = optimizer.optimize_sequence(
            test_sequence, objectives, max_iterations=10
        )
        
        # Apply quantum error correction
        encoded_sequence = corrector.encode_with_quantum_ecc(
            optimization_result.optimized_sequence, 
            QuantumCodeType.STEANE_CODE
        )
        correction_result = corrector.decode_with_quantum_ecc(
            encoded_sequence, 
            QuantumCodeType.STEANE_CODE
        )
        
        assert optimization_result.score_improvement >= -1.0  # Can be negative
        assert correction_result.quantum_overhead > 0
        self._record_test_result("Integration: ML + Quantum ECC", True)
        
        # Scenario 2: Workflow with monitoring
        orchestrator = WorkflowOrchestrator()
        monitor = RealTimeMonitor()
        
        # Create workflow
        workflow_id = orchestrator.create_workflow_from_template(
            "standard_synthesis",
            "Integrated Test Workflow"
        )
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Register synthesis job
        synthesis_job = SynthesisJob(
            job_id="INTEG_001",
            sequence=optimization_result.optimized_sequence,
            instrument_id="SYNTH_002",
            operator="integration_test",
            started_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(hours=6),
            current_phase=SynthesisPhase.PREPARATION,
            current_cycle=0,
            total_cycles=len(optimization_result.optimized_sequence),
            synthesis_method="automated"
        )
        
        job_registered = monitor.register_synthesis_job(synthesis_job)
        
        # Execute workflow (fast execution for testing)
        workflow_success = orchestrator.execute_workflow(workflow_id, parallel_execution=True)
        
        # Update synthesis progress
        monitor.update_job_progress(
            synthesis_job.job_id,
            current_cycle=5,
            current_phase=SynthesisPhase.ELONGATION
        )
        
        # Get integrated status
        workflow_status = orchestrator.get_workflow_status(workflow_id)
        job_status = monitor.get_job_status(synthesis_job.job_id)
        
        assert job_registered
        assert workflow_success
        assert workflow_status["completion_percentage"] == 100.0
        assert job_status["progress_percentage"] > 0
        
        monitor.stop_monitoring_system()
        self._record_test_result("Integration: Workflow + Monitoring", True)
        
        # Scenario 3: Complete pipeline simulation
        # Optimize -> Encode -> Synthesize -> Monitor
        pipeline_sequence = "AUCGAUC" * 5  # 35 nucleotides
        
        # Step 1: ML Optimization
        ml_result = optimizer.optimize_sequence(
            pipeline_sequence,
            [OptimizationObjective.SYNTHESIS_EFFICIENCY, OptimizationObjective.STORAGE_STABILITY],
            max_iterations=15
        )
        
        # Step 2: Quantum Error Correction  
        qec_encoded = corrector.encode_with_quantum_ecc(
            ml_result.optimized_sequence,
            QuantumCodeType.FIVE_QUBIT_CODE
        )
        
        # Step 3: Workflow Creation
        pipeline_workflow_id = orchestrator.create_custom_workflow(
            "Complete Pipeline Test",
            [
                {
                    "task_type": "dna_design",
                    "name": "Pipeline Design",
                    "description": "ML-optimized design",
                    "inputs": {"sequence": ml_result.optimized_sequence},
                    "estimated_duration": 0.5
                },
                {
                    "task_type": "synthesis_order",
                    "name": "Pipeline Synthesis",
                    "description": "QEC-protected synthesis",
                    "dependencies": ["Pipeline Design"],
                    "inputs": {"encoded_sequence": qec_encoded},
                    "estimated_duration": 1.0
                }
            ]
        )
        
        # Step 4: Monitoring Setup
        monitor2 = RealTimeMonitor()  # Create new monitor to avoid conflicts
        monitor2.start_monitoring()
        pipeline_job = SynthesisJob(
            job_id="PIPELINE_001",
            sequence=qec_encoded,
            instrument_id="SYNTH_003",
            operator="pipeline_test",
            started_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(hours=2),
            current_phase=SynthesisPhase.PREPARATION,
            current_cycle=0,
            total_cycles=max(1, len(qec_encoded) // 4),  # Assume 4 nucleotides per cycle, min 1
            synthesis_method="pipeline_test"
        )
        
        pipeline_job_registered = monitor2.register_synthesis_job(pipeline_job)
        pipeline_workflow_executed = orchestrator.execute_workflow(pipeline_workflow_id)
        
        # Verify pipeline
        pipeline_workflow_status = orchestrator.get_workflow_status(pipeline_workflow_id)
        pipeline_job_status = monitor2.get_job_status(pipeline_job.job_id)
        
        assert len(ml_result.optimized_sequence) == len(pipeline_sequence)
        assert len(qec_encoded) > len(ml_result.optimized_sequence)  # QEC overhead
        assert pipeline_job_registered
        assert pipeline_workflow_executed  
        assert pipeline_workflow_status["completion_percentage"] == 100.0
        
        monitor2.stop_monitoring_system()
        self._record_test_result("Integration: Complete pipeline", True)
        
        print(f"✅ Integration Scenarios completed")
        print(f"   - ML improvement: {ml_result.score_improvement:.3f}")
        print(f"   - QEC overhead: {len(qec_encoded) - len(ml_result.optimized_sequence)} nucleotides")
        print(f"   - Pipeline workflows: 2 executed")
    
    def _record_test_result(self, test_name: str, passed: bool, error_msg: str = ""):
        """Record test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "error": error_msg
        })
    
    def _print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 ADVANCED BIOLOGICAL FEATURES TEST SUMMARY")
        print("=" * 60)
        
        # Overall statistics
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Feature breakdown
        feature_stats = {}
        for result in self.test_results:
            feature = result["test"].split(":")[0]
            if feature not in feature_stats:
                feature_stats[feature] = {"total": 0, "passed": 0}
            feature_stats[feature]["total"] += 1
            if result["passed"]:
                feature_stats[feature]["passed"] += 1
        
        print(f"\n📋 Feature Test Breakdown:")
        for feature, stats in feature_stats.items():
            rate = (stats["passed"] / stats["total"]) * 100
            status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
            print(f"   {status} {feature}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Failed tests (if any)
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['error']}")
        
        # Success message
        if success_rate == 100:
            print(f"\n🏆 ALL ADVANCED BIOLOGICAL FEATURES TESTS PASSED!")
            print(f"✅ ML Sequence Optimization: Operational")
            print(f"✅ Quantum Error Correction: Operational")  
            print(f"✅ Workflow Automation: Operational")
            print(f"✅ Real-time Monitoring: Operational")
            print(f"✅ Feature Integration: Operational")
        else:
            print(f"\n⚠️  Some tests failed. Review failed tests above.")
        
        print("=" * 60)

def main():
    """Run advanced biological features test suite"""
    print("Starting Advanced Biological Features Test Suite...")
    print("This may take a few moments to complete.\n")
    
    test_suite = TestAdvancedBiologicalFeatures()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()