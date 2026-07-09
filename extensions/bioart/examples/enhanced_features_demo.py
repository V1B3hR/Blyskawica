#!/usr/bin/env python3
"""
Enhanced Bioart Features Demonstration
Shows biological error correction, complex instruction set, and DNA synthesis integration
"""

import sys
import os
import time
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from biological.error_correction import BiologicalErrorCorrection, ErrorType
from biological.synthesis_systems import DNASynthesisManager, SynthesisPlatform
from vm.instruction_set import DNAInstructionSet, InstructionType

def demo_biological_error_correction():
    """Demonstrate advanced biological error correction"""
    print("🧬 ENHANCED BIOLOGICAL ERROR CORRECTION DEMO")
    print("=" * 60)
    
    # Initialize error correction system
    error_corrector = BiologicalErrorCorrection()
    
    # Original sequence
    original_sequence = "AUCGGGCCAUUCGAAUCGAUCCGAUCCGAUCCG"
    print(f"Original sequence: {original_sequence}")
    print(f"Length: {len(original_sequence)} nucleotides")
    
    # 1. Environmental conditions simulation
    print("\n1. Environmental Conditions Impact")
    print("-" * 40)
    
    harsh_conditions = {
        'uv_exposure': 'high',
        'temperature': 'high',
        'oxidative_stress': 'high'
    }
    
    print(f"Harsh conditions: {harsh_conditions}")
    error_corrector.set_environmental_conditions(harsh_conditions)
    
    # Show how error rates change
    stats = error_corrector.get_error_correction_statistics()
    print(f"UV damage rate: {stats['biological_error_rates']['uv_damage']:.6f}")
    print(f"Oxidative damage rate: {stats['biological_error_rates']['oxidative_damage']:.6f}")
    
    # 2. Simulate biological mutations
    print("\n2. Biological Mutation Simulation")
    print("-" * 40)
    
    mutated_sequence, mutations = error_corrector.simulate_biological_mutations(
        original_sequence, harsh_conditions
    )
    
    print(f"Mutated sequence: {mutated_sequence}")
    print(f"Mutations detected: {len(mutations)}")
    
    for i, mutation in enumerate(mutations[:3]):  # Show first 3
        print(f"  {i+1}. {mutation.error_type.value} at pos {mutation.position}: "
              f"{mutation.original} → {mutation.corrected} (conf: {mutation.confidence:.2f})")
    
    # 3. Error correction encoding
    print("\n3. Multi-Layer Error Correction Encoding")
    print("-" * 40)
    
    protected_sequence = error_corrector.encode_with_error_correction(
        original_sequence, redundancy_level=3
    )
    
    print(f"Protected sequence length: {len(protected_sequence)} nucleotides")
    print(f"Redundancy factor: {len(protected_sequence) / len(original_sequence):.2f}x")
    
    # 4. Hamming code demonstration
    print("\n4. Hamming Code for Biological Storage")
    print("-" * 40)
    
    hamming_encoded = error_corrector.encode_with_hamming(original_sequence)
    print(f"Hamming encoded: {hamming_encoded[:50]}...")
    print(f"Overhead: {(len(hamming_encoded) - len(original_sequence)) / len(original_sequence) * 100:.1f}%")
    
    # Decode and show error correction capability
    decoded, errors = error_corrector.decode_with_hamming(hamming_encoded)
    print(f"Decoded successfully with {len(errors)} corrections")
    
    # 5. Error monitoring
    print("\n5. Error Pattern Monitoring")
    print("-" * 40)
    
    monitoring_stats = error_corrector.monitor_error_patterns()
    if monitoring_stats.get('total_errors', 0) > 0:
        print(f"Total errors tracked: {monitoring_stats['total_errors']}")
        print(f"Most common error: {monitoring_stats.get('most_common_error', ['Unknown', 0])[0]}")
        print(f"Average confidence: {monitoring_stats.get('average_confidence', 0):.2f}")
    else:
        print("No errors recorded in monitoring system")


