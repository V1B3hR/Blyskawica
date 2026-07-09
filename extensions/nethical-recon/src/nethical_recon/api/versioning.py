"""
API Versioning (/api/v1, /api/v2)
"""

import logging
from typing import Any
from enum import Enum


class APIVersion(Enum):
    """Supported API versions"""

    V1 = "v1"
    V2 = "v2"


class VersionManager:
    """Manages API versioning"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.api.version")
        self._initialize_logger()
        self.current_version = APIVersion.V2
        self.supported_versions = [APIVersion.V1, APIVersion.V2]

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [APIVersion] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def is_supported(self, version: str) -> bool:
        """Check if version is supported"""
        try:
            ver = APIVersion(version)
            return ver in self.supported_versions
        except ValueError:
            return False

    def get_version_info(self) -> dict[str, Any]:
        """Get version information"""
        return {
            "current": self.current_version.value,
            "supported": [v.value for v in self.supported_versions],
            "deprecated": ["v0"],
        }
