#!/usr/bin/env python3
"""
Bioart Translator Module
Complete, reversible translator for DNA-based encoding with real-world usability
"""

from typing import Union, Optional, Dict, Any, List
import sys
import os

# Handle both relative and absolute imports
try:
    from .core.encoding import DNAEncoder
except ImportError:
    from core.encoding import DNAEncoder


class BioartTranslator:
    """
    Comprehensive translator for converting between text, binary, and DNA sequences.
    Provides a clean, user-friendly API for real-world applications.
    """
    
    def __init__(self):
        """Initialize the translator with DNA encoder"""
        self.encoder = DNAEncoder()
        self.stats = {
            'translations': 0,
            'reversals': 0,
            'modifications': 0,
            'validations': 0
        }
    
    # ======================================
    # TEXT TO DNA TRANSLATION
    # ======================================
    
    def text_to_dna(self, text: str) -> str:
        """
        Convert text string to DNA sequence
        
        Args:
            text: Input text string
            
        Returns:
            DNA sequence representing the text
            
        Example:
            >>> translator.text_to_dna("Hello")
            'UACAUCUUUCGAUCGAUCGA'
        """
        try:
            byte_data = text.encode('utf-8')
            dna_sequence = self.encoder.encode_bytes(byte_data)
            self.stats['translations'] += 1
            return dna_sequence
        except Exception as e:
            raise ValueError(f"Failed to convert text to DNA: {e}")
    
    def dna_to_text(self, dna_sequence: str) -> str:
        """
        Convert DNA sequence back to text string
        
        Args:
            dna_sequence: DNA sequence to decode
            
        Returns:
            Decoded text string
            
        Example:
            >>> translator.dna_to_text('UACAUCUUUCGAUCGAUCGA')
            'Hello'
        """
        try:
            byte_data = self.encoder.decode_dna(dna_sequence)
            text = bytes(byte_data).decode('utf-8')
            self.stats['reversals'] += 1
            return text
        except UnicodeDecodeError:
            raise ValueError("DNA sequence does not represent valid UTF-8 text")
        except Exception as e:
            raise ValueError(f"Failed to convert DNA to text: {e}")
    
    # ======================================
    # BINARY TO DNA TRANSLATION
    # ======================================
    
    def binary_to_dna(self, data: Union[bytes, bytearray, List[int]]) -> str:
        """
        Convert binary data to DNA sequence
        
        Args:
            data: Binary data (bytes, bytearray, or list of integers)
            
        Returns:
            DNA sequence representing the binary data
            
        Example:
            >>> translator.binary_to_dna(b'\\x48\\x65\\x6c\\x6c\\x6f')
            'UACAUCUUUCGAUCGAUCGA'
        """
        try:
            dna_sequence = self.encoder.encode_bytes(data)
            self.stats['translations'] += 1
            return dna_sequence
        except Exception as e:
            raise ValueError(f"Failed to convert binary to DNA: {e}")
    
    def dna_to_binary(self, dna_sequence: str) -> bytes:
        """
        Convert DNA sequence to binary data
        
        Args:
            dna_sequence: DNA sequence to decode
            
        Returns:
            Binary data as bytes
            
        Example:
            >>> translator.dna_to_binary('UACAUCUUUCGAUCGAUCGA')
            b'Hello'
        """
        try:
            byte_data = self.encoder.decode_dna(dna_sequence)
            self.stats['reversals'] += 1
            return bytes(byte_data)
        except Exception as e:
            raise ValueError(f"Failed to convert DNA to binary: {e}")
    
    # ======================================
    # FILE OPERATIONS
    # ======================================
    
    def file_to_dna(self, filename: str) -> str:
        """
        Convert entire file to DNA sequence
        
        Args:
            filename: Path to file to convert
            
        Returns:
            DNA sequence representing the file contents
        """
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            dna_sequence = self.encoder.encode_bytes(data)
            self.stats['translations'] += 1
            return dna_sequence
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except Exception as e:
            raise ValueError(f"Failed to convert file to DNA: {e}")
    
    def dna_to_file(self, dna_sequence: str, filename: str) -> None:
        """
        Convert DNA sequence to file
        
        Args:
            dna_sequence: DNA sequence to decode
            filename: Path to output file
        """
        try:
            byte_data = self.encoder.decode_dna(dna_sequence)
            with open(filename, 'wb') as f:
                f.write(bytes(byte_data))
            self.stats['reversals'] += 1
        except Exception as e:
            raise ValueError(f"Failed to write DNA to file: {e}")
    
    # ======================================
    # DNA SEQUENCE MODIFICATION
    # ======================================
    
    def modify_nucleotide(self, dna_sequence: str, position: int, new_nucleotide: str) -> str:
        """
        Modify a single nucleotide in a DNA sequence
        
        Args:
            dna_sequence: Original DNA sequence
            position: Position to modify (0-indexed)
            new_nucleotide: New nucleotide (A, U, C, or G)
            
        Returns:
            Modified DNA sequence
        """
        if position < 0 or position >= len(dna_sequence):
            raise ValueError(f"Position {position} out of range for sequence of length {len(dna_sequence)}")
        
        if new_nucleotide.upper() not in ['A', 'U', 'C', 'G']:
            raise ValueError(f"Invalid nucleotide: {new_nucleotide}")
        
        seq_list = list(dna_sequence.upper())
        seq_list[position] = new_nucleotide.upper()
        self.stats['modifications'] += 1
        return ''.join(seq_list)
    
    def insert_sequence(self, dna_sequence: str, position: int, insert_seq: str) -> str:
        """
        Insert a DNA sequence at a specific position
        
        Args:
            dna_sequence: Original DNA sequence
            position: Position to insert at (0-indexed)
            insert_seq: Sequence to insert
            
        Returns:
            Modified DNA sequence
        """
        if position < 0 or position > len(dna_sequence):
            raise ValueError(f"Position {position} out of range for sequence of length {len(dna_sequence)}")
        
        # Validate insert sequence
        for nucleotide in insert_seq.upper():
            if nucleotide not in ['A', 'U', 'C', 'G']:
                raise ValueError(f"Invalid nucleotide in insert sequence: {nucleotide}")
        
        modified = dna_sequence[:position] + insert_seq.upper() + dna_sequence[position:]
        self.stats['modifications'] += 1
        return modified
    
    def delete_sequence(self, dna_sequence: str, start: int, length: int) -> str:
        """
        Delete a portion of DNA sequence
        
        Args:
            dna_sequence: Original DNA sequence
            start: Starting position (0-indexed)
            length: Number of nucleotides to delete
            
        Returns:
            Modified DNA sequence
        """
        if start < 0 or start >= len(dna_sequence):
            raise ValueError(f"Start position {start} out of range")
        
        if start + length > len(dna_sequence):
            raise ValueError(f"Deletion extends beyond sequence length")
        
        modified = dna_sequence[:start] + dna_sequence[start + length:]
        self.stats['modifications'] += 1
        return modified
    
    def replace_sequence(self, dna_sequence: str, start: int, length: int, new_seq: str) -> str:
        """
        Replace a portion of DNA sequence with new sequence
        
        Args:
            dna_sequence: Original DNA sequence
            start: Starting position (0-indexed)
            length: Number of nucleotides to replace
            new_seq: New sequence to insert
            
        Returns:
            Modified DNA sequence
        """
        if start < 0 or start >= len(dna_sequence):
            raise ValueError(f"Start position {start} out of range")
        
        # Validate new sequence
        for nucleotide in new_seq.upper():
            if nucleotide not in ['A', 'U', 'C', 'G']:
                raise ValueError(f"Invalid nucleotide in new sequence: {nucleotide}")
        
        modified = dna_sequence[:start] + new_seq.upper() + dna_sequence[start + length:]
        self.stats['modifications'] += 1
        return modified
    
    # ======================================
    # VALIDATION AND VERIFICATION
    # ======================================
    
    def validate_dna(self, dna_sequence: str) -> bool:
        """
        Validate that a string is a valid DNA sequence
        
        Args:
            dna_sequence: DNA sequence to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            for nucleotide in dna_sequence.upper():
                if nucleotide not in ['A', 'U', 'C', 'G']:
                    return False
            self.stats['validations'] += 1
            return True
        except:
            return False
    
    def verify_reversibility(self, data: Union[str, bytes]) -> Dict[str, Any]:
        """
        Verify that data can be converted to DNA and back without loss
        
        Args:
            data: String or bytes to verify
            
        Returns:
            Dictionary with verification results
        """
        result = {
            'success': False,
            'original_size': 0,
            'dna_size': 0,
            'restored_size': 0,
            'match': False,
            'error': None
        }
        
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                original_bytes = data.encode('utf-8')
                result['original_size'] = len(data)
            else:
                original_bytes = data
                result['original_size'] = len(original_bytes)
            
            # Convert to DNA
            dna_sequence = self.encoder.encode_bytes(original_bytes)
            result['dna_size'] = len(dna_sequence)
            
            # Convert back
            restored_bytes = bytes(self.encoder.decode_dna(dna_sequence))
            result['restored_size'] = len(restored_bytes)
            
            # Verify match
            result['match'] = (original_bytes == restored_bytes)
            result['success'] = result['match']
            
            self.stats['validations'] += 1
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    # ======================================
    # UTILITY FUNCTIONS
    # ======================================
    
    def get_sequence_info(self, dna_sequence: str) -> Dict[str, Any]:
        """
        Get information about a DNA sequence
        
        Args:
            dna_sequence: DNA sequence to analyze
            
        Returns:
            Dictionary with sequence information
        """
        info = {
            'length': len(dna_sequence),
            'byte_capacity': len(dna_sequence) // 4,
            'is_valid': self.validate_dna(dna_sequence),
            'is_complete': len(dna_sequence) % 4 == 0,
            'nucleotide_counts': {},
            'gc_content': 0.0
        }
        
        if info['is_valid']:
            seq_upper = dna_sequence.upper()
            for nucleotide in ['A', 'U', 'C', 'G']:
                count = seq_upper.count(nucleotide)
                info['nucleotide_counts'][nucleotide] = count
            
            # Calculate GC content
            total = len(dna_sequence)
            gc_count = info['nucleotide_counts'].get('G', 0) + info['nucleotide_counts'].get('C', 0)
            if total > 0:
                info['gc_content'] = (gc_count / total) * 100
        
        return info
    
    def format_dna(self, dna_sequence: str, width: int = 80, group_size: int = 4) -> str:
        """
        Format DNA sequence for display
        
        Args:
            dna_sequence: DNA sequence to format
            width: Line width for wrapping
            group_size: Group nucleotides in chunks
            
        Returns:
            Formatted DNA sequence
        """
        formatted = []
        for i in range(0, len(dna_sequence), group_size):
            chunk = dna_sequence[i:i+group_size]
            formatted.append(chunk)
        
        # Join with spaces and wrap at width
        grouped = ' '.join(formatted)
        lines = []
        for i in range(0, len(grouped), width):
            lines.append(grouped[i:i+width])
        
        return '\n'.join(lines)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get translator usage statistics
        
        Returns:
            Dictionary with usage stats
        """
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset usage statistics"""
        self.stats = {
            'translations': 0,
            'reversals': 0,
            'modifications': 0,
            'validations': 0
        }


# Convenience functions for quick access
def translate_text_to_dna(text: str) -> str:
    """Quick function to translate text to DNA"""
    translator = BioartTranslator()
    return translator.text_to_dna(text)


def translate_dna_to_text(dna: str) -> str:
    """Quick function to translate DNA to text"""
    translator = BioartTranslator()
    return translator.dna_to_text(dna)


def translate_binary_to_dna(data: bytes) -> str:
    """Quick function to translate binary to DNA"""
    translator = BioartTranslator()
    return translator.binary_to_dna(data)


def translate_dna_to_binary(dna: str) -> bytes:
    """Quick function to translate DNA to binary"""
    translator = BioartTranslator()
    return translator.dna_to_binary(dna)