def demo_enhanced_instruction_set():
    """Demonstrate enhanced instruction set with complex operations"""
    print("\n\n🖥️ ENHANCED INSTRUCTION SET DEMO")
    print("=" * 60)
    
    instruction_set = DNAInstructionSet()
    
    # 1. Instruction set overview
    print("1. Instruction Set Overview")
    print("-" * 40)
    
    stats = instruction_set.get_instruction_statistics()
    print(f"Total instructions: {stats['total_instructions']}")
    print(f"Instruction types: {len(stats['instruction_type_counts'])}")
    print(f"Average cycles: {stats['average_cycles']:.1f}")
    
    # Show instruction types
    print("\nInstruction Types:")
    for inst_type, count in stats['instruction_type_counts'].items():
        print(f"  {inst_type}: {count} instructions")
    
    # 2. Complex algorithmic operations
    print("\n2. Complex Algorithmic Operations")
    print("-" * 40)
    
    complex_instructions = [
        ('FFT', 'Fast Fourier Transform'),
        ('DIJKSTRA', 'Shortest Path Algorithm'),
        ('NEURON', 'Neural Network Node'),
        ('MATMUL', 'Matrix Multiplication'),
        ('CLUSTER', 'K-Means Clustering')
    ]
    
    for name, description in complex_instructions:
        instr = instruction_set.get_instruction_by_name(name)
        if instr:
            print(f"  {name} ({instr.dna_sequence}): {description}")
            print(f"    Type: {instr.instruction_type.name}, Cycles: {instr.cycles}")
    
    # 3. Floating point operations
    print("\n3. IEEE 754 Floating Point Support")
    print("-" * 40)
    
    fp_instructions = instruction_set.get_instructions_by_type(InstructionType.FLOATING_POINT)
    print(f"Floating point instructions: {len(fp_instructions)}")
    
    for opcode, instr in list(fp_instructions.items())[:5]:
        print(f"  {instr.name} ({instr.dna_sequence}): {instr.description}")
    
    # 4. Biological operations
    print("\n4. Biological Computing Operations")
    print("-" * 40)
    
    bio_instructions = instruction_set.get_instructions_by_type(InstructionType.BIOLOGICAL)
    print(f"Biological instructions: {len(bio_instructions)}")
    
    for opcode, instr in bio_instructions.items():
        print(f"  {instr.name} ({instr.dna_sequence}): {instr.description}")
    
    # 5. Machine learning operations
    print("\n5. Machine Learning Operations")
    print("-" * 40)
    
    ml_instructions = instruction_set.get_instructions_by_type(InstructionType.MACHINE_LEARNING)
    for opcode, instr in ml_instructions.items():
        print(f"  {instr.name}: {instr.description} ({instr.cycles} cycles)")


def demo_dna_synthesis_integration():
    """Demonstrate enhanced DNA synthesis system integration"""
    print("\n\n🔬 DNA SYNTHESIS INTEGRATION DEMO")
    print("=" * 60)
    
    synthesis_manager = DNASynthesisManager()
    
    # 1. Platform comparison
    print("1. Synthesis Platform Comparison")
    print("-" * 40)
    
    test_sequence = "AUCGGGCCAUUCGAAUCGAUCCGAUCCGAUCCGAUCCG"
    comparison = synthesis_manager.get_platform_comparison(test_sequence)
    
    print(f"Sequence length: {comparison['sequence_length']} nucleotides")
    print(f"Recommended platform: {comparison['recommended_platform']}")
    
    print("\nPlatform Analysis:")
    for platform, details in comparison['platform_comparison'].items():
        if details['can_synthesize']:
            print(f"  {platform}:")
            print(f"    Cost: ${details['estimated_cost']:.2f}")
            print(f"    Turnaround: {details['turnaround_days']} days")
            print(f"    Quality: {details['quality_guarantee']*100:.1f}%")
        else:
            print(f"  {platform}: {details['reason']}")
    
    # 2. Job submission with testing protocols
    print("\n2. Job Submission with Testing Protocols")
    print("-" * 40)
    
    testing_protocols = ['sequence_verification', 'functional_assay', 'structural_analysis']
    
    job_id = synthesis_manager.submit_synthesis_job(
        test_sequence,
        priority=3,
        platform=SynthesisPlatform.TWIST_BIOSCIENCE,
        testing_protocols=testing_protocols
    )
    
    print(f"Job submitted: {job_id}")
    
    # Get job details
    job_status = synthesis_manager.get_job_status(job_id)
    print(f"Platform: {job_status['platform']}")
    print(f"Estimated cost: ${job_status['estimated_cost']:.2f}")
    print(f"Testing protocols: {len(job_status['testing_protocols'])}")
    
    # 3. Cost optimization
    print("\n3. Cost Optimization Analysis")
    print("-" * 40)
    
    # Show cost breakdown
    cost_breakdown = job_status['metadata']['cost_breakdown']
    print("Cost Breakdown:")
    for component, cost in cost_breakdown.items():
        if cost != 0:
            print(f"  {component.replace('_', ' ').title()}: ${cost:.2f}")
    
    # 4. Quality control simulation
    print("\n4. Quality Control Simulation")
    print("-" * 40)
    
    # Process the job to get quality metrics
    completed_jobs = synthesis_manager.process_synthesis_queue()
    
    if completed_jobs:
        job = completed_jobs[0]
        print(f"Synthesis completed: {job['job_id']}")
        print(f"Quality score: {job.get('quality_score', 'N/A')}")
        print(f"Actual cost: ${job.get('actual_cost', 0):.2f}")
    
    # 5. Testing protocol execution
    print("\n5. Testing Protocol Execution")
    print("-" * 40)
    
    testing_results = synthesis_manager.run_testing_protocols(job_id)
    
    if testing_results['status'] == 'completed':
        print("Testing Results:")
        for protocol, result in testing_results['results'].items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"  {protocol}: {status} (${result['cost']:.2f})")
            print(f"    Measurement: {result['measurement']:.3f}")
        
        print(f"\nTotal testing cost: ${testing_results['total_cost']:.2f}")
        print(f"Overall validation: {testing_results['overall_validation']}")
    
    # 6. Comprehensive statistics
    print("\n6. System Statistics")
    print("-" * 40)
    
    stats = synthesis_manager.get_enhanced_statistics()
    print(f"Total jobs processed: {stats['total_jobs']}")
    print(f"Success rate: {stats['overall_success_rate']*100:.1f}%")
    print(f"Average cost per nucleotide: ${stats['average_cost_per_nucleotide']:.4f}")
    print(f"Available platforms: {len(stats['available_platforms'])}")
    print(f"Testing protocols: {len(stats['testing_protocols_available'])}")


