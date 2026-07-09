#!/usr/bin/env python3
"""
Advanced Biological Features Demo
Demonstration of machine learning optimization, quantum error correction, 
workflow automation, and real-time monitoring
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from biological.ml_sequence_optimizer import MLSequenceOptimizer, OptimizationObjective
from biological.quantum_error_correction import QuantumErrorCorrector, QuantumCodeType
from biological.workflow_automation import WorkflowOrchestrator, TaskType
from biological.realtime_monitoring import RealTimeMonitor, SynthesisJob, SynthesisPhase

def demo_ml_sequence_optimizer():
    """Demonstrate ML sequence optimization"""
    print("🤖 Machine Learning Sequence Optimization Demo")
    print("=" * 50)
    
    optimizer = MLSequenceOptimizer()
    
    # Example DNA sequence
    sequence = "AUCGAUCGAUCGAUCGAUC"
    print(f"Original sequence: {sequence}")
    print(f"Length: {len(sequence)} nucleotides")
    
    # Extract features
    features = optimizer.extract_features(sequence)
    print(f"\nSequence Features:")
    print(f"  GC Content: {features.gc_content:.3f}")
    print(f"  Homopolymer runs: {features.homopolymer_runs}")
    print(f"  Codon Adaptation Index: {features.codon_adaptation_index:.3f}")
    print(f"  Synthesis complexity: {features.synthesis_complexity:.3f}")
    
    # Optimize sequence
    objectives = [
        OptimizationObjective.GC_CONTENT,
        OptimizationObjective.SYNTHESIS_EFFICIENCY,
        OptimizationObjective.ERROR_RESILIENCE
    ]
    
    print(f"\nOptimizing for: {[obj.value for obj in objectives]}")
    result = optimizer.optimize_sequence(sequence, objectives, max_iterations=20)
    
    print(f"\nOptimization Results:")
    print(f"  Optimized sequence: {result.optimized_sequence}")
    print(f"  Score improvement: {result.score_improvement:.3f}")
    print(f"  Optimization steps: {result.optimization_steps}")
    
    # Show final features
    final_features = result.features_after
    print(f"\nImproved Features:")
    print(f"  GC Content: {final_features.gc_content:.3f}")
    print(f"  Synthesis complexity: {final_features.synthesis_complexity:.3f}")
    
    return result.optimized_sequence

def demo_quantum_error_correction():
    """Demonstrate quantum error correction"""
    print("\n⚛️  Quantum Error Correction Demo")
    print("=" * 50)
    
    corrector = QuantumErrorCorrector()
    
    # Example sequence
    sequence = "AUCGAUC"
    print(f"Original DNA sequence: {sequence}")
    
    # Convert to quantum state
    quantum_state = corrector.dna_to_quantum_state(sequence)
    print(f"Quantum state: {quantum_state.num_qubits} qubits, {len(quantum_state.amplitudes)} amplitudes")
    
    # Apply error correction encoding
    encoded_sequence = corrector.encode_with_quantum_ecc(sequence, QuantumCodeType.STEANE_CODE)
    print(f"Encoded sequence: {encoded_sequence}")
    print(f"Encoding overhead: {len(encoded_sequence) - len(sequence)} nucleotides")
    
    # Simulate error correction
    correction_result = corrector.decode_with_quantum_ecc(encoded_sequence, QuantumCodeType.STEANE_CODE)
    print(f"\nError Correction Results:")
    print(f"  Correction applied: {correction_result.correction_applied}")
    print(f"  Error syndrome: {correction_result.error_syndrome}")
    print(f"  Fidelity improvement: {correction_result.fidelity_improvement:.3f}")
    print(f"  Quantum overhead: {correction_result.quantum_overhead} qubits")
    
    # Create quantum-biological mapping
    mapping = corrector.create_quantum_biological_mapping(sequence)
    print(f"\nQuantum-Biological Mapping:")
    print(f"  Encoding fidelity: {mapping.encoding_fidelity:.3f}")
    print(f"  Decoherence time: {mapping.decoherence_time:.1f} time units")
    
    return encoded_sequence

def demo_workflow_automation():
    """Demonstrate workflow automation"""
    print("\n🔄 Workflow Automation Demo")
    print("=" * 50)
    
    orchestrator = WorkflowOrchestrator()
    
    # Create workflow from template
    workflow_id = orchestrator.create_workflow_from_template(
        "standard_synthesis",
        "Demo DNA Synthesis Workflow"
    )
    
    print(f"Created workflow: {workflow_id}")
    
    # Get workflow status
    status = orchestrator.get_workflow_status(workflow_id)
    print(f"Initial status: {status['status']}")
    print(f"Total tasks: {status['total_tasks']}")
    
    # Execute workflow
    print("\nExecuting workflow...")
    success = orchestrator.execute_workflow(workflow_id, parallel_execution=True)
    
    if success:
        print("✅ Workflow completed successfully!")
        
        # Get final status
        final_status = orchestrator.get_workflow_status(workflow_id)
        print(f"Final status: {final_status['status']}")
        print(f"Completion: {final_status['completion_percentage']:.1f}%")
        print(f"Duration: {final_status['duration']:.2f} hours")
        
        # Show task summary
        print(f"\nTask Summary:")
        for task_status, count in final_status['task_summary'].items():
            if count > 0:
                print(f"  {task_status}: {count} tasks")
    else:
        print("❌ Workflow execution failed")
    
    # Get execution statistics
    stats = orchestrator.get_execution_statistics()
    print(f"\nExecution Statistics:")
    print(f"  Total workflows: {stats['total_workflows']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    
    return workflow_id

def demo_realtime_monitoring():
    """Demonstrate real-time monitoring"""
    print("\n📊 Real-time Monitoring Demo")
    print("=" * 50)
    
    monitor = RealTimeMonitor()
    
    # Start monitoring
    monitor.start_monitoring()
    print("Real-time monitoring started")
    
    # Create a synthesis job
    job = SynthesisJob(
        job_id="DEMO_001",
        sequence="AUCGAUCGAUCGAUCGAUC",
        instrument_id="SYNTH_001",
        operator="demo_user",
        started_at=datetime.now(),
        estimated_completion=datetime.now() + timedelta(hours=2),
        current_phase=SynthesisPhase.PREPARATION,
        current_cycle=0,
        total_cycles=19,
        synthesis_method="demo_synthesis"
    )
    
    # Register job
    success = monitor.register_synthesis_job(job)
    if success:
        print(f"✅ Registered synthesis job: {job.job_id}")
    
    # Simulate some progress
    print("\nSimulating synthesis progress...")
    for cycle in range(1, 6):
        time.sleep(0.5)  # Brief pause
        phase = SynthesisPhase.ELONGATION if cycle > 1 else SynthesisPhase.PREPARATION
        monitor.update_job_progress(job.job_id, cycle, phase)
        
        job_status = monitor.get_job_status(job.job_id)
        print(f"  Cycle {cycle}: {job_status['progress_percentage']:.1f}% complete, Phase: {phase.value}")
    
    # Get monitoring data
    dashboard = monitor.get_dashboard_data()
    print(f"\nDashboard Data:")
    print(f"  Active jobs: {dashboard['active_jobs']}")
    print(f"  Total alerts: {dashboard['total_alerts']}")
    print(f"  Average yield: {dashboard['average_yield']:.3f}")
    print(f"  Instrument utilization: {dashboard['instrument_utilization']:.1%}")
    
    # Get recent alerts
    alerts = monitor.get_recent_alerts(hours=1)
    print(f"\nRecent Alerts: {len(alerts)}")
    for alert in alerts[:3]:  # Show first 3
        print(f"  {alert['level'].upper()}: {alert['message']}")
    
    # Get instrument status
    instrument_status = monitor.get_instrument_status("SYNTH_001")
    print(f"\nInstrument Status:")
    print(f"  Name: {instrument_status['name']}")
    print(f"  Status: {instrument_status['status']}")
    print(f"  Temperature: {instrument_status['temperature']:.1f}°C")
    print(f"  Pressure: {instrument_status['pressure']:.1f} bar")
    
    # Stop monitoring
    monitor.stop_monitoring_system()
    print("\nReal-time monitoring stopped")
    
    return job.job_id

def demo_integration_pipeline():
    """Demonstrate integration of all features"""
    print("\n🔗 Integrated Pipeline Demo")
    print("=" * 50)
    
    # Step 1: ML Optimization
    print("Step 1: ML Sequence Optimization")
    optimizer = MLSequenceOptimizer()
    sequence = "AUCGAUC" * 3  # 21 nucleotides
    objectives = [OptimizationObjective.SYNTHESIS_EFFICIENCY, OptimizationObjective.ERROR_RESILIENCE]
    
    ml_result = optimizer.optimize_sequence(sequence, objectives, max_iterations=10)
    print(f"  Optimized sequence: {ml_result.optimized_sequence}")
    print(f"  Improvement: {ml_result.score_improvement:.3f}")
    
    # Step 2: Quantum Error Correction
    print("\nStep 2: Quantum Error Correction")
    corrector = QuantumErrorCorrector()
    encoded_sequence = corrector.encode_with_quantum_ecc(
        ml_result.optimized_sequence, 
        QuantumCodeType.FIVE_QUBIT_CODE
    )
    print(f"  Encoded sequence: {encoded_sequence}")
    print(f"  QEC overhead: {len(encoded_sequence) - len(ml_result.optimized_sequence)} nucleotides")
    
    # Step 3: Workflow Creation
    print("\nStep 3: Automated Workflow")
    orchestrator = WorkflowOrchestrator()
    workflow_id = orchestrator.create_custom_workflow(
        "Integrated Pipeline Workflow",
        [
            {
                "task_type": "dna_design",
                "name": "ML-Optimized Design",
                "description": "Use ML-optimized sequence",
                "inputs": {"sequence": ml_result.optimized_sequence},
                "estimated_duration": 0.5
            },
            {
                "task_type": "synthesis_order",
                "name": "QEC-Protected Synthesis",
                "description": "Synthesize with quantum error correction",
                "dependencies": ["ML-Optimized Design"],
                "inputs": {"encoded_sequence": encoded_sequence},
                "estimated_duration": 1.0
            }
        ]
    )
    
    workflow_success = orchestrator.execute_workflow(workflow_id)
    print(f"  Workflow executed: {'✅ Success' if workflow_success else '❌ Failed'}")
    
    # Step 4: Real-time Monitoring
    print("\nStep 4: Real-time Monitoring")
    monitor = RealTimeMonitor()
    monitor.start_monitoring()
    
    pipeline_job = SynthesisJob(
        job_id="PIPELINE_DEMO",
        sequence=encoded_sequence,
        instrument_id="SYNTH_002",
        operator="pipeline_demo",
        started_at=datetime.now(),
        estimated_completion=datetime.now() + timedelta(hours=1),
        current_phase=SynthesisPhase.PREPARATION,
        current_cycle=0,
        total_cycles=max(1, len(encoded_sequence) // 4),
        synthesis_method="integrated_pipeline"
    )
    
    job_registered = monitor.register_synthesis_job(pipeline_job)
    print(f"  Job registered: {'✅ Success' if job_registered else '❌ Failed'}")
    
    # Simulate brief monitoring
    time.sleep(1)
    monitor.update_job_progress(pipeline_job.job_id, 3, SynthesisPhase.ELONGATION)
    
    final_status = monitor.get_job_status(pipeline_job.job_id)
    print(f"  Final progress: {final_status['progress_percentage']:.1f}%")
    
    monitor.stop_monitoring_system()
    
    print("\n🎉 Integrated Pipeline Complete!")
    print(f"  Original length: {len(sequence)} nucleotides")
    print(f"  Optimized length: {len(ml_result.optimized_sequence)} nucleotides")
    print(f"  Protected length: {len(encoded_sequence)} nucleotides")
    print(f"  ML improvement: {ml_result.score_improvement:.3f}")
    print(f"  QEC protection: {len(encoded_sequence) - len(ml_result.optimized_sequence)} extra nucleotides")

def main():
    """Run comprehensive demo of advanced biological features"""
    print("🧬 Advanced Biological Features Demo")
    print("="*60)
    print("Demonstrating ML optimization, quantum error correction,")
    print("workflow automation, and real-time monitoring\n")
    
    try:
        # Individual feature demos
        optimized_seq = demo_ml_sequence_optimizer()
        encoded_seq = demo_quantum_error_correction()
        workflow_id = demo_workflow_automation()
        job_id = demo_realtime_monitoring()
        
        # Integrated pipeline demo
        demo_integration_pipeline()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("All advanced biological features are operational:")
        print("✅ Machine Learning Sequence Optimization")
        print("✅ Quantum Error Correction for Biological Storage")
        print("✅ Synthetic Biology Workflow Automation")
        print("✅ Real-time DNA Synthesis Monitoring")
        print("✅ Feature Integration Pipeline")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()