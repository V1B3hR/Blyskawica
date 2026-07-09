"""
Nethical Integration Layer

Common API for integrations with other Nethical tools.
Central scoring and decision engine.
Plugin registry and extension API.

Implements ROADMAP5.md Section IV.12: Nethical Integration Layer
"""

from .decision_engine import DecisionEngine, RiskScore, ThreatContext
from .integration_api import IntegrationAPI, ToolIntegration
from .plugin_registry import Extension, ExtensionAPI, PluginRegistry

__all__ = [
    "IntegrationAPI",
    "ToolIntegration",
    "DecisionEngine",
    "RiskScore",
    "ThreatContext",
    "PluginRegistry",
    "ExtensionAPI",
    "Extension",
]
