#!/usr/bin/env python3
"""
Bioinformatics Tool Interoperability for Bioart DNA Programming Language
Support for FASTA format and other bioinformatics file formats
"""

import os
import sys
import time
import re
from typing import Dict, List, Optional, Tuple, Iterator, TextIO
from dataclasses import dataclass
from io import StringIO

# Import our encoding systems
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.encoding import DNAEncoder
from core.flexible_encoding import FlexibleDNAEncoder, DNAAlphabet, AlphabetType

@dataclass
class FASTARecord:
    """FASTA sequence record"""
    identifier: str
    description: str
    sequence: str
    length: int = 0
    
    def __post_init__(self):
        if self.length == 0:
            self.length = len(self.sequence.replace(' ', '').replace('\n', ''))

@dataclass
class DNAProgramInfo:
    """Information about a DNA program embedded in FASTA"""
    program_name: str
    compiler_version: str
    instruction_count: int
    data_size: int
    created_timestamp: str
    description: str = ""

class FASTAHandler:
    """Handler for FASTA format files"""
    
    def __init__(self, encoder: Optional[FlexibleDNAEncoder] = None):
        self.encoder = encoder or FlexibleDNAEncoder()
    
    def read_fasta_file(self, filename: str) -> List[FASTARecord]:
        """Read a FASTA file and return list of records"""
        records = []
        
        with open(filename, 'r') as f:
            current_record = None
            sequence_lines = []
            
            for line in f:
                line = line.strip()
                
                if line.startswith('>'):
                    # Save previous record if exists
                    if current_record:
                        current_record.sequence = ''.join(sequence_lines)
                        current_record.length = len(current_record.sequence.replace(' ', ''))
                        records.append(current_record)
                    
                    # Parse header
                    header = line[1:]  # Remove '>'
                    parts = header.split(' ', 1)
                    identifier = parts[0]
                    description = parts[1] if len(parts) > 1 else ""
                    
                    current_record = FASTARecord(identifier, description, "")
                    sequence_lines = []
                
                elif line and not line.startswith(';'):  # Skip comments
                    sequence_lines.append(line)
            
            # Save last record
            if current_record:
                current_record.sequence = ''.join(sequence_lines)
                current_record.length = len(current_record.sequence.replace(' ', ''))
                records.append(current_record)
        
        return records
    
    def write_fasta_file(self, filename: str, records: List[FASTARecord], 
                        line_width: int = 80):
        """Write FASTA records to file"""
        with open(filename, 'w') as f:
            for record in records:
                # Write header
                header = f">{record.identifier}"
                if record.description:
                    header += f" {record.description}"
                f.write(f"{header}\n")
                
                # Write sequence with line wrapping
                sequence = record.sequence.replace(' ', '').replace('\n', '')
                for i in range(0, len(sequence), line_width):
                    f.write(f"{sequence[i:i+line_width]}\n")
    
    def create_dna_program_fasta(self, program_data: bytes, program_info: DNAProgramInfo,
                               output_filename: str):
        """Create a FASTA file containing a DNA program"""
        # Encode program data to DNA
        dna_sequence = self.encoder.encode_bytes(program_data)
        
        # Create description with metadata
        description = f"DNA_PROGRAM compiler={program_info.compiler_version} "
        description += f"instructions={program_info.instruction_count} "
        description += f"size={program_info.data_size} "
        description += f"created={program_info.created_timestamp}"
        
        if program_info.description:
            description += f" desc=\"{program_info.description}\""
        
        # Create FASTA record
        record = FASTARecord(
            identifier=program_info.program_name,
            description=description,
            sequence=dna_sequence
        )
        
        self.write_fasta_file(output_filename, [record])
    
    def extract_dna_program_from_fasta(self, filename: str, program_name: str = None) -> Tuple[bytes, DNAProgramInfo]:
        """Extract a DNA program from FASTA file"""
        records = self.read_fasta_file(filename)
        
        # Find DNA program record
        target_record = None
        if program_name:
            target_record = next((r for r in records if r.identifier == program_name), None)
        else:
            # Look for first record with DNA_PROGRAM in description
            target_record = next((r for r in records if "DNA_PROGRAM" in r.description), None)
        
        if not target_record:
            raise ValueError(f"No DNA program found in FASTA file")
        
        # Parse metadata from description
        program_info = self._parse_dna_program_metadata(target_record)
        
        # Decode DNA sequence to bytes
        program_data = self.encoder.decode_dna(target_record.sequence)
        
        return program_data, program_info
    
    def _parse_dna_program_metadata(self, record: FASTARecord) -> DNAProgramInfo:
        """Parse DNA program metadata from FASTA description"""
        desc = record.description
        
        # Extract metadata using regex
        compiler_match = re.search(r'compiler=([^\s]+)', desc)
        instructions_match = re.search(r'instructions=(\d+)', desc)
        size_match = re.search(r'size=(\d+)', desc)
        created_match = re.search(r'created=([^\s]+)', desc)
        desc_match = re.search(r'desc="([^"]*)"', desc)
        
        return DNAProgramInfo(
            program_name=record.identifier,
            compiler_version=compiler_match.group(1) if compiler_match else "unknown",
            instruction_count=int(instructions_match.group(1)) if instructions_match else 0,
            data_size=int(size_match.group(1)) if size_match else len(record.sequence) // 4,
            created_timestamp=created_match.group(1) if created_match else "unknown",
            description=desc_match.group(1) if desc_match else ""
        )
    
    def convert_alphabet_in_fasta(self, input_filename: str, output_filename: str,
                                source_alphabet: str, target_alphabet: str):
        """Convert DNA sequences in FASTA file from one alphabet to another"""
        records = self.read_fasta_file(input_filename)
        converted_records = []
        
        for record in records:
            # Convert sequence
            converted_sequence = self.encoder.convert_between_alphabets(
                record.sequence, source_alphabet, target_alphabet
            )
            
            # Update description to indicate conversion
            new_description = record.description
            if "CONVERTED" not in new_description:
                new_description += f" CONVERTED_{source_alphabet}_to_{target_alphabet}"
            
            converted_record = FASTARecord(
                identifier=record.identifier,
                description=new_description,
                sequence=converted_sequence
            )
            converted_records.append(converted_record)
        
        self.write_fasta_file(output_filename, converted_records)
    
    def validate_fasta_sequences(self, filename: str, alphabet_name: str = "RNA") -> Dict[str, any]:
        """Validate DNA sequences in FASTA file against specified alphabet"""
        records = self.read_fasta_file(filename)
        results = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": [],
            "alphabet_used": alphabet_name,
            "statistics": {}
        }
        
        # Set alphabet for validation
        self.encoder.set_alphabet(alphabet_name)
        
        for i, record in enumerate(records):
            is_valid, errors = self.encoder.validate_sequence(record.sequence)
            
            if is_valid:
                results["valid_records"] += 1
                
                # Get sequence statistics
                stats = self.encoder.get_alphabet_statistics(record.sequence)
                results["statistics"][record.identifier] = stats
            else:
                results["invalid_records"].append({
                    "record_index": i,
                    "identifier": record.identifier,
                    "errors": errors
                })
        
        return results

