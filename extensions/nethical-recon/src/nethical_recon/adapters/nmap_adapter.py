"""Nmap tool adapter."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from nethical_recon.core.models import Evidence, EvidenceType, ToolRun, ToolStatus


class NmapAdapter:
    """Adapter for running nmap scans."""

    def __init__(self):
        """Initialize nmap adapter."""
        self.tool_name = "nmap"
        self._check_nmap_installed()

    def _check_nmap_installed(self) -> None:
        """Check if nmap is installed."""
        if not shutil.which("nmap"):
            raise RuntimeError("nmap is not installed or not in PATH")

    def get_version(self) -> str:
        """Get nmap version."""
        try:
            result = subprocess.run(
                ["nmap", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Parse version from output (e.g., "Nmap version 7.94")
            for line in result.stdout.split("\n"):
                if "version" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "version" in part.lower() and i + 1 < len(parts):
                            return parts[i + 1]
            return "unknown"
        except Exception:
            return "unknown"

    def build_command(
        self,
        target: str,
        options: dict[str, Any] | None = None,
    ) -> list[str]:
        """
        Build nmap command.

        Args:
            target: Target to scan
            options: Additional nmap options

        Returns:
            Command as list of arguments
        """
        cmd = ["nmap"]

        # Default options for safe, informative scanning
        default_options = {
            "sV": True,  # Version detection
            "sC": True,  # Default scripts
            "oX": "-",  # XML output to stdout
            "T": "3",  # Timing template (normal)
        }

        # Merge with user options
        if options:
            default_options.update(options)

        # Build command line
        for key, value in default_options.items():
            if value is True:
                cmd.append(f"-{key}")
            elif value is False:
                continue
            else:
                cmd.append(f"-{key}")
                cmd.append(str(value))

        cmd.append(target)
        return cmd

    def run(
        self,
        target: str,
        job_id: UUID,
        run_id: UUID,
        options: dict[str, Any] | None = None,
        timeout: int = 3600,
    ) -> ToolRun:
        """
        Run nmap scan.

        Args:
            target: Target to scan
            job_id: Job ID
            run_id: Tool run ID
            options: Additional nmap options
            timeout: Timeout in seconds

        Returns:
            ToolRun object with results
        """
        started_at = datetime.now(timezone.utc)
        command = self.build_command(target, options)
        version = self.get_version()

        tool_run = ToolRun(
            id=run_id,
            job_id=job_id,
            tool_name=self.tool_name,
            tool_version=version,
            command=" ".join(command),
            status=ToolStatus.RUNNING,
            started_at=started_at,
        )

        try:
            # Run nmap
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            completed_at = datetime.now(timezone.utc)
            duration = (completed_at - started_at).total_seconds()

            tool_run.exit_code = result.returncode
            tool_run.stdout = result.stdout
            tool_run.stderr = result.stderr
            tool_run.completed_at = completed_at
            tool_run.duration_seconds = duration

            if result.returncode == 0:
                tool_run.status = ToolStatus.COMPLETED
            else:
                tool_run.status = ToolStatus.FAILED

        except subprocess.TimeoutExpired:
            tool_run.status = ToolStatus.FAILED
            tool_run.stderr = f"Nmap scan timed out after {timeout} seconds"
            tool_run.completed_at = datetime.now(timezone.utc)
            tool_run.duration_seconds = (tool_run.completed_at - started_at).total_seconds()
        except Exception as e:
            tool_run.status = ToolStatus.FAILED
            tool_run.stderr = f"Error running nmap: {e}"
            tool_run.completed_at = datetime.now(timezone.utc)
            tool_run.duration_seconds = (tool_run.completed_at - started_at).total_seconds()

        return tool_run

    def save_evidence(self, tool_run: ToolRun, output_dir: Path | None = None) -> Evidence | None:
        """
        Save tool output as evidence.

        Args:
            tool_run: ToolRun with output
            output_dir: Directory to save evidence (optional)

        Returns:
            Evidence object or None
        """
        if not tool_run.stdout:
            return None

        # Generate checksums
        content_bytes = tool_run.stdout.encode("utf-8")
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        md5 = hashlib.md5(content_bytes).hexdigest()

        # Save to file if output_dir provided
        file_path = None
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / f"nmap_{tool_run.id}.xml"
            file_path.write_text(tool_run.stdout)

        evidence = Evidence(
            run_id=tool_run.id,
            type=EvidenceType.XML,
            content=tool_run.stdout,
            file_path=str(file_path) if file_path else None,
            sha256=sha256,
            md5=md5,
            captured_at=tool_run.completed_at or datetime.now(timezone.utc),
        )

        return evidence
