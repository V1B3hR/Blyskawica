"""
Enhanced Error Handling (error codes, request IDs)
"""

import logging
from typing import Any
from datetime import datetime
import uuid


class ErrorHandler:
    """Enhanced error handling with codes and tracking"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.api.error_handler")
        self._initialize_logger()
        self.error_log: list[dict[str, Any]] = []

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [ErrorHandler] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def handle_error(self, error_code: str, message: str, details: dict[str, Any] = None) -> dict[str, Any]:
        """Handle an error and return formatted response"""
        request_id = str(uuid.uuid4())

        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            }
        }

        # Log error
        self.error_log.append(error_response["error"])
        self.logger.error(f"Error {error_code}: {message} (request_id: {request_id})")

        return error_response
