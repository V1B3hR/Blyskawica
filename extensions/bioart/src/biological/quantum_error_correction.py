#!/usr/bin/env python3
"""
Quantum Error Correction for Biological Storage
Advanced quantum-biological hybrid error correction algorithms for DNA storage
"""

import math
import random
import cmath
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

class QuantumErrorType(Enum):
    """Types of quantum errors"""
    BIT_FLIP = "bit_flip"
    PHASE_FLIP = "phase_flip"
    DEPOLARIZING = "depolarizing"
    AMPLITUDE_DAMPING = "amplitude_damping"
    PHASE_DAMPING = "phase_damping"

class QuantumCodeType(Enum):
    """Types of quantum error correction codes"""
    SHOR_CODE = "shor_code"  # 9-qubit code
    STEANE_CODE = "steane_code"  # 7-qubit CSS code
    SURFACE_CODE = "surface_code"  # Topological code
    BACON_SHOR_CODE = "bacon_shor_code"  # Subsystem code
    FIVE_QUBIT_CODE = "five_qubit_code"  # Perfect code

@dataclass
class QuantumState:
    """Quantum state representation"""
    amplitudes: List[complex]
    num_qubits: int
    
    def __post_init__(self):
        # Normalize the state
        norm = sum(abs(amp)**2 for amp in self.amplitudes)
        if norm > 0:
            norm_factor = math.sqrt(norm)
            self.amplitudes = [amp / norm_factor for amp in self.amplitudes]
    
    def measure_probability(self, state_index: int) -> float:
        """Get measurement probability for a basis state"""
        if 0 <= state_index < len(self.amplitudes):
            return abs(self.amplitudes[state_index])**2
        return 0.0

@dataclass
class DNAQuantumMapping:
    """Mapping between DNA sequences and quantum states"""
    dna_sequence: str
    quantum_state: QuantumState
    encoding_fidelity: float
    decoherence_time: float

@dataclass
class QuantumErrorCorrectionResult:
    """Result of quantum error correction"""
    original_dna: str
    corrected_dna: str
    error_syndrome: List[int]
    correction_applied: bool
    error_types_detected: List[QuantumErrorType]
    fidelity_improvement: float
    quantum_overhead: int

