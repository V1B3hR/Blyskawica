"""
Request/Response Compression
"""

import logging
import gzip


class CompressionMiddleware:
    """Handles request/response compression"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.api.compression")
        self._initialize_logger()
        self.compression_enabled = True
        self.min_size = 1024  # Compress responses > 1KB

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [Compression] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def compress_response(self, data: bytes) -> bytes:
        """Compress response data"""
        if not self.compression_enabled or len(data) < self.min_size:
            return data

        compressed = gzip.compress(data)
        ratio = len(compressed) / len(data)
        self.logger.debug(f"Compressed {len(data)} -> {len(compressed)} bytes (ratio: {ratio:.2f})")
        return compressed
