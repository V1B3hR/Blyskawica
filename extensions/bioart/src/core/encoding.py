#!/usr/bin/env python3
"""
DNA Encoding Core Module
High-performance DNA sequence encoding/decoding with optimizations
"""

from typing import Union, List, Iterator, Tuple
import struct

class DNAEncoder:
    """
    High-performance DNA encoding/decoding with optimized algorithms
    """
    
    # Optimized lookup tables for maximum performance
    DNA_TO_BITS = {
        'A': '00', 'U': '01', 'C': '10', 'G': '11',
        'a': '00', 'u': '01', 'c': '10', 'g': '11'  # Case insensitive
    }
    
    BITS_TO_DNA = {'00': 'A', '01': 'U', '10': 'C', '11': 'G'}
    
    # Precomputed lookup tables for batch operations
    BYTE_TO_DNA_LUT = {}
    DNA_TO_BYTE_LUT = {}
    
    @classmethod
    def _initialize_lookup_tables(cls):
        """Initialize precomputed lookup tables for maximum performance"""
        if not cls.BYTE_TO_DNA_LUT:
            # Precompute all 256 byte to DNA mappings
            for byte_val in range(256):
                binary_str = f'{byte_val:08b}'
                dna_seq = ''.join(cls.BITS_TO_DNA[binary_str[i:i+2]] for i in range(0, 8, 2))
                cls.BYTE_TO_DNA_LUT[byte_val] = dna_seq
            
            # Precompute all DNA to byte mappings
            for byte, dna in cls.BYTE_TO_DNA_LUT.items():
                cls.DNA_TO_BYTE_LUT[dna] = byte
                # Add lowercase variants
                cls.DNA_TO_BYTE_LUT[dna.lower()] = byte
    
    def __init__(self):
        """Initialize the DNA encoder with optimized lookup tables"""
        self._initialize_lookup_tables()
    
    def nucleotide_to_bits(self, nucleotide: str) -> str:
        """Convert single nucleotide to 2-bit representation"""
        if nucleotide not in self.DNA_TO_BITS:
            raise ValueError(f"Invalid nucleotide: {nucleotide}")
        return self.DNA_TO_BITS[nucleotide]
    
    def bits_to_nucleotide(self, bits: str) -> str:
        """Convert 2-bit representation to nucleotide"""
        if bits not in self.BITS_TO_DNA:
            raise ValueError(f"Invalid bit pattern: {bits}")
        return self.BITS_TO_DNA[bits]
    
    def dna_to_byte(self, dna_sequence: str) -> int:
        """
        Convert 4-nucleotide DNA sequence to byte value
        Optimized with lookup table for maximum performance
        """
        if isinstance(dna_sequence, list):
            dna_sequence = ''.join(dna_sequence)
        if len(dna_sequence) != 4:
            raise ValueError(f"DNA sequence must be exactly 4 nucleotides, got {len(dna_sequence)}")
        
        # Use precomputed lookup table
        dna_upper = dna_sequence.upper()
        if dna_upper in self.DNA_TO_BYTE_LUT:
            return self.DNA_TO_BYTE_LUT[dna_upper]
        
        # Fallback for invalid sequences
        try:
            binary_str = ''.join(self.DNA_TO_BITS[nucleotide.upper()] for nucleotide in dna_sequence)
            return int(binary_str, 2)
        except KeyError as e:
            raise ValueError(f"Invalid nucleotide in sequence '{dna_sequence}': {e}")
    
    def byte_to_dna(self, byte_val: int) -> str:
        """
        Convert byte value to 4-nucleotide DNA sequence
        Optimized with lookup table for maximum performance
        """
        if not 0 <= byte_val <= 255:
            raise ValueError(f"Byte value must be 0-255, got {byte_val}")
        
        return self.BYTE_TO_DNA_LUT[byte_val]
    
    def encode_bytes(self, data: Union[bytes, bytearray, List[int]]) -> str:
        """
        Encode byte data to DNA sequence
        Optimized for bulk operations
        """
        if isinstance(data, (bytes, bytearray)):
            byte_list = list(data)
        else:
            byte_list = data
        
        # Vectorized operation using lookup table
        return ''.join(self.BYTE_TO_DNA_LUT[byte_val] for byte_val in byte_list)
    
    def decode_dna(self, dna_sequence: str) -> bytes:
        """
        Decode DNA sequence to byte data
        Optimized for bulk operations with chunking
        """
        # Remove whitespace and validate length
        clean_dna = ''.join(dna_sequence.split()).upper()
        
        if len(clean_dna) % 4 != 0:
            raise ValueError(f"DNA sequence length must be multiple of 4, got {len(clean_dna)}")
        
        # Process in chunks of 4 nucleotides
        byte_data = []
        for i in range(0, len(clean_dna), 4):
            chunk = clean_dna[i:i+4]
            # Ensure chunk is a string for lookup, not list
            if isinstance(chunk, list):
                chunk = ''.join(chunk)
            if chunk in self.DNA_TO_BYTE_LUT:
                byte_data.append(self.DNA_TO_BYTE_LUT[chunk])
            else:
                raise ValueError(f"Invalid DNA sequence chunk: {chunk}")
        
        return bytes(byte_data)
    
    def encode_string(self, text: str, encoding: str = 'utf-8') -> str:
        """Encode text string to DNA sequence"""
        byte_data = text.encode(encoding)
        return self.encode_bytes(byte_data)
    
    def decode_to_string(self, dna_sequence: str, encoding: str = 'utf-8') -> str:
        """Decode DNA sequence to text string"""
        byte_data = self.decode_dna(dna_sequence)
        return byte_data.decode(encoding)
    
    def encode_file_data(self, file_data: bytes) -> str:
        """Encode file data to DNA sequence with chunking for large files"""
        # For large files, process in chunks to avoid memory issues
        chunk_size = 1024 * 1024  # 1MB chunks
        
        if len(file_data) <= chunk_size:
            return self.encode_bytes(file_data)
        
        # Process large files in chunks
        dna_chunks = []
        for i in range(0, len(file_data), chunk_size):
            chunk = file_data[i:i + chunk_size]
            dna_chunks.append(self.encode_bytes(chunk))
        
        return ''.join(dna_chunks)
    
    def get_encoding_stats(self, data_size: int) -> dict:
        """Get encoding statistics for given data size"""
        return {
            'input_bytes': data_size,
            'output_nucleotides': data_size * 4,
            'compression_ratio': 4.0,  # 4 nucleotides per byte
            'efficiency': '100% (optimal)',
            'reversible': True
        }
    
    def validate_dna_sequence(self, dna_sequence: str) -> Tuple[bool, str]:
        """Validate DNA sequence format and content"""
        try:
            clean_dna = ''.join(dna_sequence.split()).upper()
            
            # Check length
            if len(clean_dna) % 4 != 0:
                return False, f"Length {len(clean_dna)} is not multiple of 4"
            
            # Check valid nucleotides
            valid_nucleotides = set('AUCG')
            invalid_chars = set(clean_dna) - valid_nucleotides
            if invalid_chars:
                return False, f"Invalid characters: {invalid_chars}"
            
            # Try to decode
            self.decode_dna(clean_dna)
            return True, "Valid DNA sequence"
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_theoretical_capacity(nucleotide_count: int) -> dict:
        """Calculate theoretical storage capacity for given nucleotide count"""
        byte_capacity = nucleotide_count // 4
        return {
            'nucleotides': nucleotide_count,
            'bytes': byte_capacity,
            'kilobytes': byte_capacity / 1024,
            'megabytes': byte_capacity / (1024 * 1024),
            'bits': byte_capacity * 8,
            'efficiency': '100% (maximum theoretical)'
        }


# Singleton instance for global use
dna_encoder = DNAEncoder()

# Convenience functions for direct use
def encode_bytes(data: Union[bytes, bytearray, List[int]]) -> str:
    """Encode bytes to DNA sequence"""
    return dna_encoder.encode_bytes(data)

def decode_dna(dna_sequence: str) -> bytes:
    """Decode DNA sequence to bytes"""
    return dna_encoder.decode_dna(dna_sequence)

def encode_string(text: str) -> str:
    """Encode string to DNA sequence"""
    return dna_encoder.encode_string(text)

def decode_to_string(dna_sequence: str) -> str:
    """Decode DNA sequence to string"""
    return dna_encoder.decode_to_string(dna_sequence)
