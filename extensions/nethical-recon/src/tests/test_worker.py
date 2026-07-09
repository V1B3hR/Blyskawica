"""Tests for worker tasks."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest

from nethical_recon.core.models import (
    JobStatus,
    ScanJob,
    Target,
    TargetScope,
    TargetType,
)
from nethical_recon.core.storage import init_database
from nethical_recon.core.storage.repository import (
    FindingRepository,
    ScanJobRepository,
    TargetRepository,
    ToolRunRepository,
)
from nethical_recon.worker.policy import reset_policy_engine


@pytest.fixture(autouse=True)
def setup_eager_mode():
    """Set Celery to eager mode for testing."""
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
    reset_policy_engine()  # Reset policy engine before each test
    yield
    os.environ.pop("CELERY_TASK_ALWAYS_EAGER", None)


@pytest.fixture
def test_db():
    """Create a test database."""
    db = init_database()
    yield db
    # Cleanup is handled by pytest-tmp


@pytest.fixture
def test_target(test_db):
    """Create a test target."""
    with test_db.session() as session:
        repo = TargetRepository(session)
        target = Target(
            value="127.0.0.1",
            type=TargetType.IP,
            scope=TargetScope.IN_SCOPE,
        )
        target = repo.create(target)
        session.commit()
        return target


@pytest.fixture
def test_job(test_db, test_target):
    """Create a test scan job."""
    with test_db.session() as session:
        repo = ScanJobRepository(session)
        job = ScanJob(
            target_id=test_target.id,
            name="Test Job",
            tools=["nmap"],
        )
        job = repo.create(job)
        session.commit()
        return job


class TestTaskImports:
    """Test that task modules can be imported."""

    def test_import_tasks(self):
        """Test importing tasks module."""
        from nethical_recon.worker import tasks

        assert tasks is not None

    def test_import_celery_app(self):
        """Test importing celery app."""
        from nethical_recon.worker.celery_app import celery_app

        assert celery_app is not None

    def test_tasks_registered(self):
        """Test that tasks are registered with Celery."""
        from nethical_recon.worker.celery_app import celery_app

        registered_tasks = list(celery_app.tasks.keys())
        assert "nethical_recon.worker.tasks.run_scan_job" in registered_tasks
        assert "nethical_recon.worker.tasks.run_tool" in registered_tasks
        assert "nethical_recon.worker.tasks.normalize_results" in registered_tasks
        assert "nethical_recon.worker.tasks.finalize_job" in registered_tasks


class TestNormalizeResults:
    """Tests for normalize_results task."""

    def test_normalize_nmap_results(self, test_db, test_job):
        """Test normalizing nmap results."""
        from nethical_recon.core.models import ToolRun, ToolStatus
        from nethical_recon.worker.tasks import normalize_results

        # Create a tool run with nmap XML output
        nmap_xml = """<?xml version="1.0"?>
<nmaprun>
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="8.2p1"/>
      </port>
    </ports>
  </host>
</nmaprun>
"""
        run_id = uuid4()
        with test_db.session() as session:
            tool_repo = ToolRunRepository(session)
            tool_run = ToolRun(
                id=run_id,
                job_id=test_job.id,
                tool_name="nmap",
                tool_version="7.94",
                command="nmap -sV 192.168.1.1",
                status=ToolStatus.COMPLETED,
                stdout=nmap_xml,
            )
            tool_repo.create(tool_run)
            session.commit()

        # Run normalization
        result = normalize_results({}, str(run_id))

        # Check results
        assert result["run_id"] == str(run_id)
        assert result["findings_count"] > 0

        # Verify findings were saved
        with test_db.session() as session:
            finding_repo = FindingRepository(session)
            findings = finding_repo.get_by_run(run_id)
            assert len(findings) > 0


class TestGenerateReport:
    """Tests for generate_report task."""

    def test_generate_report_basic(self, test_db, test_job):
        """Test generating a basic report."""
        from nethical_recon.worker.tasks import generate_report

        # Generate report
        report = generate_report(str(test_job.id))

        # Check report structure
        assert report["job_id"] == str(test_job.id)
        assert report["job_name"] == test_job.name
        assert "target" in report
        assert "status" in report
        assert "findings" in report
        assert "total" in report["findings"]


class TestScheduledTasks:
    """Tests for scheduled tasks."""

    def test_update_baselines(self):
        """Test update_baselines task."""
        from nethical_recon.worker.tasks import update_baselines

        result = update_baselines()
        assert result["status"] == "success"

    def test_cleanup_old_results(self):
        """Test cleanup_old_results task."""
        from nethical_recon.worker.tasks import cleanup_old_results

        result = cleanup_old_results()
        assert result["status"] in ["success", "error"]
