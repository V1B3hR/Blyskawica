#!/usr/bin/env python3
"""
Plugin-style Error Correction System for Bioart DNA Programming Language
Allows different error correction schemes to be plugged in with parameterization
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import random
import json

# Import the existing error correction system
from .error_correction import BiologicalErrorCorrection, ErrorPattern, ErrorType

@dataclass
class ErrorCorrectionParameters:
    """Parameters for error correction schemes"""
    mutation_rate: float = 0.001
    environmental_factors: Dict[str, Any] = None
    redundancy_level: int = 3
    correction_strength: float = 1.0
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.environmental_factors is None:
            self.environmental_factors = {}
        if self.custom_params is None:
            self.custom_params = {}

class ErrorCorrectionPlugin(ABC):
    """Abstract base class for error correction plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this error correction scheme"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of this error correction scheme"""
        pass
    
    @abstractmethod
    def encode(self, sequence: str, params: ErrorCorrectionParameters) -> str:
        """Encode sequence with error correction"""
        pass
    
    @abstractmethod
    def decode(self, encoded_sequence: str, params: ErrorCorrectionParameters) -> Tuple[str, List[ErrorPattern]]:
        """Decode sequence and correct errors"""
        pass
    
    @abstractmethod
    def get_default_parameters(self) -> ErrorCorrectionParameters:
        """Get default parameters for this scheme"""
        pass
    
    def validate_parameters(self, params: ErrorCorrectionParameters) -> bool:
        """Validate parameters for this scheme"""
        return True

class SimpleRedundancyPlugin(ErrorCorrectionPlugin):
    """Simple redundancy-based error correction"""
    
    def get_name(self) -> str:
        return "Simple Redundancy"
    
    def get_description(self) -> str:
        return "Basic error correction using sequence repetition and majority voting"
    
    def encode(self, sequence: str, params: ErrorCorrectionParameters) -> str:
        """Encode with simple redundancy"""
        # Repeat each nucleotide based on redundancy level
        encoded = ""
        for nucleotide in sequence:
            encoded += nucleotide * params.redundancy_level
        
        # Add checksum
        checksum = self._calculate_checksum(sequence)
        checksum_dna = self._value_to_dna(checksum)
        
        return encoded + checksum_dna
    
    def decode(self, encoded_sequence: str, params: ErrorCorrectionParameters) -> Tuple[str, List[ErrorPattern]]:
        """Decode with majority voting"""
        errors = []
        
        # Extract checksum (last 8 nucleotides)
        if len(encoded_sequence) < 8:
            return encoded_sequence, [ErrorPattern(ErrorType.SUBSTITUTION, 0, "", "", 0.0)]
        
        data_part = encoded_sequence[:-8]
        checksum_part = encoded_sequence[-8:]
        
        # Decode with majority voting
        decoded = ""
        data_length = len(data_part) // params.redundancy_level
        
        for i in range(data_length):
            start_idx = i * params.redundancy_level
            end_idx = start_idx + params.redundancy_level
            
            if end_idx <= len(data_part):
                votes = data_part[start_idx:end_idx]
                # Majority vote
                nucleotide_counts = {'A': 0, 'U': 0, 'C': 0, 'G': 0}
                for n in votes:
                    if n in nucleotide_counts:
                        nucleotide_counts[n] += 1
                
                best_nucleotide = max(nucleotide_counts, key=nucleotide_counts.get)
                decoded += best_nucleotide
                
                # Check for errors
                if nucleotide_counts[best_nucleotide] < params.redundancy_level:
                    confidence = nucleotide_counts[best_nucleotide] / params.redundancy_level
                    errors.append(ErrorPattern(
                        ErrorType.SUBSTITUTION, i, votes, best_nucleotide, confidence
                    ))
        
        # Verify checksum
        expected_checksum = self._calculate_checksum(decoded)
        actual_checksum = self._dna_to_value(checksum_part)
        
        if expected_checksum != actual_checksum:
            errors.append(ErrorPattern(
                ErrorType.SUBSTITUTION, len(decoded), checksum_part, 
                self._value_to_dna(expected_checksum), 0.5
            ))
        
        return decoded, errors
    
    def get_default_parameters(self) -> ErrorCorrectionParameters:
        return ErrorCorrectionParameters(
            mutation_rate=0.001,
            redundancy_level=3,
            correction_strength=1.0
        )
    
    def _calculate_checksum(self, sequence: str) -> int:
        """Simple XOR checksum"""
        checksum = 0
        for nucleotide in sequence:
            checksum ^= ord(nucleotide)
        return checksum % 256
    
    def _value_to_dna(self, value: int) -> str:
        """Convert integer to DNA representation (2 nucleotides per byte)"""
        # Simple mapping: A=0, U=1, C=2, G=3
        dna_map = ['A', 'U', 'C', 'G']
        result = ""
        for _ in range(4):  # 4 nucleotides for 8 bits
            result = dna_map[value % 4] + result
            value //= 4
        return result
    
    def _dna_to_value(self, dna: str) -> int:
        """Convert DNA representation to integer"""
        dna_values = {'A': 0, 'U': 1, 'C': 2, 'G': 3}
        value = 0
        for nucleotide in dna:
            if nucleotide in dna_values:
                value = value * 4 + dna_values[nucleotide]
        return value

