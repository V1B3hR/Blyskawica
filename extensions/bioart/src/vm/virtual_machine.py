#!/usr/bin/env python3
"""
DNA Virtual Machine
High-performance virtual machine with improved architecture and debugging
"""

from typing import List, Dict, Optional, Callable, Any
import time
import math
import random
import hashlib
import threading
from enum import Enum
from dataclasses import dataclass

from ..core.encoding import DNAEncoder
from .instruction_set import DNAInstructionSet, InstructionType

class VMState(Enum):
    """Virtual machine execution states"""
    STOPPED = "stopped"
    RUNNING = "running" 
    PAUSED = "paused"
    HALTED = "halted"
    ERROR = "error"

@dataclass
class ExecutionStats:
    """Execution statistics tracking"""
    instructions_executed: int = 0
    cycles_elapsed: int = 0
    execution_time: float = 0.0
    memory_accesses: int = 0
    io_operations: int = 0

class DNAVirtualMachine:
    """
    High-performance DNA Virtual Machine with advanced features
    """
    
    def __init__(self, memory_size: int = 256, register_count: int = 4):
        """Initialize virtual machine with configurable architecture"""
        
        # Core components
        self.encoder = DNAEncoder()
        self.instruction_set = DNAInstructionSet()
        
        # Architecture configuration
        self.memory_size = memory_size
        self.register_count = register_count
        
        # VM State
        self.state = VMState.STOPPED
        
        # Performance tracking
        self.stats = ExecutionStats()
        
        # Debugging support
        self.debug_mode = False
        self.breakpoints = set()
        self.instruction_trace = []
        
        # I/O handlers
        self.input_handler = input
        self.output_handler = print
        
        # Extended functionality support
        self.thread_pool = []
        self.locks = {}
        self.biological_storage = {}  # Simulated biological storage
        self.synthesis_queue = []     # DNA synthesis queue
        self.error_correction_enabled = True
        
        # Instruction execution mapping
        self._setup_instruction_handlers()
        
        # Initialize after all attributes are set
        self.reset()
    
    def reset(self):
        """Reset virtual machine to initial state"""
        # Memory initialization
        self.memory = bytearray(self.memory_size)
        
        # Register initialization (A, B, C, D by default)
        self.registers = [0] * self.register_count
        
        # Control registers
        self.pc = 0  # Program counter
        self.sp = self.memory_size - 1  # Stack pointer
        self.flags = {
            'zero': False,
            'carry': False,
            'overflow': False,
            'negative': False
        }
        
        # Execution state
        self.state = VMState.STOPPED
        self.program = bytearray()
        self.program_size = 0
        
        # Reset statistics
        self.stats = ExecutionStats()
        self.instruction_trace.clear()
    
    def _setup_instruction_handlers(self):
        """Setup instruction execution handlers"""
        self.instruction_handlers = {
            0x00: self._execute_nop,
            0x01: self._execute_load,
            0x02: self._execute_store,
            0x03: self._execute_add,
            0x04: self._execute_sub,
            0x05: self._execute_mul,
            0x06: self._execute_div,
            0x07: self._execute_print,
            0x08: self._execute_input,
            0x09: self._execute_jmp,
            0x0A: self._execute_jeq,
            0x0B: self._execute_jne,
            0x0C: self._execute_halt,
            0x0D: self._execute_loadr,
            0x0E: self._execute_storer,
            0x0F: self._execute_mod,
            0x10: self._execute_inc,
            0x11: self._execute_dec,
            0x12: self._execute_and,
            0x13: self._execute_or,
            0x14: self._execute_xor,
            0x15: self._execute_not,
            0x16: self._execute_printc,
            0x17: self._execute_prints,
        }
        
        # Add extended instruction handlers
        extended_handlers = {
            # Mathematical/Scientific Operations
            0x18: self._execute_pow,
            0x19: self._execute_sqrt,
            0x1A: self._execute_log,
            0x1B: self._execute_sin,
            0x1C: self._execute_cos,
            0x1D: self._execute_rand,
            
            # Matrix Operations
            0x1E: self._execute_matmul,
            0x1F: self._execute_matinv,
            0x20: self._execute_mattrans,
            
            # Biological Operations
            0x21: self._execute_dnacmp,
            0x22: self._execute_dnarev,
            0x23: self._execute_transcribe,
            0x24: self._execute_translate,
            0x25: self._execute_mutate,
            0x26: self._execute_synthesize,
            
            # Cryptographic Operations
            0x27: self._execute_hash,
            0x28: self._execute_encrypt,
            0x29: self._execute_decrypt,
            0x2A: self._execute_checksum,
            
            # Error Correction Operations
            0x2B: self._execute_encode_rs,
            0x2C: self._execute_decode_rs,
            0x2D: self._execute_correct,
            0x2E: self._execute_detect,
            
            # Threading Operations
            0x2F: self._execute_spawn,
            0x30: self._execute_join,
            0x31: self._execute_lock,
            0x32: self._execute_unlock,
            0x33: self._execute_sync,
        }
        
        self.instruction_handlers.update(extended_handlers)
    
    def load_program(self, program_data: bytes):
        """Load program into memory"""
        if len(program_data) > self.memory_size:
            raise ValueError(f"Program too large: {len(program_data)} bytes > {self.memory_size}")
        
        self.program = bytearray(program_data)
        self.program_size = len(program_data)
        
        # Load program into memory starting at address 0
        self.memory[:len(program_data)] = program_data
        
        self.pc = 0
        self.state = VMState.STOPPED
    
    def load_dna_program(self, dna_program: str):
        """Load DNA program by compiling to bytecode"""
        # Validate program
        is_valid, errors = self.instruction_set.validate_program(dna_program)
        if not is_valid:
            raise ValueError(f"Invalid DNA program: {errors}")
        
        # Compile DNA to bytecode
        bytecode = self._compile_dna_program(dna_program)
        self.load_program(bytecode)
    
    def _compile_dna_program(self, dna_program: str) -> bytes:
        """Compile DNA program to bytecode"""
        sequences = dna_program.replace(' ', '').replace('\n', '')
        bytecode = []
        
        for i in range(0, len(sequences), 4):
            dna_seq = sequences[i:i+4]
            opcode = self.instruction_set.dna_to_opcode(dna_seq)
            if opcode is not None:
                bytecode.append(opcode)
            else:
                # Try to interpret as data
                try:
                    byte_val = self.encoder.dna_to_byte(dna_seq)
                    bytecode.append(byte_val)
                except:
                    raise ValueError(f"Invalid DNA sequence: {dna_seq}")
        
        return bytes(bytecode)
    
    def execute(self, max_cycles: int = 1000000) -> ExecutionStats:
        """Execute loaded program with cycle limit"""
        if not self.program:
            raise RuntimeError("No program loaded")
        
        self.state = VMState.RUNNING
        start_time = time.time()
        cycles = 0
        
        try:
            while (self.state == VMState.RUNNING and 
                   cycles < max_cycles and 
                   self.pc < len(self.program)):
                
                # Check breakpoints in debug mode
                if self.debug_mode and self.pc in self.breakpoints:
                    self.state = VMState.PAUSED
                    break
                
                # Fetch instruction
                if self.pc >= len(self.program):
                    break
                
                opcode = self.program[self.pc]
                instruction = self.instruction_set.get_instruction_by_opcode(opcode)
                
                if instruction:
                    # Execute instruction
                    self._execute_instruction(instruction)
                    cycles += instruction.cycles
                    self.stats.instructions_executed += 1
                    self.stats.cycles_elapsed += instruction.cycles
                    
                    # Debug trace
                    if self.debug_mode:
                        self.instruction_trace.append({
                            'pc': self.pc,
                            'opcode': opcode,
                            'instruction': instruction.name,
                            'registers': self.registers.copy(),
                            'flags': self.flags.copy()
                        })
                else:
                    # Invalid instruction
                    self.state = VMState.ERROR
                    raise RuntimeError(f"Invalid instruction at PC {self.pc}: 0x{opcode:02X}")
        
        except Exception as e:
            self.state = VMState.ERROR
            raise RuntimeError(f"VM execution error at PC {self.pc}: {e}")
        
        finally:
            execution_time = time.time() - start_time
            self.stats.execution_time = execution_time
            
            if self.state == VMState.RUNNING:
                self.state = VMState.STOPPED
        
        return self.stats
    
    def _execute_instruction(self, instruction):
        """Execute single instruction"""
        handler = self.instruction_handlers.get(instruction.opcode)
        if handler:
            handler(instruction)
        else:
            raise RuntimeError(f"No handler for instruction: {instruction.name}")
    
    def _update_flags(self, result: int):
        """Update processor flags based on result"""
        self.flags['zero'] = (result == 0)
        self.flags['negative'] = (result < 0)
        self.flags['carry'] = (result > 255 or result < 0)
        self.flags['overflow'] = (result > 127 or result < -128)
    
    def _get_operand(self) -> int:
        """Get next operand from program"""
        self.pc += 1
        if self.pc < len(self.program):
            return self.program[self.pc]
        return 0
    
    # Instruction implementations
    def _execute_nop(self, instruction):
        """NOP - No operation"""
        self.pc += 1
    
    def _execute_load(self, instruction):
        """LOAD - Load immediate value to register A"""
        value = self._get_operand()
        self.registers[0] = value
        self._update_flags(value)
        self.pc += 1
    
    def _execute_store(self, instruction):
        """STORE - Store register A to memory address"""
        address = self._get_operand()
        if address < len(self.memory):
            self.memory[address] = self.registers[0] & 0xFF
            self.stats.memory_accesses += 1
        self.pc += 1
    
    def _execute_add(self, instruction):
        """ADD - Add immediate value to register A"""
        value = self._get_operand()
        result = self.registers[0] + value
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_sub(self, instruction):
        """SUB - Subtract immediate value from register A"""
        value = self._get_operand()
        result = self.registers[0] - value
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_mul(self, instruction):
        """MUL - Multiply register A by immediate value"""
        value = self._get_operand()
        result = self.registers[0] * value
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_div(self, instruction):
        """DIV - Divide register A by immediate value"""
        value = self._get_operand()
        if value == 0:
            raise RuntimeError("Division by zero")
        result = self.registers[0] // value
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_print(self, instruction):
        """PRINT - Print register A value"""
        self.output_handler(f"Output: {self.registers[0]}")
        self.stats.io_operations += 1
        self.pc += 1
    
    def _execute_input(self, instruction):
        """INPUT - Read input to register A"""
        try:
            value = int(self.input_handler("Input: "))
            self.registers[0] = value & 0xFF
            self.stats.io_operations += 1
        except (ValueError, EOFError):
            self.registers[0] = 0
        self.pc += 1
    
    def _execute_jmp(self, instruction):
        """JMP - Unconditional jump"""
        address = self._get_operand()
        self.pc = address
    
    def _execute_jeq(self, instruction):
        """JEQ - Jump if equal (zero flag set)"""
        address = self._get_operand()
        if self.flags['zero']:
            self.pc = address
        else:
            self.pc += 1
    
    def _execute_jne(self, instruction):
        """JNE - Jump if not equal (zero flag clear)"""
        address = self._get_operand()
        if not self.flags['zero']:
            self.pc = address
        else:
            self.pc += 1
    
    def _execute_halt(self, instruction):
        """HALT - Stop execution"""
        self.state = VMState.HALTED
        self.pc += 1
    
    def _execute_loadr(self, instruction):
        """LOADR - Load from register to register A"""
        reg_num = self._get_operand()
        if reg_num < len(self.registers):
            self.registers[0] = self.registers[reg_num]
        self.pc += 1
    
    def _execute_storer(self, instruction):
        """STORER - Store register A to another register"""
        reg_num = self._get_operand()
        if reg_num < len(self.registers):
            self.registers[reg_num] = self.registers[0]
        self.pc += 1
    
    def _execute_mod(self, instruction):
        """MOD - Modulo operation"""
        value = self._get_operand()
        if value == 0:
            raise RuntimeError("Modulo by zero")
        result = self.registers[0] % value
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_inc(self, instruction):
        """INC - Increment register A"""
        result = self.registers[0] + 1
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_dec(self, instruction):
        """DEC - Decrement register A"""
        result = self.registers[0] - 1
        self.registers[0] = result & 0xFF
        self._update_flags(result)
        self.pc += 1
    
    def _execute_and(self, instruction):
        """AND - Bitwise AND"""
        value = self._get_operand()
        result = self.registers[0] & value
        self.registers[0] = result
        self._update_flags(result)
        self.pc += 1
    
    def _execute_or(self, instruction):
        """OR - Bitwise OR"""
        value = self._get_operand()
        result = self.registers[0] | value
        self.registers[0] = result
        self._update_flags(result)
        self.pc += 1
    
    def _execute_xor(self, instruction):
        """XOR - Bitwise XOR"""
        value = self._get_operand()
        result = self.registers[0] ^ value
        self.registers[0] = result
        self._update_flags(result)
        self.pc += 1
    
    def _execute_not(self, instruction):
        """NOT - Bitwise NOT"""
        result = (~self.registers[0]) & 0xFF
        self.registers[0] = result
        self._update_flags(result)
        self.pc += 1
    
    def _execute_printc(self, instruction):
        """PRINTC - Print register A as character"""
        char = chr(self.registers[0] & 0xFF)
        self.output_handler(char, end='')
        self.stats.io_operations += 1
        self.pc += 1
    
    def _execute_prints(self, instruction):
        """PRINTS - Print string from memory"""
        address = self._get_operand()
        string_chars = []
        while address < len(self.memory) and self.memory[address] != 0:
            string_chars.append(chr(self.memory[address]))
            address += 1
        self.output_handler(''.join(string_chars))
        self.stats.io_operations += 1
        self.pc += 1
    
    # Debug and introspection methods
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode"""
        self.debug_mode = enabled
        if not enabled:
            self.instruction_trace.clear()
    
    def add_breakpoint(self, address: int):
        """Add breakpoint at address"""
        self.breakpoints.add(address)
    
    def remove_breakpoint(self, address: int):
        """Remove breakpoint at address"""
        self.breakpoints.discard(address)
    
    def get_state_info(self) -> dict:
        """Get comprehensive VM state information"""
        return {
            'state': self.state.value,
            'pc': self.pc,
            'sp': self.sp,
            'registers': self.registers.copy(),
            'flags': self.flags.copy(),
            'memory_size': self.memory_size,
            'program_size': self.program_size,
            'stats': {
                'instructions_executed': self.stats.instructions_executed,
                'cycles_elapsed': self.stats.cycles_elapsed,
                'execution_time': self.stats.execution_time,
                'memory_accesses': self.stats.memory_accesses,
                'io_operations': self.stats.io_operations
            }
        }
    
    def disassemble_program(self) -> List[str]:
        """Disassemble loaded program"""
        if not self.program:
            return []
        
        disassembly = []
        offset = 0
        
        while offset < len(self.program):
            instruction_text, next_offset = self.instruction_set.disassemble_instruction(
                self.program, offset
            )
            
            if instruction_text:
                disassembly.append(f"{offset:04X}: {instruction_text}")
            
            offset = next_offset if next_offset > offset else offset + 1
        
        return disassembly

    # ===============================
    # EXTENDED INSTRUCTION IMPLEMENTATIONS
    # ===============================
    
    # Mathematical/Scientific Operations
    def _execute_pow(self, instruction):
        """Execute power operation: A = A^B"""
        base = self.registers[0]
        exponent = self.registers[1]
        try:
            result = int(pow(base, exponent))
            self.registers[0] = result & 0xFF  # Keep in byte range
        except (OverflowError, ValueError):
            self.registers[0] = 255  # Max value on error
    
    def _execute_sqrt(self, instruction):
        """Execute square root: A = sqrt(A)"""
        value = self.registers[0]
        result = int(math.sqrt(max(0, value)))
        self.registers[0] = result & 0xFF
    
    def _execute_log(self, instruction):
        """Execute logarithm: A = log(A)"""
        value = self.registers[0]
        if value > 0:
            result = int(math.log(value))
            self.registers[0] = max(0, result) & 0xFF
        else:
            self.registers[0] = 0
    
    def _execute_sin(self, instruction):
        """Execute sine: A = sin(A) * 100 (scaled)"""
        value = self.registers[0]
        result = int(math.sin(value * math.pi / 180) * 100) + 100
        self.registers[0] = max(0, min(255, result))
    
    def _execute_cos(self, instruction):
        """Execute cosine: A = cos(A) * 100 (scaled)"""
        value = self.registers[0]
        result = int(math.cos(value * math.pi / 180) * 100) + 100
        self.registers[0] = max(0, min(255, result))
    
    def _execute_rand(self, instruction):
        """Execute random number generation: A = random(0-255)"""
        self.registers[0] = random.randint(0, 255)
    
    # Matrix Operations (simplified for DNA VM)
    def _execute_matmul(self, instruction):
        """Execute matrix multiplication (simplified 2x2)"""
        # Simplified: treat registers as 2x2 matrix elements
        a, b, c, d = self.registers[:4]
        # Result stored back in first two registers
        self.registers[0] = (a * a + b * c) & 0xFF
        self.registers[1] = (a * b + b * d) & 0xFF
    
    def _execute_matinv(self, instruction):
        """Execute matrix inverse (simplified 2x2)"""
        a, b = self.registers[0], self.registers[1]
        c, d = self.registers[2], self.registers[3]
        det = (a * d - b * c) % 256
        if det != 0:
            inv_det = pow(det, -1, 256)  # Modular inverse
            self.registers[0] = (d * inv_det) & 0xFF
            self.registers[1] = (-b * inv_det) & 0xFF
    
    def _execute_mattrans(self, instruction):
        """Execute matrix transpose"""
        # Swap elements for 2x2 matrix
        self.registers[1], self.registers[2] = self.registers[2], self.registers[1]
    
    # Biological Operations
    def _execute_dnacmp(self, instruction):
        """Execute DNA complement"""
        addr = self.registers[0]
        length = self.registers[1]
        complement_map = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C'}
        
        # Read DNA sequence from memory, complement it
        for i in range(length):
            if addr + i < len(self.memory):
                byte_val = self.memory[addr + i]
                # Convert byte to DNA and complement
                dna_char = self.encoder.byte_to_dna(byte_val)[0] if byte_val < 4 else 'A'
                comp_char = complement_map.get(dna_char, 'A')
                # Store back
                self.memory[addr + i] = ord(comp_char) & 0xFF
    
    def _execute_dnarev(self, instruction):
        """Execute DNA reverse"""
        addr = self.registers[0]
        length = self.registers[1]
        
        # Reverse DNA sequence in memory
        for i in range(length // 2):
            if addr + i < len(self.memory) and addr + length - 1 - i < len(self.memory):
                temp = self.memory[addr + i]
                self.memory[addr + i] = self.memory[addr + length - 1 - i]
                self.memory[addr + length - 1 - i] = temp
    
    def _execute_transcribe(self, instruction):
        """Execute DNA to RNA transcription"""
        addr = self.registers[0]
        length = self.registers[1]
        
        # Convert DNA to RNA (U replaces T, but we use U already)
        # This is more symbolic in our 4-base system
        for i in range(length):
            if addr + i < len(self.memory):
                # Simple transcription simulation
                self.memory[addr + i] = (self.memory[addr + i] + 1) & 0xFF
    
    def _execute_translate(self, instruction):
        """Execute RNA to protein translation"""
        addr = self.registers[0]
        length = self.registers[1]
        
        # Simplified translation (codons to amino acids)
        # Process in groups of 3 nucleotides
        for i in range(0, length - 2, 3):
            if addr + i + 2 < len(self.memory):
                # Convert triplet to amino acid code (simplified)
                codon = (self.memory[addr + i] + self.memory[addr + i + 1] + self.memory[addr + i + 2]) % 20
                self.memory[addr + i // 3] = codon
    
    def _execute_mutate(self, instruction):
        """Execute DNA mutation simulation"""
        addr = self.registers[0]
        length = self.registers[1]
        mutation_rate = self.registers[2]  # Probability out of 255
        
        for i in range(length):
            if addr + i < len(self.memory) and random.randint(0, 255) < mutation_rate:
                # Random mutation
                self.memory[addr + i] = random.randint(0, 255)
    
    def _execute_synthesize(self, instruction):
        """Execute DNA synthesis simulation"""
        addr = self.registers[0]
        length = self.registers[1]
        
        # Add to synthesis queue for biological integration
        synthesis_request = {
            'address': addr,
            'length': length,
            'sequence': list(self.memory[addr:addr + length]),
            'timestamp': time.time()
        }
        self.synthesis_queue.append(synthesis_request)
        
        # Set status in register A
        self.registers[0] = len(self.synthesis_queue)
    
    # Cryptographic Operations
    def _execute_hash(self, instruction):
        """Execute hash function"""
        addr = self.registers[0]
        length = self.registers[1]
        
        data = bytes(self.memory[addr:addr + length])
        hash_obj = hashlib.sha256(data)
        hash_bytes = hash_obj.digest()[:4]  # Take first 4 bytes
        
        # Store hash in registers
        for i, byte_val in enumerate(hash_bytes):
            if i < len(self.registers):
                self.registers[i] = byte_val
    
    def _execute_encrypt(self, instruction):
        """Execute simple encryption (XOR cipher)"""
        addr = self.registers[0]
        length = self.registers[1]
        key = self.registers[2]
        
        for i in range(length):
            if addr + i < len(self.memory):
                self.memory[addr + i] ^= key
    
    def _execute_decrypt(self, instruction):
        """Execute simple decryption (XOR cipher)"""
        # Same as encrypt for XOR cipher
        self._execute_encrypt(instruction)
    
    def _execute_checksum(self, instruction):
        """Execute checksum calculation"""
        addr = self.registers[0]
        length = self.registers[1]
        
        checksum = 0
        for i in range(length):
            if addr + i < len(self.memory):
                checksum = (checksum + self.memory[addr + i]) & 0xFF
        
        self.registers[0] = checksum
    
    # Error Correction Operations
    def _execute_encode_rs(self, instruction):
        """Execute Reed-Solomon encoding (simplified)"""
        addr = self.registers[0]
        data_length = self.registers[1]
        parity_length = self.registers[2]
        
        # Simplified Reed-Solomon: add parity bytes
        for i in range(parity_length):
            if addr + data_length + i < len(self.memory):
                parity = 0
                for j in range(data_length):
                    parity ^= self.memory[addr + j]
                self.memory[addr + data_length + i] = parity
    
    def _execute_decode_rs(self, instruction):
        """Execute Reed-Solomon decoding (simplified)"""
        addr = self.registers[0]
        data_length = self.registers[1]
        parity_length = self.registers[2]
        
        # Simplified error detection
        calculated_parity = 0
        for i in range(data_length):
            calculated_parity ^= self.memory[addr + i]
        
        stored_parity = self.memory[addr + data_length] if addr + data_length < len(self.memory) else 0
        
        # Set error flag in register A
        self.registers[0] = 1 if calculated_parity != stored_parity else 0
    
    def _execute_correct(self, instruction):
        """Execute error correction"""
        addr = self.registers[0]
        length = self.registers[1]
        
        # Simple error correction: flip bits that seem wrong
        for i in range(length):
            if addr + i < len(self.memory):
                # Simplified: if byte is 0xFF, might be corrupted
                if self.memory[addr + i] == 0xFF:
                    self.memory[addr + i] = random.randint(0, 254)
    
    def _execute_detect(self, instruction):
        """Execute error detection"""
        addr = self.registers[0]
        length = self.registers[1]
        
        # Count suspicious patterns
        error_count = 0
        for i in range(length):
            if addr + i < len(self.memory):
                if self.memory[addr + i] == 0xFF or self.memory[addr + i] == 0x00:
                    error_count += 1
        
        self.registers[0] = min(255, error_count)
    
    # Threading Operations
    def _execute_spawn(self, instruction):
        """Execute thread spawn"""
        thread_id = len(self.thread_pool)
        
        # Create a simple thread simulation
        thread_info = {
            'id': thread_id,
            'status': 'running',
            'created': time.time(),
            'registers': self.registers.copy()
        }
        self.thread_pool.append(thread_info)
        
        self.registers[0] = thread_id
    
    def _execute_join(self, instruction):
        """Execute thread join"""
        thread_id = self.registers[0]
        
        if thread_id < len(self.thread_pool):
            thread_info = self.thread_pool[thread_id]
            thread_info['status'] = 'joined'
            # Return thread's final register state
            self.registers = thread_info['registers'].copy()
    
    def _execute_lock(self, instruction):
        """Execute lock acquisition"""
        lock_id = self.registers[0]
        
        if lock_id not in self.locks:
            self.locks[lock_id] = {'locked': True, 'owner': 'main'}
            self.registers[0] = 1  # Success
        else:
            self.registers[0] = 0  # Failed
    
    def _execute_unlock(self, instruction):
        """Execute lock release"""
        lock_id = self.registers[0]
        
        if lock_id in self.locks:
            del self.locks[lock_id]
            self.registers[0] = 1  # Success
        else:
            self.registers[0] = 0  # No such lock
    
    def _execute_sync(self, instruction):
        """Execute thread synchronization"""
        # Wait for all threads to complete
        for thread_info in self.thread_pool:
            thread_info['status'] = 'synchronized'
        
        self.registers[0] = len(self.thread_pool)


# Convenience function for quick VM creation
def create_vm(memory_size: int = 256, registers: int = 4) -> DNAVirtualMachine:
    """Create a new DNA Virtual Machine instance"""
    return DNAVirtualMachine(memory_size, registers) 