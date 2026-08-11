"""
Canary Detection System for Nethical

This module implements Phase 4 Canary capabilities for detecting
active reconnaissance and malicious behavior through honeypots,
tripwires, and watermarking.

Components:
- HoneypotDetector: Decoy prompts to detect active reconnaissance
- TripwireDetector: Fake API endpoints that should never be called
- WatermarkDetector: Invisible watermarks in responses

Phase 4 Objective: Early warning system for sophisticated attacks

Author: Nethical Core Team
Version: 1.0.0
"""

from .honeypot_detector import (
    Honeypot,
    HoneypotDetector,
    HoneypotType,
)
from .tripwire_detector import (
    EndpointType,
    TripwireDetector,
    TripwireEndpoint,
)
from .watermark_detector import (
    Watermark,
    WatermarkDetector,
    WatermarkType,
)

__all__ = [
    "HoneypotDetector",
    "HoneypotType",
    "Honeypot",
    "TripwireDetector",
    "EndpointType",
    "TripwireEndpoint",
    "WatermarkDetector",
    "WatermarkType",
    "Watermark",
]
