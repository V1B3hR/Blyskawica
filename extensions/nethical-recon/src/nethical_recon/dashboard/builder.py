"""
Dashboard Builder

Composable dashboard builder allowing users to create custom dashboards
with drag-and-drop widgets.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class WidgetType(Enum):
    """Dashboard widget types."""

    CHART = "chart"
    TABLE = "table"
    METRIC = "metric"
    GRAPH = "graph"
    ALERT_FEED = "alert_feed"


@dataclass
class WidgetPosition:
    """Widget position in grid layout."""

    x: int  # Grid column (0-11 for 12-column grid)
    y: int  # Grid row
    width: int  # Width in grid columns
    height: int  # Height in grid rows


@dataclass
class Widget:
    """Base widget configuration."""

    widget_id: UUID = field(default_factory=uuid4)
    widget_type: WidgetType = WidgetType.METRIC
    title: str = ""
    position: Optional[WidgetPosition] = None
    data_source: str = ""
    refresh_interval: int = 60  # seconds
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Dashboard configuration."""

    dashboard_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    widgets: list[Widget] = field(default_factory=list)
    layout: dict[str, Any] = field(default_factory=dict)
    is_public: bool = False


class DashboardBuilder:
    """
    Dashboard Builder.

    Provides CRUD operations for creating and managing custom dashboards
    with composable widgets.

    Features:
    - Create/Read/Update/Delete dashboards
    - Add/Remove/Move widgets
    - Save/Load layout
    - Widget library
    - Real-time data binding
    """

    def __init__(self):
        """Initialize dashboard builder."""
        self._dashboards: dict[UUID, Dashboard] = {}

    def create_dashboard(
        self,
        name: str,
        description: str = "",
        owner: str = "",
        is_public: bool = False,
    ) -> Dashboard:
        """
        Create new dashboard.

        Args:
            name: Dashboard name
            description: Dashboard description
            owner: Dashboard owner
            is_public: Whether dashboard is publicly accessible

        Returns:
            Created dashboard
        """
        dashboard = Dashboard(
            name=name,
            description=description,
            owner=owner,
            is_public=is_public,
        )

        self._dashboards[dashboard.dashboard_id] = dashboard

        logger.info(f"Created dashboard: {dashboard.dashboard_id} - {name}")

        return dashboard

    def get_dashboard(self, dashboard_id: UUID) -> Optional[Dashboard]:
        """
        Get dashboard by ID.

        Args:
            dashboard_id: Dashboard identifier

        Returns:
            Dashboard if found, None otherwise
        """
        return self._dashboards.get(dashboard_id)

    def list_dashboards(self, owner: Optional[str] = None) -> list[Dashboard]:
        """
        List dashboards.

        Args:
            owner: Optional filter by owner

        Returns:
            List of dashboards
        """
        dashboards = list(self._dashboards.values())

        if owner:
            dashboards = [d for d in dashboards if d.owner == owner]

        return dashboards

    def update_dashboard(
        self,
        dashboard_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Optional[Dashboard]:
        """
        Update dashboard metadata.

        Args:
            dashboard_id: Dashboard identifier
            name: New name
            description: New description
            is_public: New public status

        Returns:
            Updated dashboard if found
        """
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None

        if name is not None:
            dashboard.name = name
        if description is not None:
            dashboard.description = description
        if is_public is not None:
            dashboard.is_public = is_public

        dashboard.updated_at = datetime.utcnow()

        logger.info(f"Updated dashboard: {dashboard_id}")

        return dashboard

    def delete_dashboard(self, dashboard_id: UUID) -> bool:
        """
        Delete dashboard.

        Args:
            dashboard_id: Dashboard identifier

        Returns:
            True if deleted, False if not found
        """
        if dashboard_id in self._dashboards:
            del self._dashboards[dashboard_id]
            logger.info(f"Deleted dashboard: {dashboard_id}")
            return True

        return False

    def add_widget(
        self,
        dashboard_id: UUID,
        widget_type: WidgetType,
        title: str,
        data_source: str,
        position: Optional[WidgetPosition] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> Optional[Widget]:
        """
        Add widget to dashboard.

        Args:
            dashboard_id: Dashboard identifier
            widget_type: Type of widget
            title: Widget title
            data_source: Data source endpoint
            position: Widget position in grid
            config: Widget configuration

        Returns:
            Created widget if dashboard found
        """
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None

        widget = Widget(
            widget_type=widget_type,
            title=title,
            data_source=data_source,
            position=position,
            config=config or {},
        )

        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.utcnow()

        logger.info(f"Added widget {widget.widget_id} to dashboard {dashboard_id}")

        return widget

    def remove_widget(self, dashboard_id: UUID, widget_id: UUID) -> bool:
        """
        Remove widget from dashboard.

        Args:
            dashboard_id: Dashboard identifier
            widget_id: Widget identifier

        Returns:
            True if removed, False if not found
        """
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False

        original_count = len(dashboard.widgets)
        dashboard.widgets = [w for w in dashboard.widgets if w.widget_id != widget_id]

        if len(dashboard.widgets) < original_count:
            dashboard.updated_at = datetime.utcnow()
            logger.info(f"Removed widget {widget_id} from dashboard {dashboard_id}")
            return True

        return False

    def move_widget(
        self,
        dashboard_id: UUID,
        widget_id: UUID,
        position: WidgetPosition,
    ) -> bool:
        """
        Move widget to new position.

        Args:
            dashboard_id: Dashboard identifier
            widget_id: Widget identifier
            position: New position

        Returns:
            True if moved, False if not found
        """
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False

        for widget in dashboard.widgets:
            if widget.widget_id == widget_id:
                widget.position = position
                dashboard.updated_at = datetime.utcnow()
                logger.info(f"Moved widget {widget_id} in dashboard {dashboard_id}")
                return True

        return False

    def save_layout(self, dashboard_id: UUID, layout: dict[str, Any]) -> bool:
        """
        Save dashboard layout.

        Args:
            dashboard_id: Dashboard identifier
            layout: Layout configuration

        Returns:
            True if saved, False if dashboard not found
        """
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False

        dashboard.layout = layout
        dashboard.updated_at = datetime.utcnow()

        logger.info(f"Saved layout for dashboard {dashboard_id}")

        return True

    def get_dashboard_config(self, dashboard_id: UUID) -> Optional[dict[str, Any]]:
        """
        Get complete dashboard configuration.

        Args:
            dashboard_id: Dashboard identifier

        Returns:
            Dashboard configuration dictionary
        """
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None

        return {
            "dashboard_id": str(dashboard.dashboard_id),
            "name": dashboard.name,
            "description": dashboard.description,
            "owner": dashboard.owner,
            "created_at": dashboard.created_at.isoformat(),
            "updated_at": dashboard.updated_at.isoformat(),
            "is_public": dashboard.is_public,
            "widgets": [
                {
                    "widget_id": str(w.widget_id),
                    "widget_type": w.widget_type.value,
                    "title": w.title,
                    "position": (
                        {
                            "x": w.position.x,
                            "y": w.position.y,
                            "width": w.position.width,
                            "height": w.position.height,
                        }
                        if w.position
                        else None
                    ),
                    "data_source": w.data_source,
                    "refresh_interval": w.refresh_interval,
                    "config": w.config,
                }
                for w in dashboard.widgets
            ],
            "layout": dashboard.layout,
        }
