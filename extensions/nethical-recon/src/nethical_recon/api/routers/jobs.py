"""Scan job management endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from nethical_recon.core.models import JobStatus, ScanJob
from nethical_recon.core.storage import get_database
from nethical_recon.core.storage.repository import FindingRepository, ScanJobRepository, ToolRunRepository
from nethical_recon.worker.tasks import run_scan_job

from ..auth import User, require_admin, require_read, require_write
from ..models import JobCreate, JobResponse, JobStatusResponse, PaginatedResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    _current_user: Annotated[User, Depends(require_write)],
):
    """Create and submit a new scan job."""
    db = get_database()
    with db.session() as session:
        job_repo = ScanJobRepository(session)

        # Create job
        job = ScanJob(
            target_id=job_data.target_id,
            name=job_data.name,
            description=job_data.description,
            tools=job_data.tools,
            config=job_data.config,
        )
        job = job_repo.create(job)
        session.commit()

        # Submit to worker queue
        try:
            run_scan_job.delay(str(job.id))
        except Exception as e:
            # If worker submission fails, update job status
            updates = {
                "status": JobStatus.FAILED,
                "error_message": f"Failed to submit to worker queue: {str(e)}",
            }
            job_repo.update(job.id, updates)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit job to worker queue: {str(e)}",
            )

        return JobResponse.model_validate(job)


@router.get("", response_model=PaginatedResponse)
async def list_jobs(
    _current_user: Annotated[User, Depends(require_read)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    status_filter: JobStatus | None = Query(None, alias="status", description="Filter by job status"),
    target_id: UUID | None = Query(None, description="Filter by target ID"),
):
    """List scan jobs with optional filtering and pagination."""
    db = get_database()
    with db.session() as session:
        job_repo = ScanJobRepository(session)

        # Get jobs with optional filtering
        if target_id:
            jobs = job_repo.get_by_target(target_id)
        else:
            jobs = job_repo.get_all()

        # Apply status filter
        if status_filter:
            jobs = [j for j in jobs if j.status == status_filter]

        # Sort by created_at descending
        jobs = sorted(jobs, key=lambda j: j.created_at, reverse=True)

        # Pagination
        total = len(jobs)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_jobs = jobs[start:end]

        return PaginatedResponse(
            items=[JobResponse.model_validate(j) for j in paginated_jobs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    _current_user: Annotated[User, Depends(require_read)],
):
    """Get a specific job by ID."""
    db = get_database()
    with db.session() as session:
        job_repo = ScanJobRepository(session)
        job = job_repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID '{job_id}' not found",
            )

        return JobResponse.model_validate(job)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    _current_user: Annotated[User, Depends(require_read)],
):
    """Get detailed status of a job including statistics."""
    db = get_database()
    with db.session() as session:
        job_repo = ScanJobRepository(session)
        tool_repo = ToolRunRepository(session)
        finding_repo = FindingRepository(session)

        job = job_repo.get_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID '{job_id}' not found",
            )

        # Get tool runs and findings
        tool_runs = tool_repo.get_by_job(job_id)
        all_findings = []
        for run in tool_runs:
            findings = finding_repo.get_by_run(run.id)
            all_findings.extend(findings)

        # Count findings by severity
        findings_by_severity = {}
        for finding in all_findings:
            severity = finding.severity.value
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

        return JobStatusResponse(
            id=job.id,
            target_id=job.target_id,
            name=job.name,
            status=job.status,
            tools=job.tools,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            tool_runs_count=len(tool_runs),
            findings_count=len(all_findings),
            findings_by_severity=findings_by_severity,
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    _current_user: Annotated[User, Depends(require_admin)],
):
    """Delete a job (admin only)."""
    db = get_database()
    with db.session() as session:
        job_repo = ScanJobRepository(session)
        job = job_repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID '{job_id}' not found",
            )

        job_repo.delete(job_id)
        session.commit()
