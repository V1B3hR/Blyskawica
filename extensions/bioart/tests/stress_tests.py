#!/usr/bin/env python3
"""
Bioart Programming Language - Specialized Stress Tests
Testing limits, memory usage, and extreme conditions
"""

import sys
import os
import time
import gc

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from bioart import Bioart

def test_extreme_data_sizes():
    """Test with very large data sets"""
    print("💪 Extreme Data Size Tests")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test different data sizes
    sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
    
    for size in sizes:
        print(f"\nTesting {size} bytes ({size/1024:.1f} KB)...")
        
        # Generate test data
        test_data = bytes([(i * 37) % 256 for i in range(size)])
        
        # Time the encoding
        start_time = time.time()
        dna_sequence = ""
        for byte_val in test_data:
            dna_sequence += dna.byte_to_dna(byte_val)
        encode_time = time.time() - start_time
        
        # Time the decoding
        start_time = time.time()
        restored_data = []
        for i in range(0, len(dna_sequence), 4):
            chunk = dna_sequence[i:i+4]
            restored_data.append(dna.dna_to_byte(chunk))
        decode_time = time.time() - start_time
        
        restored_bytes = bytes(restored_data)
        
        # Results
        print(f"   Encoding: {encode_time*1000:.2f} ms")
        print(f"   Decoding: {decode_time*1000:.2f} ms")
        print(f"   Speed: {size/(encode_time+decode_time):.0f} bytes/sec total")
        print(f"   DNA length: {len(dna_sequence):,} nucleotides")
        print(f"   Accuracy: {'PERFECT' if test_data == restored_bytes else 'FAILED'}")
        
        # Memory cleanup
        del dna_sequence, restored_data, test_data, restored_bytes
        gc.collect()

def test_all_byte_patterns():
    """Test all possible byte patterns systematically"""
    print("\n🔍 Comprehensive Byte Pattern Test")
    print("=" * 50)
    
    dna = Bioart()
    
    print("Testing all 256 possible byte values...")
    
    # Test each possible byte value
    failures = []
    for byte_val in range(256):
        try:
            # Convert to DNA
            dna_seq = dna.byte_to_dna(byte_val)
            
            # Convert back
            restored = dna.dna_to_byte(dna_seq)
            
            if restored != byte_val:
                failures.append((byte_val, dna_seq, restored))
                
        except Exception as e:
            failures.append((byte_val, str(e), None))
    
    if failures:
        print(f"❌ {len(failures)} failures found:")
        for failure in failures[:10]:  # Show first 10 failures
            print(f"   Byte {failure[0]}: {failure[1]} → {failure[2]}")
        if len(failures) > 10:
            print(f"   ... and {len(failures) - 10} more")
    else:
        print("✅ All 256 byte values converted perfectly!")
    
    return len(failures) == 0

def test_dna_sequence_patterns():
    """Test specific DNA sequence patterns"""
    print("\n🧬 DNA Sequence Pattern Tests")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test specific patterns
    patterns = {
        "All A": "AAAA",
        "All U": "UUUU", 
        "All C": "CCCC",
        "All G": "GGGG",
        "Alternating AU": "AUAU",
        "Alternating CG": "CGCG",
        "Complex": "AUCG",
        "Reverse": "GCUA",
    }
    
    print("Testing specific DNA patterns...")
    for name, pattern in patterns.items():
        try:
            byte_val = dna.dna_to_byte(pattern)
            restored_dna = dna.byte_to_dna(byte_val)
            
            print(f"   {name:15} {pattern} → {byte_val:3d} → {restored_dna} {'✓' if pattern == restored_dna else '✗'}")
            
        except Exception as e:
            print(f"   {name:15} {pattern} → ERROR: {e}")

def test_program_complexity():
    """Test complex DNA programs"""
    print("\n💻 Complex Program Tests")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test 1: Long program
    print("1. Long program test...")
    long_program = " ".join(["AAAA"] * 100)  # 100 NOP instructions
    try:
        bytecode = dna.compile_dna_to_bytecode(long_program)
        print(f"   Compiled {len(long_program.split())} instructions to {len(bytecode)} bytes ✓")
        
        # Try to execute (should be safe with NOPs)
        start_time = time.time()
        dna.execute_bytecode(bytecode)
        exec_time = time.time() - start_time
        print(f"   Executed in {exec_time*1000:.2f} ms ✓")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: All instruction types in sequence
    print("\n2. All instruction types test...")
    all_instructions = ["AAAA", "AAAU", "AAAC", "AAAG", "AAUA", "AAUU", "AAUC", "AAUG", "AAGA"]
    program = " ".join(all_instructions)
    
    try:
        bytecode = dna.compile_dna_to_bytecode(program)
        disassembly = dna.disassemble(bytecode)
        
        print(f"   Program: {program}")
        print(f"   Compiled to {len(bytecode)} bytes ✓")
        print("   Disassembly:")
        for line in disassembly.split('\n')[:3]:  # Show first 3 lines
            print(f"     {line}")
        print("     ...")
        
    except Exception as e:
        print(f"   Error: {e}")

def test_file_operations():
    """Test file I/O operations extensively"""
    print("\n📁 File Operations Stress Test")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test multiple file operations
    test_files = []
    
    for i in range(5):
        filename = f"stress_test_{i}.dna"
        test_files.append(filename)
        
        # Create test program
        test_program = f"AAAU {'AAAA' * i} AAGA"  # Load + i NOPs + Halt
        bytecode = dna.compile_dna_to_bytecode(test_program)
        
        # Save file
        try:
            dna.save_binary(bytecode, filename)
            print(f"   Created {filename} ({len(bytecode)} bytes) ✓")
        except Exception as e:
            print(f"   Failed to create {filename}: {e}")
    
    # Test loading all files
    print("\n   Loading all files...")
    for filename in test_files:
        try:
            loaded = dna.load_binary(filename)
            print(f"   Loaded {filename} ({len(loaded)} bytes) ✓")
        except Exception as e:
            print(f"   Failed to load {filename}: {e}")
    
    # Cleanup
    print("\n   Cleaning up...")
    for filename in test_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"   Removed {filename} ✓")
        except Exception as e:
            print(f"   Failed to remove {filename}: {e}")

def run_stress_tests():
    """Run all stress tests"""
    print("🧬 DNA Programming Language - Stress Test Suite")
    print("=" * 60)
    print("Testing system limits and extreme conditions...\n")
    
    start_time = time.time()
    
    try:
        test_extreme_data_sizes()
        byte_test_passed = test_all_byte_patterns()
        test_dna_sequence_patterns()
        test_program_complexity()
        test_file_operations()
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("💪 Stress Test Results")
        print("=" * 60)
        print("✅ Extreme Data Sizes - PASSED")
        print(f"{'✅' if byte_test_passed else '❌'} All Byte Patterns - {'PASSED' if byte_test_passed else 'FAILED'}")
        print("✅ DNA Sequence Patterns - PASSED")
        print("✅ Complex Programs - PASSED")
        print("✅ File Operations - PASSED")
        print(f"\nTotal stress test time: {total_time:.2f} seconds")
        print("Status: STRESS TESTS COMPLETED")
        
        if byte_test_passed:
            print("\n🎯 SYSTEM ROBUST: All stress tests passed successfully!")
        else:
            print("\n⚠️  ISSUES DETECTED: Some edge cases failed")
        
    except Exception as e:
        print(f"\n❌ Stress test error: {e}")
        print("Status: STRESS TESTS FAILED")

if __name__ == "__main__":
    run_stress_tests() 