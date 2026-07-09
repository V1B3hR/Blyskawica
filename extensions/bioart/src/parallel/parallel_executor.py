#!/usr/bin/env python3
"""
Parallel DNA Executor
High-level interface for parallel DNA program execution
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import multiprocessing

from .dna_threading import DNAThreadManager, DNAThread, DNAThreadContext

class ExecutionStrategy(Enum):
    """Parallel execution strategies"""
    SEQUENTIAL = "sequential"
    THREADED = "threaded" 
    MULTIPROCESS = "multiprocess"
    DISTRIBUTED = "distributed"
    BIOLOGICAL_SIMULATION = "biological_simulation"

@dataclass
class ParallelTask:
    """Parallel DNA execution task"""
    task_id: str
    program: bytes
    input_data: Optional[bytes] = None
    priority: int = 5
    dependencies: List[str] = None
    expected_runtime: float = 1.0
    memory_requirements: int = 256
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class ParallelDNAExecutor:
    """
    High-level parallel executor for DNA programs
    Supports multiple execution strategies and optimizations
    """
    
    def __init__(self, max_threads: int = None, max_processes: int = None):
        """Initialize parallel executor"""
        self.max_threads = max_threads or min(32, (multiprocessing.cpu_count() or 1) + 4)
        self.max_processes = max_processes or multiprocessing.cpu_count() or 1
        
        # Thread manager for threaded execution
        self.thread_manager = DNAThreadManager(self.max_threads)
        
        # Process pool for multiprocessing
        self.process_pool = None
        
        # Task management
        self.tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        self.task_dependencies = {}
        
        # Performance tracking
        self.execution_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_execution_time': 0.0,
            'parallel_efficiency': 0.0
        }
        
        # VM factory
        self.vm_factory = None
    
    def set_vm_factory(self, factory_func: Callable):
        """Set VM factory function"""
        self.vm_factory = factory_func
        self.thread_manager.set_vm_factory(factory_func)
    
    def submit_task(self, program: bytes, task_id: Optional[str] = None,
                   input_data: Optional[bytes] = None, priority: int = 5,
                   dependencies: Optional[List[str]] = None) -> str:
        """Submit task for parallel execution"""
        import uuid
        
        if task_id is None:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists")
        
        task = ParallelTask(
            task_id=task_id,
            program=program,
            input_data=input_data,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        self.execution_stats['total_tasks'] += 1
        
        # Track dependencies
        for dep_id in task.dependencies:
            if dep_id not in self.task_dependencies:
                self.task_dependencies[dep_id] = []
            self.task_dependencies[dep_id].append(task_id)
        
        return task_id
    
    def execute_parallel(self, strategy: ExecutionStrategy = ExecutionStrategy.THREADED,
                        max_concurrent: Optional[int] = None) -> Dict[str, Any]:
        """Execute all submitted tasks in parallel"""
        if not self.tasks:
            return {'success': True, 'results': {}, 'message': 'No tasks to execute'}
        
        max_concurrent = max_concurrent or self.max_threads
        
        if strategy == ExecutionStrategy.SEQUENTIAL:
            return self._execute_sequential()
        elif strategy == ExecutionStrategy.THREADED:
            return self._execute_threaded(max_concurrent)
        elif strategy == ExecutionStrategy.MULTIPROCESS:
            return self._execute_multiprocess(max_concurrent)
        elif strategy == ExecutionStrategy.BIOLOGICAL_SIMULATION:
            return self._execute_biological_simulation(max_concurrent)
        else:
            raise ValueError(f"Unsupported execution strategy: {strategy}")
    
    def _execute_sequential(self) -> Dict[str, Any]:
        """Execute tasks sequentially"""
        if self.vm_factory is None:
            raise RuntimeError("VM factory not set")
        
        results = {}
        start_time = time.time()
        
        # Resolve dependencies and create execution order
        execution_order = self._resolve_task_dependencies()
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            try:
                # Create VM and execute
                vm = self.vm_factory()
                
                # Load input data if provided
                if task.input_data:
                    vm.memory[:len(task.input_data)] = task.input_data
                
                vm.load_program(task.program)
                
                task_start = time.time()
                vm.run()
                task_end = time.time()
                
                results[task_id] = {
                    'success': True,
                    'execution_time': task_end - task_start,
                    'final_registers': vm.registers.copy(),
                    'output': getattr(vm, 'output_buffer', []),
                    'instructions_executed': getattr(vm, 'instructions_executed', 0)
                }
                
                self.completed_tasks[task_id] = results[task_id]
                self.execution_stats['completed_tasks'] += 1
                
            except Exception as e:
                results[task_id] = {
                    'success': False,
                    'error': str(e),
                    'execution_time': 0.0
                }
                
                self.failed_tasks[task_id] = results[task_id]
                self.execution_stats['failed_tasks'] += 1
        
        total_time = time.time() - start_time
        self.execution_stats['total_execution_time'] += total_time
        
        return {
            'success': True,
            'strategy': 'sequential',
            'results': results,
            'total_execution_time': total_time,
            'tasks_completed': len([r for r in results.values() if r['success']]),
            'tasks_failed': len([r for r in results.values() if not r['success']])
        }
    
    def _execute_threaded(self, max_concurrent: int) -> Dict[str, Any]:
        """Execute tasks using threading"""
        results = {}
        start_time = time.time()
        
        # Resolve dependencies
        execution_order = self._resolve_task_dependencies()
        
        # Execute in batches respecting dependencies
        batch_results = {}
        current_batch = []
        
        for task_id in execution_order:
            # Check if dependencies are satisfied
            task = self.tasks[task_id]
            dependencies_ready = all(
                dep_id in batch_results and batch_results[dep_id]['success']
                for dep_id in task.dependencies
            )
            
            if dependencies_ready:
                current_batch.append(task_id)
                
                # Execute batch when full or at end
                if len(current_batch) >= max_concurrent or task_id == execution_order[-1]:
                    batch_results.update(self._execute_thread_batch(current_batch))
                    current_batch = []
        
        total_time = time.time() - start_time
        self.execution_stats['total_execution_time'] += total_time
        
        # Calculate parallel efficiency
        sequential_time = sum(r.get('execution_time', 0) for r in batch_results.values())
        parallel_efficiency = sequential_time / total_time if total_time > 0 else 0
        self.execution_stats['parallel_efficiency'] = parallel_efficiency
        
        return {
            'success': True,
            'strategy': 'threaded',
            'results': batch_results,
            'total_execution_time': total_time,
            'parallel_efficiency': parallel_efficiency,
            'tasks_completed': len([r for r in batch_results.values() if r['success']]),
            'tasks_failed': len([r for r in batch_results.values() if not r['success']])
        }
    
    def _execute_thread_batch(self, task_ids: List[str]) -> Dict[str, Any]:
        """Execute a batch of tasks using threads"""
        batch_results = {}
        thread_ids = []
        
        # Create and start threads
        for task_id in task_ids:
            task = self.tasks[task_id]
            
            # Create thread context with input data
            context = DNAThreadContext(thread_id=f"thread_{task_id}")
            if task.input_data:
                context.memory[:len(task.input_data)] = task.input_data
            
            thread_id = self.thread_manager.create_thread(
                task.program, 
                thread_id=f"thread_{task_id}",
                priority=task.priority,
                context=context
            )
            
            thread_ids.append((task_id, thread_id))
            self.thread_manager.start_thread(thread_id)
        
        # Wait for completion
        for task_id, thread_id in thread_ids:
            result = self.thread_manager.wait_for_thread(thread_id)
            
            if result and result['success']:
                batch_results[task_id] = result
                self.completed_tasks[task_id] = result
                self.execution_stats['completed_tasks'] += 1
            else:
                error_result = {
                    'success': False,
                    'error': result.get('error', 'Unknown error') if result else 'Thread failed',
                    'execution_time': result.get('execution_time', 0) if result else 0
                }
                batch_results[task_id] = error_result
                self.failed_tasks[task_id] = error_result
                self.execution_stats['failed_tasks'] += 1
        
        return batch_results
    
    def _execute_multiprocess(self, max_concurrent: int) -> Dict[str, Any]:
        """Execute tasks using multiprocessing"""
        if self.process_pool is None:
            self.process_pool = multiprocessing.Pool(processes=min(max_concurrent, self.max_processes))
        
        results = {}
        start_time = time.time()
        
        try:
            # Prepare tasks for multiprocessing
            execution_order = self._resolve_task_dependencies()
            
            # Execute in dependency-respecting batches
            batch_results = {}
            
            for task_id in execution_order:
                task = self.tasks[task_id]
                
                # Check dependencies
                dependencies_ready = all(
                    dep_id in batch_results and batch_results[dep_id]['success']
                    for dep_id in task.dependencies
                )
                
                if dependencies_ready:
                    # Submit to process pool
                    future = self.process_pool.apply_async(
                        self._execute_single_task,
                        (task.program, task.input_data, self.vm_factory)
                    )
                    
                    try:
                        result = future.get(timeout=30.0)  # 30 second timeout
                        batch_results[task_id] = result
                        
                        if result['success']:
                            self.completed_tasks[task_id] = result
                            self.execution_stats['completed_tasks'] += 1
                        else:
                            self.failed_tasks[task_id] = result
                            self.execution_stats['failed_tasks'] += 1
                            
                    except multiprocessing.TimeoutError:
                        error_result = {
                            'success': False,
                            'error': 'Process timeout',
                            'execution_time': 30.0
                        }
                        batch_results[task_id] = error_result
                        self.failed_tasks[task_id] = error_result
                        self.execution_stats['failed_tasks'] += 1
            
            total_time = time.time() - start_time
            self.execution_stats['total_execution_time'] += total_time
            
            return {
                'success': True,
                'strategy': 'multiprocess',
                'results': batch_results,
                'total_execution_time': total_time,
                'tasks_completed': len([r for r in batch_results.values() if r['success']]),
                'tasks_failed': len([r for r in batch_results.values() if not r['success']])
            }
            
        finally:
            pass  # Keep pool open for reuse
    
    def _execute_biological_simulation(self, max_concurrent: int) -> Dict[str, Any]:
        """Execute with biological process simulation"""
        results = {}
        start_time = time.time()
        
        # Simulate biological parallel execution
        # DNA strands executing in parallel within a cell
        
        execution_order = self._resolve_task_dependencies()
        strand_results = {}
        
        # Simulate cellular environment
        cellular_energy = 1000.0  # Total cellular energy
        enzyme_availability = 0.8  # 80% enzyme availability
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            
            # Check cellular conditions
            if cellular_energy < 10.0:
                # Energy depleted
                strand_results[task_id] = {
                    'success': False,
                    'error': 'Cellular energy depleted',
                    'execution_time': 0.0,
                    'biological_factors': {
                        'energy_remaining': cellular_energy,
                        'enzyme_availability': enzyme_availability
                    }
                }
                continue
            
            # Simulate biological execution
            bio_start = time.time()
            
            try:
                # Create VM with biological constraints
                vm = self.vm_factory()
                
                # Apply biological factors
                execution_efficiency = enzyme_availability * (cellular_energy / 1000.0)
                
                # Load task
                if task.input_data:
                    vm.memory[:len(task.input_data)] = task.input_data
                
                vm.load_program(task.program)
                
                # Simulate biological execution delays
                import random
                bio_delay = random.uniform(0.01, 0.1) * len(task.program)
                time.sleep(bio_delay)
                
                # Execute
                vm.run()
                
                bio_end = time.time()
                execution_time = bio_end - bio_start
                
                # Consume cellular energy
                energy_consumed = len(task.program) * 0.1
                cellular_energy -= energy_consumed
                
                # Simulate enzyme recycling
                enzyme_availability = min(1.0, enzyme_availability + 0.05)
                
                strand_results[task_id] = {
                    'success': True,
                    'execution_time': execution_time,
                    'final_registers': vm.registers.copy(),
                    'output': getattr(vm, 'output_buffer', []),
                    'biological_factors': {
                        'energy_consumed': energy_consumed,
                        'energy_remaining': cellular_energy,
                        'enzyme_availability': enzyme_availability,
                        'execution_efficiency': execution_efficiency
                    }
                }
                
                self.completed_tasks[task_id] = strand_results[task_id]
                self.execution_stats['completed_tasks'] += 1
                
            except Exception as e:
                strand_results[task_id] = {
                    'success': False,
                    'error': str(e),
                    'execution_time': time.time() - bio_start,
                    'biological_factors': {
                        'energy_remaining': cellular_energy,
                        'enzyme_availability': enzyme_availability
                    }
                }
                
                self.failed_tasks[task_id] = strand_results[task_id]
                self.execution_stats['failed_tasks'] += 1
        
        total_time = time.time() - start_time
        self.execution_stats['total_execution_time'] += total_time
        
        return {
            'success': True,
            'strategy': 'biological_simulation',
            'results': strand_results,
            'total_execution_time': total_time,
            'cellular_state': {
                'final_energy': cellular_energy,
                'enzyme_availability': enzyme_availability
            },
            'tasks_completed': len([r for r in strand_results.values() if r['success']]),
            'tasks_failed': len([r for r in strand_results.values() if not r['success']])
        }
    
    @staticmethod
    def _execute_single_task(program: bytes, input_data: Optional[bytes], vm_factory: Callable) -> Dict[str, Any]:
        """Execute single task (for multiprocessing)"""
        try:
            vm = vm_factory()
            
            if input_data:
                vm.memory[:len(input_data)] = input_data
            
            vm.load_program(program)
            
            start_time = time.time()
            vm.run()
            end_time = time.time()
            
            return {
                'success': True,
                'execution_time': end_time - start_time,
                'final_registers': vm.registers.copy(),
                'output': getattr(vm, 'output_buffer', []),
                'instructions_executed': getattr(vm, 'instructions_executed', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0.0
            }
    
    def _resolve_task_dependencies(self) -> List[str]:
        """Resolve task dependencies and return execution order"""
        # Topological sort for dependency resolution
        in_degree = {task_id: 0 for task_id in self.tasks}
        
        # Calculate in-degrees
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id in in_degree:
                    in_degree[task_id] += 1
        
        # Queue tasks with no dependencies
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            # Sort by priority
            queue.sort(key=lambda tid: self.tasks[tid].priority, reverse=True)
            current = queue.pop(0)
            execution_order.append(current)
            
            # Update dependent tasks
            if current in self.task_dependencies:
                for dependent in self.task_dependencies[current]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # Check for circular dependencies
        if len(execution_order) != len(self.tasks):
            remaining = set(self.tasks.keys()) - set(execution_order)
            raise RuntimeError(f"Circular dependencies detected in tasks: {remaining}")
        
        return execution_order
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Wait for specific task completion"""
        start_time = time.time()
        
        while task_id not in self.completed_tasks and task_id not in self.failed_tasks:
            if timeout and (time.time() - start_time) >= timeout:
                return None
            
            time.sleep(0.1)  # Small delay
        
        return self.completed_tasks.get(task_id) or self.failed_tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        if task_id not in self.tasks:
            return {'error': 'Task not found'}
        
        task = self.tasks[task_id]
        
        if task_id in self.completed_tasks:
            status = 'completed'
            result = self.completed_tasks[task_id]
        elif task_id in self.failed_tasks:
            status = 'failed'
            result = self.failed_tasks[task_id]
        else:
            status = 'pending'
            result = None
        
        return {
            'task_id': task_id,
            'status': status,
            'priority': task.priority,
            'dependencies': task.dependencies,
            'memory_requirements': task.memory_requirements,
            'result': result
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_tasks = self.execution_stats['total_tasks']
        completed = self.execution_stats['completed_tasks']
        failed = self.execution_stats['failed_tasks']
        
        success_rate = completed / total_tasks if total_tasks > 0 else 0
        avg_execution_time = (self.execution_stats['total_execution_time'] / 
                            max(1, completed + failed))
        
        return {
            **self.execution_stats,
            'success_rate': success_rate,
            'average_execution_time': avg_execution_time,
            'pending_tasks': total_tasks - completed - failed,
            'thread_manager_stats': self.thread_manager.get_threading_statistics()
        }
    
    def clear_completed_tasks(self):
        """Clear completed tasks to free memory"""
        self.completed_tasks.clear()
        self.failed_tasks.clear()
    
    def shutdown(self):
        """Shutdown executor"""
        self.thread_manager.shutdown()
        
        if self.process_pool:
            self.process_pool.close()
            self.process_pool.join()