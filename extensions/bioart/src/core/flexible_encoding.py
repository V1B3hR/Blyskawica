#!/usr/bin/env python3
"""
Flexible Input Alphabet Support for Bioart DNA Programming Language
Allows alternate mappings (T instead of U, custom mappings) for flexibility
"""

from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json

class AlphabetType(Enum):
    """Types of DNA alphabets"""
    STANDARD_RNA = "RNA"  # A, U, C, G (default)
    STANDARD_DNA = "DNA"  # A, T, C, G  
    CUSTOM = "CUSTOM"     # User-defined

@dataclass
class DNAAlphabet:
    """DNA alphabet configuration"""
    name: str
    alphabet_type: AlphabetType
    nucleotides: List[str]
    bit_mapping: Dict[str, str]
    description: str = ""
    
    def __post_init__(self):
        if len(self.nucleotides) != 4:
            raise ValueError("DNA alphabet must have exactly 4 nucleotides")
        if len(self.bit_mapping) != 4:
            raise ValueError("Bit mapping must have exactly 4 entries")
        
        # Validate bit patterns are unique and valid
        bit_patterns = set(self.bit_mapping.values())
        if len(bit_patterns) != 4:
            raise ValueError("All bit patterns must be unique")
        
        expected_patterns = {'00', '01', '10', '11'}
        if bit_patterns != expected_patterns:
            raise ValueError(f"Bit patterns must be {expected_patterns}")

