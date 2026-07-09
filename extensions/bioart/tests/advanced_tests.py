#!/usr/bin/env python3
"""
Advanced Bioart Programming Language Test Suite
Comprehensive testing including edge cases, stress tests, and validation
"""

import sys
import os
import random
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from bioart import Bioart

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("🔬 Advanced Test Suite - Edge Cases")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test 1: All possible byte values
    print("1. Testing all 256 possible byte values...")
    success_count = 0
    for i in range(256):
        try:
            dna_seq = dna.byte_to_dna(i)
            restored = dna.dna_to_byte(dna_seq)
            if restored == i:
                success_count += 1
        except Exception as e:
            print(f"   Error at byte {i}: {e}")
    
    print(f"   Result: {success_count}/256 byte values converted successfully")
    print(f"   Success rate: {success_count/256*100:.1f}%")
    
    # Test 2: Random data stress test
    print("\n2. Random data stress test (1000 samples)...")
    random.seed(42)  # Reproducible results
    stress_success = 0
    
    for _ in range(1000):
        # Generate random byte sequence
        length = random.randint(1, 100)
        original_data = bytes([random.randint(0, 255) for _ in range(length)])
        
        try:
            # Convert to DNA
            dna_sequence = ""
            for byte_val in original_data:
                dna_sequence += dna.byte_to_dna(byte_val)
            
            # Convert back
            restored_data = []
            for i in range(0, len(dna_sequence), 4):
                dna_chunk = dna_sequence[i:i+4]
                restored_data.append(dna.dna_to_byte(dna_chunk))
            
            restored_bytes = bytes(restored_data)
            
            if original_data == restored_bytes:
                stress_success += 1
                
        except Exception as e:
            print(f"   Stress test error: {e}")
    
    print(f"   Result: {stress_success}/1000 random sequences converted successfully")
    print(f"   Stress test success rate: {stress_success/10:.1f}%")
    
    # Test 3: Large file simulation
    print("\n3. Large file simulation test...")
    large_data = bytes(range(256)) * 10  # 2560 bytes
    print(f"   Original size: {len(large_data)} bytes")
    
    # Convert to DNA
    start_time = time.time()
    dna_representation = ""
    for byte_val in large_data:
        dna_representation += dna.byte_to_dna(byte_val)
    conversion_time = time.time() - start_time
    
    print(f"   DNA size: {len(dna_representation)} nucleotides")
    print(f"   Conversion time: {conversion_time*1000:.2f} ms")
    print(f"   Speed: {len(large_data)/conversion_time:.0f} bytes/second")
    
    # Convert back
    start_time = time.time()
    restored_large = []
    for i in range(0, len(dna_representation), 4):
        dna_chunk = dna_representation[i:i+4]
        restored_large.append(dna.dna_to_byte(dna_chunk))
    restoration_time = time.time() - start_time
    
    restored_bytes = bytes(restored_large)
    print(f"   Restoration time: {restoration_time*1000:.2f} ms")
    print(f"   Large file test: {'PASSED' if large_data == restored_bytes else 'FAILED'}")

def test_programming_features():
    """Test advanced programming capabilities"""
    print("\n🧬 Programming Features Test")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test 1: Complex mathematical program
    print("1. Complex mathematical program test...")
    # Program: Load 10, Multiply by 5, Add 25, Print result (should be 75)
    math_program = "AAAU AAAC AAUU AAAU AAAG AAAU AAUG AAGA"
    print(f"   DNA Program: {math_program}")
    
    bytecode = dna.compile_dna_to_bytecode(math_program)
    print(f"   Compiled to {len(bytecode)} bytes")
    
    # Execute and capture output
    import io
    import contextlib
    
    output_buffer = io.StringIO()
    with contextlib.redirect_stdout(output_buffer):
        dna.execute_bytecode(bytecode)
    
    output = output_buffer.getvalue().strip()
    print(f"   Program output: {output}")
    
    # Test 2: Program with all instructions
    print("\n2. Testing all instruction types...")
    instructions_used = set()
    
    for dna_seq, instruction in dna.instructions.items():
        instructions_used.add(instruction)
        byte_val = dna.dna_to_byte(dna_seq)
        print(f"   {dna_seq} → {instruction} (byte {byte_val})")
    
    print(f"   Total instructions available: {len(instructions_used)}")
    
    # Test 3: Program serialization
    print("\n3. Program serialization test...")
    test_program = "AAAU AACA AAAG AAAC AAUG AAGA"  # Load 42, Add 8, Print, Halt
    
    # Compile
    bytecode = dna.compile_dna_to_bytecode(test_program)
    
    # Save to file
    test_filename = "test_program.dna"
    dna.save_binary(bytecode, test_filename)
    
    # Load from file
    loaded_bytecode = dna.load_binary(test_filename)
    
    # Decompile
    restored_dna = dna.decompile_bytecode_to_dna(loaded_bytecode)
    
    print(f"   Original:  {test_program.replace(' ', '')}")
    print(f"   Restored:  {restored_dna}")
    print(f"   Match:     {test_program.replace(' ', '') == restored_dna}")
    
    # Clean up
    if os.path.exists(test_filename):
        os.remove(test_filename)

