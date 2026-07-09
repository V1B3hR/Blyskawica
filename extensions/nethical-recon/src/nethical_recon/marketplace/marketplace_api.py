"""
Marketplace API - REST API for marketplace operations

Provides endpoints for browsing, submitting, and managing marketplace plugins.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.integration.plugin_registry import ExtensionInfo, PluginRegistry

from .approval import ApprovalWorkflow, ReviewCheckType, SubmissionStatus


class PluginSubmissionRequest(BaseModel):
    """Request to submit plugin"""

    plugin_name: str
    plugin_version: str
    author: str
    source_url: str
    documentation_url: str
    changelog: str = ""


class ReviewRequest(BaseModel):
    """Request to review plugin"""

    check_type: str
    passed: bool
    notes: str = ""
    reviewer: str = ""


class MarketplaceAPI:
    """
    Marketplace API for public plugin management.

    Provides endpoints for:
    - Browsing plugins
    - Submitting new plugins
    - Reviewing and approving plugins
    - Managing plugin lifecycle
    """

    def __init__(self, registry: PluginRegistry, workflow: ApprovalWorkflow):
        self.router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])
        self.registry = registry
        self.workflow = workflow
        self._register_routes()

    def _register_routes(self):
        """Register API routes"""

        @self.router.get("/plugins", response_model=List[ExtensionInfo])
        async def list_plugins(
            extension_type: Optional[str] = None,
            approved_only: bool = True,
            search: Optional[str] = None,
            limit: int = Query(50, le=100),
        ):
            """List marketplace plugins"""
            # Get extensions from registry
            extensions = self.registry.list_extensions()

            # Filter by type
            if extension_type:
                from nethical_recon.integration.plugin_registry import ExtensionType

                try:
                    ext_type = ExtensionType(extension_type)
                    extensions = [e for e in extensions if e.metadata and e.metadata.extension_type == ext_type]
                except ValueError:
                    pass

            # Filter by approval status
            if approved_only:
                from nethical_recon.integration.plugin_registry import ExtensionStatus

                extensions = [e for e in extensions if e.status == ExtensionStatus.APPROVED]

            # Search
            if search:
                search_lower = search.lower()
                extensions = [
                    e
                    for e in extensions
                    if e.metadata
                    and (search_lower in e.metadata.name.lower() or search_lower in e.metadata.description.lower())
                ]

            # Limit results
            extensions = extensions[:limit]

            # Convert to response format
            return [
                ExtensionInfo(
                    id=str(e.id),
                    name=e.metadata.name if e.metadata else "Unknown",
                    version=e.metadata.version if e.metadata else "0.0.0",
                    author=e.metadata.author if e.metadata else "Unknown",
                    description=e.metadata.description if e.metadata else "",
                    extension_type=e.metadata.extension_type.value if e.metadata else "unknown",
                    status=e.status.value,
                    tags=e.metadata.tags if e.metadata else [],
                    downloads=e.downloads,
                    rating=e.rating,
                    created_at=e.created_at,
                    updated_at=e.updated_at,
                )
                for e in extensions
            ]

        @self.router.post("/plugins/submit")
        async def submit_plugin(request: PluginSubmissionRequest):
            """Submit new plugin for review"""
            submission_id = self.workflow.submit_plugin(
                plugin_name=request.plugin_name,
                plugin_version=request.plugin_version,
                author=request.author,
                source_url=request.source_url,
                documentation_url=request.documentation_url,
                changelog=request.changelog,
            )

            # Automatically run security scan
            self.workflow.run_security_scan(submission_id)

            return {
                "submission_id": str(submission_id),
                "status": "submitted",
                "message": "Plugin submitted for review. Security scan initiated.",
            }

        @self.router.get("/submissions")
        async def list_submissions(status: Optional[str] = None):
            """List plugin submissions"""
            if status:
                try:
                    status_enum = SubmissionStatus(status)
                    submissions = self.workflow.list_submissions(status_enum)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
            else:
                submissions = self.workflow.list_submissions()

            return [
                {
                    "submission_id": str(s.submission_id),
                    "plugin_name": s.plugin_name,
                    "plugin_version": s.plugin_version,
                    "author": s.author,
                    "status": s.status.value,
                    "submitted_at": s.submitted_at.isoformat(),
                    "checks_count": len(s.checks),
                    "checks_passed": sum(1 for c in s.checks if c.passed),
                }
                for s in submissions
            ]

        @self.router.get("/submissions/{submission_id}")
        async def get_submission(submission_id: str):
            """Get submission details"""
            from uuid import UUID

            try:
                sub_uuid = UUID(submission_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid submission ID")

            submission = self.workflow.get_submission(sub_uuid)
            if not submission:
                raise HTTPException(status_code=404, detail="Submission not found")

            return {
                "submission_id": str(submission.submission_id),
                "plugin_id": str(submission.plugin_id),
                "plugin_name": submission.plugin_name,
                "plugin_version": submission.plugin_version,
                "author": submission.author,
                "status": submission.status.value,
                "submitted_at": submission.submitted_at.isoformat(),
                "source_url": submission.source_url,
                "documentation_url": submission.documentation_url,
                "changelog": submission.changelog,
                "checks": [
                    {
                        "type": c.check_type.value,
                        "passed": c.passed,
                        "notes": c.notes,
                        "checked_at": c.checked_at.isoformat(),
                        "reviewer": c.reviewer,
                    }
                    for c in submission.checks
                ],
                "reviewer_notes": submission.reviewer_notes,
            }

        @self.router.post("/submissions/{submission_id}/review")
        async def add_review(submission_id: str, review: ReviewRequest):
            """Add review check to submission"""
            from uuid import UUID

            try:
                sub_uuid = UUID(submission_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid submission ID")

            try:
                check_type = ReviewCheckType(review.check_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid check type: {review.check_type}")

            self.workflow.add_review_check(
                sub_uuid,
                check_type,
                review.passed,
                review.notes,
                review.reviewer,
            )

            return {"status": "review_added", "submission_id": submission_id}

        @self.router.post("/submissions/{submission_id}/approve")
        async def approve_submission(submission_id: str, reviewer: str, notes: str = ""):
            """Approve plugin submission"""
            from uuid import UUID

            try:
                sub_uuid = UUID(submission_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid submission ID")

            try:
                self.workflow.approve(sub_uuid, reviewer, notes)
                return {"status": "approved", "submission_id": submission_id}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.post("/submissions/{submission_id}/reject")
        async def reject_submission(submission_id: str, reviewer: str, reason: str):
            """Reject plugin submission"""
            from uuid import UUID

            try:
                sub_uuid = UUID(submission_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid submission ID")

            self.workflow.reject(sub_uuid, reviewer, reason)
            return {"status": "rejected", "submission_id": submission_id}

        @self.router.post("/submissions/{submission_id}/publish")
        async def publish_plugin(submission_id: str):
            """Publish approved plugin to marketplace"""
            from uuid import UUID

            try:
                sub_uuid = UUID(submission_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid submission ID")

            try:
                self.workflow.publish(sub_uuid)
                return {"status": "published", "submission_id": submission_id}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.get("/stats")
        async def get_marketplace_stats():
            """Get marketplace statistics"""
            all_submissions = self.workflow.list_submissions()
            published = self.workflow.get_published_plugins()

            return {
                "total_plugins": len(published),
                "total_submissions": len(all_submissions),
                "pending_review": len(self.workflow.get_pending_reviews()),
                "approved_pending_publish": len(self.workflow.get_approved_plugins()),
                "status_breakdown": {
                    status.value: len(self.workflow.list_submissions(status)) for status in SubmissionStatus
                },
            }

    def get_router(self) -> APIRouter:
        """Get configured router"""
        return self.router
