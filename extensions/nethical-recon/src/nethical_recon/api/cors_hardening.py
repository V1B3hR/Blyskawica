"""
CORS Hardening
"""

import logging
from typing import Any


class CORSHardening:
    """Enhanced CORS configuration"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.api.cors")
        self._initialize_logger()
        self.allowed_origins = ["https://app.nethical-recon.com"]
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE"]
        self.allowed_headers = ["Content-Type", "Authorization"]
        self.max_age = 3600

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [CORS] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        return origin in self.allowed_origins

    def get_cors_headers(self, origin: str) -> dict[str, str]:
        """Get CORS headers for response"""
        if not self.is_origin_allowed(origin):
            return {}

        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
            "Access-Control-Max-Age": str(self.max_age),
        }
