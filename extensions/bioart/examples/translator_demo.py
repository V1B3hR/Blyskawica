#!/usr/bin/env python3
"""
Bioart Translator Demo
Demonstrates the comprehensive translator capabilities
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from translator import BioartTranslator


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_basic_translation():
    """Demonstrate basic text to DNA translation"""
    print_section("1. BASIC TEXT TO DNA TRANSLATION")
    
    translator = BioartTranslator()
    
    # Simple text
    text = "Hello, World!"
    print(f"\nOriginal text: '{text}'")
    
    # Encode to DNA
    dna = translator.text_to_dna(text)
    print(f"DNA sequence:  {dna}")
    print(f"Length:        {len(dna)} nucleotides ({len(text)} bytes × 4)")
    
    # Decode back
    restored = translator.dna_to_text(dna)
    print(f"Restored text: '{restored}'")
    print(f"Match:         {'✓ YES' if text == restored else '✗ NO'}")


def demo_binary_translation():
    """Demonstrate binary data translation"""
    print_section("2. BINARY DATA TRANSLATION")
    
    translator = BioartTranslator()
    
    # Binary data (all byte values 0-10)
    data = bytes(range(11))
    print(f"\nOriginal binary: {list(data)}")
    
    # Encode to DNA
    dna = translator.binary_to_dna(data)
    print(f"DNA sequence:    {dna}")
    
    # Decode back
    restored = translator.dna_to_binary(dna)
    print(f"Restored binary: {list(restored)}")
    print(f"Match:           {'✓ YES' if data == restored else '✗ NO'}")


def demo_modification():
    """Demonstrate DNA sequence modification"""
    print_section("3. DNA SEQUENCE MODIFICATION")
    
    translator = BioartTranslator()
    
    original = "AAAAUUUU"
    print(f"\nOriginal DNA: {original}")
    
    # Modify single nucleotide
    modified = translator.modify_nucleotide(original, 0, 'G')
    print(f"After mutating position 0 to G: {modified}")
    
    # Insert sequence
    modified = translator.insert_sequence(original, 4, "CCCC")
    print(f"After inserting CCCC at position 4: {modified}")
    
    # Delete sequence
    modified = translator.delete_sequence(original, 2, 4)
    print(f"After deleting 4 nucleotides from position 2: {modified}")
    
    # Replace sequence
    modified = translator.replace_sequence(original, 0, 4, "GGGG")
    print(f"After replacing first 4 with GGGG: {modified}")


def demo_validation():
    """Demonstrate validation and verification"""
    print_section("4. VALIDATION AND VERIFICATION")
    
    translator = BioartTranslator()
    
    # Validate DNA sequences
    print("\nValidation tests:")
    test_sequences = [
        ("AUCGAUCG", True),
        ("ATCGATCG", False),  # T instead of U
        ("AUCX", False),      # Invalid character
        ("aucg", True),       # Lowercase is valid
    ]
    
    for seq, expected in test_sequences:
        is_valid = translator.validate_dna(seq)
        status = "✓" if is_valid == expected else "✗"
        print(f"  {status} '{seq}' -> {'Valid' if is_valid else 'Invalid'}")
    
    # Verify reversibility
    print("\nReversibility verification:")
    test_data = "Test data for reversibility check"
    result = translator.verify_reversibility(test_data)
    
    print(f"  Original size:  {result['original_size']} bytes")
    print(f"  DNA size:       {result['dna_size']} nucleotides")
    print(f"  Restored size:  {result['restored_size']} bytes")
    print(f"  Match:          {'✓ YES' if result['match'] else '✗ NO'}")
    print(f"  Status:         {'✓ PASSED' if result['success'] else '✗ FAILED'}")


def demo_sequence_info():
    """Demonstrate sequence information analysis"""
    print_section("5. SEQUENCE INFORMATION ANALYSIS")
    
    translator = BioartTranslator()
    
    dna = "AUCGAUCGGGCCAAUU"
    print(f"\nAnalyzing sequence: {dna}")
    
    info = translator.get_sequence_info(dna)
    
    print(f"\nSequence properties:")
    print(f"  Length:        {info['length']} nucleotides")
    print(f"  Byte capacity: {info['byte_capacity']} bytes")
    print(f"  Valid:         {'✓ YES' if info['is_valid'] else '✗ NO'}")
    print(f"  Complete:      {'✓ YES' if info['is_complete'] else '✗ NO'}")
    
    print(f"\n  Nucleotide composition:")
    for nt in ['A', 'U', 'C', 'G']:
        count = info['nucleotide_counts'].get(nt, 0)
        percentage = (count / info['length'] * 100) if info['length'] > 0 else 0
        print(f"    {nt}: {count:2d} ({percentage:5.1f}%)")
    
    print(f"\n  GC content: {info['gc_content']:.1f}%")


def demo_real_world_scenario():
    """Demonstrate a real-world use case"""
    print_section("6. REAL-WORLD SCENARIO: STORING JSON DATA")
    
    import json
    translator = BioartTranslator()
    
    # Sample JSON data
    data = {
        "id": 12345,
        "name": "John Doe",
        "email": "john@example.com",
        "items": ["item1", "item2", "item3"],
        "active": True
    }
    
    print("\nOriginal JSON data:")
    print(json.dumps(data, indent=2))
    
    # Convert to DNA
    json_str = json.dumps(data)
    dna = translator.text_to_dna(json_str)
    
    print(f"\nEncoded to DNA:")
    print(f"  Length: {len(dna)} nucleotides")
    print(f"  First 60 chars: {dna[:60]}...")
    
    # Restore from DNA
    restored_json = translator.dna_to_text(dna)
    restored_data = json.loads(restored_json)
    
    print(f"\nRestored JSON data:")
    print(json.dumps(restored_data, indent=2))
    
    print(f"\nData integrity: {'✓ PASSED' if data == restored_data else '✗ FAILED'}")


def demo_formatting():
    """Demonstrate DNA formatting"""
    print_section("7. DNA SEQUENCE FORMATTING")
    
    translator = BioartTranslator()
    
    text = "This is a longer text to demonstrate DNA formatting"
    dna = translator.text_to_dna(text)
    
    print(f"\nOriginal text: '{text}'")
    print(f"DNA length: {len(dna)} nucleotides")
    
    print("\nFormatted DNA (width=60, groups of 4):")
    formatted = translator.format_dna(dna, width=60, group_size=4)
    print(formatted)


def demo_statistics():
    """Demonstrate usage statistics"""
    print_section("8. USAGE STATISTICS")
    
    translator = BioartTranslator()
    
    # Reset stats
    translator.reset_stats()
    
    # Perform various operations
    translator.text_to_dna("Hello")
    translator.text_to_dna("World")
    dna = translator.text_to_dna("Test")
    translator.dna_to_text(dna)
    translator.modify_nucleotide("AAAA", 0, 'G')
    translator.validate_dna("AUCG")
    translator.verify_reversibility("Data")
    
    # Get stats
    stats = translator.get_stats()
    
    print("\nUsage statistics:")
    print(f"  Translations:   {stats['translations']}")
    print(f"  Reversals:      {stats['reversals']}")
    print(f"  Modifications:  {stats['modifications']}")
    print(f"  Validations:    {stats['validations']}")


def demo_all_byte_values():
    """Demonstrate translation of all possible byte values"""
    print_section("9. ALL BYTE VALUES TEST (0-255)")
    
    translator = BioartTranslator()
    
    # Create data with all possible byte values
    all_bytes = bytes(range(256))
    
    print(f"\nTesting all {len(all_bytes)} possible byte values...")
    
    # Encode to DNA
    dna = translator.binary_to_dna(all_bytes)
    print(f"DNA length: {len(dna)} nucleotides")
    
    # Decode back
    restored = translator.dna_to_binary(dna)
    
    # Verify
    match = (all_bytes == restored)
    print(f"All bytes restored correctly: {'✓ YES' if match else '✗ NO'}")
    
    if match:
        print("✓ 100% reversibility confirmed for all 256 byte values!")


def main():
    """Run all demonstrations"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  BIOART TRANSLATOR - COMPREHENSIVE DEMONSTRATION".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    try:
        demo_basic_translation()
        demo_binary_translation()
        demo_modification()
        demo_validation()
        demo_sequence_info()
        demo_real_world_scenario()
        demo_formatting()
        demo_statistics()
        demo_all_byte_values()
        
        print("\n" + "=" * 70)
        print("  ✓ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