class GenBankHandler:
    """Basic GenBank format handler (simplified)"""
    
    def __init__(self, encoder: Optional[FlexibleDNAEncoder] = None):
        self.encoder = encoder or FlexibleDNAEncoder()
    
    def extract_sequence_from_genbank(self, filename: str) -> str:
        """Extract DNA sequence from GenBank file (basic implementation)"""
        sequence_lines = []
        in_origin = False
        
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('ORIGIN'):
                    in_origin = True
                    continue
                
                if line.startswith('//'):
                    in_origin = False
                    break
                
                if in_origin:
                    # Remove line numbers and spaces
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        sequence_lines.extend(parts[1:])
        
        return ''.join(sequence_lines).upper()

class BioinformaticsConverter:
    """Converter between bioinformatics formats and DNA programs"""
    
    def __init__(self):
        self.encoder = FlexibleDNAEncoder()
        self.fasta_handler = FASTAHandler(self.encoder)
        self.genbank_handler = GenBankHandler(self.encoder)
    
    def bioart_to_fasta(self, program_data: bytes, program_name: str, 
                       output_filename: str, description: str = ""):
        """Convert Bioart DNA program to FASTA format"""
        
        # Create program info
        program_info = DNAProgramInfo(
            program_name=program_name,
            compiler_version="2.0.0",
            instruction_count=len(program_data),
            data_size=len(program_data),
            created_timestamp=time.strftime("%Y-%m-%d_%H:%M:%S"),
            description=description
        )
        
        self.fasta_handler.create_dna_program_fasta(program_data, program_info, output_filename)
    
    def fasta_to_bioart(self, fasta_filename: str, program_name: str = None) -> bytes:
        """Convert FASTA DNA program back to Bioart format"""
        program_data, program_info = self.fasta_handler.extract_dna_program_from_fasta(
            fasta_filename, program_name
        )
        return program_data
    
    def create_multi_program_fasta(self, programs: Dict[str, bytes], 
                                 output_filename: str, descriptions: Dict[str, str] = None):
        """Create FASTA file with multiple DNA programs"""
        records = []
        descriptions = descriptions or {}
        
        for program_name, program_data in programs.items():
            program_info = DNAProgramInfo(
                program_name=program_name,
                compiler_version="2.0.0",
                instruction_count=len(program_data),
                data_size=len(program_data),
                created_timestamp=time.strftime("%Y-%m-%d_%H:%M:%S"),
                description=descriptions.get(program_name, "")
            )
            
            # Encode to DNA
            dna_sequence = self.encoder.encode_bytes(program_data)
            
            # Create description
            desc = f"DNA_PROGRAM compiler={program_info.compiler_version} "
            desc += f"instructions={program_info.instruction_count} "
            desc += f"size={program_info.data_size} "
            desc += f"created={program_info.created_timestamp}"
            
            if program_info.description:
                desc += f" desc=\"{program_info.description}\""
            
            record = FASTARecord(
                identifier=program_name,
                description=desc,
                sequence=dna_sequence
            )
            records.append(record)
        
        self.fasta_handler.write_fasta_file(output_filename, records)

