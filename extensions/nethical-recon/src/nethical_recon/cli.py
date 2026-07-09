"""Command line interface for nethical_recon."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="nethical",
    help="Nethical Recon - Advanced Cybersecurity Reconnaissance & Threat Hunting Platform",
    no_args_is_help=True,
)

# Job management subcommand
job_app = typer.Typer(help="Job management commands")
app.add_typer(job_app, name="job")

# API server subcommand
api_app = typer.Typer(help="API server commands")
app.add_typer(api_app, name="api")


@app.command()
def version():
    """Show version information."""
    from . import __author__, __version__

    typer.echo(f"Nethical Recon v{__version__}")
    typer.echo(f"Author: {__author__}")


@app.command()
def interactive():
    """Launch interactive mode (original interface)."""
    typer.echo("Interactive mode - Coming in Phase B")


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target to scan (domain, IP, or CIDR)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Scan a target."""
    typer.echo(f"Scan command - Target: {target}, Output: {output}")
    typer.echo("Full implementation coming in Phase B")


# Job management commands
@job_app.command("submit")
def job_submit(
    target: str = typer.Argument(..., help="Target to scan"),
    name: str = typer.Option(..., "--name", "-n", help="Job name"),
    tools: str = typer.Option("nmap", "--tools", "-t", help="Comma-separated list of tools"),
    description: str | None = typer.Option(None, "--description", "-d", help="Job description"),
):
    """Submit a new scan job to the worker queue."""
    import ipaddress

    from nethical_recon.core.models import ScanJob, Target, TargetScope, TargetType
    from nethical_recon.core.storage import init_database
    from nethical_recon.core.storage.repository import ScanJobRepository, TargetRepository
    from nethical_recon.worker.tasks import run_scan_job

    try:
        # Initialize database
        db = init_database()

        with db.session() as session:
            target_repo = TargetRepository(session)
            job_repo = ScanJobRepository(session)

            # Create or find target
            existing_target = target_repo.get_by_value(target)
            if existing_target:
                target_obj = existing_target
                typer.echo(f"Using existing target: {target_obj.id}")
            else:
                # Determine target type using proper IP validation
                target_type = TargetType.DOMAIN  # Default to domain
                try:
                    # Validate IP address and determine type
                    ipaddress.ip_address(target)
                    # Both IPv4 and IPv6 use the same IP type
                    target_type = TargetType.IP
                except ValueError:
                    # Not a valid IP, treat as domain/hostname
                    target_type = TargetType.DOMAIN

                target_obj = Target(
                    value=target,
                    type=target_type,
                    scope=TargetScope.IN_SCOPE,
                )
                target_obj = target_repo.create(target_obj)
                typer.echo(f"Created new target: {target_obj.id}")

            # Create scan job
            tool_list = [t.strip() for t in tools.split(",")]
            job = ScanJob(
                target_id=target_obj.id,
                name=name,
                description=description,
                tools=tool_list,
            )
            job = job_repo.create(job)
            session.commit()

            typer.echo(f"✓ Created job: {job.id}")
            typer.echo(f"  Target: {target}")
            typer.echo(f"  Tools: {', '.join(tool_list)}")

            # Submit to worker queue
            task = run_scan_job.delay(str(job.id))
            typer.echo("✓ Submitted to worker queue")
            typer.echo(f"  Task ID: {task.id}")
            typer.echo(f"\nUse 'nethical job status {job.id}' to check progress")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


@job_app.command("status")
def job_status(
    job_id: str = typer.Argument(..., help="Job ID to check"),
):
    """Check the status of a scan job."""
    from uuid import UUID

    from nethical_recon.core.storage import init_database
    from nethical_recon.core.storage.repository import (
        FindingRepository,
        ScanJobRepository,
        ToolRunRepository,
    )

    try:
        db = init_database()

        with db.session() as session:
            job_repo = ScanJobRepository(session)
            tool_repo = ToolRunRepository(session)
            finding_repo = FindingRepository(session)

            job = job_repo.get_by_id(UUID(job_id))
            if not job:
                typer.echo(f"Job {job_id} not found", err=True)
                raise typer.Exit(1)

            typer.echo(f"\n=== Job Status:  {job.name} ===")
            typer.echo(f"ID: {job.id}")
            typer.echo(f"Status: {job.status.value.upper()}")
            typer.echo(f"Created: {job.created_at}")
            if job.started_at:
                typer.echo(f"Started: {job.started_at}")
            if job.completed_at:
                typer.echo(f"Completed: {job.completed_at}")
            if job.error_message:
                typer.echo(f"Error: {job.error_message}")

            # Get tool runs
            tool_runs = tool_repo.get_by_job(UUID(job_id))
            if tool_runs:
                typer.echo(f"\n=== Tool Runs ({len(tool_runs)}) ===")
                for run in tool_runs:
                    typer.echo(f"\n  {run.tool_name} ({run.tool_version})")
                    typer.echo(f"    Status: {run.status.value}")
                    typer.echo(f"    Exit code: {run.exit_code}")
                    if run.duration_seconds:
                        typer.echo(f"    Duration: {run.duration_seconds:.2f}s")

                    # Get findings for this run
                    findings = finding_repo.get_by_run(run.id)
                    if findings:
                        typer.echo(f"    Findings: {len(findings)}")
                        severity_counts = {}
                        for finding in findings:
                            severity_counts[finding.severity.value] = severity_counts.get(finding.severity.value, 0) + 1
                        for severity, count in sorted(severity_counts.items()):
                            typer.echo(f"      {severity}: {count}")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