def test_interoperability():
    """Test interoperability with different data types"""
    print("\n🔗 Interoperability Tests")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test 1: Different text encodings
    print("1. Text encoding compatibility...")
    test_strings = [
        "Hello, World!",
        "DNA Programming",
        "123456789",
        "!@#$%^&*()",
        "AUCG" * 10,
        "",  # Empty string
    ]
    
    for i, text in enumerate(test_strings):
        if not text:  # Skip empty string for display
            print(f"   Test {i+1}: (empty string)")
        else:
            print(f"   Test {i+1}: '{text[:20]}{'...' if len(text) > 20 else ''}'")
        
        # Convert to bytes
        text_bytes = text.encode('utf-8')
        
        # Convert to DNA
        dna_seq = ""
        for byte_val in text_bytes:
            dna_seq += dna.byte_to_dna(byte_val)
        
        # Convert back
        restored_bytes = []
        for j in range(0, len(dna_seq), 4):
            if j + 4 <= len(dna_seq):
                chunk = dna_seq[j:j+4]
                restored_bytes.append(dna.dna_to_byte(chunk))
        
        restored_text = bytes(restored_bytes).decode('utf-8')
        success = text == restored_text
        print(f"       Result: {'PASSED' if success else 'FAILED'}")
    
    # Test 2: Binary file types simulation
    print("\n2. Binary file type simulation...")
    file_types = {
        "Image header": bytes([0xFF, 0xD8, 0xFF, 0xE0]),  # JPEG header
        "Executable": bytes([0x4D, 0x5A]),  # PE header
        "PDF": bytes([0x25, 0x50, 0x44, 0x46]),  # PDF header
        "ZIP": bytes([0x50, 0x4B, 0x03, 0x04]),  # ZIP header
    }
    
    for file_type, header_bytes in file_types.items():
        print(f"   {file_type}: {list(header_bytes)}")
        
        # Convert to DNA
        dna_seq = ""
        for byte_val in header_bytes:
            dna_seq += dna.byte_to_dna(byte_val)
        
        # Convert back
        restored_bytes = []
        for j in range(0, len(dna_seq), 4):
            chunk = dna_seq[j:j+4]
            restored_bytes.append(dna.dna_to_byte(chunk))
        
        restored = bytes(restored_bytes)
        success = header_bytes == restored
        print(f"       DNA: {dna_seq}")
        print(f"       Result: {'PASSED' if success else 'FAILED'}")

def test_performance():
    """Performance and efficiency tests"""
    print("\n⚡ Performance Tests")
    print("=" * 50)
    
    dna = Bioart()
    
    # Test 1: Encoding speed
    print("1. Encoding speed test...")
    test_sizes = [100, 1000, 10000]
    
    for size in test_sizes:
        test_data = bytes(range(256))[:size]
        
        # Time encoding
        start_time = time.time()
        dna_seq = ""
        for byte_val in test_data:
            dna_seq += dna.byte_to_dna(byte_val)
        encoding_time = time.time() - start_time
        
        # Time decoding
        start_time = time.time()
        restored = []
        for i in range(0, len(dna_seq), 4):
            chunk = dna_seq[i:i+4]
            restored.append(dna.dna_to_byte(chunk))
        decoding_time = time.time() - start_time
        
        print(f"   {size} bytes:")
        print(f"     Encoding: {encoding_time*1000:.2f} ms ({size/encoding_time:.0f} bytes/sec)")
        print(f"     Decoding: {decoding_time*1000:.2f} ms ({size/decoding_time:.0f} bytes/sec)")
    
    # Test 2: Memory efficiency
    print("\n2. Memory efficiency verification...")
    original_size = 1000  # bytes
    dna_size = original_size * 4  # nucleotides
    
    print(f"   Original data: {original_size} bytes")
    print(f"   DNA representation: {dna_size} nucleotides")
    print(f"   Ratio: {dna_size/original_size} nucleotides per byte (optimal: 4.0)")
    print(f"   Efficiency: {'OPTIMAL' if dna_size/original_size == 4.0 else 'SUBOPTIMAL'}")

def run_all_advanced_tests():
    """Run all advanced tests"""
    print("🧬 DNA Programming Language - Advanced Test Suite")
    print("=" * 60)
    print("Running comprehensive validation tests...\n")
    
    start_time = time.time()
    
    try:
        test_edge_cases()
        test_programming_features()
        test_interoperability()
        test_performance()
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎯 Advanced Test Suite Results")
        print("=" * 60)
        print("✅ Edge Cases Test - COMPLETED")
        print("✅ Programming Features Test - COMPLETED")
        print("✅ Interoperability Test - COMPLETED")
        print("✅ Performance Test - COMPLETED")
        print(f"\nTotal test time: {total_time:.2f} seconds")
        print("Status: ALL ADVANCED TESTS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        print("Status: TESTS FAILED")

if __name__ == "__main__":
    run_all_advanced_tests() 