class HammingCodePlugin(ErrorCorrectionPlugin):
    """Hamming code error correction plugin"""
    
    def get_name(self) -> str:
        return "Hamming Code"
    
    def get_description(self) -> str:
        return "Hamming code error correction adapted for DNA sequences"
    
    def encode(self, sequence: str, params: ErrorCorrectionParameters) -> str:
        """Encode with Hamming code"""
        # Convert DNA to binary
        binary_data = self._dna_to_binary(sequence)
        
        # Apply Hamming code
        encoded_binary = self._hamming_encode(binary_data)
        
        # Convert back to DNA
        return self._binary_to_dna(encoded_binary)
    
    def decode(self, encoded_sequence: str, params: ErrorCorrectionParameters) -> Tuple[str, List[ErrorPattern]]:
        """Decode with Hamming code error correction"""
        errors = []
        
        # Convert DNA to binary
        binary_data = self._dna_to_binary(encoded_sequence)
        
        # Apply Hamming decode
        decoded_binary, error_positions = self._hamming_decode(binary_data)
        
        # Record errors
        for pos in error_positions:
            errors.append(ErrorPattern(
                ErrorType.SUBSTITUTION, pos // 2, "", "", 0.9
            ))
        
        # Convert back to DNA
        decoded_sequence = self._binary_to_dna(decoded_binary)
        
        return decoded_sequence, errors
    
    def get_default_parameters(self) -> ErrorCorrectionParameters:
        return ErrorCorrectionParameters(
            mutation_rate=0.01,
            correction_strength=0.8
        )
    
    def _dna_to_binary(self, sequence: str) -> str:
        """Convert DNA sequence to binary"""
        dna_to_bits = {'A': '00', 'U': '01', 'C': '10', 'G': '11'}
        return ''.join(dna_to_bits.get(n, '00') for n in sequence)
    
    def _binary_to_dna(self, binary: str) -> str:
        """Convert binary to DNA sequence"""
        bits_to_dna = {'00': 'A', '01': 'U', '10': 'C', '11': 'G'}
        result = ""
        for i in range(0, len(binary), 2):
            bits = binary[i:i+2]
            if len(bits) == 2:
                result += bits_to_dna.get(bits, 'A')
        return result
    
    def _hamming_encode(self, data: str) -> str:
        """Simple Hamming(7,4) encoding"""
        # Pad data to multiple of 4 bits
        while len(data) % 4 != 0:
            data += '0'
        
        encoded = ""
        for i in range(0, len(data), 4):
            block = data[i:i+4]
            if len(block) == 4:
                # Hamming(7,4) parity calculation
                d1, d2, d3, d4 = [int(b) for b in block]
                p1 = d1 ^ d2 ^ d4
                p2 = d1 ^ d3 ^ d4
                p3 = d2 ^ d3 ^ d4
                
                encoded += f"{p1}{p2}{d1}{p3}{d2}{d3}{d4}"
        
        return encoded
    
    def _hamming_decode(self, encoded: str) -> Tuple[str, List[int]]:
        """Simple Hamming(7,4) decoding"""
        errors = []
        decoded = ""
        
        for i in range(0, len(encoded), 7):
            block = encoded[i:i+7]
            if len(block) == 7:
                # Extract bits
                bits = [int(b) for b in block]
                if len(bits) == 7:
                    p1, p2, d1, p3, d2, d3, d4 = bits
                    
                    # Calculate syndrome
                    s1 = p1 ^ d1 ^ d2 ^ d4
                    s2 = p2 ^ d1 ^ d3 ^ d4
                    s3 = p3 ^ d2 ^ d3 ^ d4
                    
                    syndrome = s3 * 4 + s2 * 2 + s1
                    
                    if syndrome != 0:
                        # Error detected
                        errors.append(i + syndrome - 1)
                        # Correct single-bit error
                        if 0 <= syndrome - 1 < 7:
                            bits[syndrome - 1] ^= 1
                            p1, p2, d1, p3, d2, d3, d4 = bits
                    
                    # Extract data bits
                    decoded += f"{d1}{d2}{d3}{d4}"
        
        return decoded, errors

