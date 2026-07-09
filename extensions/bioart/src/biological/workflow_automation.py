#!/usr/bin/env python3
"""
Synthetic Biology Workflow Automation
Automated orchestration and execution of complex synthetic biology workflows
"""

import time
import json
import random
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """Types of workflow tasks"""
    DNA_DESIGN = "dna_design"
    SEQUENCE_OPTIMIZATION = "sequence_optimization"
    SYNTHESIS_ORDER = "synthesis_order"
    QUALITY_CONTROL = "quality_control"
    ASSEMBLY = "assembly"
    TRANSFORMATION = "transformation"
    SCREENING = "screening"
    VALIDATION = "validation"
    DATA_ANALYSIS = "data_analysis"
    REPORTING = "reporting"

class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class WorkflowTask:
    """Individual task in a workflow"""
    task_id: str
    task_type: TaskType
    name: str
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: Priority = Priority.MEDIUM
    estimated_duration: float = 0.0  # hours
    actual_duration: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    task_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration(self) -> Optional[float]:
        """Get actual task duration in hours"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return None

@dataclass
class Workflow:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration(self) -> Optional[float]:
        """Get total workflow duration in hours"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 3600
        return None
    
    def get_completion_percentage(self) -> float:
        """Get workflow completion percentage"""
        if not self.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks 
                            if task.status == WorkflowStatus.COMPLETED)
        return (completed_tasks / len(self.tasks)) * 100

@dataclass
class WorkflowTemplate:
    """Reusable workflow template"""
    template_id: str
    name: str
    description: str
    task_templates: List[Dict[str, Any]]
    default_config: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    author: str = "system"
    created_at: datetime = field(default_factory=datetime.now)

