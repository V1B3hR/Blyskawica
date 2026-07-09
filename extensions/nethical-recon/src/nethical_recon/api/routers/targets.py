"""Target management endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from nethical_recon.core.models import Target, TargetScope, TargetType
from nethical_recon.core.storage import get_database
from nethical_recon.core.storage.repository import TargetRepository

from ..auth import User, require_admin, require_read, require_write
from ..models import PaginatedResponse, TargetCreate, TargetResponse, TargetUpdate

router = APIRouter(prefix="/targets", tags=["targets"])


@router.post("", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    _current_user: Annotated[User, Depends(require_write)],
):
    """Create a new target."""
    db = get_database()
    with db.session() as session:
        repo = TargetRepository(session)

        # Check if target already exists
        existing = repo.get_by_value(target_data.value)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Target with value '{target_data.value}' already exists",
            )

        # Create target
        target = Target(
            value=target_data.value,
            type=target_data.type,
            scope=target_data.scope,
            description=target_data.description,
            tags=target_data.tags,
        )
        target = repo.create(target)
        session.commit()

        return TargetResponse.model_validate(target)


@router.get("", response_model=PaginatedResponse)
async def list_targets(
    _current_user: Annotated[User, Depends(require_read)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    scope: TargetScope | None = Query(None, description="Filter by scope"),
    type: TargetType | None = Query(None, description="Filter by type"),
):
    """List targets with optional filtering and pagination."""
    db = get_database()
    with db.session() as session:
        repo = TargetRepository(session)

        # Get all targets (filtering logic would go here)
        targets = repo.get_all()

        # Apply filters
        if scope:
            targets = [t for t in targets if t.scope == scope]
        if type:
            targets = [t for t in targets if t.type == type]

        # Pagination
        total = len(targets)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_targets = targets[start:end]

        return PaginatedResponse(
            items=[TargetResponse.model_validate(t) for t in paginated_targets],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: UUID,
    _current_user: Annotated[User, Depends(require_read)],
):
    """Get a specific target by ID."""
    db = get_database()
    with db.session() as session:
        repo = TargetRepository(session)
        target = repo.get_by_id(target_id)

        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target with ID '{target_id}' not found",
            )

        return TargetResponse.model_validate(target)


@router.patch("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: UUID,
    target_data: TargetUpdate,
    _current_user: Annotated[User, Depends(require_write)],
):
    """Update a target."""
    db = get_database()
    with db.session() as session:
        repo = TargetRepository(session)
        target = repo.get_by_id(target_id)

        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target with ID '{target_id}' not found",
            )

        # Update fields
        updates = {}
        if target_data.scope is not None:
            updates["scope"] = target_data.scope
        if target_data.description is not None:
            updates["description"] = target_data.description
        if target_data.tags is not None:
            updates["tags"] = target_data.tags

        target = repo.update(target_id, updates)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to update target with ID '{target_id}'",
            )
        session.commit()

        return TargetResponse.model_validate(target)


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: UUID,
    _current_user: Annotated[User, Depends(require_admin)],
):
    """Delete a target (admin only)."""
    db = get_database()
    with db.session() as session:
        repo = TargetRepository(session)
        target = repo.get_by_id(target_id)

        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target with ID '{target_id}' not found",
            )

        repo.delete(target_id)
        session.commit()
