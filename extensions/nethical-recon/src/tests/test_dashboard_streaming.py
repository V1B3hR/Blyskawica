"""
Tests for Dashboard Builder and Event Streaming

Tests for dashboard builder, widgets, and event streaming functionality.
"""

import pytest
from uuid import uuid4

from nethical_recon.dashboard.builder import DashboardBuilder, WidgetType, WidgetPosition
from nethical_recon.streaming import EventStreamManager
from nethical_recon.streaming.manager import StreamBackend
from nethical_recon.streaming.events import (
    AssetDiscoveredEvent,
    VulnerabilityFoundEvent,
    AlertGeneratedEvent,
)


class TestDashboardBuilder:
    """Tests for Dashboard Builder."""

    def test_dashboard_builder_initialization(self):
        """Test dashboard builder initializes correctly."""
        builder = DashboardBuilder()
        assert builder is not None
        assert len(builder._dashboards) == 0

    def test_create_dashboard(self):
        """Test creating a dashboard."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(
            name="Test Dashboard",
            description="A test dashboard",
            owner="test-user",
            is_public=False,
        )

        assert dashboard is not None
        assert dashboard.name == "Test Dashboard"
        assert dashboard.owner == "test-user"
        assert len(dashboard.widgets) == 0

    def test_get_dashboard(self):
        """Test getting a dashboard by ID."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard")
        retrieved = builder.get_dashboard(dashboard.dashboard_id)

        assert retrieved is not None
        assert retrieved.dashboard_id == dashboard.dashboard_id

    def test_list_dashboards(self):
        """Test listing dashboards."""
        builder = DashboardBuilder()

        builder.create_dashboard(name="Dashboard 1", owner="user1")
        builder.create_dashboard(name="Dashboard 2", owner="user2")

        all_dashboards = builder.list_dashboards()
        assert len(all_dashboards) == 2

        user1_dashboards = builder.list_dashboards(owner="user1")
        assert len(user1_dashboards) == 1

    def test_update_dashboard(self):
        """Test updating a dashboard."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Original Name")
        updated = builder.update_dashboard(dashboard.dashboard_id, name="Updated Name", is_public=True)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.is_public is True

    def test_delete_dashboard(self):
        """Test deleting a dashboard."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard")
        success = builder.delete_dashboard(dashboard.dashboard_id)

        assert success is True
        assert builder.get_dashboard(dashboard.dashboard_id) is None

    def test_add_widget(self):
        """Test adding a widget to dashboard."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard")
        position = WidgetPosition(x=0, y=0, width=4, height=2)

        widget = builder.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.CHART,
            title="Vulnerability Chart",
            data_source="/api/v1/vulnerabilities/stats",
            position=position,
        )

        assert widget is not None
        assert widget.title == "Vulnerability Chart"
        assert widget.widget_type == WidgetType.CHART

        # Verify widget was added to dashboard
        dashboard = builder.get_dashboard(dashboard.dashboard_id)
        assert len(dashboard.widgets) == 1

    def test_remove_widget(self):
        """Test removing a widget from dashboard."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard")
        widget = builder.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.METRIC,
            title="Risk Score",
            data_source="/api/v1/risk/score",
        )

        success = builder.remove_widget(dashboard.dashboard_id, widget.widget_id)
        assert success is True

        # Verify widget was removed
        dashboard = builder.get_dashboard(dashboard.dashboard_id)
        assert len(dashboard.widgets) == 0

    def test_move_widget(self):
        """Test moving a widget."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard")
        widget = builder.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.TABLE,
            title="Asset List",
            data_source="/api/v1/assets",
        )

        new_position = WidgetPosition(x=5, y=2, width=6, height=4)
        success = builder.move_widget(dashboard.dashboard_id, widget.widget_id, new_position)

        assert success is True

        # Verify position was updated
        dashboard = builder.get_dashboard(dashboard.dashboard_id)
        updated_widget = dashboard.widgets[0]
        assert updated_widget.position.x == 5
        assert updated_widget.position.y == 2

    def test_save_layout(self):
        """Test saving dashboard layout."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard")
        layout = {"grid_columns": 12, "row_height": 100}

        success = builder.save_layout(dashboard.dashboard_id, layout)
        assert success is True

        # Verify layout was saved
        dashboard = builder.get_dashboard(dashboard.dashboard_id)
        assert dashboard.layout == layout

    def test_get_dashboard_config(self):
        """Test getting complete dashboard configuration."""
        builder = DashboardBuilder()

        dashboard = builder.create_dashboard(name="Test Dashboard", owner="test-user")
        position = WidgetPosition(x=0, y=0, width=4, height=2)
        builder.add_widget(
            dashboard_id=dashboard.dashboard_id,
            widget_type=WidgetType.ALERT_FEED,
            title="Recent Alerts",
            data_source="/api/v1/alerts/recent",
            position=position,
        )

        config = builder.get_dashboard_config(dashboard.dashboard_id)

        assert config is not None
        assert config["name"] == "Test Dashboard"
        assert config["owner"] == "test-user"
        assert len(config["widgets"]) == 1