class AdvancedBiologicalPlugin(ErrorCorrectionPlugin):
    """Advanced biological error correction using existing system"""
    
    def __init__(self):
        self.bio_corrector = BiologicalErrorCorrection()
    
    def get_name(self) -> str:
        return "Advanced Biological"
    
    def get_description(self) -> str:
        return "Advanced biological error correction with Reed-Solomon and environmental modeling"
    
    def encode(self, sequence: str, params: ErrorCorrectionParameters) -> str:
        """Encode using advanced biological system"""
        # Set environmental conditions
        if params.environmental_factors:
            self.bio_corrector.set_environmental_conditions(params.environmental_factors)
        
        return self.bio_corrector.encode_with_error_correction(
            sequence, params.redundancy_level
        )
    
    def decode(self, encoded_sequence: str, params: ErrorCorrectionParameters) -> Tuple[str, List[ErrorPattern]]:
        """Decode using advanced biological system"""
        # Set environmental conditions
        if params.environmental_factors:
            self.bio_corrector.set_environmental_conditions(params.environmental_factors)
        
        return self.bio_corrector.decode_with_error_correction(encoded_sequence)
    
    def get_default_parameters(self) -> ErrorCorrectionParameters:
        return ErrorCorrectionParameters(
            mutation_rate=0.001,
            redundancy_level=3,
            environmental_factors={
                'temperature': 'medium',
                'humidity': 'medium',
                'uv_exposure': 'low'
            },
            correction_strength=1.0
        )

class ErrorCorrectionPluginManager:
    """Manager for error correction plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, ErrorCorrectionPlugin] = {}
        self.default_plugin = "Advanced Biological"
        
        # Register built-in plugins
        self._register_builtin_plugins()
    
    def _register_builtin_plugins(self):
        """Register built-in error correction plugins"""
        plugins = [
            SimpleRedundancyPlugin(),
            HammingCodePlugin(),
            AdvancedBiologicalPlugin(),
        ]
        
        for plugin in plugins:
            self.register_plugin(plugin)
    
    def register_plugin(self, plugin: ErrorCorrectionPlugin):
        """Register a new error correction plugin"""
        name = plugin.get_name()
        self.plugins[name] = plugin
        print(f"Registered error correction plugin: {name}")
    
    def get_plugin(self, name: str) -> Optional[ErrorCorrectionPlugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all available plugin names"""
        return list(self.plugins.keys())
    
    def get_plugin_info(self, name: str) -> Dict[str, str]:
        """Get information about a plugin"""
        plugin = self.get_plugin(name)
        if plugin:
            return {
                "name": plugin.get_name(),
                "description": plugin.get_description(),
                "default_params": str(plugin.get_default_parameters())
            }
        return {}
    
    def encode_with_plugin(self, sequence: str, plugin_name: str = None, 
                          params: ErrorCorrectionParameters = None) -> str:
        """Encode sequence using specified plugin"""
        if plugin_name is None:
            plugin_name = self.default_plugin
        
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Unknown plugin: {plugin_name}")
        
        if params is None:
            params = plugin.get_default_parameters()
        
        if not plugin.validate_parameters(params):
            raise ValueError(f"Invalid parameters for plugin: {plugin_name}")
        
        return plugin.encode(sequence, params)
    
    def decode_with_plugin(self, encoded_sequence: str, plugin_name: str = None,
                          params: ErrorCorrectionParameters = None) -> Tuple[str, List[ErrorPattern]]:
        """Decode sequence using specified plugin"""
        if plugin_name is None:
            plugin_name = self.default_plugin
        
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Unknown plugin: {plugin_name}")
        
        if params is None:
            params = plugin.get_default_parameters()
        
        if not plugin.validate_parameters(params):
            raise ValueError(f"Invalid parameters for plugin: {plugin_name}")
        
        return plugin.decode(encoded_sequence, params)
    
    def save_plugin_config(self, filename: str):
        """Save plugin configuration to file"""
        config = {
            "default_plugin": self.default_plugin,
            "plugins": {name: plugin.get_plugin_info(name) 
                       for name, plugin in self.plugins.items()}
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    
    def benchmark_plugins(self, test_sequence: str = "AUCGAUCGAUCGAUCG") -> Dict[str, Dict[str, Any]]:
        """Benchmark all plugins with a test sequence"""
        results = {}
        
        for name, plugin in self.plugins.items():
            try:
                import time
                params = plugin.get_default_parameters()
                
                # Benchmark encoding
                start_time = time.perf_counter()
                encoded = plugin.encode(test_sequence, params)
                encode_time = time.perf_counter() - start_time
                
                # Benchmark decoding
                start_time = time.perf_counter()
                decoded, errors = plugin.decode(encoded, params)
                decode_time = time.perf_counter() - start_time
                
                # Calculate accuracy
                accuracy = 1.0 if decoded == test_sequence else 0.0
                
                results[name] = {
                    "encode_time_ms": encode_time * 1000,
                    "decode_time_ms": decode_time * 1000,
                    "accuracy": accuracy,
                    "error_count": len(errors),
                    "expansion_ratio": len(encoded) / len(test_sequence),
                    "status": "success"
                }
                
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        
        return results

# Global plugin manager instance
plugin_manager = ErrorCorrectionPluginManager()

def get_error_correction_manager() -> ErrorCorrectionPluginManager:
    """Get the global error correction plugin manager"""
    return plugin_manager