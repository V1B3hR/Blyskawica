"""
Base Plugin Interface for Reconnaissance Tools

Defines the interface that all tool adapters must implement
for consistent integration with Nethical Recon.
"""

import logging
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from nethical_recon.core.models import Evidence, EvidenceType, Finding


class ToolPlugin(ABC):
    """
    Base class for all reconnaissance tool plugins.

    Each plugin must implement:
    - validate_target: Check if target is valid for this tool
    - build_command: Build command line arguments
    - run: Execute the tool
    - parse_output: Parse tool output
    - to_findings: Convert parsed output to normalized Findings
    """

    def __init__(self, tool_name: str, tool_path: str | None = None):
        """
        Initialize plugin.

        Args:
            tool_name: Name of the tool (e.g., "masscan", "nuclei")
            tool_path: Path to tool binary (if None, assumes in PATH)
        """
        self.tool_name = tool_name
        self.tool_path = tool_path or tool_name
        self.logger = logging.getLogger(f"{__name__}.{tool_name}")

    @abstractmethod
    def validate_target(self, target: str) -> tuple[bool, str]:
        """
        Validate if target is appropriate for this tool.

        Args:
            target: Target specification (IP, domain, URL, etc.)

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    def build_command(self, target: str, output_path: Path, options: dict[str, Any] | None = None) -> list[str]:
        """
        Build command line arguments for tool execution.

        Args:
            target: Target specification
            output_path: Path for output file
            options: Additional tool-specific options

        Returns:
            List of command arguments
        """
        pass

    def run(
        self, target: str, run_id: UUID, output_dir: Path, options: dict[str, Any] | None = None, timeout: int = 300
    ) -> tuple[Evidence, int]:
        """
        Execute the tool and capture output.

        Args:
            target: Target specification
            run_id: Tool run ID
            output_dir: Directory for output files
            options: Tool-specific options
            timeout: Execution timeout in seconds

        Returns:
            Tuple of (Evidence object, return_code)
        """
        # Validate target
        is_valid, error_msg = self.validate_target(target)
        if not is_valid:
            raise ValueError(f"Invalid target for {self.tool_name}: {error_msg}")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build output path
        output_file = output_dir / f"{self.tool_name}_{run_id}.json"

        # Build command
        cmd = self.build_command(target, output_file, options)

        self.logger.info(f"Executing {self.tool_name}: {' '.join(cmd)}")

        # Execute tool
        start_time = datetime.utcnow()
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True)
            return_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr

        except subprocess.TimeoutExpired:
            self.logger.error(f"{self.tool_name} execution timed out after {timeout}s")
            return_code = -1
            stdout = ""
            stderr = f"Execution timed out after {timeout} seconds"

        except Exception as e:
            self.logger.error(f"{self.tool_name} execution failed: {e}")
            return_code = -1
            stdout = ""
            stderr = str(e)

        end_time = datetime.utcnow()

        # Read output file if it exists
        output_content = ""
        if output_file.exists():
            output_content = output_file.read_text()

        # Create evidence
        evidence = Evidence(
            id=uuid4(),
            run_id=run_id,
            type=EvidenceType.TOOL_OUTPUT,
            tool_name=self.tool_name,
            tool_version=self.get_tool_version(),
            command_line=" ".join(cmd),
            file_path=str(output_file),
            content=output_content or stdout,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            metadata={
                "target": target,
                "duration_seconds": (end_time - start_time).total_seconds(),
                "output_size_bytes": len(output_content or stdout),
            },
        )

        return evidence, return_code

    @abstractmethod
    def parse_output(self, content: str) -> dict[str, Any]:
        """
        Parse tool output into structured data.

        Args:
            content: Raw tool output

        Returns:
            Parsed data dictionary
        """
        pass

    @abstractmethod
    def to_findings(self, parsed_data: dict[str, Any], run_id: UUID, evidence_id: UUID) -> list[Finding]:
        """
        Convert parsed data to normalized Finding objects.

        Args:
            parsed_data: Parsed tool output
            run_id: Tool run ID
            evidence_id: Evidence ID

        Returns:
            List of Finding objects
        """
        pass

    def get_tool_version(self) -> str:
        """
        Get tool version.

        Returns:
            Version string or "unknown"
        """
        try:
            result = subprocess.run([self.tool_path, "--version"], capture_output=True, timeout=5, text=True)
            # Extract version from output (varies by tool)
            output = result.stdout + result.stderr
            return output.strip().split("\n")[0][:100]  # First line, max 100 chars
        except Exception as e:
            self.logger.debug(f"Could not get {self.tool_name} version: {e}")
            return "unknown"

    def is_installed(self) -> bool:
        """
        Check if tool is installed and accessible.

        Returns:
            True if tool is available
        """
        try:
            subprocess.run([self.tool_path, "--help"], capture_output=True, timeout=5)
            return True
        except Exception:
            return False
