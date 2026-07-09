"""
Job Orchestrator and Playbook Engine

Manages playbook execution, job dependencies, and workflow orchestration.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import UUID, uuid4


class JobStatus(str, Enum):
    """Status of orchestrated jobs"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_DEPENDENCY = "waiting_dependency"


@dataclass
class JobDependency:
    """Dependency between jobs"""

    job_id: UUID
    depends_on: List[UUID] = field(default_factory=list)
    wait_for_all: bool = True  # True: wait for all deps, False: wait for any


@dataclass
class OrchestratedJob:
    """Job managed by orchestrator"""

    id: UUID
    name: str
    playbook_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    dependencies: List[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class JobOrchestrator:
    """
    Job orchestrator managing playbook execution and dependencies.

    Handles complex workflows with job dependencies, parallel execution,
    and error recovery.
    """

    def __init__(self):
        self.jobs: Dict[UUID, OrchestratedJob] = {}
        self.dependencies: Dict[UUID, JobDependency] = {}
        self.playbook_engine: Optional["PlaybookEngine"] = None
        self._running_jobs: Set[UUID] = set()

    def set_playbook_engine(self, engine: "PlaybookEngine"):
        """Set playbook engine for job execution"""
        self.playbook_engine = engine

    def create_job(
        self,
        playbook_name: str,
        parameters: Dict[str, Any],
        dependencies: Optional[List[UUID]] = None,
        job_id: Optional[UUID] = None,
    ) -> UUID:
        """
        Create orchestrated job.

        Args:
            playbook_name: Name of playbook to execute
            parameters: Playbook parameters
            dependencies: List of job IDs this job depends on
            job_id: Optional job ID (generates new if not provided)

        Returns:
            Job ID
        """
        if job_id is None:
            job_id = uuid4()

        job = OrchestratedJob(
            id=job_id,
            name=playbook_name,
            playbook_name=playbook_name,
            parameters=parameters,
            dependencies=dependencies or [],
        )

        self.jobs[job_id] = job

        if dependencies:
            self.dependencies[job_id] = JobDependency(job_id=job_id, depends_on=dependencies)

        return job_id

    def create_workflow(self, workflow: List[Dict[str, Any]]) -> List[UUID]:
        """
        Create workflow with multiple dependent jobs.

        Args:
            workflow: List of job definitions with dependencies

        Returns:
            List of created job IDs

        Example:
            workflow = [
                {"name": "domain_recon", "params": {"domain": "example.com"}},
                {
                    "name": "port_scan",
                    "params": {"target": "example.com"},
                    "depends_on": [0],  # Index of previous job
                },
            ]
        """
        job_ids = []

        for i, job_def in enumerate(workflow):
            # Resolve dependency indices to job IDs
            deps = []
            if "depends_on" in job_def:
                for dep_idx in job_def["depends_on"]:
                    if isinstance(dep_idx, int) and 0 <= dep_idx < len(job_ids):
                        deps.append(job_ids[dep_idx])

            job_id = self.create_job(
                playbook_name=job_def["name"],
                parameters=job_def.get("params", {}),
                dependencies=deps,
            )
            job_ids.append(job_id)

        return job_ids

    async def execute_job(self, job_id: UUID) -> Any:
        """
        Execute single job.

        Args:
            job_id: Job to execute

        Returns:
            Job result
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")

        job = self.jobs[job_id]

        # Check dependencies
        if not await self._dependencies_satisfied(job_id):
            job.status = JobStatus.WAITING_DEPENDENCY
            raise RuntimeError(f"Job {job_id} dependencies not satisfied")

        if self.playbook_engine is None:
            raise RuntimeError("Playbook engine not set")

        # Execute job
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        self._running_jobs.add(job_id)

        try:
            result = await self.playbook_engine.execute_playbook(job.playbook_name, job.parameters)

            job.status = JobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.now(timezone.utc)

            return result

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now(timezone.utc)
            raise

        finally:
            self._running_jobs.discard(job_id)

    async def execute_workflow(self, job_ids: List[UUID]) -> Dict[UUID, Any]:
        """
        Execute workflow of jobs respecting dependencies.

        Args:
            job_ids: List of job IDs to execute

        Returns:
            Dictionary mapping job IDs to results
        """
        results = {}
        pending = set(job_ids)
        completed = set()

        while pending:
            # Find jobs ready to execute
            ready = []
            for job_id in pending:
                if await self._dependencies_satisfied(job_id):
                    ready.append(job_id)

            if not ready:
                # No jobs ready - check for circular dependencies
                if not self._running_jobs:
                    raise RuntimeError("Circular dependency detected or all jobs blocked")

                # Wait a bit for running jobs to complete
                await asyncio.sleep(1)
                continue

            # Execute ready jobs in parallel
            tasks = [self.execute_job(job_id) for job_id in ready]
            job_results = await asyncio.gather(*tasks, return_exceptions=True)

            for job_id, result in zip(ready, job_results):
                if isinstance(result, Exception):
                    results[job_id] = {"error": str(result)}
                else:
                    results[job_id] = result

                pending.discard(job_id)
                completed.add(job_id)

        return results

    async def _dependencies_satisfied(self, job_id: UUID) -> bool:
        """Check if job dependencies are satisfied"""
        if job_id not in self.dependencies:
            return True  # No dependencies

        dependency = self.dependencies[job_id]

        for dep_id in dependency.depends_on:
            if dep_id not in self.jobs:
                return False

            dep_job = self.jobs[dep_id]
            if dep_job.status != JobStatus.COMPLETED:
                if dependency.wait_for_all:
                    return False  # Wait for all deps to complete
                # If wait_for_any, continue checking

        return True

    def get_job_status(self, job_id: UUID) -> Optional[JobStatus]:
        """Get job status"""
        job = self.jobs.get(job_id)
        return job.status if job else None

    def cancel_job(self, job_id: UUID):
        """Cancel job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status in [JobStatus.PENDING, JobStatus.WAITING_DEPENDENCY]:
                job.status = JobStatus.CANCELLED


class PlaybookEngine:
    """
    Playbook execution engine.

    Executes registered playbooks and manages playbook registry.
    """

    def __init__(self):
        self.playbooks: Dict[str, Callable] = {}

    def register_playbook(self, name: str, playbook: Callable):
        """
        Register playbook.

        Args:
            name: Playbook name
            playbook: Async callable playbook function
        """
        self.playbooks[name] = playbook

    async def execute_playbook(self, name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute playbook by name.

        Args:
            name: Playbook name
            parameters: Playbook parameters

        Returns:
            Playbook result
        """
        if name not in self.playbooks:
            raise ValueError(f"Playbook '{name}' not found")

        playbook = self.playbooks[name]

        if asyncio.iscoroutinefunction(playbook):
            return await playbook(**parameters)
        else:
            return playbook(**parameters)

    def list_playbooks(self) -> List[str]:
        """List registered playbooks"""
        return list(self.playbooks.keys())