class QuantumErrorCorrector:
    """
    Quantum Error Correction for Biological Storage
    Implements quantum error correction codes adapted for biological systems
    """
    
    def __init__(self):
        self.nucleotides = ['A', 'U', 'C', 'G']
        
        # DNA to quantum state mapping (2-bit encoding)
        self.dna_to_qubit = {
            'A': [1, 0],  # |0⟩
            'U': [0, 1],  # |1⟩
            'C': [1/math.sqrt(2), 1/math.sqrt(2)],  # |+⟩
            'G': [1/math.sqrt(2), -1j/math.sqrt(2)]  # |i⟩
        }
        
        self.qubit_to_dna = {
            (1, 0): 'A',
            (0, 1): 'U',
            (1/math.sqrt(2), 1/math.sqrt(2)): 'C',
            (1/math.sqrt(2), -1j/math.sqrt(2)): 'G'
        }
        
        # Quantum error correction codes
        self.error_correction_codes = {
            QuantumCodeType.SHOR_CODE: self._get_shor_code_params(),
            QuantumCodeType.STEANE_CODE: self._get_steane_code_params(),
            QuantumCodeType.FIVE_QUBIT_CODE: self._get_five_qubit_code_params()
        }
        
        self.correction_history = []
    
    def _get_shor_code_params(self) -> Dict[str, Any]:
        """Get Shor 9-qubit code parameters"""
        return {
            "physical_qubits": 9,
            "logical_qubits": 1,
            "distance": 3,
            "correctable_errors": 1,
            "stabilizer_generators": [
                # X-type stabilizers
                [1, 1, 0, 0, 0, 0, 0, 0, 0],  # X1X2
                [0, 1, 1, 0, 0, 0, 0, 0, 0],  # X2X3
                [0, 0, 0, 1, 1, 0, 0, 0, 0],  # X4X5
                [0, 0, 0, 0, 1, 1, 0, 0, 0],  # X5X6
                [0, 0, 0, 0, 0, 0, 1, 1, 0],  # X7X8
                [0, 0, 0, 0, 0, 0, 0, 1, 1],  # X8X9
                # Z-type stabilizers
                [1, 1, 1, 1, 1, 1, 0, 0, 0],  # Z1Z2Z3Z4Z5Z6
                [0, 0, 0, 1, 1, 1, 1, 1, 1],  # Z4Z5Z6Z7Z8Z9
            ]
        }
    
    def _get_steane_code_params(self) -> Dict[str, Any]:
        """Get Steane 7-qubit code parameters"""
        return {
            "physical_qubits": 7,
            "logical_qubits": 1,
            "distance": 3,
            "correctable_errors": 1,
            "stabilizer_generators": [
                # X-type stabilizers
                [1, 0, 1, 0, 1, 0, 1],  # X1X3X5X7
                [0, 1, 1, 0, 0, 1, 1],  # X2X3X6X7
                [0, 0, 0, 1, 1, 1, 1],  # X4X5X6X7
                # Z-type stabilizers
                [1, 0, 1, 0, 1, 0, 1],  # Z1Z3Z5Z7
                [0, 1, 1, 0, 0, 1, 1],  # Z2Z3Z6Z7
                [0, 0, 0, 1, 1, 1, 1],  # Z4Z5Z6Z7
            ]
        }
    
    def _get_five_qubit_code_params(self) -> Dict[str, Any]:
        """Get 5-qubit perfect code parameters"""
        return {
            "physical_qubits": 5,
            "logical_qubits": 1,
            "distance": 3,
            "correctable_errors": 1,
            "stabilizer_generators": [
                [1, 0, 0, 1, 0],  # X1X4
                [0, 1, 0, 0, 1],  # X2X5
                [1, 0, 1, 0, 0],  # X1X3
                [0, 1, 0, 1, 0],  # X2X4
            ]
        }
    
    def dna_to_quantum_state(self, dna_sequence: str) -> QuantumState:
        """Convert DNA sequence to quantum state representation"""
        if not dna_sequence:
            return QuantumState([1.0 + 0j], 0)
        
        # Limit sequence length to prevent memory issues
        max_qubits = 10  # 2^10 = 1024 states maximum
        limited_sequence = dna_sequence[:max_qubits]
        
        # Convert each nucleotide to qubit state
        qubit_states = []
        for nucleotide in limited_sequence:
            if nucleotide in self.dna_to_qubit:
                qubit_states.append(self.dna_to_qubit[nucleotide])
            else:
                # Default to |0⟩ for unknown nucleotides
                qubit_states.append([1, 0])
        
        # Create tensor product of all qubit states
        num_qubits = len(qubit_states)
        num_states = 2 ** num_qubits
        amplitudes = [0.0 + 0j] * num_states
        
        # Calculate tensor product
        for state_index in range(num_states):
            amplitude = 1.0 + 0j
            for qubit_idx in range(num_qubits):
                bit = (state_index >> (num_qubits - 1 - qubit_idx)) & 1
                amplitude *= qubit_states[qubit_idx][bit]
            amplitudes[state_index] = amplitude
        
        return QuantumState(amplitudes, num_qubits)
    
    def quantum_state_to_dna(self, quantum_state: QuantumState) -> str:
        """Convert quantum state back to DNA sequence"""
        if quantum_state.num_qubits == 0:
            return ""
        
        # Find the most probable computational basis state
        max_prob = 0.0
        most_probable_state = 0
        
        for i, amplitude in enumerate(quantum_state.amplitudes):
            prob = abs(amplitude)**2
            if prob > max_prob:
                max_prob = prob
                most_probable_state = i
        
        # Convert basis state index to DNA sequence
        dna_sequence = ""
        for qubit_idx in range(quantum_state.num_qubits):
            bit = (most_probable_state >> (quantum_state.num_qubits - 1 - qubit_idx)) & 1
            if bit == 0:
                dna_sequence += 'A'
            else:
                dna_sequence += 'U'
        
        return dna_sequence
    
    def apply_quantum_noise(self, quantum_state: QuantumState, 
                          noise_probability: float = 0.01) -> QuantumState:
        """Apply quantum noise to simulate decoherence"""
        new_amplitudes = quantum_state.amplitudes.copy()
        
        for i in range(len(new_amplitudes)):
            if random.random() < noise_probability:
                # Apply random quantum error
                error_type = random.choice(list(QuantumErrorType))
                
                if error_type == QuantumErrorType.BIT_FLIP:
                    # Flip a random qubit
                    if quantum_state.num_qubits > 0:
                        qubit_to_flip = random.randint(0, quantum_state.num_qubits - 1)
                        new_state_idx = i ^ (1 << (quantum_state.num_qubits - 1 - qubit_to_flip))
                        if 0 <= new_state_idx < len(new_amplitudes) and new_state_idx != i:
                            # Swap amplitudes
                            temp = new_amplitudes[i]
                            new_amplitudes[i] = new_amplitudes[new_state_idx]
                            new_amplitudes[new_state_idx] = temp
                
                elif error_type == QuantumErrorType.PHASE_FLIP:
                    # Apply phase flip
                    new_amplitudes[i] *= -1
                
                elif error_type == QuantumErrorType.DEPOLARIZING:
                    # Depolarizing error
                    new_amplitudes[i] *= 0.9
                
                elif error_type == QuantumErrorType.AMPLITUDE_DAMPING:
                    # Amplitude damping
                    new_amplitudes[i] *= 0.95
        
        return QuantumState(new_amplitudes, quantum_state.num_qubits)
    
    def calculate_syndrome(self, quantum_state: QuantumState, 
                          code_type: QuantumCodeType) -> List[int]:
        """Calculate error syndrome for quantum error correction"""
        if code_type not in self.error_correction_codes:
            return []
        
        code_params = self.error_correction_codes[code_type]
        stabilizers = code_params["stabilizer_generators"]
        syndrome = []
        
        for stabilizer in stabilizers:
            # Simplified syndrome calculation
            # In real implementation, this would involve Pauli measurements
            measurement_result = 0
            for i, pauli_op in enumerate(stabilizer):
                if pauli_op == 1 and i < quantum_state.num_qubits:
                    # Simulate Pauli measurement
                    prob = quantum_state.measure_probability(i)
                    if prob > 0.5:
                        measurement_result ^= 1
            
            syndrome.append(measurement_result)
        
        return syndrome
    
    def lookup_correction(self, syndrome: List[int], 
                         code_type: QuantumCodeType) -> Optional[List[int]]:
        """Look up correction operations based on syndrome"""
        if not syndrome or all(s == 0 for s in syndrome):
            return None  # No error detected
        
        # Simplified correction lookup
        # In practice, this would use syndrome tables
        if code_type == QuantumCodeType.SHOR_CODE:
            return self._shor_code_correction(syndrome)
        elif code_type == QuantumCodeType.STEANE_CODE:
            return self._steane_code_correction(syndrome)
        elif code_type == QuantumCodeType.FIVE_QUBIT_CODE:
            return self._five_qubit_correction(syndrome)
        
        return None
    
    def _shor_code_correction(self, syndrome: List[int]) -> Optional[List[int]]:
        """Shor code correction lookup"""
        # Simplified correction for demonstration
        if syndrome == [1, 0, 0, 0, 0, 0, 0, 0]:
            return [1, 0, 0, 0, 0, 0, 0, 0, 0]  # X error on qubit 1
        elif syndrome == [0, 1, 0, 0, 0, 0, 0, 0]:
            return [0, 1, 0, 0, 0, 0, 0, 0, 0]  # X error on qubit 2
        elif syndrome == [0, 0, 0, 0, 0, 0, 1, 0]:
            return [1, 1, 1, 0, 0, 0, 0, 0, 0]  # Z error on first block
        
        return [0] * 9  # No specific correction found
    
    def _steane_code_correction(self, syndrome: List[int]) -> Optional[List[int]]:
        """Steane code correction lookup"""
        syndrome_int = sum(syndrome[i] * (2**i) for i in range(len(syndrome)))
        
        # Error position based on syndrome
        if syndrome_int > 0 and syndrome_int <= 7:
            correction = [0] * 7
            correction[syndrome_int - 1] = 1
            return correction
        
        return [0] * 7
    
    def _five_qubit_correction(self, syndrome: List[int]) -> Optional[List[int]]:
        """5-qubit code correction lookup"""
        if syndrome == [1, 0, 0, 0]:
            return [1, 0, 0, 0, 0]  # Error on qubit 1
        elif syndrome == [0, 1, 0, 0]:
            return [0, 1, 0, 0, 0]  # Error on qubit 2
        elif syndrome == [0, 0, 1, 0]:
            return [0, 0, 1, 0, 0]  # Error on qubit 3
        elif syndrome == [0, 0, 0, 1]:
            return [0, 0, 0, 1, 0]  # Error on qubit 4
        
        return [0] * 5
    
    def apply_correction(self, quantum_state: QuantumState, 
                        correction: List[int]) -> QuantumState:
        """Apply quantum error correction"""
        if not correction or all(c == 0 for c in correction):
            return quantum_state
        
        new_amplitudes = quantum_state.amplitudes.copy()
        
        # Apply Pauli corrections
        for qubit_idx, correction_op in enumerate(correction):
            if correction_op == 1 and qubit_idx < quantum_state.num_qubits:
                # Apply X (bit flip) correction
                for state_idx in range(len(new_amplitudes)):
                    # Check if this qubit is |1⟩ in this basis state
                    qubit_bit = (state_idx >> (quantum_state.num_qubits - 1 - qubit_idx)) & 1
                    if qubit_bit == 1:
                        # Flip this qubit in the basis state
                        flipped_state = state_idx ^ (1 << (quantum_state.num_qubits - 1 - qubit_idx))
                        if 0 <= flipped_state < len(new_amplitudes) and flipped_state != state_idx:
                            # Swap amplitudes
                            temp = new_amplitudes[state_idx]
                            new_amplitudes[state_idx] = new_amplitudes[flipped_state]
                            new_amplitudes[flipped_state] = temp
        
        return QuantumState(new_amplitudes, quantum_state.num_qubits)
    
    def calculate_fidelity(self, state1: QuantumState, state2: QuantumState) -> float:
        """Calculate quantum state fidelity"""
        if state1.num_qubits != state2.num_qubits:
            return 0.0
        
        # Fidelity = |⟨ψ1|ψ2⟩|²
        overlap = sum(
            (amp1.conjugate() * amp2).real
            for amp1, amp2 in zip(state1.amplitudes, state2.amplitudes)
        )
        
        return abs(overlap)**2
    
    def encode_with_quantum_ecc(self, dna_sequence: str, 
                               code_type: QuantumCodeType = QuantumCodeType.STEANE_CODE) -> str:
        """Encode DNA sequence with quantum error correction"""
        if code_type not in self.error_correction_codes:
            return dna_sequence
        
        code_params = self.error_correction_codes[code_type]
        logical_qubits = code_params["logical_qubits"]
        physical_qubits = code_params["physical_qubits"]
        
        # Limit encoding to prevent excessive length
        max_input_length = 8  # Reasonable limit for demo
        limited_sequence = dna_sequence[:max_input_length]
        
        encoded_sequence = ""
        
        # Process sequence in blocks
        for i in range(0, len(limited_sequence), logical_qubits):
            block = limited_sequence[i:i + logical_qubits]
            
            # Pad block if necessary
            while len(block) < logical_qubits:
                block += 'A'
            
            # Encode logical qubits to physical qubits
            # Simplified encoding - in practice would use quantum circuits
            encoded_block = block
            
            # Add redundancy based on code parameters (limited)
            redundancy_factor = min(3, physical_qubits // logical_qubits)  # Cap redundancy
            for _ in range(redundancy_factor - 1):
                encoded_block += block
            
            # Add parity nucleotides for error detection
            parity = self._calculate_dna_parity(encoded_block)
            encoded_block += parity
            
            encoded_sequence += encoded_block
        
        return encoded_sequence
    
    def _calculate_dna_parity(self, sequence: str) -> str:
        """Calculate parity nucleotides for DNA sequence"""
        if not sequence:
            return ""
        
        # Simple parity calculation
        counts = {'A': 0, 'U': 0, 'C': 0, 'G': 0}
        for nucleotide in sequence:
            if nucleotide in counts:
                counts[nucleotide] += 1
        
        # Generate parity based on counts
        parity = ""
        if counts['A'] % 2 == 1:
            parity += 'A'
        if counts['U'] % 2 == 1:
            parity += 'U'
        if counts['C'] % 2 == 1:
            parity += 'C'
        if counts['G'] % 2 == 1:
            parity += 'G'
        
        return parity if parity else 'A'
    
    def decode_with_quantum_ecc(self, encoded_sequence: str, 
                               code_type: QuantumCodeType = QuantumCodeType.STEANE_CODE) -> QuantumErrorCorrectionResult:
        """Decode DNA sequence with quantum error correction"""
        original_state = self.dna_to_quantum_state(encoded_sequence)
        
        # Apply quantum noise simulation
        noisy_state = self.apply_quantum_noise(original_state, 0.02)
        
        # Calculate error syndrome
        syndrome = self.calculate_syndrome(noisy_state, code_type)
        
        # Look up correction
        correction = self.lookup_correction(syndrome, code_type)
        correction_applied = correction is not None and any(c != 0 for c in correction)
        
        # Apply correction if needed
        if correction_applied:
            corrected_state = self.apply_correction(noisy_state, correction)
        else:
            corrected_state = noisy_state
        
        # Convert back to DNA
        corrected_dna = self.quantum_state_to_dna(corrected_state)
        
        # Calculate fidelity improvement
        original_fidelity = self.calculate_fidelity(original_state, noisy_state)
        corrected_fidelity = self.calculate_fidelity(original_state, corrected_state)
        fidelity_improvement = corrected_fidelity - original_fidelity
        
        # Determine error types (simplified)
        error_types_detected = []
        if correction_applied:
            error_types_detected.append(QuantumErrorType.BIT_FLIP)
        
        # Calculate quantum overhead
        code_params = self.error_correction_codes[code_type]
        quantum_overhead = code_params["physical_qubits"] - code_params["logical_qubits"]
        
        result = QuantumErrorCorrectionResult(
            original_dna=encoded_sequence,
            corrected_dna=corrected_dna,
            error_syndrome=syndrome,
            correction_applied=correction_applied,
            error_types_detected=error_types_detected,
            fidelity_improvement=fidelity_improvement,
            quantum_overhead=quantum_overhead
        )
        
        self.correction_history.append(result)
        return result
    
    def create_quantum_biological_mapping(self, dna_sequence: str) -> DNAQuantumMapping:
        """Create mapping between DNA and quantum representations"""
        quantum_state = self.dna_to_quantum_state(dna_sequence)
        
        # Calculate encoding fidelity
        reconstructed_dna = self.quantum_state_to_dna(quantum_state)
        encoding_fidelity = len(set(dna_sequence) & set(reconstructed_dna)) / max(len(dna_sequence), 1)
        
        # Estimate decoherence time (simplified model)
        gc_content = (dna_sequence.count('G') + dna_sequence.count('C')) / max(len(dna_sequence), 1)
        decoherence_time = 100.0 * (1.0 + gc_content)  # Higher GC content = longer coherence
        
        return DNAQuantumMapping(
            dna_sequence=dna_sequence,
            quantum_state=quantum_state,
            encoding_fidelity=encoding_fidelity,
            decoherence_time=decoherence_time
        )
    
    def benchmark_quantum_codes(self, test_sequences: List[str]) -> Dict[str, Any]:
        """Benchmark different quantum error correction codes"""
        results = {}
        
        for code_type in [QuantumCodeType.STEANE_CODE, QuantumCodeType.FIVE_QUBIT_CODE]:
            code_results = {
                "total_sequences": len(test_sequences),
                "corrections_applied": 0,
                "average_fidelity_improvement": 0.0,
                "average_overhead": 0.0,
                "error_detection_rate": 0.0
            }
            
            fidelity_improvements = []
            overheads = []
            errors_detected = 0
            
            for sequence in test_sequences:
                encoded = self.encode_with_quantum_ecc(sequence, code_type)
                result = self.decode_with_quantum_ecc(encoded, code_type)
                
                if result.correction_applied:
                    code_results["corrections_applied"] += 1
                
                if result.error_syndrome and any(s != 0 for s in result.error_syndrome):
                    errors_detected += 1
                
                fidelity_improvements.append(result.fidelity_improvement)
                overheads.append(result.quantum_overhead)
            
            code_results["average_fidelity_improvement"] = sum(fidelity_improvements) / len(fidelity_improvements)
            code_results["average_overhead"] = sum(overheads) / len(overheads)
            code_results["error_detection_rate"] = errors_detected / len(test_sequences)
            
            results[code_type.value] = code_results
        
        return results
    
    def get_correction_statistics(self) -> Dict[str, Any]:
        """Get statistics from correction history"""
        if not self.correction_history:
            return {"message": "No corrections performed yet"}
        
        total_corrections = len(self.correction_history)
        successful_corrections = sum(1 for r in self.correction_history if r.correction_applied)
        
        avg_fidelity_improvement = sum(r.fidelity_improvement for r in self.correction_history) / total_corrections
        avg_overhead = sum(r.quantum_overhead for r in self.correction_history) / total_corrections
        
        error_types_count = {}
        for result in self.correction_history:
            for error_type in result.error_types_detected:
                error_types_count[error_type.value] = error_types_count.get(error_type.value, 0) + 1
        
        return {
            "total_corrections": total_corrections,
            "successful_corrections": successful_corrections,
            "success_rate": successful_corrections / total_corrections,
            "average_fidelity_improvement": avg_fidelity_improvement,
            "average_quantum_overhead": avg_overhead,
            "error_types_detected": error_types_count,
            "recent_corrections": [
                {
                    "original_length": len(r.original_dna),
                    "corrected_length": len(r.corrected_dna),
                    "correction_applied": r.correction_applied,
                    "fidelity_improvement": r.fidelity_improvement,
                    "quantum_overhead": r.quantum_overhead
                }
                for r in self.correction_history[-5:]
            ]
        }