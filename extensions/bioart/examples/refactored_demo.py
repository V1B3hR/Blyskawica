#!/usr/bin/env python3
"""
Refactored Bioart Programming Language Demo
Demonstrates the improved modular architecture and new features
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bioart_language import BioartLanguage, create_bioart_language
from core.encoding import DNAEncoder
from vm.instruction_set import DNAInstructionSet, InstructionType
from vm.virtual_machine import VMState

def demo_header():
    """Display demo header"""
    print("🧬 DNA Programming Language - Refactored Version 2.0")
    print("=" * 60)
    print("Advanced modular architecture with enhanced performance")
    print()

def demo_version_info():
    """Demonstrate version and system information"""
    print("📋 System Information")
    print("-" * 30)
    
    dna_lang = create_bioart_language()
    stats = dna_lang.get_system_statistics()
    
    print(f"Version: {stats['language_info']['version']}")
    print(f"Encoding: {stats['language_info']['encoding']}")
    print(f"Architecture: {stats['language_info']['architecture']}")
    print(f"Instructions Available: {stats['instruction_set']['total_instructions']}")
    print(f"Instruction Coverage: {stats['instruction_set']['coverage']}")
    print()

def demo_enhanced_encoding():
    """Demonstrate enhanced encoding features"""
    print("⚡ Enhanced Encoding Performance")
    print("-" * 30)
    
    encoder = DNAEncoder()
    
    # Test data
    test_strings = [
        "Hello, DNA World!",
        "Refactored version 2.0",
        "🧬 DNA Programming Language",
        "AUCG" * 50  # 200 nucleotides
    ]
    
    for text in test_strings:
        start_time = time.time()
        dna_sequence = encoder.encode_string(text)
        encode_time = time.time() - start_time
        
        start_time = time.time()
        decoded_text = encoder.decode_to_string(dna_sequence)
        decode_time = time.time() - start_time
        
        print(f"Text: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        print(f"  DNA Length: {len(dna_sequence)} nucleotides")
        print(f"  Encode Time: {encode_time*1000:.3f} ms")
        print(f"  Decode Time: {decode_time*1000:.3f} ms")
        print(f"  Accuracy: {'✓' if text == decoded_text else '✗'}")
        print()

def demo_extended_instruction_set():
    """Demonstrate extended instruction set"""
    print("🔧 Extended Instruction Set")
    print("-" * 30)
    
    instruction_set = DNAInstructionSet()
    
    # Group instructions by type
    by_type = {}
    for instruction in instruction_set.list_all_instructions():
        inst_type = instruction['type']
        if inst_type not in by_type:
            by_type[inst_type] = []
        by_type[inst_type].append(instruction)
    
    for inst_type, instructions in by_type.items():
        print(f"{inst_type} Instructions ({len(instructions)}):")
        for instr in instructions:
            print(f"  {instr['dna_sequence']} - {instr['name']:8} : {instr['description']}")
        print()

def demo_advanced_programs():
    """Demonstrate advanced DNA programs"""
    print("🧪 Advanced DNA Programs")
    print("-" * 30)
    
    dna_lang = create_bioart_language()
    
    # Complex program examples
    programs = {
        "Hello World Enhanced": "AAAU UACA AAUG AAGA",  # Load 'H', Print, Halt
        "Mathematical Operations": "AAAU AAAC AAUU AAAU AAAG AAAU AAUG AAGA",  # Load 3, Mul 2, Add 1, Print, Halt
        "Conditional Logic": "AAAU AAAA AACC AAAU AAAG AAAU AAUG AAGA",  # Load 0, JEQ, Add 1, Print, Halt
        "Memory Operations": "AAAU AACA AAAC AAAA AAUG AAGA",  # Load 42, Store 0, Print, Halt
    }
    
    for name, program in programs.items():
        print(f"Program: {name}")
        print(f"DNA Code: {program}")
        
        try:
            result = dna_lang.execute_dna_program(program)
            
            if result['success']:
                stats = result['execution_stats']
                print(f"  ✓ Executed successfully")
                print(f"  Instructions: {stats['instructions_executed']}")
                print(f"  Cycles: {stats['cycles_elapsed']}")
                print(f"  Time: {stats['execution_time']*1000:.3f} ms")
                print(f"  Final State: {result['final_state']}")
            else:
                print(f"  ✗ Execution failed: {result['error']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()

def demo_debugging_features():
    """Demonstrate debugging capabilities"""
    print("🐛 Debugging Features")
    print("-" * 30)
    
    dna_lang = create_bioart_language()
    
    # Enable debug mode
    dna_lang.set_debug_mode(True)
    
    # Simple program for debugging
    debug_program = "AAAU AAAC AUCA AAUG AAGA"  # Load 3, Inc, Print, Halt
    
    print("Debug Program:", debug_program)
    
    try:
        # Compile and load program
        bytecode = dna_lang.compile_dna_program(debug_program)
        dna_lang.vm.load_program(bytecode)
        
        # Show disassembly
        disassembly = dna_lang.disassemble_program(bytecode)
        print("Disassembly:")
        for line in disassembly:
            print(f"  {line}")
        
        # Execute with debugging
        result = dna_lang.execute_dna_program(debug_program)
        print(f"Debug execution: {'✓' if result['success'] else '✗'}")
        
    except Exception as e:
        print(f"Debug error: {e}")
    
    print()

def demo_file_management():
    """Demonstrate file management features"""
    print("📁 File Management")
    print("-" * 30)
    
    dna_lang = create_bioart_language()
    
    # Save a sample program
    sample_program = "AAAU UACA AAUG AAGA"  # Hello World
    metadata = {
        'author': 'DNA Language Demo',
        'description': 'Hello World program',
        'category': 'example'
    }
    
    try:
        # Save program
        dna_lang.save_dna_program('hello_world_v2', sample_program, metadata)
        print("✓ Saved DNA program with metadata")
        
        # List programs
        programs = dna_lang.file_manager.list_programs('source')
        print(f"✓ Found {len(programs)} source programs")
        
        # Save compiled version
        bytecode = dna_lang.compile_dna_program(sample_program)
        dna_lang.save_compiled_program('hello_world_v2_compiled', bytecode)
        print("✓ Saved compiled program")
        
        # Get storage info
        storage_info = dna_lang.file_manager.get_storage_info()
        print("Storage Information:")
        for dir_name, info in storage_info['directories'].items():
            print(f"  {dir_name}: {info['file_count']} files, {info['total_size_kb']:.1f} KB")
        
    except Exception as e:
        print(f"File management error: {e}")
    
    print()

def demo_performance_benchmarks():
    """Demonstrate performance benchmarks"""
    print("⚡ Performance Benchmarks")
    print("-" * 30)
    
    dna_lang = create_bioart_language()
    
    # Test different data sizes
    test_sizes = [100, 1000, 10000]
    
    for size in test_sizes:
        print(f"Testing {size} bytes:")
        
        try:
            benchmark = dna_lang.benchmark_performance(size)
            
            print(f"  Encoding: {benchmark['encoding_speed_mbps']:.2f} MB/s")
            print(f"  Decoding: {benchmark['decoding_speed_mbps']:.2f} MB/s")
            print(f"  Accuracy: {'✓' if benchmark['accuracy'] else '✗'}")
            print(f"  Efficiency: {benchmark['efficiency_ratio']:.1f} nucleotides/byte")
            
        except Exception as e:
            print(f"  Benchmark error: {e}")
        
        print()

def demo_validation_features():
    """Demonstrate validation capabilities"""
    print("✅ Validation Features")
    print("-" * 30)
    
    dna_lang = create_bioart_language()
    
    # Test various DNA sequences
    test_sequences = [
        "AUCG",  # Valid 4-nucleotide sequence
        "AUCGAUCA",  # Valid 8-nucleotide sequence  
        "AUCGAUCG AAAA",  # Valid with spaces
        "AUCX",  # Invalid character
        "AUC",   # Invalid length
        "AAAU AAAG AAUG AAGA",  # Valid program
    ]
    
    for sequence in test_sequences:
        validation = dna_lang.validate_dna_sequence(sequence)
        
        print(f"Sequence: '{sequence}'")
        print(f"  Valid: {'✓' if validation['valid'] else '✗'}")
        print(f"  Length: {validation['length']} nucleotides")
        
        if not validation['valid']:
            print(f"  Error: {validation['message']}")
        
        if 'valid_as_program' in validation:
            print(f"  Program: {'✓' if validation['valid_as_program'] else '✗'}")
        
        print()

def main():
    """Run all demonstrations"""
    demo_header()
    
    try:
        demo_version_info()
        demo_enhanced_encoding()
        demo_extended_instruction_set()
        demo_advanced_programs()
        demo_debugging_features()
        demo_file_management()
        demo_performance_benchmarks()
        demo_validation_features()
        
        print("🎉 Refactored DNA Programming Language Demo Complete!")
        print("All features demonstrated successfully.")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 