"""
Dashboard API - FastAPI endpoints for web UI

Provides REST API for dashboard frontend to access monitoring data,
graphs, timelines, and reports.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.core.storage import get_db_session
from nethical_recon.core.storage.repository import (
    FindingRepository,
    ScanJobRepository,
    TargetRepository,
)


class AssetNode(BaseModel):
    """Asset node for graph visualization"""

    id: str
    type: str = Field(..., description="Type: target, host, service, technology")
    label: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssetEdge(BaseModel):
    """Asset edge for graph visualization"""

    source: str
    target: str
    relationship: str


class AssetGraph(BaseModel):
    """Complete asset graph structure"""

    nodes: List[AssetNode]
    edges: List[AssetEdge]


class TimelineEvent(BaseModel):
    """Timeline event for reconnaissance activities"""

    timestamp: datetime
    event_type: str
    description: str
    severity: str = Field(default="info")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LiveMetrics(BaseModel):
    """Live monitoring metrics"""

    total_assets: int
    active_scans: int
    recent_findings: int
    open_alerts: int
    last_updated: datetime


class DashboardAPI:
    """Dashboard API providing data for web UI"""

    def __init__(self):
        self.router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
        self._register_routes()

    def _register_routes(self):
        """Register all dashboard API routes"""

        @self.router.get("/graph", response_model=AssetGraph)
        async def get_asset_graph(
            target_id: Optional[UUID] = None,
            session=Depends(get_db_session),
        ):
            """
            Get asset graph for D3.js visualization.

            Returns nodes (targets, hosts, services, technologies) and edges
            representing relationships between assets.
            """
            target_repo = TargetRepository(session)

            nodes = []
            edges = []

            if target_id:
                target = target_repo.get_by_id(target_id)
                if not target:
                    raise HTTPException(status_code=404, detail="Target not found")
                targets = [target]
            else:
                targets = target_repo.list_all()

            # Build graph from targets and their findings
            for target in targets:
                # Add target node
                nodes.append(
                    AssetNode(
                        id=f"target-{target.id}",
                        type="target",
                        label=target.value,
                        metadata={"target_type": target.target_type.value},
                    )
                )

                # Add related findings as nodes
                finding_repo = FindingRepository(session)
                findings = finding_repo.get_by_target(target.id)

                for finding in findings[:50]:  # Limit to avoid overwhelming graph
                    finding_id = f"finding-{finding.id}"
                    nodes.append(
                        AssetNode(
                            id=finding_id,
                            type="finding",
                            label=finding.title,
                            metadata={
                                "severity": finding.severity.value,
                                "category": finding.category.value,
                            },
                        )
                    )

                    edges.append(
                        AssetEdge(
                            source=f"target-{target.id}",
                            target=finding_id,
                            relationship="has_finding",
                        )
                    )

            return AssetGraph(nodes=nodes, edges=edges)

        @self.router.get("/timeline", response_model=List[TimelineEvent])
        async def get_timeline(
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            limit: int = Query(100, le=1000),
            session=Depends(get_db_session),
        ):
            """
            Get timeline of reconnaissance activities.

            Returns chronological events including scans, findings, and alerts.
            """
            if not end_date:
                end_date = datetime.now(timezone.utc)
            if not start_date:
                start_date = end_date - timedelta(days=7)

            events = []

            # Get scan jobs in time range
            job_repo = ScanJobRepository(session)
            jobs = job_repo.list_all()

            for job in jobs:
                if job.created_at and start_date <= job.created_at <= end_date:
                    events.append(
                        TimelineEvent(
                            timestamp=job.created_at,
                            event_type="scan_started",
                            description=f"Scan job started: {job.id}",
                            metadata={"job_id": str(job.id), "status": job.status.value},
                        )
                    )

                if job.completed_at and start_date <= job.completed_at <= end_date:
                    events.append(
                        TimelineEvent(
                            timestamp=job.completed_at,
                            event_type="scan_completed",
                            description=f"Scan job completed: {job.id}",
                            severity="success" if job.status.value == "completed" else "warning",
                            metadata={"job_id": str(job.id), "status": job.status.value},
                        )
                    )

            # Sort by timestamp
            events.sort(key=lambda e: e.timestamp, reverse=True)
            return events[:limit]

        @self.router.get("/metrics/live", response_model=LiveMetrics)
        async def get_live_metrics(session=Depends(get_db_session)):
            """
            Get live monitoring metrics.

            Returns current counts of assets, active scans, findings, and alerts.
            """
            target_repo = TargetRepository(session)
            job_repo = ScanJobRepository(session)
            finding_repo = FindingRepository(session)

            total_assets = len(target_repo.list_all())

            # Count active scans
            jobs = job_repo.list_all()
            active_scans = sum(1 for job in jobs if job.status.value in ["pending", "running"])

            # Count recent findings (last 24 hours)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            all_findings = []
            for target in target_repo.list_all():
                all_findings.extend(finding_repo.get_by_target(target.id))
            recent_findings = sum(1 for f in all_findings if f.created_at and f.created_at >= cutoff)

            # Count open alerts (high/critical severity findings)
            open_alerts = sum(
                1 for f in all_findings if f.severity.value in ["high", "critical"] and f.status.value == "open"
            )

            return LiveMetrics(
                total_assets=total_assets,
                active_scans=active_scans,
                recent_findings=recent_findings,
                open_alerts=open_alerts,
                last_updated=datetime.now(timezone.utc),
            )

    def get_router(self) -> APIRouter:
        """Get the configured router"""
        return self.router
