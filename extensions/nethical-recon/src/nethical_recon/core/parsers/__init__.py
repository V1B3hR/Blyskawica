"""Parser interface and base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from ..models import Finding


class ParserInterface(ABC):
    """Base interface for tool output parsers."""

    @abstractmethod
    def parse(self, output: str | dict, run_id: UUID) -> list[Finding]:
        """Parse tool output and return list of findings.

        Args:
            output: Raw tool output (string or dict).
            run_id: ID of the tool run that generated this output.

        Returns:
            List of normalized Finding objects.
        """
        pass

    @abstractmethod
    def can_parse(self, tool_name: str) -> bool:
        """Check if this parser can handle the given tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            True if this parser can handle the tool.
        """
        pass


class BaseParser(ParserInterface):
    """Base parser with common functionality."""

    def __init__(self):
        """Initialize base parser."""
        self.supported_tools: list[str] = []

    def can_parse(self, tool_name: str) -> bool:
        """Check if this parser supports the tool."""
        return tool_name.lower() in [t.lower() for t in self.supported_tools]
