#!/usr/bin/env python3
"""
Real-World Bioart Translator Usage Demo
Shows practical applications of the translator in real scenarios
"""

import sys
import os
import json
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from translator import BioartTranslator


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def scenario_1_message_storage():
    """Scenario 1: Store and retrieve secret messages"""
    print_header("SCENARIO 1: SECRET MESSAGE STORAGE")
    
    translator = BioartTranslator()
    
    # Original message
    message = "Meet me at the lab at midnight. Bring the samples."
    print(f"\nOriginal message:\n  '{message}'")
    
    # Encode to DNA
    dna = translator.text_to_dna(message)
    print(f"\nEncoded as DNA:")
    print(f"  {translator.format_dna(dna, width=60)[:100]}...")
    print(f"  Length: {len(dna)} nucleotides")
    
    # Decode back
    restored = translator.dna_to_text(dna)
    print(f"\nDecoded message:\n  '{restored}'")
    
    # Verify
    print(f"\nVerification: {'✓ PASSED' if message == restored else '✗ FAILED'}")


def scenario_2_config_storage():
    """Scenario 2: Store application configuration in DNA"""
    print_header("SCENARIO 2: APPLICATION CONFIGURATION STORAGE")
    
    translator = BioartTranslator()
    
    # Application config
    config = {
        "app_name": "BioDatabase",
        "version": "2.1.0",
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "biodata"
        },
        "features": {
            "dna_storage": True,
            "compression": True,
            "encryption": False
        },
        "max_connections": 100
    }
    
    print("\nOriginal configuration:")
    print(json.dumps(config, indent=2))
    
    # Store as DNA
    config_json = json.dumps(config)
    dna = translator.text_to_dna(config_json)
    
    print(f"\nStored as DNA:")
    print(f"  Size: {len(dna)} nucleotides ({len(config_json)} bytes)")
    print(f"  Sample: {dna[:60]}...")
    
    # Retrieve and use
    restored_json = translator.dna_to_text(dna)
    restored_config = json.loads(restored_json)
    
    print(f"\nRestored configuration:")
    print(json.dumps(restored_config, indent=2))
    
    print(f"\nVerification: {'✓ PASSED' if config == restored_config else '✗ FAILED'}")


def scenario_3_backup_restore():
    """Scenario 3: Backup and restore important documents"""
    print_header("SCENARIO 3: DOCUMENT BACKUP AND RESTORE")
    
    translator = BioartTranslator()
    
    # Important document
    document = """
RESEARCH NOTES - PROJECT BIOART
================================
Date: 2025-10-21
Researcher: Dr. Smith

FINDINGS:
1. DNA storage density: 4 nucleotides per byte achieved
2. Reversibility: 100% across all test cases
3. Speed: Consistent performance up to 78M bytes/sec
4. Applications: Universal file format support confirmed

NEXT STEPS:
- Implement error correction mechanisms
- Test with larger datasets (>1GB)
- Develop compression algorithms
- Begin clinical trials

STATUS: APPROVED FOR PUBLICATION
"""
    
    print("\nOriginal document:")
    print(document[:200] + "...")
    
    # Backup to DNA
    dna_backup = translator.text_to_dna(document)
    
    print(f"\nBackup created:")
    print(f"  DNA length: {len(dna_backup)} nucleotides")
    print(f"  Original: {len(document)} bytes")
    print(f"  Storage ratio: {len(dna_backup) / len(document):.1f}x")
    
    # Simulate storage and retrieval
    print("\nSimulating long-term storage...")
    
    # Restore from DNA
    restored_document = translator.dna_to_text(dna_backup)
    
    print("\nDocument restored from DNA backup")
    print(restored_document[:200] + "...")
    
    # Verify integrity
    integrity = translator.verify_reversibility(document)
    print(f"\nIntegrity check:")
    print(f"  Original size: {integrity['original_size']} bytes")
    print(f"  Restored size: {integrity['restored_size']} bytes")
    print(f"  Match: {'✓ YES' if integrity['match'] else '✗ NO'}")
    print(f"  Status: {'✓ PASSED' if integrity['success'] else '✗ FAILED'}")


def scenario_4_data_modification():
    """Scenario 4: Modify DNA sequences for research"""
    print_header("SCENARIO 4: DNA SEQUENCE MODIFICATION FOR RESEARCH")
    
    translator = BioartTranslator()
    
    # Original data
    data = "RESEARCH"
    dna = translator.text_to_dna(data)
    
    print(f"\nOriginal data: '{data}'")
    print(f"Original DNA:  {dna}")
    
    # Get info
    info = translator.get_sequence_info(dna)
    print(f"\nSequence properties:")
    print(f"  Length: {info['length']} nucleotides")
    print(f"  GC content: {info['gc_content']:.1f}%")
    
    # Modify sequence (simulate mutation)
    print("\nSimulating genetic mutations...")
    
    mutated = translator.modify_nucleotide(dna, 0, 'G')
    print(f"  Mutation 1 (position 0): {mutated}")
    
    mutated = translator.modify_nucleotide(mutated, 4, 'A')
    print(f"  Mutation 2 (position 4): {mutated}")
    
    # Try to decode mutated sequence
    try:
        decoded = translator.dna_to_text(mutated)
        print(f"\nMutated sequence decodes to: '{decoded}'")
    except Exception as e:
        print(f"\nMutated sequence cannot be decoded as text (expected)")
        print(f"  Reason: Mutations changed the data")