def main():
    """Demo of bioinformatics format support"""
    print("🧬 BIOINFORMATICS INTEROPERABILITY DEMO")
    print("=" * 45)
    
    # Create test DNA program
    from bioart import Bioart
    bioart = Bioart()
    sample_program = "AAAU AACA AAAG AAAC AAUG AAGA"
    program_data = bioart.compile_dna_to_bytecode(sample_program)
    
    print(f"Sample program: {sample_program}")
    print(f"Compiled size: {len(program_data)} bytes")
    
    # Create converter
    converter = BioinformaticsConverter()
    
    # Test Bioart to FASTA conversion
    print("\n--- Bioart to FASTA Conversion ---")
    fasta_filename = "test_program.fasta"
    converter.bioart_to_fasta(
        program_data, 
        "arithmetic_program", 
        fasta_filename,
        "Simple arithmetic: Load 42, Add input, Print result"
    )
    print(f"Created FASTA file: {fasta_filename}")
    
    # Read and display FASTA content
    with open(fasta_filename, 'r') as f:
        fasta_content = f.read()
    print(f"FASTA content:\n{fasta_content}")
    
    # Test FASTA to Bioart conversion
    print("--- FASTA to Bioart Conversion ---")
    converted_data = converter.fasta_to_bioart(fasta_filename)
    print(f"Converted back: {len(converted_data)} bytes")
    print(f"Roundtrip: {'✅ PASS' if converted_data == program_data else '❌ FAIL'}")
    
    # Test FASTA validation
    print("\n--- FASTA Validation ---")
    fasta_handler = FASTAHandler()
    validation_results = fasta_handler.validate_fasta_sequences(fasta_filename, "RNA")
    print(f"Valid records: {validation_results['valid_records']}/{validation_results['total_records']}")
    
    if validation_results['statistics']:
        for record_id, stats in validation_results['statistics'].items():
            print(f"  {record_id}: GC content = {stats['gc_content']:.2%}")
    
    # Test multiple programs
    print("\n--- Multiple Programs FASTA ---")
    programs = {
        "hello_world": bioart.compile_dna_to_bytecode("AAAU AAUG AAGA"),
        "calculator": program_data
    }
    descriptions = {
        "hello_world": "Simple hello world program",
        "calculator": "Arithmetic calculator program"
    }
    
    multi_fasta = "multi_programs.fasta"
    converter.create_multi_program_fasta(programs, multi_fasta, descriptions)
    print(f"Created multi-program FASTA: {multi_fasta}")
    
    # Display multi-program FASTA
    with open(multi_fasta, 'r') as f:
        multi_content = f.read()
    print(f"Multi-program FASTA:\n{multi_content}")
    
    # Cleanup
    for filename in [fasta_filename, multi_fasta]:
        if os.path.exists(filename):
            os.remove(filename)
    
    print("✅ Bioinformatics demo completed!")

if __name__ == "__main__":
    main()