class FlexibleDNAEncoder:
    """DNA encoder with flexible alphabet support"""
    
    def __init__(self, alphabet: DNAAlphabet = None):
        """Initialize with specified alphabet"""
        self.alphabets = self._create_standard_alphabets()
        self.current_alphabet = alphabet or self.alphabets["RNA"]
        self._update_lookup_tables()
    
    def _create_standard_alphabets(self) -> Dict[str, DNAAlphabet]:
        """Create standard alphabet configurations"""
        alphabets = {}
        
        # Standard RNA alphabet (A, U, C, G)
        alphabets["RNA"] = DNAAlphabet(
            name="Standard RNA",
            alphabet_type=AlphabetType.STANDARD_RNA,
            nucleotides=['A', 'U', 'C', 'G'],
            bit_mapping={'A': '00', 'U': '01', 'C': '10', 'G': '11'},
            description="Standard RNA nucleotides with Uracil"
        )
        
        # Standard DNA alphabet (A, T, C, G)
        alphabets["DNA"] = DNAAlphabet(
            name="Standard DNA",
            alphabet_type=AlphabetType.STANDARD_DNA,
            nucleotides=['A', 'T', 'C', 'G'],
            bit_mapping={'A': '00', 'T': '01', 'C': '10', 'G': '11'},
            description="Standard DNA nucleotides with Thymine"
        )
        
        # Purine/Pyrimidine alphabet
        alphabets["PUPY"] = DNAAlphabet(
            name="Purine-Pyrimidine",
            alphabet_type=AlphabetType.CUSTOM,
            nucleotides=['R', 'Y', 'S', 'W'],  # R=purine, Y=pyrimidine, S=strong, W=weak
            bit_mapping={'R': '00', 'Y': '01', 'S': '10', 'W': '11'},
            description="Purine/Pyrimidine based encoding"
        )
        
        return alphabets
    
    def _update_lookup_tables(self):
        """Update lookup tables for current alphabet"""
        self.nucleotide_to_bits = self.current_alphabet.bit_mapping.copy()
        
        # Add lowercase support
        for nuc, bits in self.current_alphabet.bit_mapping.items():
            self.nucleotide_to_bits[nuc.lower()] = bits
        
        # Create reverse mapping
        self.bits_to_nucleotide = {v: k for k, v in self.current_alphabet.bit_mapping.items()}
        
        # Create byte lookup tables
        self._create_byte_lookup_tables()
    
    def _create_byte_lookup_tables(self):
        """Create optimized byte <-> DNA lookup tables"""
        self.byte_to_dna_lut = {}
        self.dna_to_byte_lut = {}
        
        # Create all 256 byte to DNA mappings
        for byte_val in range(256):
            binary_str = f'{byte_val:08b}'
            dna_seq = ''.join(self.bits_to_nucleotide[binary_str[i:i+2]] for i in range(0, 8, 2))
            self.byte_to_dna_lut[byte_val] = dna_seq
        
        # Create DNA to byte mappings
        for byte_val, dna_seq in self.byte_to_dna_lut.items():
            self.dna_to_byte_lut[dna_seq] = byte_val
            # Add lowercase version
            self.dna_to_byte_lut[dna_seq.lower()] = byte_val
    
    def set_alphabet(self, alphabet_name: str):
        """Set the current alphabet by name"""
        if alphabet_name not in self.alphabets:
            raise ValueError(f"Unknown alphabet: {alphabet_name}. Available: {list(self.alphabets.keys())}")
        
        self.current_alphabet = self.alphabets[alphabet_name]
        self._update_lookup_tables()
    
    def add_custom_alphabet(self, alphabet: DNAAlphabet):
        """Add a custom alphabet"""
        self.alphabets[alphabet.name] = alphabet
    
    def get_current_alphabet_info(self) -> Dict[str, any]:
        """Get information about the current alphabet"""
        return {
            "name": self.current_alphabet.name,
            "type": self.current_alphabet.alphabet_type.value,
            "nucleotides": self.current_alphabet.nucleotides,
            "mapping": self.current_alphabet.bit_mapping,
            "description": self.current_alphabet.description
        }
    
    def list_alphabets(self) -> List[str]:
        """List all available alphabets"""
        return list(self.alphabets.keys())
    
    def encode_bytes(self, data: Union[bytes, bytearray, List[int]]) -> str:
        """Encode byte data to DNA sequence using current alphabet"""
        if isinstance(data, (bytes, bytearray)):
            byte_list = list(data)
        else:
            byte_list = data
        
        return ''.join(self.byte_to_dna_lut[byte_val] for byte_val in byte_list)
    
    def decode_dna(self, dna_sequence: str) -> bytes:
        """Decode DNA sequence to byte data using current alphabet"""
        # Remove whitespace and normalize case
        clean_dna = ''.join(dna_sequence.split()).upper()
        
        if len(clean_dna) % 4 != 0:
            raise ValueError(f"DNA sequence length must be multiple of 4, got {len(clean_dna)}")
        
        # Process in chunks of 4 nucleotides
        byte_data = []
        for i in range(0, len(clean_dna), 4):
            chunk = clean_dna[i:i+4]
            if chunk in self.dna_to_byte_lut:
                byte_data.append(self.dna_to_byte_lut[chunk])
            else:
                raise ValueError(f"Invalid DNA sequence chunk: {chunk} for alphabet {self.current_alphabet.name}")
        
        return bytes(byte_data)
    
    def convert_between_alphabets(self, dna_sequence: str, 
                                source_alphabet: str, target_alphabet: str) -> str:
        """Convert DNA sequence from one alphabet to another"""
        # Save current alphabet key (not name)
        original_alphabet_key = None
        for key, alphabet in self.alphabets.items():
            if alphabet == self.current_alphabet:
                original_alphabet_key = key
                break
        
        try:
            # Decode using source alphabet
            self.set_alphabet(source_alphabet)
            byte_data = self.decode_dna(dna_sequence)
            
            # Encode using target alphabet
            self.set_alphabet(target_alphabet)
            converted_sequence = self.encode_bytes(byte_data)
            
            return converted_sequence
            
        finally:
            # Restore original alphabet
            if original_alphabet_key:
                self.set_alphabet(original_alphabet_key)
    
    def validate_sequence(self, dna_sequence: str) -> Tuple[bool, List[str]]:
        """Validate a DNA sequence against the current alphabet"""
        errors = []
        clean_dna = ''.join(dna_sequence.split()).upper()
        
        # Check length
        if len(clean_dna) % 4 != 0:
            errors.append(f"Sequence length {len(clean_dna)} is not multiple of 4")
        
        # Check nucleotides
        valid_nucleotides = set(self.current_alphabet.nucleotides)
        for i, nucleotide in enumerate(clean_dna):
            if nucleotide not in valid_nucleotides:
                errors.append(f"Invalid nucleotide '{nucleotide}' at position {i}")
        
        return len(errors) == 0, errors
    
    def get_alphabet_statistics(self, dna_sequence: str) -> Dict[str, any]:
        """Get statistics about a DNA sequence"""
        clean_dna = ''.join(dna_sequence.split()).upper()
        
        # Count nucleotides
        counts = {nuc: clean_dna.count(nuc) for nuc in self.current_alphabet.nucleotides}
        total = sum(counts.values())
        
        # Calculate frequencies
        frequencies = {nuc: count / total if total > 0 else 0 
                      for nuc, count in counts.items()}
        
        return {
            "alphabet": self.current_alphabet.name,
            "length": len(clean_dna),
            "counts": counts,
            "frequencies": frequencies,
            "gc_content": self._calculate_gc_content(clean_dna),
            "purine_content": self._calculate_purine_content(clean_dna)
        }
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content (if applicable to current alphabet)"""
        gc_nucleotides = {'G', 'C'}
        gc_count = sum(1 for nuc in sequence if nuc in gc_nucleotides)
        return gc_count / len(sequence) if len(sequence) > 0 else 0.0
    
    def _calculate_purine_content(self, sequence: str) -> float:
        """Calculate purine content (A, G if using standard alphabets)"""
        purine_nucleotides = {'A', 'G', 'R'}  # R represents purine in IUPAC
        purine_count = sum(1 for nuc in sequence if nuc in purine_nucleotides)
        return purine_count / len(sequence) if len(sequence) > 0 else 0.0
    
    def save_alphabet_config(self, filename: str):
        """Save alphabet configurations to file"""
        config = {}
        for name, alphabet in self.alphabets.items():
            config[name] = {
                "name": alphabet.name,
                "type": alphabet.alphabet_type.value,
                "nucleotides": alphabet.nucleotides,
                "bit_mapping": alphabet.bit_mapping,
                "description": alphabet.description
            }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_alphabet_config(self, filename: str):
        """Load alphabet configurations from file"""
        with open(filename, 'r') as f:
            config = json.load(f)
        
        for name, alphabet_data in config.items():
            alphabet = DNAAlphabet(
                name=alphabet_data["name"],
                alphabet_type=AlphabetType(alphabet_data["type"]),
                nucleotides=alphabet_data["nucleotides"],
                bit_mapping=alphabet_data["bit_mapping"],
                description=alphabet_data.get("description", "")
            )
            self.alphabets[name] = alphabet

def main():
    """Demo of flexible alphabet encoding"""
    print("🧬 FLEXIBLE ALPHABET ENCODING DEMO")
    print("=" * 40)
    
    encoder = FlexibleDNAEncoder()
    
    # Test data
    test_data = b"Hello, DNA!"
    print(f"Test data: {test_data}")
    
    # Test different alphabets
    alphabets_to_test = ["RNA", "DNA", "PUPY"]
    
    for alphabet_name in alphabets_to_test:
        print(f"\n--- {alphabet_name} Alphabet ---")
        encoder.set_alphabet(alphabet_name)
        
        # Show alphabet info
        info = encoder.get_current_alphabet_info()
        print(f"Nucleotides: {info['nucleotides']}")
        print(f"Mapping: {info['mapping']}")
        
        # Encode data
        dna_sequence = encoder.encode_bytes(test_data)
        print(f"Encoded: {dna_sequence}")
        
        # Decode back
        decoded_data = encoder.decode_dna(dna_sequence)
        print(f"Decoded: {decoded_data}")
        print(f"Roundtrip: {'✅ PASS' if decoded_data == test_data else '❌ FAIL'}")
        
        # Get statistics
        stats = encoder.get_alphabet_statistics(dna_sequence)
        print(f"GC Content: {stats['gc_content']:.2%}")
    
    # Test alphabet conversion
    print(f"\n--- Alphabet Conversion ---")
    encoder.set_alphabet("RNA")
    rna_sequence = encoder.encode_bytes(b"DNA")
    print(f"RNA encoding of 'DNA': {rna_sequence}")
    
    dna_sequence = encoder.convert_between_alphabets(rna_sequence, "RNA", "DNA")
    print(f"DNA encoding of same data: {dna_sequence}")
    
    # Verify conversion
    encoder.set_alphabet("DNA")
    decoded = encoder.decode_dna(dna_sequence)
    print(f"Decoded from DNA: {decoded}")
    print(f"Conversion: {'✅ PASS' if decoded == b'DNA' else '❌ FAIL'}")

if __name__ == "__main__":
    main()