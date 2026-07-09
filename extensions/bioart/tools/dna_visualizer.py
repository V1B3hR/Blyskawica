#!/usr/bin/env python3
"""
DNA Program Visualization Tool
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bioart import Bioart
from core.encoding import DNAEncoder

def main():
    """Demo of DNA visualization tools"""
    print("🧬 DNA PROGRAM VISUALIZATION TOOL")
    print("=" * 40)
    
    bioart = Bioart()
    
    # Example DNA program
    sample_program = "AAAU AACA AAAG AAAC AAUG AAGA"
    print(f"\nSample DNA Program: {sample_program}")
    
    # Clean and parse program
    clean_dna = ''.join(sample_program.split()).upper()
    print(f"Cleaned: {clean_dna}")
    print(f"Length: {len(clean_dna)} nucleotides")
    
    # Show instructions
    print("\n💻 Instructions:")
    for i in range(0, len(clean_dna), 4):
        instruction_dna = clean_dna[i:i+4]
        byte_val = bioart.dna_to_byte(instruction_dna)
        
        if byte_val in bioart.byte_to_instruction:
            _, instruction_name = bioart.byte_to_instruction[byte_val]
        else:
            instruction_name = "DATA"
        
        print(f"{i//4:04d}: {instruction_dna} ({byte_val:02X}) {instruction_name}")

if __name__ == "__main__":
    main()