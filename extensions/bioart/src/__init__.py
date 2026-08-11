#!/usr/bin/env python3
"""
Bioart Programming Language - Refactored Version 2.0
High-performance modular bioart programming language implementation
"""

__version__ = "2.0.0-refactored"
__author__ = "Bioart Programming Language Project"
__license__ = "MIT"

# Import main components for easy access
from .bioart_language import BioartLanguage, create_bioart_system
from .biological.error_correction import BiologicalErrorCorrection
from .biological.genetic_tools import GeneticEngineeringInterface
from .biological.storage_systems import BiologicalStorageManager

# New enhanced modules
from .biological.synthesis_systems import DNASynthesisManager
from .compiler.dna_compiler import DNACompiler
from .core.encoding import DNAEncoder, decode_dna, decode_to_string, encode_bytes, encode_string
from .parallel.distributed_computing import DistributedDNAComputer, NodeType
from .parallel.dna_threading import DNAThreadManager
from .parallel.parallel_executor import ExecutionStrategy, ParallelDNAExecutor
from .utils.file_manager import DNAFileManager
from .vm.instruction_set import DNAInstructionSet, get_instruction, is_valid_instruction
from .vm.virtual_machine import DNAVirtualMachine, VMState, create_vm

# AI Ethics Framework
try:
    from .ethics.ai_ethics_framework import EthicsFramework, EthicsLevel, EthicsViolationError
    ETHICS_AVAILABLE = True
except ImportError:
    ETHICS_AVAILABLE = False

# Version information
VERSION_INFO = {
    'version': __version__,
    'architecture': 'Modular refactored implementation',
    'encoding': '2-bit DNA (A=00, U=01, C=10, G=11)',
    'features': [
        'High-performance encoding with lookup tables',
        'Extended instruction set with 52+ instructions',
        'Advanced virtual machine with biological simulation',
        'Biological DNA synthesis and storage integration',
        'CRISPR and genetic engineering tools interface',
        'Multi-threading and parallel execution support',
        'Distributed computing capabilities',
        'Advanced error correction for biological environments',
        'Real-time biological constraint simulation',
        'Comprehensive AI Ethics Framework integration'
    ],
    'improvements': [
        'Biological synthesis systems integration',
        'Real DNA storage and retrieval mechanisms',
        'Error correction coding for biological environments',
        'Multi-threading support for parallel DNA execution',
        'Interface with genetic engineering tools',
        'Extended instruction set for complex operations',
        'Advanced biological constraint simulation',
        'Distributed computing framework',
        'AI Ethics Framework with 25 principles and laws'
    ]
}

def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO.copy()

def create_default_system():
    """Create a default bioart language system with standard configuration"""
    return create_bioart_system(memory_size=256, enable_all_features=True)

# Package-level convenience functions
def encode_text_to_dna(text: str) -> str:
    """Quick function to encode text to DNA"""
    encoder = DNAEncoder()
    return encoder.encode_string(text)

def decode_dna_to_text(dna_sequence: str) -> str:
    """Quick function to decode DNA to text"""
    encoder = DNAEncoder()
    return encoder.decode_to_string(dna_sequence)

def run_dna_program(dna_code: str) -> dict:
    """Quick function to run DNA program"""
    system = create_default_system()
    try:
        bytecode = system.compile_dna_program(dna_code)
        result = system.execute_program(bytecode)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Export all public components
__all__ = [
    # Main classes
    'BioartLanguage',
    'DNAEncoder',
    'DNAVirtualMachine',
    'DNAInstructionSet',
    'DNACompiler',
    'DNAFileManager',

    # Enums and types
    'VMState',

    # Factory functions
    'create_bioart_system',
    'create_vm',
    'create_default_system',

    # Convenience functions
    'encode_bytes',
    'decode_dna',
    'encode_string',
    'decode_to_string',
    'encode_text_to_dna',
    'decode_dna_to_text',
    'run_dna_program',
    'get_instruction',
    'is_valid_instruction',

    # Enhanced biological components
    'DNASynthesisManager',
    'BiologicalStorageManager',
    'GeneticEngineeringInterface',
    'BiologicalErrorCorrection',

    # Parallel processing components
    'DNAThreadManager',
    'ParallelDNAExecutor',
    'ExecutionStrategy',
    'DistributedDNAComputer',
    'NodeType',

    # AI Ethics Framework (if available)
    'ETHICS_AVAILABLE',

    # Utility functions
    'get_version_info',

    # Version info
    '__version__',
    'VERSION_INFO'
]

# Add ethics framework exports if available
if ETHICS_AVAILABLE:
    __all__.extend([
        'EthicsFramework',
        'EthicsLevel',
        'EthicsViolationError'
    ])
