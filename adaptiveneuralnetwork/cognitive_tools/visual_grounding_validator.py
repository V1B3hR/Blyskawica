"""
[Module: Visual Grounding & Spatial UI Autonomy Validator for Sparkle (Tauri / Win 11)]
Modeled after Roboflow / Caniverse-Win11 UI Ground-Truth dataset structure.
Provides physical bounding box verification, viewport clipping detection,
and mathematical state synchronization between Sparkle UI DOM and Blyskawica Rust logic.
"""

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s")
logger = logging.getLogger("visual_grounding")


@dataclass
class UIBoundingBox:
    element_id: str
    element_type: str  # SLIDER, CANVAS, BADGE, TERMINAL, BUTTON, CONTAINER, OSCILLOSCOPE
    bbox: Tuple[float, float, float, float]  # (xmin, ymin, xmax, ymax) in physical window coordinates
    is_visible: bool = True
    z_index: int = 0
    rendered_value: Optional[Any] = None

    @property
    def width(self) -> float:
        return max(0.0, self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> float:
        return max(0.0, self.bbox[3] - self.bbox[1])

    @property
    def area(self) -> float:
        return self.width * self.height

    def intersection(self, other: "UIBoundingBox") -> float:
        """Calculates intersection area with another bounding box."""
        x_left = max(self.bbox[0], other.bbox[0])
        y_top = max(self.bbox[1], other.bbox[1])
        x_right = min(self.bbox[2], other.bbox[2])
        y_bottom = min(self.bbox[3], other.bbox[3])

        if x_right < x_left or y_bottom < y_top:
            return 0.0
        return (x_right - x_left) * (y_bottom - y_top)

    def iou(self, other: "UIBoundingBox") -> float:
        """Intersection over Union (IoU) metric."""
        inter = self.intersection(other)
        union = self.area + other.area - inter
        return inter / union if union > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UILayoutSnapshot:
    window_width: int
    window_height: int
    elements: Dict[str, UIBoundingBox] = field(default_factory=dict)
    fps_render_rate: float = 60.0
    timestamp: float = field(default_factory=time.time)

    def add_element(self, element: UIBoundingBox):
        self.elements[element.element_id] = element


@dataclass
class VisualHealthReport:
    is_healthy: bool
    health_score: float  # 0.0 to 1.0
    total_elements: int
    synced_elements: int
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VisualGroundingValidator:
    """
    Validates physical screen bounding boxes and verifies zero-discrepancy
    synchronization between Sparkle UI DOM and Blyskawica Core Rust state.
    """
    def __init__(self, tolerance: float = 0.005):
        self.tolerance = tolerance

    def validate_layout_geometry(self, snapshot: UILayoutSnapshot) -> List[Dict[str, Any]]:
        """
        Scans all UI bounding boxes for physical layout anomalies:
        - Viewport boundary clipping (elements cut off by window edges)
        - Degenerate zero-area boxes (failed CSS render)
        - Negative dimensions
        - Accidental occlusions / collisions between interactive controls
        """
        anomalies = []
        w_w = float(snapshot.window_width)
        w_h = float(snapshot.window_height)

        # 1. Individual geometry checks
        for elem_id, elem in snapshot.elements.items():
            if not elem.is_visible:
                continue

            xmin, ymin, xmax, ymax = elem.bbox

            # Check negative dimensions
            if xmax < xmin or ymax < ymin:
                anomalies.append({
                    "severity": "CRITICAL",
                    "type": "NEGATIVE_BBOX_DIMENSION",
                    "element_id": elem_id,
                    "message": f"Element {elem_id} posiada ujemne wymiary: {elem.bbox}"
                })
                continue

            # Check zero area
            if elem.area <= 1.0:
                anomalies.append({
                    "severity": "WARNING",
                    "type": "ZERO_AREA_ELEMENT",
                    "element_id": elem_id,
                    "message": f"Element {elem_id} ma zerową lub mikroskopijną powierzchnię ({elem.area} px)"
                })

            # Check viewport clipping
            if xmin < 0 or ymin < 0 or xmax > w_w or ymax > w_h:
                clipped_px = max(0, -xmin) + max(0, -ymin) + max(0, xmax - w_w) + max(0, ymax - w_h)
                anomalies.append({
                    "severity": "CRITICAL" if clipped_px > 10.0 else "WARNING",
                    "type": "VIEWPORT_CLIPPING_ANOMALY",
                    "element_id": elem_id,
                    "clipped_pixels": round(clipped_px, 2),
                    "message": f"Element {elem_id} wystaje poza okno aplikacji ({clipped_px:.1f}px poza oknem {w_w}x{w_h})"
                })

        # 2. Collision and Occlusion checks between interactive elements
        elements_list = [e for e in snapshot.elements.values() if e.is_visible and e.element_type != "CONTAINER"]
        for i in range(len(elements_list)):
            for j in range(i + 1, len(elements_list)):
                e1 = elements_list[i]
                e2 = elements_list[j]

                # If same z-index and high overlap (IoU > 0.3)
                if e1.z_index == e2.z_index:
                    iou_val = e1.iou(e2)
                    if iou_val > 0.25:
                        anomalies.append({
                            "severity": "WARNING",
                            "type": "UNINTENDED_CONTROL_OVERLAP",
                            "element_1": e1.element_id,
                            "element_2": e2.element_id,
                            "iou": round(iou_val, 4),
                            "message": f"Nieoczekiwana kolizja kontrolek {e1.element_id} i {e2.element_id} (IoU: {iou_val:.2f})"
                        })

        return anomalies

    def validate_state_synchronization(
        self, snapshot: UILayoutSnapshot, rust_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Cross-validates rendered DOM values with internal Rust/Python logic state.
        Detects silent UI freezes (e.g. WebView2 process throttled by Win 11).
        """
        anomalies = []

        for elem_id, elem in snapshot.elements.items():
            if elem.rendered_value is None:
                continue

            # Case: Neurochemistry slider verification
            if elem_id in rust_state:
                expected_val = rust_state[elem_id]
                rendered_val = elem.rendered_value

                if isinstance(expected_val, (int, float)) and isinstance(rendered_val, (int, float)):
                    diff = abs(float(expected_val) - float(rendered_val))
                    if diff > self.tolerance:
                        anomalies.append({
                            "severity": "CRITICAL",
                            "type": "STATE_DESYNC_HARD_ANOMALY",
                            "element_id": elem_id,
                            "expected_rust_state": expected_val,
                            "rendered_ui_state": rendered_val,
                            "delta": round(diff, 6),
                            "message": f"Desynchronizacja stanu {elem_id}: UI renderuje {rendered_val}, podczas gdy Rust ma {expected_val} (Delta: {diff:.4f})"
                        })
                elif str(expected_val) != str(rendered_val):
                    anomalies.append({
                        "severity": "WARNING",
                        "type": "STATE_MISMATCH_STRING",
                        "element_id": elem_id,
                        "expected_rust_state": str(expected_val),
                        "rendered_ui_state": str(rendered_val),
                        "message": f"Niezgodność tekstu {elem_id}: UI='{rendered_val}', Rust='{expected_val}'"
                    })

        return anomalies

    def audit_visual_health(
        self, snapshot: UILayoutSnapshot, rust_state: Dict[str, Any]
    ) -> VisualHealthReport:
        """
        Performs full visual autonomy audit (Geometry + State Sync + Frame rate health).
        """
        geo_anomalies = self.validate_layout_geometry(snapshot)
        state_anomalies = self.validate_state_synchronization(snapshot, rust_state)
        all_anomalies = geo_anomalies + state_anomalies

        # Check render loop health (FPS)
        if snapshot.fps_render_rate < 20.0:
            all_anomalies.append({
                "severity": "CRITICAL",
                "type": "RENDER_LOOP_STARVATION",
                "fps": snapshot.fps_render_rate,
                "message": f"Pętla renderowania Sparkle zwolniła do {snapshot.fps_render_rate:.1f} FPS (potencjalne zamrożenie WebView2)"
            })

        total_elems = len(snapshot.elements)
        critical_count = sum(1 for a in all_anomalies if a.get("severity") == "CRITICAL")
        warning_count = sum(1 for a in all_anomalies if a.get("severity") == "WARNING")

        score = max(0.0, 1.0 - (critical_count * 0.35 + warning_count * 0.10))
        is_healthy = critical_count == 0 and score >= 0.80

        synced_count = total_elems - len(state_anomalies)

        return VisualHealthReport(
            is_healthy=is_healthy,
            health_score=round(score, 4),
            total_elements=total_elems,
            synced_elements=max(0, synced_count),
            anomalies=all_anomalies
        )
