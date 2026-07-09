"""Tool run endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from nethical_recon.core.storage import get_database
from nethical_recon.core.storage.repository import ToolRunRepository

from ..auth import User, require_read
from ..models import PaginatedResponse, ToolRunResponse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("", response_model=PaginatedResponse)
async def list_runs(
    _current_user: Annotated[User, Depends(require_read)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    job_id: UUID | None = Query(None, description="Filter by job ID"),
    tool_name: str | None = Query(None, description="Filter by tool name"),
):
    """List tool runs with optional filtering and pagination."""
    db = get_database()
    with db.session() as session:
        repo = ToolRunRepository(session)

        # Get runs with optional filtering
        if job_id:
            runs = repo.get_by_job(job_id)
        else:
            runs = repo.get_all()

        # Apply tool filter
        if tool_name:
            runs = [r for r in runs if r.tool_name == tool_name]

        # Sort by started_at descending
        runs = sorted(runs, key=lambda r: r.started_at or r.created_at, reverse=True)

        # Pagination
        total = len(runs)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_runs = runs[start:end]

        return PaginatedResponse(
            items=[ToolRunResponse.model_validate(r) for r in paginated_runs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )


@router.get("/{run_id}", response_model=ToolRunResponse)
async def get_run(
    run_id: UUID,
    _current_user: Annotated[User, Depends(require_read)],
):
    """Get a specific tool run by ID."""
    db = get_database()
    with db.session() as session:
        repo = ToolRunRepository(session)
        run = repo.get_by_id(run_id)

        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool run with ID '{run_id}' not found",
            )

        return ToolRunResponse.model_validate(run)