@job_app.command("list")
def job_list(
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of jobs to show"),
):
    """List recent scan jobs."""
    from sqlalchemy import select

    from nethical_recon.core.storage import init_database
    from nethical_recon.core.storage.models import ScanJobModel

    try:
        db = init_database()

        with db.session() as session:
            # Get all jobs (in production, add pagination)
            stmt = select(ScanJobModel).order_by(ScanJobModel.created_at.desc()).limit(limit)
            result = session.execute(stmt)
            jobs = result.scalars().all()

            if not jobs:
                typer.echo("No jobs found")
                return

            typer.echo(f"\n=== Recent Jobs (showing {len(jobs)}) ===\n")
            for job in jobs:
                status_emoji = {
                    "pending": "⏳",
                    "running": "🔄",
                    "completed": "✓",
                    "failed": "✗",
                    "cancelled": "⊘",
                }.get(job.status, "?")

                typer.echo(f"{status_emoji} {job.name}")
                typer.echo(f"  ID: {job.id}")
                typer.echo(f"  Status: {job.status}")
                typer.echo(f"  Created: {job.created_at}")
                typer.echo(f"  Tools: {', '.join(job.tools)}")
                typer.echo()

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


@job_app.command("logs")
def job_logs(
    job_id: str = typer.Argument(..., help="Job ID to show logs for"),
    tool: str | None = typer.Option(None, "--tool", "-t", help="Filter by tool name"),
):
    """Show logs for a scan job."""
    from uuid import UUID

    from nethical_recon.core.storage import init_database
    from nethical_recon.core.storage.repository import ToolRunRepository

    try:
        db = init_database()

        with db.session() as session:
            tool_repo = ToolRunRepository(session)

            tool_runs = tool_repo.get_by_job(UUID(job_id))
            if not tool_runs:
                typer.echo("No tool runs found for this job")
                return

            for run in tool_runs:
                if tool and run.tool_name != tool:
                    continue

                typer.echo(f"\n=== {run.tool_name} ({run.id}) ===")
                typer.echo(f"Command: {run.command}")
                typer.echo(f"Status: {run.status.value}")

                if run.stdout:
                    typer.echo("\n--- STDOUT ---")
                    typer.echo(run.stdout[:1000])  # Limit output
                    if len(run.stdout) > 1000:
                        typer.echo(f"... ({len(run.stdout) - 1000} more characters)")

                if run.stderr:
                    typer.echo("\n--- STDERR ---")
                    typer.echo(run.stderr[:1000])
                    if len(run.stderr) > 1000:
                        typer.echo(f"... ({len(run.stderr) - 1000} more characters)")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def report(job_id: str | None = typer.Argument(None, help="Job ID to generate report for")):
    """Generate reports."""
    typer.echo(f"Report generation - Job ID: {job_id}")
    typer.echo("Full implementation coming in Phase B")


# API server commands
@api_app.command("serve")
def api_serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of workers"),
):
    """Start the REST API server."""
    import uvicorn

    from nethical_recon.api import create_app
    from nethical_recon.api.config import APIConfig

    config = APIConfig(
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )

    typer.echo(f"Starting Nethical Recon API server on http://{host}:{port}")
    typer.echo(f"API documentation: http://{host}:{port}{config.api_prefix}/docs")
    typer.echo(f"ReDoc documentation: http://{host}:{port}{config.api_prefix}/redoc")
    typer.echo("")
    typer.echo("Default credentials:")
    typer.echo("  Admin: admin / admin123 (scopes: read, write, admin)")
    typer.echo("  Operator: operator / admin123 (scopes: read, write)")
    typer.echo("  Viewer: viewer / admin123 (scopes: read)")
    typer.echo("")
    typer.echo("Default API key:")
    typer.echo("  nethical_test_key_12345 (scopes: read, write)")
    typer.echo("")

    app_instance = create_app(config)

    # Run with uvicorn
    uvicorn.run(
        app_instance,
        host=host,
        port=port,
        reload=reload,
        workers=1 if reload else workers,
    )


def main(argv: list[str] | None = None) -> int:
    """Main entry point for CLI."""
    try:
        app()
        return 0
    except SystemExit as e:
        return e.code if e.code else 0
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        return 1
