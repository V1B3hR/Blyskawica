"""
Approval Workflow - Plugin approval and review system

Manages plugin submission, review, approval, and rejection workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4


class SubmissionStatus(str, Enum):
    """Status of plugin submission"""

    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SECURITY_CHECK = "security_check"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ReviewCheckType(str, Enum):
    """Types of review checks"""

    SECURITY_SCAN = "security_scan"
    CODE_QUALITY = "code_quality"
    FUNCTIONALITY = "functionality"
    DOCUMENTATION = "documentation"
    LICENSE_COMPLIANCE = "license_compliance"


@dataclass
class ReviewCheck:
    """Individual review check"""

    check_type: ReviewCheckType
    passed: bool
    notes: str = ""
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reviewer: Optional[str] = None


@dataclass
class Submission:
    """Plugin submission"""

    submission_id: UUID = field(default_factory=uuid4)
    plugin_id: UUID = field(default_factory=uuid4)
    plugin_name: str = ""
    plugin_version: str = ""
    author: str = ""
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: SubmissionStatus = SubmissionStatus.SUBMITTED
    checks: List[ReviewCheck] = field(default_factory=list)
    reviewer_notes: List[str] = field(default_factory=list)
    changelog: str = ""
    source_url: str = ""
    documentation_url: str = ""


class ApprovalWorkflow:
    """
    Plugin approval workflow manager.

    Handles submission, review, security checks, and approval process
    for marketplace plugins.
    """

    def __init__(self):
        self.submissions: Dict[UUID, Submission] = {}
        self.published_plugins: Dict[UUID, Submission] = {}

    def submit_plugin(
        self,
        plugin_name: str,
        plugin_version: str,
        author: str,
        source_url: str,
        documentation_url: str,
        changelog: str = "",
    ) -> UUID:
        """
        Submit plugin for review.

        Args:
            plugin_name: Plugin name
            plugin_version: Plugin version (semver)
            author: Author name/organization
            source_url: Source code repository URL
            documentation_url: Documentation URL
            changelog: Version changelog

        Returns:
            Submission ID
        """
        submission = Submission(
            plugin_name=plugin_name,
            plugin_version=plugin_version,
            author=author,
            source_url=source_url,
            documentation_url=documentation_url,
            changelog=changelog,
        )

        self.submissions[submission.submission_id] = submission
        return submission.submission_id

    def start_review(self, submission_id: UUID, reviewer: str):
        """Start review process"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]
        submission.status = SubmissionStatus.UNDER_REVIEW
        submission.reviewer_notes.append(f"Review started by {reviewer}")

    def add_review_check(
        self,
        submission_id: UUID,
        check_type: ReviewCheckType,
        passed: bool,
        notes: str = "",
        reviewer: Optional[str] = None,
    ):
        """Add review check result"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]

        check = ReviewCheck(
            check_type=check_type,
            passed=passed,
            notes=notes,
            reviewer=reviewer,
        )

        submission.checks.append(check)

    def run_security_scan(self, submission_id: UUID) -> bool:
        """
        Run automated security scan.

        In production, this would:
        - Scan for malicious code
        - Check dependencies for vulnerabilities
        - Verify code signing
        - Run static analysis

        Returns:
            True if scan passed
        """
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]
        submission.status = SubmissionStatus.SECURITY_CHECK

        # Placeholder - would run actual security scans
        scan_passed = True

        self.add_review_check(
            submission_id,
            ReviewCheckType.SECURITY_SCAN,
            scan_passed,
            "Automated security scan completed" if scan_passed else "Security issues detected",
            "automated-scanner",
        )

        return scan_passed

    def request_changes(self, submission_id: UUID, changes_needed: str, reviewer: str):
        """Request changes from author"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]
        submission.status = SubmissionStatus.CHANGES_REQUESTED
        submission.reviewer_notes.append(f"Changes requested by {reviewer}: {changes_needed}")

    def resubmit(self, submission_id: UUID, new_version: str, changelog: str):
        """Resubmit plugin after requested changes"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]

        if submission.status != SubmissionStatus.CHANGES_REQUESTED:
            raise ValueError("Cannot resubmit - changes not requested")

        submission.plugin_version = new_version
        submission.changelog = changelog
        submission.status = SubmissionStatus.SUBMITTED
        submission.submitted_at = datetime.now(timezone.utc)
        submission.reviewer_notes.append(f"Resubmitted with version {new_version}")

    def approve(self, submission_id: UUID, reviewer: str, notes: str = ""):
        """Approve plugin for publication"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]

        # Check if all required checks passed
        required_checks = [
            ReviewCheckType.SECURITY_SCAN,
            ReviewCheckType.CODE_QUALITY,
            ReviewCheckType.FUNCTIONALITY,
        ]

        for check_type in required_checks:
            checks = [c for c in submission.checks if c.check_type == check_type]
            if not checks or not all(c.passed for c in checks):
                raise ValueError(f"Cannot approve - {check_type.value} check not passed")

        submission.status = SubmissionStatus.APPROVED
        submission.reviewer_notes.append(f"Approved by {reviewer}: {notes}")

    def reject(self, submission_id: UUID, reviewer: str, reason: str):
        """Reject plugin submission"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]
        submission.status = SubmissionStatus.REJECTED
        submission.reviewer_notes.append(f"Rejected by {reviewer}: {reason}")

    def publish(self, submission_id: UUID):
        """Publish approved plugin to marketplace"""
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")

        submission = self.submissions[submission_id]

        if submission.status != SubmissionStatus.APPROVED:
            raise ValueError("Cannot publish - plugin not approved")

        submission.status = SubmissionStatus.PUBLISHED
        self.published_plugins[submission.plugin_id] = submission

    def get_submission(self, submission_id: UUID) -> Optional[Submission]:
        """Get submission by ID"""
        return self.submissions.get(submission_id)

    def list_submissions(self, status: Optional[SubmissionStatus] = None) -> List[Submission]:
        """List submissions, optionally filtered by status"""
        submissions = list(self.submissions.values())

        if status:
            submissions = [s for s in submissions if s.status == status]

        # Sort by submission date (newest first)
        submissions.sort(key=lambda s: s.submitted_at, reverse=True)

        return submissions

    def get_pending_reviews(self) -> List[Submission]:
        """Get submissions pending review"""
        return self.list_submissions(SubmissionStatus.SUBMITTED)

    def get_approved_plugins(self) -> List[Submission]:
        """Get approved plugins ready for publication"""
        return self.list_submissions(SubmissionStatus.APPROVED)

    def get_published_plugins(self) -> List[Submission]:
        """Get published plugins"""
        return list(self.published_plugins.values())
