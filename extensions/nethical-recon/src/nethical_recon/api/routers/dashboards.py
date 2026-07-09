"""
Dashboards API Router

FastAPI router for dashboard builder endpoints including CRUD operations
for dashboards and widgets.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.dashboard.builder import DashboardBuilder, WidgetType, WidgetPosition

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboards", tags=["dashboards"])

# Initialize dashboard builder
dashboard_builder = DashboardBuilder()


# Request/Response Models


class CreateDashboardRequest(BaseModel):
    """Request to create a dashboard."""

    name: str = Field(..., description="Dashboard name")
    description: str = Field("", description="Dashboard description")
    owner: str = Field("", description="Dashboard owner")
    is_public: bool = Field(False, description="Is dashboard publicly accessible")


class UpdateDashboardRequest(BaseModel):
    """Request to update a dashboard."""

    name: Optional[str] = Field(None, description="Dashboard name")
    description: Optional[str] = Field(None, description="Dashboard description")
    is_public: Optional[bool] = Field(None, description="Is dashboard publicly accessible")


class AddWidgetRequest(BaseModel):
    """Request to add a widget to dashboard."""

    widget_type: str = Field(..., description="Widget type: chart, table, metric, graph, alert_feed")
    title: str = Field(..., description="Widget title")
    data_source: str = Field(..., description="Data source endpoint")
    position: Optional[dict[str, int]] = Field(None, description="Widget position {x, y, width, height}")
    config: dict[str, Any] = Field(default_factory=dict, description="Widget configuration")


class MoveWidgetRequest(BaseModel):
    """Request to move a widget."""

    position: dict[str, int] = Field(..., description="New position {x, y, width, height}")


class SaveLayoutRequest(BaseModel):
    """Request to save dashboard layout."""

    layout: dict[str, Any] = Field(..., description="Layout configuration")


# Dashboard CRUD Endpoints


@router.post("/create")
async def create_dashboard(request: CreateDashboardRequest):
    """Create new dashboard."""
    try:
        dashboard = dashboard_builder.create_dashboard(
            name=request.name,
            description=request.description,
            owner=request.owner,
            is_public=request.is_public,
        )

        return {
            "success": True,
            "data": {
                "dashboard_id": str(dashboard.dashboard_id),
                "name": dashboard.name,
                "created_at": dashboard.created_at.isoformat(),
            },
        }
    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_dashboards(owner: Optional[str] = Query(None, description="Filter by owner")):
    """List all dashboards."""
    try:
        dashboards = dashboard_builder.list_dashboards(owner=owner)

        return {
            "success": True,
            "data": [
                {
                    "dashboard_id": str(d.dashboard_id),
                    "name": d.name,
                    "description": d.description,
                    "owner": d.owner,
                    "widget_count": len(d.widgets),
                    "created_at": d.created_at.isoformat(),
                    "updated_at": d.updated_at.isoformat(),
                    "is_public": d.is_public,
                }
                for d in dashboards
            ],
        }
    except Exception as e:
        logger.error(f"Failed to list dashboards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: UUID):
    """Get dashboard configuration."""
    try:
        config = dashboard_builder.get_dashboard_config(dashboard_id)

        if not config:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return {"success": True, "data": config}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dashboard_id}")
async def update_dashboard(dashboard_id: UUID, request: UpdateDashboardRequest):
    """Update dashboard metadata."""
    try:
        dashboard = dashboard_builder.update_dashboard(
            dashboard_id=dashboard_id,
            name=request.name,
            description=request.description,
            is_public=request.is_public,
        )

        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return {
            "success": True,
            "data": {
                "dashboard_id": str(dashboard.dashboard_id),
                "name": dashboard.name,
                "updated_at": dashboard.updated_at.isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: UUID):
    """Delete dashboard."""
    try:
        success = dashboard_builder.delete_dashboard(dashboard_id)

        if not success:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return {"success": True, "message": "Dashboard deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Widget Management Endpoints


@router.post("/{dashboard_id}/widgets/add")
async def add_widget(dashboard_id: UUID, request: AddWidgetRequest):
    """Add widget to dashboard."""
    try:
        # Convert widget type string to enum
        try:
            widget_type = WidgetType(request.widget_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid widget type: {request.widget_type}")

        # Convert position dict to WidgetPosition if provided
        position = None
        if request.position:
            position = WidgetPosition(
                x=request.position["x"],
                y=request.position["y"],
                width=request.position["width"],
                height=request.position["height"],
            )

        widget = dashboard_builder.add_widget(
            dashboard_id=dashboard_id,
            widget_type=widget_type,
            title=request.title,
            data_source=request.data_source,
            position=position,
            config=request.config,
        )

        if not widget:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return {
            "success": True,
            "data": {
                "widget_id": str(widget.widget_id),
                "widget_type": widget.widget_type.value,
                "title": widget.title,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(dashboard_id: UUID, widget_id: UUID):
    """Remove widget from dashboard."""
    try:
        success = dashboard_builder.remove_widget(dashboard_id, widget_id)

        if not success:
            raise HTTPException(status_code=404, detail="Dashboard or widget not found")

        return {"success": True, "message": "Widget removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dashboard_id}/widgets/{widget_id}/move")
async def move_widget(dashboard_id: UUID, widget_id: UUID, request: MoveWidgetRequest):
    """Move widget to new position."""
    try:
        position = WidgetPosition(
            x=request.position["x"],
            y=request.position["y"],
            width=request.position["width"],
            height=request.position["height"],
        )

        success = dashboard_builder.move_widget(dashboard_id, widget_id, position)

        if not success:
            raise HTTPException(status_code=404, detail="Dashboard or widget not found")

        return {"success": True, "message": "Widget moved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to move widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dashboard_id}/layout")
async def save_layout(dashboard_id: UUID, request: SaveLayoutRequest):
    """Save dashboard layout."""
    try:
        success = dashboard_builder.save_layout(dashboard_id, request.layout)

        if not success:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        return {"success": True, "message": "Layout saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save layout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Widget Templates Endpoint


@router.get("/widgets/templates")
async def get_widget_templates():
    """Get available widget templates."""
    templates = [
        {
            "type": "chart",
            "name": "Vulnerability Chart",
            "description": "Displays vulnerability statistics as charts",
            "config_schema": {
                "chart_type": ["pie", "bar", "line", "donut"],
                "group_by": ["severity", "status", "asset"],
            },
        },
        {
            "type": "table",
            "name": "Vulnerability Table",
            "description": "Displays vulnerabilities in tabular format",
            "config_schema": {
                "page": "integer",
                "per_page": "integer",
                "filter_severity": ["critical", "high", "medium", "low"],
            },
        },
        {
            "type": "graph",
            "name": "Asset Map",
            "description": "Displays assets on network topology",
            "config_schema": {
                "map_type": ["network", "geographic", "logical"],
                "show_connections": "boolean",
            },
        },
        {
            "type": "metric",
            "name": "Compliance Score",
            "description": "Displays overall compliance score",
            "config_schema": {
                "frameworks": "array",
                "show_trend": "boolean",
            },
        },
        {
            "type": "metric",
            "name": "KEV Widget",
            "description": "Displays CISA KEV vulnerabilities status",
            "config_schema": {
                "show_details": "boolean",
                "max_items": "integer",
            },
        },
        {
            "type": "alert_feed",
            "name": "Alert Feed",
            "description": "Displays recent security alerts",
            "config_schema": {
                "max_items": "integer",
                "filter_severity": ["critical", "high", "medium", "low", "info"],
            },
        },
        {
            "type": "metric",
            "name": "Risk Score",
            "description": "Displays overall risk score and metrics",
            "config_schema": {
                "show_trend": "boolean",
                "show_top_risks": "boolean",
            },
        },
    ]

    return {"success": True, "data": templates}
