"""Report generation endpoints."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from nethical_recon.core.storage import get_database
from nethical_recon.core.storage.repository import (
    FindingRepository,
    ScanJobRepository,
    TargetRepository,
    ToolRunRepository,
)

from ..auth import User, require_read
from ..models import FindingResponse, ReportResponse, ToolRunResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{job_id}", response_model=ReportResponse)
async def get_job_report(
    job_id: UUID,
    _current_user: Annotated[User, Depends(require_read)],
):
    """Generate and retrieve a comprehensive report for a job."""
    db = get_database()
    with db.session() as session:
        job_repo = ScanJobRepository(session)
        target_repo = TargetRepository(session)
        tool_repo = ToolRunRepository(session)
        finding_repo = FindingRepository(session)

        # Get job
        job = job_repo.get_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID '{job_id}' not found",
            )

        # Get target
        target = target_repo.get_by_id(job.target_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target with ID '{job.target_id}' not found",
            )

        # Get tool runs
        tool_runs = tool_repo.get_by_job(job_id)

        # Get all findings
        all_findings = []
        for run in tool_runs:
            findings = finding_repo.get_by_run(run.id)
            all_findings.extend(findings)

        # Count findings by severity
        findings_by_severity = {}
        for finding in all_findings:
            severity = finding.severity.value
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

        return ReportResponse(
            job_id=job.id,
            job_name=job.name,
            target=target.value,
            generated_at=datetime.now(timezone.utc),
            tools=job.tools,
            findings_count=len(all_findings),
            findings_by_severity=findings_by_severity,
            findings=[FindingResponse.model_validate(f) for f in all_findings],
            tool_runs=[ToolRunResponse.model_validate(r) for r in tool_runs],
        )
