"""Tool adapters for external security tools."""

from .amass_adapter import AmassAdapter
from .base_plugin import ToolPlugin
from .ffuf_adapter import FfufAdapter
from .httpx_adapter import HttpxAdapter
from .masscan_adapter import MasscanAdapter
from .nmap_adapter import NmapAdapter
from .nuclei_adapter import NucleiAdapter

__all__ = [
    "ToolPlugin",
    "NmapAdapter",
    # Phase I additions
    "MasscanAdapter",
    "NucleiAdapter",
    "HttpxAdapter",
    "FfufAdapter",
    "AmassAdapter",
]