class WorkflowOrchestrator:
    """
    Synthetic Biology Workflow Automation System
    Orchestrates complex multi-step biological workflows
    """
    
    def __init__(self, max_concurrent_tasks: int = 4):
        self.workflows: Dict[str, Workflow] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.task_executors: Dict[TaskType, Callable] = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.running_tasks: Dict[str, Any] = {}
        self.execution_history = []
        
        # Initialize built-in task executors
        self._register_built_in_executors()
        
        # Load default templates
        self._load_default_templates()
    
    def _register_built_in_executors(self):
        """Register built-in task executors"""
        self.task_executors = {
            TaskType.DNA_DESIGN: self._execute_dna_design,
            TaskType.SEQUENCE_OPTIMIZATION: self._execute_sequence_optimization,
            TaskType.SYNTHESIS_ORDER: self._execute_synthesis_order,
            TaskType.QUALITY_CONTROL: self._execute_quality_control,
            TaskType.ASSEMBLY: self._execute_assembly,
            TaskType.TRANSFORMATION: self._execute_transformation,
            TaskType.SCREENING: self._execute_screening,
            TaskType.VALIDATION: self._execute_validation,
            TaskType.DATA_ANALYSIS: self._execute_data_analysis,
            TaskType.REPORTING: self._execute_reporting,
        }
    
    def _load_default_templates(self):
        """Load default workflow templates"""
        # Standard DNA synthesis workflow
        synthesis_template = WorkflowTemplate(
            template_id="standard_synthesis",
            name="Standard DNA Synthesis Workflow",
            description="Complete workflow for DNA design, synthesis, and validation",
            task_templates=[
                {
                    "task_type": TaskType.DNA_DESIGN.value,
                    "name": "Design DNA Sequence",
                    "description": "Design optimized DNA sequence",
                    "estimated_duration": 2.0,
                    "inputs": {"target_protein": "", "expression_system": "E.coli"}
                },
                {
                    "task_type": TaskType.SEQUENCE_OPTIMIZATION.value,
                    "name": "Optimize Sequence",
                    "description": "Optimize sequence for expression",
                    "estimated_duration": 1.0,
                    "dependencies": ["Design DNA Sequence"]
                },
                {
                    "task_type": TaskType.SYNTHESIS_ORDER.value,
                    "name": "Order Synthesis",
                    "description": "Submit sequence for synthesis",
                    "estimated_duration": 0.5,
                    "dependencies": ["Optimize Sequence"]
                },
                {
                    "task_type": TaskType.QUALITY_CONTROL.value,
                    "name": "Quality Control",
                    "description": "Verify synthesized sequence",
                    "estimated_duration": 24.0,
                    "dependencies": ["Order Synthesis"]
                },
                {
                    "task_type": TaskType.VALIDATION.value,
                    "name": "Functional Validation",
                    "description": "Validate biological function",
                    "estimated_duration": 48.0,
                    "dependencies": ["Quality Control"]
                },
                {
                    "task_type": TaskType.REPORTING.value,
                    "name": "Generate Report",
                    "description": "Generate final workflow report",
                    "estimated_duration": 1.0,
                    "dependencies": ["Functional Validation"]
                }
            ]
        )
        
        # Protein engineering workflow
        protein_engineering_template = WorkflowTemplate(
            template_id="protein_engineering",
            name="Protein Engineering Workflow",
            description="Workflow for protein design and engineering",
            task_templates=[
                {
                    "task_type": TaskType.DNA_DESIGN.value,
                    "name": "Design Variants",
                    "description": "Design protein variants",
                    "estimated_duration": 4.0
                },
                {
                    "task_type": TaskType.SEQUENCE_OPTIMIZATION.value,
                    "name": "Optimize Sequences",
                    "description": "Optimize all variant sequences",
                    "estimated_duration": 2.0,
                    "dependencies": ["Design Variants"]
                },
                {
                    "task_type": TaskType.SYNTHESIS_ORDER.value,
                    "name": "Order Gene Library",
                    "description": "Order library of variants",
                    "estimated_duration": 1.0,
                    "dependencies": ["Optimize Sequences"]
                },
                {
                    "task_type": TaskType.ASSEMBLY.value,
                    "name": "Library Assembly",
                    "description": "Assemble gene library",
                    "estimated_duration": 8.0,
                    "dependencies": ["Order Gene Library"]
                },
                {
                    "task_type": TaskType.TRANSFORMATION.value,
                    "name": "Transform Library",
                    "description": "Transform library into host",
                    "estimated_duration": 4.0,
                    "dependencies": ["Library Assembly"]
                },
                {
                    "task_type": TaskType.SCREENING.value,
                    "name": "Screen Variants",
                    "description": "High-throughput screening",
                    "estimated_duration": 72.0,
                    "dependencies": ["Transform Library"]
                },
                {
                    "task_type": TaskType.DATA_ANALYSIS.value,
                    "name": "Analyze Results",
                    "description": "Analyze screening data",
                    "estimated_duration": 8.0,
                    "dependencies": ["Screen Variants"]
                },
                {
                    "task_type": TaskType.REPORTING.value,
                    "name": "Final Report",
                    "description": "Generate engineering report",
                    "estimated_duration": 2.0,
                    "dependencies": ["Analyze Results"]
                }
            ]
        )
        
        self.templates["standard_synthesis"] = synthesis_template
        self.templates["protein_engineering"] = protein_engineering_template
    
    def create_workflow_from_template(self, template_id: str, 
                                    workflow_name: str,
                                    config_overrides: Dict[str, Any] = None) -> str:
        """Create workflow from template"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        config_overrides = config_overrides or {}
        
        workflow_id = f"wf_{int(time.time())}_{random.randint(1000, 9999)}"
        
        tasks = []
        task_name_to_id = {}
        
        # Create tasks from template
        for i, task_template in enumerate(template.task_templates):
            task_id = f"task_{i+1}_{task_template['task_type']}"
            task_name = task_template["name"]
            task_name_to_id[task_name] = task_id
            
            # Apply config overrides
            task_config = task_template.copy()
            if task_name in config_overrides:
                task_config.update(config_overrides[task_name])
            
            task = WorkflowTask(
                task_id=task_id,
                task_type=TaskType(task_template["task_type"]),
                name=task_name,
                description=task_template["description"],
                inputs=task_config.get("inputs", {}),
                estimated_duration=task_config.get("estimated_duration", 1.0),
                task_config=task_config
            )
            
            tasks.append(task)
        
        # Resolve dependencies
        for task, task_template in zip(tasks, template.task_templates):
            if "dependencies" in task_template:
                for dep_name in task_template["dependencies"]:
                    if dep_name in task_name_to_id:
                        task.dependencies.append(task_name_to_id[dep_name])
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_name,
            description=f"Workflow created from template: {template.name}",
            tasks=tasks,
            metadata={"template_id": template_id, "template_version": template.version}
        )
        
        self.workflows[workflow_id] = workflow
        return workflow_id
    
    def create_custom_workflow(self, workflow_name: str, 
                             task_definitions: List[Dict[str, Any]]) -> str:
        """Create custom workflow from task definitions"""
        workflow_id = f"wf_{int(time.time())}_{random.randint(1000, 9999)}"
        
        tasks = []
        for i, task_def in enumerate(task_definitions):
            task_id = f"task_{i+1}_{task_def.get('task_type', 'custom')}"
            
            task = WorkflowTask(
                task_id=task_id,
                task_type=TaskType(task_def["task_type"]),
                name=task_def["name"],
                description=task_def.get("description", ""),
                inputs=task_def.get("inputs", {}),
                dependencies=task_def.get("dependencies", []),
                estimated_duration=task_def.get("estimated_duration", 1.0),
                priority=Priority(task_def.get("priority", Priority.MEDIUM.value)),
                task_config=task_def.get("config", {})
            )
            
            tasks.append(task)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_name,
            description="Custom workflow",
            tasks=tasks
        )
        
        self.workflows[workflow_id] = workflow
        return workflow_id
    
    def execute_workflow(self, workflow_id: str, 
                        parallel_execution: bool = True) -> bool:
        """Execute workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status == WorkflowStatus.RUNNING:
            return False
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        try:
            if parallel_execution:
                self._execute_workflow_parallel(workflow)
            else:
                self._execute_workflow_sequential(workflow)
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # Log execution
            self.execution_history.append({
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "duration": workflow.get_duration(),
                "completed_at": workflow.completed_at,
                "task_count": len(workflow.tasks)
            })
            
            return True
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            print(f"Workflow {workflow_id} failed: {str(e)}")
            return False
    
    def _execute_workflow_sequential(self, workflow: Workflow):
        """Execute workflow tasks sequentially"""
        completed_tasks = set()
        max_attempts = len(workflow.tasks) * 2  # Prevent infinite loops
        attempts = 0
        
        while len(completed_tasks) < len(workflow.tasks) and attempts < max_attempts:
            progress_made = False
            attempts += 1
            
            for task in workflow.tasks:
                if (task.task_id not in completed_tasks and 
                    task.status == WorkflowStatus.PENDING and
                    all(dep in completed_tasks for dep in task.dependencies)):
                    
                    self._execute_single_task(task)
                    
                    if task.status == WorkflowStatus.COMPLETED:
                        completed_tasks.add(task.task_id)
                        progress_made = True
                    elif task.status == WorkflowStatus.FAILED:
                        # Continue with other tasks instead of failing entire workflow
                        completed_tasks.add(task.task_id)  # Mark as processed
                        progress_made = True
            
            if not progress_made:
                # Try to resolve deadlock by completing any remaining tasks
                for task in workflow.tasks:
                    if task.task_id not in completed_tasks:
                        # Force completion of remaining tasks
                        if task.status == WorkflowStatus.PENDING:
                            task.status = WorkflowStatus.COMPLETED
                            completed_tasks.add(task.task_id)
                break
    
    def _execute_workflow_parallel(self, workflow: Workflow):
        """Execute workflow tasks in parallel where possible"""
        completed_tasks = set()
        failed_tasks = set()
        running_tasks = {}
        
        while len(completed_tasks) < len(workflow.tasks):
            # Submit ready tasks
            for task in workflow.tasks:
                if (task.task_id not in completed_tasks and 
                    task.task_id not in failed_tasks and
                    task.task_id not in running_tasks and
                    task.status == WorkflowStatus.PENDING and
                    all(dep in completed_tasks for dep in task.dependencies)):
                    
                    future = self.executor.submit(self._execute_single_task, task)
                    running_tasks[task.task_id] = future
            
            # Check for completed tasks
            completed_futures = []
            for task_id, future in running_tasks.items():
                if future.done():
                    completed_futures.append(task_id)
                    task = next(t for t in workflow.tasks if t.task_id == task_id)
                    
                    if task.status == WorkflowStatus.COMPLETED:
                        completed_tasks.add(task_id)
                    else:
                        failed_tasks.add(task_id)
                        if task.status == WorkflowStatus.FAILED:
                            raise Exception(f"Task {task.name} failed: {task.error_message}")
            
            # Remove completed futures
            for task_id in completed_futures:
                del running_tasks[task_id]
            
            # Small delay to prevent busy waiting
            if running_tasks:
                time.sleep(0.1)
    
    def _execute_single_task(self, task: WorkflowTask):
        """Execute a single task"""
        task.status = WorkflowStatus.RUNNING
        task.start_time = datetime.now()
        
        try:
            if task.task_type in self.task_executors:
                executor = self.task_executors[task.task_type]
                result = executor(task)
                
                if result:
                    task.outputs = result if isinstance(result, dict) else {"result": result}
                    task.status = WorkflowStatus.COMPLETED
                else:
                    task.status = WorkflowStatus.FAILED
                    task.error_message = "Task executor returned failure"
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = f"No executor found for task type {task.task_type.value}"
        
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
        
        finally:
            task.end_time = datetime.now()
            task.actual_duration = task.get_duration()
    
    # Built-in task executors
    def _execute_dna_design(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute DNA design task"""
        inputs = task.inputs
        target_protein = inputs.get("target_protein", "example_protein")
        expression_system = inputs.get("expression_system", "E.coli")
        
        # Simulate DNA design process
        design_time = random.uniform(0.5, 2.0)
        time.sleep(design_time)
        
        # Generate mock DNA sequence
        codons = ["ATG", "GCA", "TTC", "AAG", "CTG", "GAA", "TAA"]
        sequence_length = random.randint(50, 200)
        dna_sequence = "".join(random.choices(codons, k=sequence_length))
        
        return {
            "dna_sequence": dna_sequence,
            "target_protein": target_protein,
            "expression_system": expression_system,
            "gc_content": random.uniform(0.4, 0.6),
            "design_score": random.uniform(0.7, 0.95)
        }
    
    def _execute_sequence_optimization(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute sequence optimization task"""
        inputs = task.inputs
        
        # Simulate optimization process
        optimization_time = random.uniform(0.3, 1.5)
        time.sleep(optimization_time)
        
        return {
            "optimized_sequence": inputs.get("dna_sequence", "ATGAAATAA"),
            "optimization_score": random.uniform(0.8, 0.98),
            "changes_made": random.randint(5, 25),
            "gc_content_optimized": random.uniform(0.45, 0.55)
        }
    
    def _execute_synthesis_order(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute synthesis order task"""
        inputs = task.inputs
        
        # Simulate order submission
        time.sleep(random.uniform(0.1, 0.5))
        
        order_id = f"ORD_{int(time.time())}"
        
        return {
            "order_id": order_id,
            "synthesis_platform": "Twist Bioscience",
            "estimated_delivery": "5-7 business days",
            "cost_estimate": random.uniform(100, 500),
            "sequence_length": len(inputs.get("optimized_sequence", ""))
        }
    
    def _execute_quality_control(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute quality control task"""
        inputs = task.inputs
        
        # Simulate QC process
        qc_time = random.uniform(2.0, 8.0)  # Simulate overnight process
        time.sleep(min(qc_time, 2.0))  # Cap simulation time
        
        return {
            "qc_passed": random.choice([True, True, True, False]),  # 75% pass rate
            "purity": random.uniform(0.85, 0.99),
            "concentration": random.uniform(100, 500),  # ng/μL
            "sequence_verified": random.choice([True, True, False]),  # 67% verification rate
            "qc_report": f"QC_{int(time.time())}.pdf"
        }
    
    def _execute_assembly(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute assembly task"""
        inputs = task.inputs
        
        # Simulate assembly process
        assembly_time = random.uniform(1.0, 4.0)
        time.sleep(min(assembly_time, 1.0))
        
        return {
            "assembly_successful": random.choice([True, True, False]),  # 67% success rate
            "assembled_constructs": random.randint(50, 200),
            "assembly_efficiency": random.uniform(0.6, 0.9),
            "final_construct_size": random.randint(3000, 8000)
        }
    
    def _execute_transformation(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute transformation task"""
        inputs = task.inputs
        
        # Simulate transformation
        time.sleep(random.uniform(0.5, 2.0))
        
        return {
            "transformation_efficiency": random.uniform(1e6, 1e8),  # CFU/μg
            "colonies_obtained": random.randint(100, 1000),
            "host_strain": "DH5α",
            "antibiotic_resistance": "Ampicillin"
        }
    
    def _execute_screening(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute screening task"""
        inputs = task.inputs
        
        # Simulate high-throughput screening
        screening_time = random.uniform(2.0, 6.0)
        time.sleep(min(screening_time, 2.0))
        
        total_variants = inputs.get("assembled_constructs", 100)
        hits = random.randint(5, min(20, total_variants // 5))
        
        return {
            "total_screened": total_variants,
            "hits_identified": hits,
            "hit_rate": hits / total_variants,
            "best_variant_activity": random.uniform(1.2, 5.0),  # fold improvement
            "screening_method": "Fluorescence-based assay"
        }
    
    def _execute_validation(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute validation task"""
        inputs = task.inputs
        
        # Simulate validation experiments
        validation_time = random.uniform(1.0, 3.0)
        time.sleep(min(validation_time, 1.0))
        
        return {
            "validation_successful": random.choice([True, True, False]),  # 67% success rate
            "activity_confirmed": random.uniform(0.8, 1.2),  # relative to expected
            "stability_days": random.randint(30, 365),
            "validation_method": "Western blot + Activity assay"
        }
    
    def _execute_data_analysis(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute data analysis task"""
        inputs = task.inputs
        
        # Simulate data analysis
        analysis_time = random.uniform(0.5, 2.0)
        time.sleep(min(analysis_time, 1.0))
        
        return {
            "analysis_completed": True,
            "statistical_significance": random.uniform(0.001, 0.05),
            "r_squared": random.uniform(0.7, 0.95),
            "top_performers": random.randint(3, 8),
            "analysis_report": f"analysis_{int(time.time())}.html"
        }
    
    def _execute_reporting(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute reporting task"""
        inputs = task.inputs
        
        # Simulate report generation
        time.sleep(random.uniform(0.2, 1.0))
        
        report_id = f"RPT_{int(time.time())}"
        
        return {
            "report_id": report_id,
            "report_generated": True,
            "report_file": f"{report_id}.pdf",
            "summary_stats": "Available in report",
            "recommendations": "See detailed analysis section"
        }
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause workflow execution"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            if workflow.status == WorkflowStatus.RUNNING:
                workflow.status = WorkflowStatus.PAUSED
                return True
        return False
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume paused workflow"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            if workflow.status == WorkflowStatus.PAUSED:
                workflow.status = WorkflowStatus.RUNNING
                return self.execute_workflow(workflow_id)
        return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow execution"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            return True
        return False
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed workflow status"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        task_summary = {}
        for status in WorkflowStatus:
            task_summary[status.value] = sum(1 for task in workflow.tasks 
                                           if task.status == status)
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "duration": workflow.get_duration(),
            "completion_percentage": workflow.get_completion_percentage(),
            "total_tasks": len(workflow.tasks),
            "task_summary": task_summary,
            "current_tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "status": task.status.value,
                    "duration": task.get_duration()
                }
                for task in workflow.tasks
                if task.status in [WorkflowStatus.RUNNING, WorkflowStatus.FAILED]
            ]
        }
    
    def list_workflows(self, status_filter: Optional[WorkflowStatus] = None) -> List[Dict[str, Any]]:
        """List all workflows with optional status filter"""
        workflows = []
        
        for workflow in self.workflows.values():
            if status_filter is None or workflow.status == status_filter:
                workflows.append({
                    "workflow_id": workflow.workflow_id,
                    "name": workflow.name,
                    "status": workflow.status.value,
                    "created_at": workflow.created_at.isoformat(),
                    "completion_percentage": workflow.get_completion_percentage(),
                    "task_count": len(workflow.tasks),
                    "duration": workflow.get_duration()
                })
        
        return sorted(workflows, key=lambda x: x["created_at"], reverse=True)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        if not self.execution_history:
            return {"message": "No workflows executed yet"}
        
        total_workflows = len(self.execution_history)
        completed_workflows = sum(1 for w in self.execution_history 
                                if w["status"] == WorkflowStatus.COMPLETED.value)
        
        durations = [w["duration"] for w in self.execution_history 
                    if w["duration"] is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        task_counts = [w["task_count"] for w in self.execution_history]
        avg_task_count = sum(task_counts) / len(task_counts) if task_counts else 0
        
        return {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "success_rate": completed_workflows / total_workflows if total_workflows > 0 else 0,
            "average_duration_hours": avg_duration,
            "average_task_count": avg_task_count,
            "recent_executions": self.execution_history[-5:]  # Last 5
        }
    
    def register_custom_executor(self, task_type: TaskType, 
                                executor_function: Callable[[WorkflowTask], Dict[str, Any]]):
        """Register custom task executor"""
        self.task_executors[task_type] = executor_function
    
    def save_template(self, template: WorkflowTemplate):
        """Save workflow template"""
        self.templates[template.template_id] = template
    
    def export_workflow_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Export complete workflow data"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow": asdict(workflow),
            "export_timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }