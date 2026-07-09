#!/usr/bin/env python3
"""
Bioart Programming Language - Option 1 Implementation
2-bit encoding: A=00, U=01, C=10, G=11
Maximum efficiency: 4 nucleotides per byte
Direct binary compatibility with existing systems
"""

import sys
import struct
from typing import List, Dict, Any

class Bioart:
    def __init__(self):
        # 2-bit encoding mapping
        self.dna_to_bits = {'A': '00', 'U': '01', 'C': '10', 'G': '11'}
        self.bits_to_dna = {'00': 'A', '01': 'U', '10': 'C', '11': 'G'}
        
        # DNA instruction set (using 4 nucleotides = 1 byte = 1 instruction)
        self.instructions = {
            'AAAA': 'NOP',      # 00000000 = 0   - No operation
            'AAAU': 'LOAD',     # 00000001 = 1   - Load value
            'AAAC': 'STORE',    # 00000010 = 2   - Store value
            'AAAG': 'ADD',      # 00000011 = 3   - Add
            'AAUA': 'SUB',      # 00000100 = 4   - Subtract
            'AAUU': 'MUL',      # 00000101 = 5   - Multiply
            'AAUC': 'DIV',      # 00000110 = 6   - Divide
            'AAUG': 'PRINT',    # 00000111 = 7   - Print
            'AACA': 'INPUT',    # 00001000 = 8   - Input
            'AACU': 'JMP',      # 00001001 = 9   - Jump
            'AACC': 'JEQ',      # 00001010 = 10  - Jump if equal
            'AACG': 'JNE',      # 00001011 = 11  - Jump if not equal
            'AAGA': 'HALT',     # 00001100 = 12  - Halt program
        }
        
        # Reverse mapping for disassembly
        self.byte_to_instruction = {}
        for dna, inst in self.instructions.items():
            byte_val = self.dna_to_byte(dna)
            self.byte_to_instruction[byte_val] = (dna, inst)
        
        # Virtual machine state
        self.memory = [0] * 256  # 256 bytes of memory
        self.registers = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        self.pc = 0  # Program counter
        self.running = True
        
    def dna_to_byte(self, dna_sequence: str) -> int:
        """Convert 4 DNA nucleotides to 1 byte"""
        if len(dna_sequence) != 4:
            raise ValueError("DNA sequence must be exactly 4 nucleotides")
        
        binary_str = ''.join(self.dna_to_bits[nucleotide] for nucleotide in dna_sequence)
        return int(binary_str, 2)
    
    def byte_to_dna(self, byte_val: int) -> str:
        """Convert 1 byte to 4 DNA nucleotides"""
        binary_str = format(byte_val, '08b')
        dna_sequence = ''
        for i in range(0, 8, 2):
            two_bits = binary_str[i:i+2]
            dna_sequence += self.bits_to_dna[two_bits]
        return dna_sequence
    
    def compile_dna_to_bytecode(self, dna_program: str) -> bytes:
        """Compile DNA source code to binary bytecode"""
        # Remove whitespace and newlines
        clean_dna = ''.join(dna_program.split())
        
        # Ensure program length is multiple of 4
        while len(clean_dna) % 4 != 0:
            clean_dna += 'A'  # Pad with NOP
        
        bytecode = []
        for i in range(0, len(clean_dna), 4):
            dna_instruction = clean_dna[i:i+4]
            byte_val = self.dna_to_byte(dna_instruction)
            bytecode.append(byte_val)
        
        return bytes(bytecode)
    
    def decompile_bytecode_to_dna(self, bytecode: bytes) -> str:
        """Decompile binary bytecode back to DNA source code"""
        dna_program = ""
        for byte_val in bytecode:
            dna_program += self.byte_to_dna(byte_val)
        return dna_program
    
    def save_binary(self, bytecode: bytes, filename: str):
        """Save compiled DNA program as binary file"""
        with open(filename, 'wb') as f:
            f.write(bytecode)
    
    def load_binary(self, filename: str) -> bytes:
        """Load binary file and return bytecode"""
        with open(filename, 'rb') as f:
            return f.read()
    
    def execute_bytecode(self, bytecode: bytes):
        """Execute compiled DNA bytecode"""
        self.pc = 0
        self.running = True
        program = list(bytecode)
        
        while self.running and self.pc < len(program):
            opcode = program[self.pc]
            
            if opcode in self.byte_to_instruction:
                dna, instruction = self.byte_to_instruction[opcode]
                self.execute_instruction(instruction, program)
            else:
                # Unknown instruction - treat as data
                pass
            
            self.pc += 1
    
    def execute_instruction(self, instruction: str, program: List[int]):
        """Execute a single instruction"""
        if instruction == 'NOP':
            pass
        elif instruction == 'LOAD':
            if self.pc + 1 < len(program):
                self.registers['A'] = program[self.pc + 1]
                self.pc += 1
        elif instruction == 'STORE':
            if self.pc + 1 < len(program):
                addr = program[self.pc + 1]
                self.memory[addr] = self.registers['A']
                self.pc += 1
        elif instruction == 'ADD':
            if self.pc + 1 < len(program):
                self.registers['A'] += program[self.pc + 1]
                self.pc += 1
        elif instruction == 'SUB':
            if self.pc + 1 < len(program):
                self.registers['A'] -= program[self.pc + 1]
                self.pc += 1
        elif instruction == 'PRINT':
            print(f"Output: {self.registers['A']}")
        elif instruction == 'HALT':
            self.running = False
    
    def disassemble(self, bytecode: bytes) -> str:
        """Disassemble bytecode to human-readable format"""
        result = []
        for i, byte_val in enumerate(bytecode):
            if byte_val in self.byte_to_instruction:
                dna, instruction = self.byte_to_instruction[byte_val]
                result.append(f"{i:04d}: {dna} ({byte_val:02X}) - {instruction}")
            else:
                dna = self.byte_to_dna(byte_val)
                result.append(f"{i:04d}: {dna} ({byte_val:02X}) - DATA")
        return '\n'.join(result)

