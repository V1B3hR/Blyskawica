"""
Base Widget Class

Abstract base class for all dashboard widgets.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseWidget(ABC):
    """
    Base class for dashboard widgets.

    All widgets must implement:
    - get_data(): Fetch widget data
    - get_schema(): Get widget configuration schema
    """

    def __init__(self, widget_id: str, title: str, config: dict[str, Any]):
        """
        Initialize base widget.

        Args:
            widget_id: Unique widget identifier
            title: Widget display title
            config: Widget configuration
        """
        self.widget_id = widget_id
        self.title = title
        self.config = config

    @abstractmethod
    async def get_data(self) -> dict[str, Any]:
        """
        Fetch widget data.

        Returns:
            Widget data dictionary
        """
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """
        Get widget configuration schema.

        Returns:
            JSON schema for widget configuration
        """
        pass

    def get_metadata(self) -> dict[str, Any]:
        """
        Get widget metadata.

        Returns:
            Widget metadata
        """
        return {
            "widget_id": self.widget_id,
            "title": self.title,
            "type": self.__class__.__name__,
            "config": self.config,
        }
