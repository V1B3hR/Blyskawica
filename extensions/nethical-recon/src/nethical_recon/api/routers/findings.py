"""Finding endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from nethical_recon.core.models import Severity
from nethical_recon.core.storage import get_database
from nethical_recon.core.storage.repository import FindingRepository, ToolRunRepository

from ..auth import User, require_read
from ..models import FindingResponse, PaginatedResponse

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("", response_model=PaginatedResponse)
async def list_findings(
    _current_user: Annotated[User, Depends(require_read)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    severity: Severity | None = Query(None, description="Filter by severity"),
    run_id: UUID | None = Query(None, description="Filter by tool run ID"),
    job_id: UUID | None = Query(None, description="Filter by job ID"),
    tag: str | None = Query(None, description="Filter by tag"),
    tool: str | None = Query(None, description="Filter by tool name"),
    since: datetime | None = Query(None, description="Filter findings discovered after this timestamp"),
):
    """List findings with extensive filtering options."""
    db = get_database()
    with db.session() as session:
        finding_repo = FindingRepository(session)
        tool_repo = ToolRunRepository(session)

        # Get findings based on filters
        if run_id:
            findings = finding_repo.get_by_run(run_id)
        elif job_id:
            # Get all tool runs for the job
            tool_runs = tool_repo.get_by_job(job_id)
            findings = []
            for run in tool_runs:
                findings.extend(finding_repo.get_by_run(run.id))
        else:
            findings = finding_repo.get_all()

        # Apply additional filters
        if severity:
            findings = [f for f in findings if f.severity == severity]

        if tag:
            findings = [f for f in findings if tag in f.tags]

        if tool:
            # Need to lookup tool runs to filter by tool name
            tool_run_ids = set()
            if run_id:
                tool_runs = [tool_repo.get_by_id(run_id)]
            elif job_id:
                tool_runs = tool_repo.get_by_job(job_id)
            else:
                tool_runs = tool_repo.get_all()

            tool_run_ids = {run.id for run in tool_runs if run.tool_name == tool}
            findings = [f for f in findings if f.run_id in tool_run_ids]

        if since:
            findings = [f for f in findings if f.discovered_at >= since]

        # Sort by severity (descending) then discovered_at (descending)
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        findings = sorted(findings, key=lambda f: (severity_order.get(f.severity, 999), -f.discovered_at.timestamp()))

        # Pagination
        total = len(findings)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_findings = findings[start:end]

        return PaginatedResponse(
            items=[FindingResponse.model_validate(f) for f in paginated_findings],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: UUID,
    _current_user: Annotated[User, Depends(require_read)],
):
    """Get a specific finding by ID."""
    db = get_database()
    with db.session() as session:
        repo = FindingRepository(session)
        finding = repo.get_by_id(finding_id)

        if not finding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Finding with ID '{finding_id}' not found",
            )

        return FindingResponse.model_validate(finding)