def scenario_5_multi_file_archive():
    """Scenario 5: Archive multiple files in DNA format"""
    print_header("SCENARIO 5: MULTI-FILE ARCHIVE IN DNA FORMAT")
    
    translator = BioartTranslator()
    
    # Create a simulated archive
    files = {
        "README.txt": "This is a README file\nContains important information",
        "config.json": json.dumps({"version": "1.0", "enabled": True}),
        "data.csv": "Name,Age,City\nAlice,30,NYC\nBob,25,LA\n"
    }
    
    print("\nFiles to archive:")
    for filename, content in files.items():
        print(f"  {filename}: {len(content)} bytes")
    
    # Archive structure
    archive = {}
    total_dna_size = 0
    
    print("\nArchiving to DNA...")
    for filename, content in files.items():
        dna = translator.text_to_dna(content)
        archive[filename] = dna
        total_dna_size += len(dna)
        print(f"  {filename}: {len(dna)} nucleotides")
    
    print(f"\nArchive created:")
    print(f"  Files: {len(archive)}")
    print(f"  Total DNA size: {total_dna_size} nucleotides")
    
    # Restore files
    print("\nRestoring files from DNA archive...")
    restored_files = {}
    for filename, dna in archive.items():
        content = translator.dna_to_text(dna)
        restored_files[filename] = content
        print(f"  {filename}: ✓ Restored")
    
    # Verify
    print("\nVerification:")
    all_match = True
    for filename in files:
        match = files[filename] == restored_files[filename]
        all_match = all_match and match
        status = "✓" if match else "✗"
        print(f"  {filename}: {status}")
    
    print(f"\nArchive integrity: {'✓ PASSED' if all_match else '✗ FAILED'}")


def scenario_6_streaming_data():
    """Scenario 6: Stream data through DNA encoding"""
    print_header("SCENARIO 6: STREAMING DATA PROCESSING")
    
    translator = BioartTranslator()
    
    print("\nSimulating data stream...")
    
    # Simulate streaming chunks
    chunks = [
        "Chunk 1: First data packet",
        "Chunk 2: Second data packet",
        "Chunk 3: Third data packet",
        "Chunk 4: Final data packet"
    ]
    
    encoded_stream = []
    decoded_stream = []
    
    print("\nProcessing stream:")
    for i, chunk in enumerate(chunks, 1):
        # Encode
        dna = translator.text_to_dna(chunk)
        encoded_stream.append(dna)
        
        # Decode
        decoded = translator.dna_to_text(dna)
        decoded_stream.append(decoded)
        
        print(f"  Chunk {i}: {len(chunk)} bytes → {len(dna)} nt → {len(decoded)} bytes ✓")
    
    # Verify stream integrity
    print("\nStream verification:")
    matches = sum(1 for orig, dec in zip(chunks, decoded_stream) if orig == dec)
    print(f"  Chunks processed: {len(chunks)}")
    print(f"  Matches: {matches}/{len(chunks)}")
    print(f"  Success rate: {matches/len(chunks)*100:.0f}%")
    print(f"  Status: {'✓ PASSED' if matches == len(chunks) else '✗ FAILED'}")


def scenario_7_database_field():
    """Scenario 7: Use DNA encoding for database fields"""
    print_header("SCENARIO 7: DATABASE FIELD STORAGE")
    
    translator = BioartTranslator()
    
    # Simulate database records
    records = [
        {"id": 1, "name": "Alice Smith", "notes": "Regular customer"},
        {"id": 2, "name": "Bob Jones", "notes": "VIP member"},
        {"id": 3, "name": "Carol White", "notes": "New registration"}
    ]
    
    print("\nOriginal database records:")
    for record in records:
        print(f"  ID {record['id']}: {record['name']} - {record['notes']}")
    
    # Encode notes field as DNA
    print("\nEncoding 'notes' field as DNA...")
    for record in records:
        dna = translator.text_to_dna(record['notes'])
        record['notes_dna'] = dna
        print(f"  ID {record['id']}: {len(dna)} nucleotides")
    
    # Simulate retrieval and decode
    print("\nRetrieving and decoding notes...")
    for record in records:
        decoded_notes = translator.dna_to_text(record['notes_dna'])
        match = decoded_notes == record['notes']
        status = "✓" if match else "✗"
        print(f"  ID {record['id']}: {status} '{decoded_notes}'")


def main():
    """Run all real-world scenarios"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  BIOART TRANSLATOR - REAL-WORLD SCENARIOS".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    try:
        scenario_1_message_storage()
        scenario_2_config_storage()
        scenario_3_backup_restore()
        scenario_4_data_modification()
        scenario_5_multi_file_archive()
        scenario_6_streaming_data()
        scenario_7_database_field()
        
        print("\n" + "=" * 70)
        print("  ✓ ALL REAL-WORLD SCENARIOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nThe Bioart Translator is ready for real-world use!")
        print("\nKey Capabilities Demonstrated:")
        print("  ✓ Message storage and retrieval")
        print("  ✓ Configuration management")
        print("  ✓ Document backup and restore")
        print("  ✓ DNA sequence modification")
        print("  ✓ Multi-file archiving")
        print("  ✓ Streaming data processing")
        print("  ✓ Database field encoding")
        print("\n" + "=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