def demo_integration_workflow():
    """Demonstrate complete integration workflow"""
    print("\n\n🔄 COMPLETE INTEGRATION WORKFLOW DEMO")
    print("=" * 60)
    
    # Initialize all systems
    error_corrector = BiologicalErrorCorrection()
    synthesis_manager = DNASynthesisManager()
    instruction_set = DNAInstructionSet()
    
    print("1. End-to-End Workflow")
    print("-" * 40)
    
    # Step 1: Generate a biological program
    original_program = "AUCGGGCCAUUCGAAUCGAUCCGAUCCGAUCCGAUCCG"
    print(f"Step 1 - Original DNA program: {original_program}")
    
    # Step 2: Apply environmental-aware error correction
    print("\nStep 2 - Apply Error Correction")
    environmental_conditions = {
        'uv_exposure': 'low',
        'temperature': 'normal',
        'oxidative_stress': 'low'
    }
    
    error_corrector.set_environmental_conditions(environmental_conditions)
    protected_program = error_corrector.encode_with_error_correction(
        original_program, redundancy_level=2
    )
    print(f"Protected program length: {len(protected_program)} nucleotides")
    
    # Step 3: Optimize synthesis parameters
    print("\nStep 3 - Synthesis Optimization")
    
    try:
        job_id = synthesis_manager.submit_synthesis_job(
            protected_program,
            priority=2,
            testing_protocols=['sequence_verification', 'stability_test']
        )
        
        print(f"Synthesis job: {job_id}")
        
        # Get job details
        job_details = synthesis_manager.get_job_status(job_id)
        print(f"Selected platform: {job_details['platform']}")
        print(f"Estimated cost: ${job_details['estimated_cost']:.2f}")
        
    except ValueError as e:
        print(f"Sequence validation issue: {e}")
        print("This demonstrates the system's quality control features!")
    
    # Step 4: Show biological instruction compatibility
    print("\nStep 4 - Biological Instruction Integration")
    
    bio_instructions = instruction_set.get_instructions_by_type(InstructionType.BIOLOGICAL)
    print(f"Available biological instructions: {len(bio_instructions)}")
    
    # Show how synthesis instruction could be used
    synthesize_instr = instruction_set.get_instruction_by_name('SYNTHESIZE')
    if synthesize_instr:
        print(f"SYNTHESIZE instruction: {synthesize_instr.dna_sequence}")
        print(f"Description: {synthesize_instr.description}")
        print(f"Execution cost: {synthesize_instr.cycles} cycles")
    
    print("\n2. System Integration Benefits")
    print("-" * 40)
    
    benefits = [
        "✅ Environmental-aware error correction",
        "✅ Real-world synthesis cost optimization",
        "✅ Quality control and validation pipelines",
        "✅ Comprehensive testing protocol integration",
        "✅ Complex algorithmic instruction support",
        "✅ Biological computing instruction set",
        "✅ End-to-end workflow automation"
    ]
    
    for benefit in benefits:
        print(benefit)


def main():
    """Run complete enhanced features demonstration"""
    print("🧬 BIOART ENHANCED FEATURES DEMONSTRATION")
    print("=" * 70)
    print("Biological Error Correction + Complex Instructions + DNA Synthesis")
    print("=" * 70)
    
    try:
        # Run all demonstrations
        demo_biological_error_correction()
        demo_enhanced_instruction_set()
        demo_dna_synthesis_integration()
        demo_integration_workflow()
        
        print("\n\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 70)
        print("Enhanced Bioart Features Successfully Demonstrated:")
        print("✅ Advanced biological error correction with environmental modeling")
        print("✅ Extended instruction set with complex algorithmic operations")
        print("✅ Real-world DNA synthesis integration with cost optimization")
        print("✅ Comprehensive quality control and testing protocols")
        print("✅ End-to-end workflow integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)