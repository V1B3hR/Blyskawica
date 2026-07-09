"""
Enrichment Plugin API

Provides plugin infrastructure for adding custom threat intelligence sources.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from .providers import ThreatData


@dataclass
class PluginMetadata:
    """Metadata for an enrichment plugin."""

    name: str
    version: str
    author: str
    description: str
    supported_indicators: list[str]  # ip, domain, url, hash, email


class EnrichmentPlugin(ABC):
    """
    Base class for enrichment plugins.

    Custom threat intelligence sources can extend this class
    to integrate with the enrichment system.
    """

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin configuration

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def query(self, indicator: str, indicator_type: str) -> ThreatData | None:
        """
        Query threat intelligence for an indicator.

        Args:
            indicator: Indicator to query
            indicator_type: Type of indicator

        Returns:
            Threat data or None if not found
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass


class PluginRegistry:
    """
    Plugin Registry

    Manages enrichment plugins, including registration,
    discovery, and lifecycle management.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.plugins: dict[str, EnrichmentPlugin] = {}
        self.plugin_configs: dict[str, dict[str, Any]] = {}

    def register_plugin(self, plugin: EnrichmentPlugin, config: dict[str, Any] | None = None) -> bool:
        """
        Register an enrichment plugin.

        Args:
            plugin: Plugin instance
            config: Optional plugin configuration

        Returns:
            True if registration successful, False otherwise
        """
        metadata = plugin.get_metadata()
        plugin_name = metadata.name

        self.logger.info(f"Registering plugin: {plugin_name} v{metadata.version}")

        # Initialize plugin
        if not plugin.initialize(config or {}):
            self.logger.error(f"Failed to initialize plugin: {plugin_name}")
            return False

        self.plugins[plugin_name] = plugin
        self.plugin_configs[plugin_name] = config or {}

        self.logger.info(f"Plugin registered: {plugin_name}")
        return True

    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin not found: {plugin_name}")
            return False

        self.logger.info(f"Unregistering plugin: {plugin_name}")

        plugin = self.plugins[plugin_name]
        plugin.shutdown()

        del self.plugins[plugin_name]
        del self.plugin_configs[plugin_name]

        return True

    def get_plugin(self, plugin_name: str) -> EnrichmentPlugin | None:
        """Get a registered plugin by name."""
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> list[PluginMetadata]:
        """List all registered plugins."""
        return [plugin.get_metadata() for plugin in self.plugins.values()]

    def query_all_plugins(self, indicator: str, indicator_type: str) -> list[ThreatData]:
        """
        Query all registered plugins for threat intelligence.

        Args:
            indicator: Indicator to query
            indicator_type: Type of indicator

        Returns:
            List of threat data from all plugins
        """
        self.logger.info(f"Querying all plugins for {indicator_type}: {indicator}")
        results = []

        for plugin_name, plugin in self.plugins.items():
            try:
                metadata = plugin.get_metadata()
                if indicator_type in metadata.supported_indicators:
                    threat_data = plugin.query(indicator, indicator_type)
                    if threat_data:
                        results.append(threat_data)
            except Exception as e:
                self.logger.error(f"Error querying plugin {plugin_name}: {e}")

        return results

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin with its current configuration.

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin not found: {plugin_name}")
            return False

        config = self.plugin_configs.get(plugin_name, {})
        plugin = self.plugins[plugin_name]

        # Shutdown and reinitialize
        plugin.shutdown()
        success = plugin.initialize(config)

        if not success:
            self.logger.error(f"Failed to reload plugin: {plugin_name}")
            return False

        self.logger.info(f"Plugin reloaded: {plugin_name}")
        return True


class CustomFeedPlugin(EnrichmentPlugin):
    """
    Example custom feed plugin implementation.

    Demonstrates how to create a custom threat feed plugin.
    """

    def __init__(self, name: str, query_func: Callable[[str, str], ThreatData | None]):
        self.name = name
        self.query_func = query_func
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            version="1.0.0",
            author="Custom",
            description=f"Custom threat feed: {self.name}",
            supported_indicators=["ip", "domain", "url", "hash"],
        )

    def initialize(self, config: dict[str, Any]) -> bool:
        self.logger.info(f"Initializing {self.name} plugin")
        return True

    def query(self, indicator: str, indicator_type: str) -> ThreatData | None:
        return self.query_func(indicator, indicator_type)

    def shutdown(self) -> None:
        self.logger.info(f"Shutting down {self.name} plugin")
