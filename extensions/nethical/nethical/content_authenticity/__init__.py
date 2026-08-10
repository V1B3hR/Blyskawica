"""Content Authenticity Module for Nethical.

This module provides content authenticity and provenance tracking
for AI-generated content, including watermarking and C2PA integration.
"""

from .c2pa_integration import (
    C2PAAssertion,
    C2PAIngredient,
    C2PAIntegration,
    C2PAManifest,
    C2PAVerificationResult,
    SignedManifest,
)
from .deepfake_watermark import (
    ContentMetadata,
    ContentProvenance,
    DeepfakeWatermarkingSystem,
    DisclosureLabel,
    ExtractionQuality,
    WatermarkDetectionResult,
    WatermarkedAudio,
    WatermarkedImage,
    WatermarkedVideo,
    WatermarkStrength,
)

__all__ = [
    "DeepfakeWatermarkingSystem",
    "ContentMetadata",
    "WatermarkedImage",
    "WatermarkedVideo",
    "WatermarkedAudio",
    "WatermarkDetectionResult",
    "ContentProvenance",
    "DisclosureLabel",
    "WatermarkStrength",
    "ExtractionQuality",
    "C2PAIntegration",
    "C2PAManifest",
    "C2PAVerificationResult",
    "SignedManifest",
    "C2PAAssertion",
    "C2PAIngredient",
]