def main():
    dna = Bioart()
    
    print("Bioart Programming Language - Option 1 (2-bit encoding)")
    print("=" * 50)
    
    # Example DNA program: Load 42, Add 8, Print result, Halt
    dna_source = """
    AAAU AACA AAUC AAAG AAAU AAAC AAAA AAUG AAGA
    """
    
    print("DNA Source Code:")
    print(dna_source.strip())
    print()
    
    # Compile to bytecode
    bytecode = dna.compile_dna_to_bytecode(dna_source)
    print("Compiled Bytecode (hex):")
    print(' '.join(f'{b:02X}' for b in bytecode))
    print()
    
    # Show binary compatibility
    print("Binary Representation:")
    for i, byte_val in enumerate(bytecode):
        binary = format(byte_val, '08b')
        dna_seq = dna.byte_to_dna(byte_val)
        print(f"Byte {i}: {byte_val:3d} = 0b{binary} = {dna_seq}")
    print()
    
    # Disassemble
    print("Disassembly:")
    print(dna.disassemble(bytecode))
    print()
    
    # Save and load binary file
    dna.save_binary(bytecode, "program.dna")
    loaded_bytecode = dna.load_binary("program.dna")
    
    print("File Compatibility Test:")
    print(f"Original:  {bytecode.hex()}")
    print(f"Loaded:    {loaded_bytecode.hex()}")
    print(f"Match:     {bytecode == loaded_bytecode}")
    print()
    
    # Decompile back to DNA
    restored_dna = dna.decompile_bytecode_to_dna(bytecode)
    print("Decompiled DNA:")
    print(restored_dna)
    print()
    
    # Execute the program
    print("Execution:")
    dna.execute_bytecode(bytecode)
    
    # Demonstrate ANY file type storage
    print("\nUniversal File Storage Demo:")
    test_data = b"Hello, World!"
    print(f"Original data: {test_data}")
    
    # Convert any binary data to DNA
    dna_representation = ""
    for byte_val in test_data:
        dna_representation += dna.byte_to_dna(byte_val)
    
    print(f"As DNA: {dna_representation}")
    
    # Convert back to original data
    restored_data = bytes([dna.dna_to_byte(dna_representation[i:i+4]) for i in range(0, len(dna_representation), 4)])
    print(f"Restored: {restored_data}")
    print(f"Perfect match: {test_data == restored_data}")

if __name__ == "__main__":
    main()
