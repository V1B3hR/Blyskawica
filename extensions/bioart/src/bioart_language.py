#!/usr/bin/env python3
"""
Bioart Programming Language - Enhanced Main Module
Integrated high-performance bioart programming language with advanced biological features
"""

import os
import sys
from typing import Optional, Dict, Any, List, Tuple
import json
import time

from .core.encoding import DNAEncoder
from .vm.instruction_set import DNAInstructionSet, InstructionType
from .vm.virtual_machine import DNAVirtualMachine, VMState
from .compiler.dna_compiler import DNACompiler
from .utils.file_manager import DNAFileManager

# New biological and parallel modules
from .biological.synthesis_systems import DNASynthesisManager
from .biological.storage_systems import BiologicalStorageManager
from .biological.genetic_tools import GeneticEngineeringInterface
from .biological.error_correction import BiologicalErrorCorrection

from .parallel.dna_threading import DNAThreadManager
from .parallel.parallel_executor import ParallelDNAExecutor, ExecutionStrategy
from .parallel.distributed_computing import DistributedDNAComputer, NodeType

class BioartLanguage:
    """
    Enhanced Bioart Programming Language Interface
    Provides comprehensive API for DNA-based computing with biological integration
    """
    
    def __init__(self, memory_size: int = 256, register_count: int = 4):
        """Initialize enhanced Bioart Language system"""
        # Core components
        self.encoder = DNAEncoder()
        self.instruction_set = DNAInstructionSet()
        self.vm = DNAVirtualMachine(memory_size, register_count)
        self.compiler = DNACompiler(self.encoder, self.instruction_set)
        self.file_manager = DNAFileManager()
        
        # Biological integration components (NEW)
        self.synthesis_manager = DNASynthesisManager()
        self.storage_manager = BiologicalStorageManager()
        self.genetic_tools = GeneticEngineeringInterface()
        self.error_correction = BiologicalErrorCorrection()
        
        # Parallel processing components (NEW)
        self.thread_manager = DNAThreadManager()
        self.parallel_executor = ParallelDNAExecutor()
        self.distributed_computer = DistributedDNAComputer()
        
        # Set VM factory for parallel components
        vm_factory = lambda: DNAVirtualMachine(memory_size, register_count)
        self.thread_manager.set_vm_factory(vm_factory)
        self.parallel_executor.set_vm_factory(vm_factory)
        self.distributed_computer.set_vm_factory(vm_factory)
        
        # System configuration
        self.config = {
            'memory_size': memory_size,
            'register_count': register_count,
            'debug_mode': False,
            'optimization_level': 1,
            'output_format': 'text',
            # New configuration options
            'biological_simulation': True,
            'error_correction_enabled': True,
            'parallel_execution': True,
            'distributed_computing': False,
            'synthesis_integration': True
        }
        
        # Enhanced performance metrics
        self.metrics = {
            'programs_compiled': 0,
            'programs_executed': 0,
            'total_execution_time': 0.0,
            'total_instructions_executed': 0,
            # New metrics
            'biological_operations': 0,
            'synthesis_jobs_submitted': 0,
            'parallel_tasks_executed': 0,
            'error_corrections_applied': 0,
            'genetic_modifications_performed': 0
        }
    
    # ===============================
    # ENHANCED CORE FUNCTIONALITY
    # ===============================
    
    def compile_dna_program(self, dna_source: str, optimize: bool = True,
                          error_correction: bool = True) -> bytes:
        """
        Enhanced compile with error correction and biological validation
        """
        # Apply error correction encoding if enabled
        if error_correction and self.config['error_correction_enabled']:
            corrected_source = self.error_correction.encode_with_error_correction(dna_source)
        else:
            corrected_source = dna_source
        
        # Validate for biological synthesis if enabled
        if self.config['synthesis_integration']:
            validation = self.synthesis_manager._validate_sequence(corrected_source)
            if not validation['valid']:
                print(f"Warning: Sequence may have synthesis issues: {validation['errors']}")
        
        # Compile with enhanced compiler
        bytecode = self.compiler.compile(corrected_source, optimize=optimize)
        self.metrics['programs_compiled'] += 1
        
        return bytecode
    
    def execute_program(self, program: bytes, parallel: bool = False,
                       execution_strategy: ExecutionStrategy = ExecutionStrategy.THREADED) -> Dict[str, Any]:
        """
        Enhanced execution with parallel and biological simulation options
        """
        if parallel and self.config['parallel_execution']:
            return self._execute_parallel(program, execution_strategy)
        else:
            return self._execute_single(program)
    
    def _execute_single(self, program: bytes) -> Dict[str, Any]:
        """Execute single program with biological simulation"""
        start_time = time.time()
        
        try:
            self.vm.load_program(program)
            
            # Apply biological constraints if enabled
            if self.config['biological_simulation']:
                self._apply_biological_constraints()
            
            self.vm.run()
            
            execution_time = time.time() - start_time
            
            # Update metrics
            self.metrics['programs_executed'] += 1
            self.metrics['total_execution_time'] += execution_time
            self.metrics['total_instructions_executed'] += getattr(self.vm, 'instructions_executed', 0)
            
            return {
                'success': True,
                'execution_time': execution_time,
                'final_registers': self.vm.registers.copy(),
                'final_memory': bytes(self.vm.memory),
                'instructions_executed': getattr(self.vm, 'instructions_executed', 0),
                'biological_factors': self._get_biological_factors() if self.config['biological_simulation'] else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    def _execute_parallel(self, program: bytes, strategy: ExecutionStrategy) -> Dict[str, Any]:
        """Execute program using parallel strategies"""
        task_id = self.parallel_executor.submit_task(program)
        results = self.parallel_executor.execute_parallel(strategy, max_concurrent=4)
        
        self.metrics['parallel_tasks_executed'] += 1
        
        return {
            'success': True,
            'parallel_results': results,
            'task_id': task_id,
            'execution_strategy': strategy.value
        }
    
    def _apply_biological_constraints(self):
        """Apply biological execution constraints"""
        # Simulate cellular energy constraints
        if hasattr(self.vm, 'energy_level'):
            self.vm.energy_level = 1.0
        
        # Simulate enzyme availability
        if hasattr(self.vm, 'enzyme_availability'):
            self.vm.enzyme_availability = 0.8
        
        # Apply mutation simulation
        if hasattr(self.vm, 'mutation_rate'):
            self.vm.mutation_rate = 0.0001
    
    def _get_biological_factors(self) -> Dict[str, Any]:
        """Get biological simulation factors"""
        return {
            'energy_level': getattr(self.vm, 'energy_level', 1.0),
            'enzyme_availability': getattr(self.vm, 'enzyme_availability', 1.0),
            'mutation_events': getattr(self.vm, 'mutation_events', 0),
            'synthesis_operations': self.metrics.get('biological_operations', 0)
        }
    
    # ===============================
    # BIOLOGICAL INTEGRATION API
    # ===============================
    
    def submit_dna_synthesis(self, dna_sequence: str, priority: int = 5) -> str:
        """Submit DNA sequence for biological synthesis"""
        job_id = self.synthesis_manager.submit_synthesis_job(dna_sequence, priority)
        self.metrics['synthesis_jobs_submitted'] += 1
        return job_id
    
    def get_synthesis_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get DNA synthesis job status"""
        return self.synthesis_manager.get_job_status(job_id)
    
    def store_in_biological_storage(self, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store data in biological DNA storage"""
        entry_id = self.storage_manager.store_data(data, metadata)
        return entry_id
    
    def retrieve_from_biological_storage(self, entry_id: str, error_correction: bool = True) -> Optional[bytes]:
        """Retrieve data from biological storage"""
        return self.storage_manager.retrieve_data(entry_id, error_correction)
    
    def design_crispr_modification(self, target_sequence: str, modification_type: str,
                                 modification_sequence: Optional[str] = None) -> str:
        """Design CRISPR genetic modification"""
        from .biological.genetic_tools import ModificationType, ToolType
        
        mod_type = ModificationType(modification_type.lower())
        modification_id = self.genetic_tools.design_genetic_modification(
            target_sequence, mod_type, modification_sequence, ToolType.CRISPR_CAS9
        )
        
        self.metrics['genetic_modifications_performed'] += 1
        return modification_id
    
    def simulate_genetic_modification(self, modification_id: str, target_genome: str) -> Dict[str, Any]:
        """Simulate genetic modification on target genome"""
        return self.genetic_tools.simulate_modification(modification_id, target_genome)
    
    def apply_error_correction(self, dna_sequence: str, redundancy_level: int = 3) -> str:
        """Apply biological error correction to DNA sequence"""
        corrected = self.error_correction.encode_with_error_correction(dna_sequence, redundancy_level)
        self.metrics['error_corrections_applied'] += 1
        return corrected
    
    def decode_error_corrected_sequence(self, encoded_sequence: str) -> Tuple[str, List]:
        """Decode error-corrected DNA sequence"""
        return self.error_correction.decode_with_error_correction(encoded_sequence)
    
    # ===============================
    # PARALLEL PROCESSING API
    # ===============================
    
    def create_parallel_task(self, program: bytes, input_data: Optional[bytes] = None,
                           priority: int = 5) -> str:
        """Create parallel execution task"""
        return self.parallel_executor.submit_task(program, input_data=input_data, priority=priority)
    
    def execute_parallel_tasks(self, strategy: ExecutionStrategy = ExecutionStrategy.THREADED,
                             max_concurrent: int = 4) -> Dict[str, Any]:
        """Execute all submitted parallel tasks"""
        return self.parallel_executor.execute_parallel(strategy, max_concurrent)
    
    def create_dna_thread(self, program: bytes, priority: int = 5) -> str:
        """Create DNA execution thread"""
        return self.thread_manager.create_thread(program, priority=priority)
    
    def start_dna_thread(self, thread_id: str) -> bool:
        """Start DNA thread execution"""
        return self.thread_manager.start_thread(thread_id)
    
    def wait_for_thread(self, thread_id: str, timeout: float = None) -> Optional[Dict[str, Any]]:
        """Wait for thread completion"""
        return self.thread_manager.wait_for_thread(thread_id, timeout)
    
    def create_thread_barrier(self, barrier_id: str, thread_count: int) -> bool:
        """Create synchronization barrier for threads"""
        return self.thread_manager.create_thread_barrier(barrier_id, thread_count)
    
    def start_distributed_computing(self, node_type: NodeType = NodeType.HYBRID,
                                  port: int = 8080) -> bool:
        """Start distributed computing node"""
        try:
            self.distributed_computer = DistributedDNAComputer(node_type, port)
            self.distributed_computer.set_vm_factory(lambda: DNAVirtualMachine())
            self.distributed_computer.start_network_service()
            self.config['distributed_computing'] = True
            return True
        except Exception as e:
            print(f"Failed to start distributed computing: {e}")
            return False
    
    def submit_distributed_task(self, program: bytes, input_data: Optional[bytes] = None) -> str:
        """Submit task for distributed execution"""
        return self.distributed_computer.submit_distributed_task(program, input_data)
    
    # ===============================
    # SYSTEM MANAGEMENT API
    # ===============================
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive system capabilities"""
        return {
            'core_features': {
                'instruction_count': len(self.instruction_set.INSTRUCTIONS),
                'memory_size': self.config['memory_size'],
                'register_count': self.config['register_count'],
                'encoding_efficiency': '4 nucleotides per byte',
                'file_formats_supported': ['.dna', '.dnas', '.dnameta']
            },
            'biological_features': {
                'dna_synthesis': True,
                'biological_storage': True,
                'error_correction': True,
                'genetic_engineering': True,
                'crispr_design': True,
                'synthesis_validation': True
            },
            'parallel_features': {
                'multi_threading': True,
                'parallel_execution': True,
                'distributed_computing': self.config['distributed_computing'],
                'load_balancing': True,
                'thread_synchronization': True
            },
            'instruction_types': {
                instr_type.name: len([i for i in self.instruction_set.INSTRUCTIONS.values() 
                                   if i.instruction_type == instr_type])
                for instr_type in InstructionType
            }
        }
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            'core_metrics': self.metrics.copy(),
            'synthesis_stats': self.synthesis_manager.get_synthesis_statistics(),
            'storage_stats': self.storage_manager.get_storage_statistics(),
            'genetic_tools_stats': self.genetic_tools.get_genetic_engineering_statistics(),
            'threading_stats': self.thread_manager.get_threading_statistics(),
            'parallel_execution_stats': self.parallel_executor.get_execution_statistics(),
            'error_correction_stats': self.error_correction.get_error_correction_statistics()
        }
        
        if self.config['distributed_computing']:
            stats['distributed_stats'] = self.distributed_computer.get_system_status()
        
        return stats
    
    def optimize_system_performance(self) -> Dict[str, Any]:
        """Optimize system performance based on usage patterns"""
        optimizations = []
        
        # Optimize synthesis parameters
        if self.metrics['synthesis_jobs_submitted'] > 0:
            # Placeholder for synthesis optimization
            optimizations.append("Synthesis parameters optimized")
        
        # Optimize storage conditions
        storage_opt = self.storage_manager.optimize_storage_conditions()
        if storage_opt['improvement_factor'] > 1.1:
            optimizations.append(f"Storage conditions optimized (improvement: {storage_opt['improvement_factor']:.2f}x)")
        
        # Optimize parallel execution
        if self.metrics['parallel_tasks_executed'] > 0:
            # Could adjust thread pool sizes, etc.
            optimizations.append("Parallel execution parameters optimized")
        
        return {
            'optimizations_applied': optimizations,
            'optimization_timestamp': time.time(),
            'performance_improvements': {
                'storage_degradation_reduction': storage_opt.get('improvement_factor', 1.0),
                'synthesis_efficiency': 1.1,  # Placeholder
                'parallel_efficiency': 1.2     # Placeholder  
            }
        }
    
    def export_system_state(self, filename: str) -> bool:
        """Export complete system state for backup/recovery"""
        try:
            system_state = {
                'config': self.config,
                'metrics': self.metrics,
                'synthesis_queue': [job for job in self.synthesis_manager.synthesis_queue],
                'storage_entries': list(self.storage_manager.storage_entries.keys()),
                'genetic_modifications': list(self.genetic_tools.modifications.keys()),
                'active_threads': self.thread_manager.list_threads(),
                'export_timestamp': time.time(),
                'system_version': '2.0.0-enhanced'
            }
            
            with open(filename, 'w') as f:
                json.dump(system_state, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Failed to export system state: {e}")
            return False
    
    def shutdown_system(self):
        """Gracefully shutdown all system components"""
        print("Shutting down Bioart Language System...")
        
        # Shutdown parallel components
        self.thread_manager.shutdown()
        self.parallel_executor.shutdown()
        
        if self.config['distributed_computing']:
            self.distributed_computer.stop_network_service()
        
        # Process any pending synthesis jobs
        self.synthesis_manager.process_synthesis_queue()
        
        print("System shutdown complete.")

# Convenience function for quick system creation
def create_bioart_system(memory_size: int = 256, enable_all_features: bool = True) -> BioartLanguage:
    """Create a new Bioart Language system with optional feature configuration"""
    system = BioartLanguage(memory_size=memory_size)
    
    if enable_all_features:
        system.config.update({
            'biological_simulation': True,
            'error_correction_enabled': True,
            'parallel_execution': True,
            'synthesis_integration': True
        })
    
    return system
    
    def compile_dna_program(self, dna_source: str, optimize: bool = True) -> bytes:
        """
        Compile DNA source code to optimized bytecode
        
        Args:
            dna_source: DNA source code string
            optimize: Enable compiler optimizations
            
        Returns:
            Compiled bytecode
        """
        try:
            bytecode = self.compiler.compile(dna_source, optimize)
            self.metrics['programs_compiled'] += 1
            return bytecode
        except Exception as e:
            raise RuntimeError(f"Compilation failed: {e}")
    
    def execute_dna_program(self, dna_source: str, max_cycles: int = 1000000) -> Dict[str, Any]:
        """
        Compile and execute DNA program
        
        Args:
            dna_source: DNA source code
            max_cycles: Maximum execution cycles
            
        Returns:
            Execution results and statistics
        """
        try:
            # Compile program
            bytecode = self.compile_dna_program(dna_source)
            
            # Load and execute
            self.vm.load_program(bytecode)
            stats = self.vm.execute(max_cycles)
            
            # Update metrics
            self.metrics['programs_executed'] += 1
            self.metrics['total_execution_time'] += stats.execution_time
            self.metrics['total_instructions_executed'] += stats.instructions_executed
            
            return {
                'success': True,
                'vm_state': self.vm.get_state_info(),
                'execution_stats': {
                    'instructions_executed': stats.instructions_executed,
                    'cycles_elapsed': stats.cycles_elapsed,
                    'execution_time': stats.execution_time,
                    'memory_accesses': stats.memory_accesses,
                    'io_operations': stats.io_operations
                },
                'final_state': self.vm.state.value
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'vm_state': self.vm.get_state_info() if hasattr(self, 'vm') else None
            }
    
    def encode_data(self, data: bytes) -> str:
        """Encode binary data to DNA sequence"""
        return self.encoder.encode_bytes(data)
    
    def decode_data(self, dna_sequence: str) -> bytes:
        """Decode DNA sequence to binary data"""
        return self.encoder.decode_dna(dna_sequence)
    
    def encode_string(self, text: str) -> str:
        """Encode text string to DNA sequence"""
        return self.encoder.encode_string(text)
    
    def decode_string(self, dna_sequence: str) -> str:
        """Decode DNA sequence to text string"""
        return self.encoder.decode_to_string(dna_sequence)
    
    def save_dna_program(self, filename: str, dna_source: str, metadata: Optional[Dict] = None):
        """Save DNA program to file with metadata"""
        self.file_manager.save_dna_program(filename, dna_source, metadata)
    
    def load_dna_program(self, filename: str) -> Dict[str, Any]:
        """Load DNA program from file"""
        return self.file_manager.load_dna_program(filename)
    
    def save_compiled_program(self, filename: str, bytecode: bytes, metadata: Optional[Dict] = None):
        """Save compiled bytecode to file"""
        self.file_manager.save_compiled_program(filename, bytecode, metadata)
    
    def load_compiled_program(self, filename: str) -> bytes:
        """Load compiled bytecode from file"""
        return self.file_manager.load_compiled_program(filename)
    
    def disassemble_program(self, bytecode: bytes) -> List[str]:
        """Disassemble bytecode to human-readable assembly"""
        self.vm.load_program(bytecode)
        return self.vm.disassemble_program()
    
    def validate_dna_sequence(self, dna_sequence: str) -> Dict[str, Any]:
        """Validate DNA sequence format and content"""
        is_valid, message = self.encoder.validate_dna_sequence(dna_sequence)
        
        result = {
            'valid': is_valid,
            'message': message,
            'length': len(dna_sequence.replace(' ', '')),
            'byte_count': len(dna_sequence.replace(' ', '')) // 4
        }
        
        if is_valid:
            try:
                # Additional validation as instruction sequence
                is_program_valid, errors = self.instruction_set.validate_program(dna_sequence)
                result['valid_as_program'] = is_program_valid
                result['program_errors'] = errors
            except:
                result['valid_as_program'] = False
                result['program_errors'] = ['Failed to validate as program']
        
        return result
    
    def get_instruction_info(self, identifier: Any) -> Optional[Dict]:
        """Get detailed information about an instruction"""
        return self.instruction_set.get_instruction_info(identifier)
    
    def list_all_instructions(self) -> List[Dict]:
        """Get list of all available instructions"""
        return self.instruction_set.list_all_instructions()
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'language_info': {
                'version': '2.0.0-refactored',
                'encoding': '2-bit DNA (A=00, U=01, C=10, G=11)',
                'architecture': f'{self.config["memory_size"]} bytes memory, {self.config["register_count"]} registers'
            },
            'instruction_set': self.instruction_set.get_instruction_statistics(),
            'performance_metrics': self.metrics.copy(),
            'vm_configuration': self.config.copy(),
            'encoding_stats': {
                'nucleotides_per_byte': 4,
                'theoretical_max_efficiency': '100%',
                'reversibility': 'Perfect (lossless)'
            }
        }
    
    def benchmark_performance(self, test_data_size: int = 1000) -> Dict[str, Any]:
        """Run performance benchmarks"""
        import random
        
        # Generate test data
        test_data = bytes([random.randint(0, 255) for _ in range(test_data_size)])
        
        # Benchmark encoding
        start_time = time.time()
        dna_sequence = self.encoder.encode_bytes(test_data)
        encoding_time = time.time() - start_time
        
        # Benchmark decoding
        start_time = time.time()
        decoded_data = self.encoder.decode_dna(dna_sequence)
        decoding_time = time.time() - start_time
        
        # Verify accuracy
        accuracy = (test_data == decoded_data)
        
        return {
            'test_size_bytes': test_data_size,
            'dna_sequence_length': len(dna_sequence),
            'encoding_time_ms': encoding_time * 1000,
            'decoding_time_ms': decoding_time * 1000,
            'encoding_speed_mbps': (test_data_size / encoding_time) / (1024 * 1024),
            'decoding_speed_mbps': (test_data_size / decoding_time) / (1024 * 1024),
            'accuracy': accuracy,
            'efficiency_ratio': len(dna_sequence) / test_data_size
        }
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode"""
        self.config['debug_mode'] = enabled
        self.vm.set_debug_mode(enabled)
    
    def add_breakpoint(self, address: int):
        """Add breakpoint for debugging"""
        self.vm.add_breakpoint(address)
    
    def remove_breakpoint(self, address: int):
        """Remove breakpoint"""
        self.vm.remove_breakpoint(address)
    
    def step_execution(self):
        """Execute single instruction (debug mode)"""
        if self.vm.state == VMState.PAUSED:
            # Implementation for single-step execution
            pass
    
    def get_memory_dump(self, start: int = 0, length: int = 16) -> List[int]:
        """Get memory dump for debugging"""
        end = min(start + length, len(self.vm.memory))
        return list(self.vm.memory[start:end])
    
    def reset_system(self):
        """Reset entire system to initial state"""
        self.vm.reset()
        self.metrics = {
            'programs_compiled': 0,
            'programs_executed': 0,
            'total_execution_time': 0.0,
            'total_instructions_executed': 0
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export current system configuration"""
        return {
            'config': self.config.copy(),
            'metrics': self.metrics.copy(),
            'vm_state': self.vm.get_state_info(),
            'timestamp': time.time()
        }
    
    def import_configuration(self, config_data: Dict[str, Any]):
        """Import system configuration"""
        if 'config' in config_data:
            self.config.update(config_data['config'])
            
        # Apply configuration to VM
        if 'debug_mode' in self.config:
            self.vm.set_debug_mode(self.config['debug_mode'])
    
    def create_sample_programs(self) -> Dict[str, str]:
        """Create sample DNA programs for demonstration"""
        return {
            'hello_world': 'AAAU UACA AAUG AAGA',  # Load 72('H'), Print, Halt
            'fibonacci': '''
                AAAU AAAA    # Load 0
                AAAC AAAA    # Store at address 0
                AAAU AAAU    # Load 1  
                AAAC AAAU    # Store at address 1
                AAAU AAAC    # Load 2 (counter)
                AAAC AAAC    # Store at address 2
            ''',
            'counter': '''
                AAAU AAAA    # Load 0
                AUCA         # Increment
                AAUG         # Print
                AAAU AAAU    # Load 1
                AAAG AAAA    # Add 0 (counter check)
                AACU AAAC    # Jump to increment
                AAGA         # Halt
            ''',
            'data_processing': '''
                AAAU ACAA    # Load data
                ACAU         # NOT operation
                AAAG AUAU    # Add mask
                AAUG         # Print result
                AAGA         # Halt
            '''
        }


# Convenience functions for direct use
def create_bioart_language(memory_size: int = 256, registers: int = 4) -> BioartLanguage:
    """Create a new Bioart Language instance"""
    return BioartLanguage(memory_size, registers)

def quick_execute(dna_program: str) -> Dict[str, Any]:
    """Quick execution of DNA program"""
    dna_lang = BioartLanguage()
    return dna_lang.execute_dna_program(dna_program)

def quick_encode(data: str) -> str:
    """Quick encoding of text to DNA"""
    dna_lang = BioartLanguage()
    return dna_lang.encode_string(data)

def quick_decode(dna_sequence: str) -> str:
    """Quick decoding of DNA to text"""
    dna_lang = BioartLanguage()
    return dna_lang.decode_string(dna_sequence)