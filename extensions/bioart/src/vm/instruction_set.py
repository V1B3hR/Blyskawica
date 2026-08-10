#!/usr/bin/env python3
"""
DNA Virtual Machine Instruction Set
Refactored instruction architecture with extensibility and performance
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


class InstructionType(Enum):
    """Instruction type enumeration"""
    CONTROL = auto()
    ARITHMETIC = auto()
    MEMORY = auto()
    IO = auto()
    LOGIC = auto()
    # New instruction types for complex operations
    BIOLOGICAL = auto()
    CRYPTOGRAPHIC = auto()
    MATRIX = auto()
    THREADING = auto()
    ERROR_CORRECTION = auto()
    # Extended complex algorithmic operations
    FLOATING_POINT = auto()
    STRING_MANIPULATION = auto()
    STATISTICAL = auto()
    MACHINE_LEARNING = auto()
    GRAPH_ALGORITHMS = auto()
    SIGNAL_PROCESSING = auto()

@dataclass(frozen=True)
class Instruction:
    """Immutable instruction definition"""
    opcode: int
    name: str
    dna_sequence: str
    instruction_type: InstructionType
    description: str
    operand_count: int = 0
    cycles: int = 1

class DNAInstructionSet:
    """
    Refactored DNA instruction set with improved architecture
    """

    # Core instruction definitions
    INSTRUCTIONS = {
        # Control Instructions
        0x00: Instruction(0x00, "NOP", "AAAA", InstructionType.CONTROL, "No Operation", 0, 1),
        0x09: Instruction(0x09, "JMP", "AACU", InstructionType.CONTROL, "Jump", 1, 2),
        0x0A: Instruction(0x0A, "JEQ", "AACC", InstructionType.CONTROL, "Jump if Equal", 2, 2),
        0x0B: Instruction(0x0B, "JNE", "AACG", InstructionType.CONTROL, "Jump if Not Equal", 2, 2),
        0x0C: Instruction(0x0C, "HALT", "AAGA", InstructionType.CONTROL, "Halt Program", 0, 1),

        # Memory Instructions
        0x01: Instruction(0x01, "LOAD", "AAAU", InstructionType.MEMORY, "Load Value", 1, 2),
        0x02: Instruction(0x02, "STORE", "AAAC", InstructionType.MEMORY, "Store Value", 1, 2),
        0x0D: Instruction(0x0D, "LOADR", "AAGU", InstructionType.MEMORY, "Load from Register", 1, 1),
        0x0E: Instruction(0x0E, "STORER", "AAGC", InstructionType.MEMORY, "Store to Register", 1, 1),

        # Arithmetic Instructions
        0x03: Instruction(0x03, "ADD", "AAAG", InstructionType.ARITHMETIC, "Add", 1, 1),
        0x04: Instruction(0x04, "SUB", "AAUA", InstructionType.ARITHMETIC, "Subtract", 1, 1),
        0x05: Instruction(0x05, "MUL", "AAUU", InstructionType.ARITHMETIC, "Multiply", 1, 3),
        0x06: Instruction(0x06, "DIV", "AAUC", InstructionType.ARITHMETIC, "Divide", 1, 4),
        0x0F: Instruction(0x0F, "MOD", "AAGG", InstructionType.ARITHMETIC, "Modulo", 1, 4),
        0x10: Instruction(0x10, "INC", "AUCA", InstructionType.ARITHMETIC, "Increment", 0, 1),
        0x11: Instruction(0x11, "DEC", "AUCU", InstructionType.ARITHMETIC, "Decrement", 0, 1),

        # Logic Instructions
        0x12: Instruction(0x12, "AND", "AUCG", InstructionType.LOGIC, "Bitwise AND", 1, 1),
        0x13: Instruction(0x13, "OR", "AUGG", InstructionType.LOGIC, "Bitwise OR", 1, 1),
        0x14: Instruction(0x14, "XOR", "ACAA", InstructionType.LOGIC, "Bitwise XOR", 1, 1),
        0x15: Instruction(0x15, "NOT", "ACAU", InstructionType.LOGIC, "Bitwise NOT", 0, 1),

        # I/O Instructions
        0x07: Instruction(0x07, "PRINT", "AAUG", InstructionType.IO, "Print Output", 0, 5),
        0x08: Instruction(0x08, "INPUT", "AACA", InstructionType.IO, "Input", 0, 10),
        0x16: Instruction(0x16, "PRINTC", "ACAC", InstructionType.IO, "Print Character", 0, 5),
        0x17: Instruction(0x17, "PRINTS", "ACAG", InstructionType.IO, "Print String", 1, 10),

        # Extended Complex Operations (NEW)
        # Mathematical/Scientific Operations
        0x18: Instruction(0x18, "POW", "ACUA", InstructionType.ARITHMETIC, "Power (A^B)", 2, 8),
        0x19: Instruction(0x19, "SQRT", "ACUU", InstructionType.ARITHMETIC, "Square Root", 1, 6),
        0x1A: Instruction(0x1A, "LOG", "ACUC", InstructionType.ARITHMETIC, "Logarithm", 1, 8),
        0x1B: Instruction(0x1B, "SIN", "ACUG", InstructionType.ARITHMETIC, "Sine", 1, 10),
        0x1C: Instruction(0x1C, "COS", "ACGA", InstructionType.ARITHMETIC, "Cosine", 1, 10),
        0x1D: Instruction(0x1D, "RAND", "ACGU", InstructionType.ARITHMETIC, "Random Number", 0, 5),

        # Matrix Operations
        0x1E: Instruction(0x1E, "MATMUL", "ACGC", InstructionType.MATRIX, "Matrix Multiply", 3, 20),
        0x1F: Instruction(0x1F, "MATINV", "ACGG", InstructionType.MATRIX, "Matrix Inverse", 2, 25),
        0x20: Instruction(0x20, "MATTRANS", "AGAA", InstructionType.MATRIX, "Matrix Transpose", 2, 10),

        # Biological Operations (NEW)
        0x21: Instruction(0x21, "DNACMP", "AGAU", InstructionType.BIOLOGICAL, "DNA Complement", 2, 8),
        0x22: Instruction(0x22, "DNAREV", "AGAC", InstructionType.BIOLOGICAL, "DNA Reverse", 2, 6),
        0x23: Instruction(0x23, "TRANSCRIBE", "AGAG", InstructionType.BIOLOGICAL, "DNA->RNA Transcription", 2, 12),
        0x24: Instruction(0x24, "TRANSLATE", "AGUA", InstructionType.BIOLOGICAL, "RNA->Protein Translation", 2, 15),
        0x25: Instruction(0x25, "MUTATE", "AGUU", InstructionType.BIOLOGICAL, "Simulate DNA Mutation", 3, 10),
        0x26: Instruction(0x26, "SYNTHESIZE", "AGUC", InstructionType.BIOLOGICAL, "DNA Synthesis Simulation", 2, 20),

        # Cryptographic Operations
        0x27: Instruction(0x27, "HASH", "AGUG", InstructionType.CRYPTOGRAPHIC, "Hash Function", 2, 15),
        0x28: Instruction(0x28, "ENCRYPT", "AGGA", InstructionType.CRYPTOGRAPHIC, "Encrypt Data", 3, 20),
        0x29: Instruction(0x29, "DECRYPT", "AGGU", InstructionType.CRYPTOGRAPHIC, "Decrypt Data", 3, 20),
        0x2A: Instruction(0x2A, "CHECKSUM", "AGGC", InstructionType.CRYPTOGRAPHIC, "Calculate Checksum", 2, 8),

        # Error Correction Operations
        0x2B: Instruction(0x2B, "ENCODE_RS", "AGGG", InstructionType.ERROR_CORRECTION, "Reed-Solomon Encode", 3, 25),
        0x2C: Instruction(0x2C, "DECODE_RS", "UCAA", InstructionType.ERROR_CORRECTION, "Reed-Solomon Decode", 3, 30),
        0x2D: Instruction(0x2D, "CORRECT", "UCAU", InstructionType.ERROR_CORRECTION, "Error Correction", 2, 15),
        0x2E: Instruction(0x2E, "DETECT", "UCAC", InstructionType.ERROR_CORRECTION, "Error Detection", 2, 10),

        # Threading Operations
        0x2F: Instruction(0x2F, "SPAWN", "UCAG", InstructionType.THREADING, "Spawn Thread", 1, 20),
        0x30: Instruction(0x30, "JOIN", "UCUA", InstructionType.THREADING, "Join Thread", 1, 15),
        0x31: Instruction(0x31, "LOCK", "UCUU", InstructionType.THREADING, "Acquire Lock", 1, 10),
        0x32: Instruction(0x32, "UNLOCK", "UCUC", InstructionType.THREADING, "Release Lock", 1, 5),
        0x33: Instruction(0x33, "SYNC", "UCUG", InstructionType.THREADING, "Synchronize Threads", 0, 12),

        # Extended Complex Algorithmic Operations (NEW)
        # Floating Point Operations (IEEE 754 support)
        0x34: Instruction(0x34, "FADD", "UCGA", InstructionType.FLOATING_POINT, "Floating Point Add", 2, 3),
        0x35: Instruction(0x35, "FSUB", "UCGU", InstructionType.FLOATING_POINT, "Floating Point Subtract", 2, 3),
        0x36: Instruction(0x36, "FMUL", "UCGC", InstructionType.FLOATING_POINT, "Floating Point Multiply", 2, 5),
        0x37: Instruction(0x37, "FDIV", "UCGG", InstructionType.FLOATING_POINT, "Floating Point Divide", 2, 8),
        0x38: Instruction(0x38, "FSQRT", "UGAA", InstructionType.FLOATING_POINT, "Floating Point Square Root", 1, 10),
        0x39: Instruction(0x39, "FABS", "UGAU", InstructionType.FLOATING_POINT, "Floating Point Absolute", 1, 2),
        0x3A: Instruction(0x3A, "FTOI", "UGAC", InstructionType.FLOATING_POINT, "Float to Integer", 1, 3),
        0x3B: Instruction(0x3B, "ITOF", "UGAG", InstructionType.FLOATING_POINT, "Integer to Float", 1, 3),

        # Advanced Control Flow
        0x3C: Instruction(0x3C, "CALL", "UGUA", InstructionType.CONTROL, "Function Call", 1, 5),
        0x3D: Instruction(0x3D, "RET", "UGUU", InstructionType.CONTROL, "Function Return", 0, 3),
        0x3E: Instruction(0x3E, "PUSH", "UGUC", InstructionType.CONTROL, "Push to Stack", 1, 2),
        0x3F: Instruction(0x3F, "POP", "UGUG", InstructionType.CONTROL, "Pop from Stack", 0, 2),
        0x40: Instruction(0x40, "LOOP", "UGGA", InstructionType.CONTROL, "Loop Control", 2, 3),
        0x41: Instruction(0x41, "BREAK", "UGGU", InstructionType.CONTROL, "Break Loop", 0, 2),
        0x42: Instruction(0x42, "CONTINUE", "UGGC", InstructionType.CONTROL, "Continue Loop", 0, 2),

        # String Manipulation Operations
        0x43: Instruction(0x43, "STRLEN", "UGGG", InstructionType.STRING_MANIPULATION, "String Length", 1, 3),
        0x44: Instruction(0x44, "STRCMP", "CAAA", InstructionType.STRING_MANIPULATION, "String Compare", 2, 5),
        0x45: Instruction(0x45, "STRCPY", "CAAU", InstructionType.STRING_MANIPULATION, "String Copy", 2, 4),
        0x46: Instruction(0x46, "STRCAT", "CAAC", InstructionType.STRING_MANIPULATION, "String Concatenate", 2, 6),
        0x47: Instruction(0x47, "SUBSTR", "CAAG", InstructionType.STRING_MANIPULATION, "Substring", 3, 5),
        0x48: Instruction(0x48, "STRFIND", "CAUA", InstructionType.STRING_MANIPULATION, "String Find", 2, 8),
        0x49: Instruction(0x49, "REPLACE", "CAUU", InstructionType.STRING_MANIPULATION, "String Replace", 3, 10),

        # Statistical Operations
        0x4A: Instruction(0x4A, "MEAN", "CAUC", InstructionType.STATISTICAL, "Calculate Mean", 2, 8),
        0x4B: Instruction(0x4B, "MEDIAN", "CAUG", InstructionType.STATISTICAL, "Calculate Median", 2, 12),
        0x4C: Instruction(0x4C, "STDDEV", "CACA", InstructionType.STATISTICAL, "Standard Deviation", 2, 15),
        0x4D: Instruction(0x4D, "VARIANCE", "CACU", InstructionType.STATISTICAL, "Calculate Variance", 2, 12),
        0x4E: Instruction(0x4E, "CORREL", "CACC", InstructionType.STATISTICAL, "Correlation", 3, 20),
        0x4F: Instruction(0x4F, "REGRESS", "CACG", InstructionType.STATISTICAL, "Linear Regression", 3, 25),

        # Machine Learning Operations
        0x50: Instruction(0x50, "NEURON", "CAGA", InstructionType.MACHINE_LEARNING, "Neural Network Node", 3, 15),
        0x51: Instruction(0x51, "ACTIVATE", "CAGU", InstructionType.MACHINE_LEARNING, "Activation Function", 2, 8),
        0x52: Instruction(0x52, "BACKPROP", "CAGC", InstructionType.MACHINE_LEARNING, "Backpropagation", 3, 20),
        0x53: Instruction(0x53, "CLASSIFY", "CAGG", InstructionType.MACHINE_LEARNING, "Classification", 2, 12),
        0x54: Instruction(0x54, "CLUSTER", "CGAA", InstructionType.MACHINE_LEARNING, "K-Means Clustering", 3, 30),
        0x55: Instruction(0x55, "SVM", "CGAU", InstructionType.MACHINE_LEARNING, "Support Vector Machine", 3, 25),

        # Graph Algorithm Operations
        0x56: Instruction(0x56, "DIJKSTRA", "CGAC", InstructionType.GRAPH_ALGORITHMS, "Shortest Path", 3, 40),
        0x57: Instruction(0x57, "BFS", "CGAG", InstructionType.GRAPH_ALGORITHMS, "Breadth-First Search", 2, 20),
        0x58: Instruction(0x58, "DFS", "CGUA", InstructionType.GRAPH_ALGORITHMS, "Depth-First Search", 2, 18),
        0x59: Instruction(0x59, "MST", "CGUU", InstructionType.GRAPH_ALGORITHMS, "Minimum Spanning Tree", 2, 35),
        0x5A: Instruction(0x5A, "TOPSORT", "CGUC", InstructionType.GRAPH_ALGORITHMS, "Topological Sort", 2, 25),

        # Signal Processing Operations
        0x5B: Instruction(0x5B, "FFT", "CGUG", InstructionType.SIGNAL_PROCESSING, "Fast Fourier Transform", 2, 50),
        0x5C: Instruction(0x5C, "IFFT", "CGGA", InstructionType.SIGNAL_PROCESSING, "Inverse FFT", 2, 50),
        0x5D: Instruction(0x5D, "FILTER", "CGGU", InstructionType.SIGNAL_PROCESSING, "Digital Filter", 3, 20),
        0x5E: Instruction(0x5E, "CONVOLVE", "CGGC", InstructionType.SIGNAL_PROCESSING, "Convolution", 3, 30),
        0x5F: Instruction(0x5F, "SAMPLE", "CGGG", InstructionType.SIGNAL_PROCESSING, "Signal Sampling", 2, 8),

        # Advanced Memory Operations
        0x60: Instruction(0x60, "MEMCPY", "GAAA", InstructionType.MEMORY, "Memory Copy", 3, 5),
        0x61: Instruction(0x61, "MEMSET", "GAAU", InstructionType.MEMORY, "Memory Set", 3, 4),
        0x62: Instruction(0x62, "MALLOC", "GAAC", InstructionType.MEMORY, "Dynamic Allocation", 1, 10),
        0x63: Instruction(0x63, "FREE", "GAAG", InstructionType.MEMORY, "Free Memory", 1, 8),
        0x64: Instruction(0x64, "REALLOC", "GAUA", InstructionType.MEMORY, "Reallocate Memory", 2, 12),

        # Advanced I/O Operations
        0x65: Instruction(0x65, "FOPEN", "GAUU", InstructionType.IO, "File Open", 2, 15),
        0x66: Instruction(0x66, "FCLOSE", "GAUC", InstructionType.IO, "File Close", 1, 10),
        0x67: Instruction(0x67, "FREAD", "GAUG", InstructionType.IO, "File Read", 3, 20),
        0x68: Instruction(0x68, "FWRITE", "GACA", InstructionType.IO, "File Write", 3, 18),
        0x69: Instruction(0x69, "FPRINTF", "GACU", InstructionType.IO, "Formatted File Print", 2, 12),
    }

    def __init__(self):
        """Initialize instruction set with optimized lookup tables"""
        self._opcode_to_instruction = self.INSTRUCTIONS.copy()
        self._dna_to_instruction = {instr.dna_sequence: instr for instr in self.INSTRUCTIONS.values()}
        self._name_to_instruction = {instr.name: instr for instr in self.INSTRUCTIONS.values()}

        # Performance optimization: cache frequently used lookups
        self._dna_to_opcode_cache = {instr.dna_sequence: instr.opcode for instr in self.INSTRUCTIONS.values()}
        self._opcode_to_dna_cache = {instr.opcode: instr.dna_sequence for instr in self.INSTRUCTIONS.values()}

    def get_instruction_by_opcode(self, opcode: int) -> Optional[Instruction]:
        """Get instruction by opcode"""
        return self._opcode_to_instruction.get(opcode)

    def get_instruction_by_dna(self, dna_sequence: str) -> Optional[Instruction]:
        """Get instruction by DNA sequence"""
        return self._dna_to_instruction.get(dna_sequence.upper())

    def get_instruction_by_name(self, name: str) -> Optional[Instruction]:
        """Get instruction by name"""
        return self._name_to_instruction.get(name.upper())

    def dna_to_opcode(self, dna_sequence: str) -> Optional[int]:
        """Convert DNA sequence to opcode (optimized)"""
        return self._dna_to_opcode_cache.get(dna_sequence.upper())

    def opcode_to_dna(self, opcode: int) -> Optional[str]:
        """Convert opcode to DNA sequence (optimized)"""
        return self._opcode_to_dna_cache.get(opcode)

    def is_valid_instruction(self, dna_sequence: str) -> bool:
        """Check if DNA sequence is a valid instruction"""
        return dna_sequence.upper() in self._dna_to_instruction

    def get_instructions_by_type(self, instruction_type: InstructionType) -> Dict[int, Instruction]:
        """Get all instructions of a specific type"""
        return {opcode: instr for opcode, instr in self.INSTRUCTIONS.items()
                if instr.instruction_type == instruction_type}

    def get_instruction_info(self, identifier: Any) -> Optional[dict]:
        """Get comprehensive instruction information"""
        instruction = None

        if isinstance(identifier, int):
            instruction = self.get_instruction_by_opcode(identifier)
        elif isinstance(identifier, str):
            if len(identifier) == 4 and identifier.upper() in self._dna_to_instruction:
                instruction = self.get_instruction_by_dna(identifier)
            else:
                instruction = self.get_instruction_by_name(identifier)

        if instruction:
            return {
                'opcode': instruction.opcode,
                'name': instruction.name,
                'dna_sequence': instruction.dna_sequence,
                'type': instruction.instruction_type.name,
                'description': instruction.description,
                'operand_count': instruction.operand_count,
                'cycles': instruction.cycles,
                'binary': f'0x{instruction.opcode:02X}',
                'binary_bits': f'{instruction.opcode:08b}'
            }
        return None

    def list_all_instructions(self) -> list:
        """Get list of all instructions with details"""
        return [self.get_instruction_info(opcode) for opcode in sorted(self.INSTRUCTIONS.keys())]

    def get_instruction_statistics(self) -> dict:
        """Get instruction set statistics"""
        type_counts = {}
        total_cycles = 0

        for instruction in self.INSTRUCTIONS.values():
            type_name = instruction.instruction_type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            total_cycles += instruction.cycles

        return {
            'total_instructions': len(self.INSTRUCTIONS),
            'instruction_type_counts': type_counts,
            'average_cycles': total_cycles / len(self.INSTRUCTIONS),
            'opcode_range': f'0x{min(self.INSTRUCTIONS.keys()):02X} - 0x{max(self.INSTRUCTIONS.keys()):02X}',
            'coverage': f'{len(self.INSTRUCTIONS)}/256 ({len(self.INSTRUCTIONS)/256*100:.1f}%)',
            'instruction_types': list(type_counts.keys())
        }

    def validate_program(self, dna_program: str) -> Tuple[bool, list]:
        """Validate a DNA program against the instruction set"""
        errors = []
        sequences = dna_program.replace(' ', '').replace('\n', '')

        if len(sequences) % 4 != 0:
            return False, [f"Program length {len(sequences)} is not multiple of 4"]

        for i in range(0, len(sequences), 4):
            dna_seq = sequences[i:i+4]
            if not self.is_valid_instruction(dna_seq):
                errors.append(f"Invalid instruction at position {i//4}: {dna_seq}")

        return len(errors) == 0, errors

    def encode_instruction(self, name: str, *operands) -> bytes:
        """Encode instruction with operands to bytecode"""
        instruction = self.get_instruction_by_name(name)
        if not instruction:
            raise ValueError(f"Unknown instruction: {name}")

        if len(operands) != instruction.operand_count:
            raise ValueError(f"Instruction {name} expects {instruction.operand_count} operands, got {len(operands)}")

        # Pack instruction and operands
        bytecode = [instruction.opcode]
        for operand in operands:
            if isinstance(operand, int) and 0 <= operand <= 255:
                bytecode.append(operand)
            else:
                raise ValueError(f"Invalid operand: {operand}")

        return bytes(bytecode)

    def disassemble_instruction(self, bytecode: bytes, offset: int = 0) -> Tuple[Optional[str], int]:
        """Disassemble single instruction from bytecode"""
        if offset >= len(bytecode):
            return None, offset

        opcode = bytecode[offset]
        instruction = self.get_instruction_by_opcode(opcode)

        if not instruction:
            return f"UNKNOWN 0x{opcode:02X}", offset + 1

        operands = []
        next_offset = offset + 1

        for _ in range(instruction.operand_count):
            if next_offset < len(bytecode):
                operands.append(bytecode[next_offset])
                next_offset += 1
            else:
                operands.append('??')

        if operands:
            operand_str = ' ' + ' '.join(str(op) for op in operands)
        else:
            operand_str = ''

        return f"{instruction.name}{operand_str}", next_offset


# Singleton instance for global use
instruction_set = DNAInstructionSet()

# Convenience functions
def get_instruction(identifier: Any) -> Optional[Instruction]:
    """Get instruction by opcode, DNA sequence, or name"""
    if isinstance(identifier, int):
        return instruction_set.get_instruction_by_opcode(identifier)
    elif isinstance(identifier, str):
        if len(identifier) == 4:
            return instruction_set.get_instruction_by_dna(identifier)
        else:
            return instruction_set.get_instruction_by_name(identifier)
    return None

def is_valid_instruction(dna_sequence: str) -> bool:
    """Check if DNA sequence is valid instruction"""
    return instruction_set.is_valid_instruction(dna_sequence)