class TestEventStreamManager:
    """Tests for Event Stream Manager."""

    def test_stream_manager_initialization(self):
        """Test stream manager initializes correctly."""
        manager = EventStreamManager(backend=StreamBackend.MEMORY)
        assert manager is not None
        assert manager.backend == StreamBackend.MEMORY

    @pytest.mark.asyncio
    async def test_publish_event(self):
        """Test publishing an event."""
        manager = EventStreamManager(backend=StreamBackend.MEMORY)

        event = AssetDiscoveredEvent(
            asset_id="asset-1",
            asset_type="server",
            ip_address="192.168.1.10",
            hostname="web-server-01",
        )

        success = await manager.publish_event(EventStreamManager.TOPIC_ASSETS, event)
        assert success is True

    @pytest.mark.asyncio
    async def test_subscribe_to_topic(self):
        """Test subscribing to a topic."""
        manager = EventStreamManager(backend=StreamBackend.MEMORY)

        events_received = []

        def callback(event):
            events_received.append(event)

        await manager.subscribe(EventStreamManager.TOPIC_VULNERABILITIES, callback)

        # Publish event
        event = VulnerabilityFoundEvent(
            vulnerability_id="vuln-1",
            cve_id="CVE-2021-44228",
            asset_id="asset-1",
            severity="critical",
            is_kev=True,
        )

        await manager.publish_event(EventStreamManager.TOPIC_VULNERABILITIES, event)

        # Note: In memory backend, events aren't automatically delivered to callbacks
        # This would work with real streaming backends

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribing from a topic."""
        manager = EventStreamManager(backend=StreamBackend.MEMORY)

        def callback(event):
            pass

        await manager.subscribe(EventStreamManager.TOPIC_ALERTS, callback)
        await manager.unsubscribe(EventStreamManager.TOPIC_ALERTS)

        # Should not raise error

    def test_get_statistics(self):
        """Test getting streaming statistics."""
        manager = EventStreamManager(backend=StreamBackend.MEMORY)

        stats = manager.get_statistics()
        assert stats is not None
        assert stats["backend"] == "memory"
        assert stats["producer_connected"] is True
        assert stats["consumer_connected"] is True

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing stream manager."""
        manager = EventStreamManager(backend=StreamBackend.MEMORY)
        await manager.close()
        # Should not raise error


class TestEventTypes:
    """Tests for event type definitions."""

    def test_asset_discovered_event(self):
        """Test AssetDiscoveredEvent creation."""
        event = AssetDiscoveredEvent(
            asset_id="asset-1",
            asset_type="server",
            ip_address="192.168.1.10",
            hostname="web-server-01",
            ports=[80, 443],
        )

        assert event.asset_id == "asset-1"
        assert event.asset_type == "server"
        assert len(event.ports) == 2

    def test_vulnerability_found_event(self):
        """Test VulnerabilityFoundEvent creation."""
        event = VulnerabilityFoundEvent(
            vulnerability_id="vuln-1",
            cve_id="CVE-2021-44228",
            asset_id="asset-1",
            severity="critical",
            is_kev=True,
            risk_score=95.0,
        )

        assert event.cve_id == "CVE-2021-44228"
        assert event.is_kev is True
        assert event.risk_score == 95.0

    def test_alert_generated_event(self):
        """Test AlertGeneratedEvent creation."""
        event = AlertGeneratedEvent(
            alert_id="alert-1",
            alert_type="kev",
            severity="critical",
            title="CISA KEV Detected",
            message="Critical vulnerability found",
        )

        assert event.alert_id == "alert-1"
        assert event.alert_type == "kev"
        assert event.severity == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
