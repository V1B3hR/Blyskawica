#!/usr/bin/env python3
"""
DNA Compiler
Advanced compiler with optimization for DNA programming language
"""

from typing import List, Dict, Optional, Tuple
import re
from ..core.encoding import DNAEncoder
from ..vm.instruction_set import DNAInstructionSet

class DNACompiler:
    """
    Advanced DNA compiler with optimization capabilities
    """
    
    def __init__(self, encoder: DNAEncoder, instruction_set: DNAInstructionSet):
        """Initialize compiler with encoder and instruction set"""
        self.encoder = encoder
        self.instruction_set = instruction_set
        
        # Compilation statistics
        self.stats = {
            'programs_compiled': 0,
            'optimizations_applied': 0,
            'instructions_optimized': 0
        }
    
    def compile(self, dna_source: str, optimize: bool = True) -> bytes:
        """
        Compile DNA source code to bytecode
        
        Args:
            dna_source: DNA source code
            optimize: Enable optimizations
            
        Returns:
            Compiled bytecode
        """
        try:
            # Preprocessing
            cleaned_source = self._preprocess(dna_source)
            
            # Validate syntax
            self._validate_syntax(cleaned_source)
            
            # Parse instructions
            instructions = self._parse_instructions(cleaned_source)
            
            # Apply optimizations if enabled
            if optimize:
                instructions = self._optimize(instructions)
            
            # Generate bytecode
            bytecode = self._generate_bytecode(instructions)
            
            # Update statistics
            self.stats['programs_compiled'] += 1
            
            return bytecode
            
        except Exception as e:
            raise RuntimeError(f"Compilation error: {e}")
    
    def _preprocess(self, source: str) -> str:
        """Preprocess source code (remove comments, normalize whitespace)"""
        # Remove comments (# to end of line)
        source = re.sub(r'#.*$', '', source, flags=re.MULTILINE)
        
        # Normalize whitespace
        source = ' '.join(source.split())
        
        # Remove empty lines and extra spaces
        source = re.sub(r'\s+', ' ', source).strip()
        
        return source
    
    def _validate_syntax(self, source: str):
        """Validate DNA source syntax"""
        if not source:
            raise ValueError("Empty program")
        
        # Check for valid DNA characters only
        valid_chars = set('AUCG aucg')
        invalid_chars = set(source) - valid_chars
        if invalid_chars:
            raise ValueError(f"Invalid characters in source: {invalid_chars}")
        
        # Validate instruction format
        is_valid, errors = self.instruction_set.validate_program(source)
        if not is_valid:
            raise ValueError(f"Invalid instruction sequence: {errors}")
    
    def _parse_instructions(self, source: str) -> List[Dict]:
        """Parse source into instruction objects"""
        sequences = source.replace(' ', '')
        instructions = []
        
        i = 0
        while i < len(sequences):
            # Get 4-nucleotide sequence
            if i + 4 <= len(sequences):
                dna_seq = sequences[i:i+4].upper()
                
                # Check if it's a valid instruction
                instruction_info = self.instruction_set.get_instruction_by_dna(dna_seq)
                
                if instruction_info:
                    # Parse operands if needed
                    operands = []
                    operand_count = instruction_info.operand_count
                    
                    for j in range(operand_count):
                        if i + 4 + (j + 1) * 4 <= len(sequences):
                            operand_seq = sequences[i + 4 + j * 4:i + 4 + (j + 1) * 4]
                            try:
                                operand_value = self.encoder.dna_to_byte(operand_seq)
                                operands.append(operand_value)
                            except:
                                # Invalid operand
                                raise ValueError(f"Invalid operand sequence: {operand_seq}")
                    
                    instructions.append({
                        'position': i // 4,
                        'dna_sequence': dna_seq,
                        'instruction': instruction_info,
                        'operands': operands,
                        'size': 1 + operand_count  # instruction + operands
                    })
                    
                    i += 4 * (1 + operand_count)
                else:
                    # Treat as data
                    try:
                        byte_value = self.encoder.dna_to_byte(dna_seq)
                        instructions.append({
                            'position': i // 4,
                            'dna_sequence': dna_seq,
                            'instruction': None,
                            'data_value': byte_value,
                            'size': 1
                        })
                        i += 4
                    except:
                        raise ValueError(f"Invalid DNA sequence: {dna_seq}")
            else:
                break
        
        return instructions
    
    def _optimize(self, instructions: List[Dict]) -> List[Dict]:
        """Apply optimization passes"""
        optimized = instructions.copy()
        initial_count = len(optimized)
        
        # Optimization pass 1: Remove redundant NOPs
        optimized = self._remove_redundant_nops(optimized)
        
        # Optimization pass 2: Combine sequential operations
        optimized = self._combine_sequential_operations(optimized)
        
        # Optimization pass 3: Optimize memory access patterns
        optimized = self._optimize_memory_access(optimized)
        
        # Update statistics
        optimizations = initial_count - len(optimized)
        self.stats['optimizations_applied'] += 1 if optimizations > 0 else 0
        self.stats['instructions_optimized'] += optimizations
        
        return optimized
    
    def _remove_redundant_nops(self, instructions: List[Dict]) -> List[Dict]:
        """Remove unnecessary NOP instructions"""
        optimized = []
        
        for i, instr in enumerate(instructions):
            # Skip NOPs that are not necessary
            if (instr.get('instruction') and 
                instr['instruction'].name == 'NOP'):
                
                # Keep NOPs that are jump targets or at critical positions
                is_jump_target = self._is_jump_target(i, instructions)
                if not is_jump_target:
                    continue  # Skip this NOP
            
            optimized.append(instr)
        
        return optimized
    
    def _combine_sequential_operations(self, instructions: List[Dict]) -> List[Dict]:
        """Combine sequential operations where possible"""
        optimized = []
        i = 0
        
        while i < len(instructions):
            current = instructions[i]
            
            # Look for patterns to optimize
            if i + 1 < len(instructions):
                next_instr = instructions[i + 1]
                
                # Pattern: LOAD followed by ADD -> could be optimized
                # For now, just pass through (more complex optimizations could be added)
                pass
            
            optimized.append(current)
            i += 1
        
        return optimized
    
    def _optimize_memory_access(self, instructions: List[Dict]) -> List[Dict]:
        """Optimize memory access patterns"""
        # For now, return as-is (future optimization opportunity)
        return instructions
    
    def _is_jump_target(self, position: int, instructions: List[Dict]) -> bool:
        """Check if position is a target of any jump instruction"""
        for instr in instructions:
            if (instr.get('instruction') and 
                instr['instruction'].name in ['JMP', 'JEQ', 'JNE'] and
                instr.get('operands')):
                target = instr['operands'][0] if instr['operands'] else None
                if target == position:
                    return True
        return False
    
    def _generate_bytecode(self, instructions: List[Dict]) -> bytes:
        """Generate final bytecode from instruction list"""
        bytecode = []
        
        for instr in instructions:
            if instr.get('instruction'):
                # Regular instruction
                bytecode.append(instr['instruction'].opcode)
                
                # Add operands
                for operand in instr.get('operands', []):
                    bytecode.append(operand)
            else:
                # Data value
                bytecode.append(instr.get('data_value', 0))
        
        return bytes(bytecode)
    
    def get_compilation_stats(self) -> Dict:
        """Get compiler statistics"""
        return self.stats.copy()
    
    def disassemble(self, bytecode: bytes) -> List[str]:
        """Disassemble bytecode back to DNA assembly"""
        disassembly = []
        offset = 0
        
        while offset < len(bytecode):
            opcode = bytecode[offset]
            instruction = self.instruction_set.get_instruction_by_opcode(opcode)
            
            if instruction:
                line = f"{offset:04X}: {instruction.dna_sequence} {instruction.name}"
                
                # Add operands
                operands = []
                for i in range(instruction.operand_count):
                    if offset + 1 + i < len(bytecode):
                        operand_val = bytecode[offset + 1 + i]
                        operand_dna = self.encoder.byte_to_dna(operand_val)
                        operands.append(f"{operand_dna}({operand_val})")
                
                if operands:
                    line += " " + " ".join(operands)
                
                disassembly.append(line)
                offset += 1 + instruction.operand_count
            else:
                # Unknown opcode - treat as data
                dna_seq = self.encoder.byte_to_dna(opcode)
                disassembly.append(f"{offset:04X}: {dna_seq} DATA({opcode})")
                offset += 1
        
        return disassembly
    
    def analyze_program(self, bytecode: bytes) -> Dict:
        """Analyze compiled program characteristics"""
        instruction_count = 0
        data_count = 0
        instruction_types = {}
        
        offset = 0
        while offset < len(bytecode):
            opcode = bytecode[offset]
            instruction = self.instruction_set.get_instruction_by_opcode(opcode)
            
            if instruction:
                instruction_count += 1
                inst_type = instruction.instruction_type.name
                instruction_types[inst_type] = instruction_types.get(inst_type, 0) + 1
                offset += 1 + instruction.operand_count
            else:
                data_count += 1
                offset += 1
        
        return {
            'total_bytes': len(bytecode),
            'instruction_count': instruction_count,
            'data_count': data_count,
            'instruction_types': instruction_types,
            'code_density': instruction_count / len(bytecode) if len(bytecode) > 0 else 0
        } 