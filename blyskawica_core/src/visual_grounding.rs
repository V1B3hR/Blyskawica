//! [Module: Native Rust Visual Grounding & Bounding Box Spatial Engine]
//! Sub-microsecond geometry validation and state synchronization for Sparkle UI on Windows 11.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustUIBoundingBox {
    pub element_id: String,
    pub element_type: String,
    pub xmin: f32,
    pub ymin: f32,
    pub xmax: f32,
    pub ymax: f32,
    pub is_visible: bool,
    pub z_index: i32,
    pub rendered_value: Option<f32>,
}

impl RustUIBoundingBox {
    pub fn width(&self) -> f32 {
        (self.xmax - self.xmin).max(0.0)
    }

    pub fn height(&self) -> f32 {
        (self.ymax - self.ymin).max(0.0)
    }

    pub fn area(&self) -> f32 {
        self.width() * self.height()
    }

    pub fn intersection(&self, other: &Self) -> f32 {
        let x_left = self.xmin.max(other.xmin);
        let y_top = self.ymin.max(other.ymin);
        let x_right = self.xmax.min(other.xmax);
        let y_bottom = self.ymax.min(other.ymax);

        if x_right < x_left || y_bottom < y_top {
            0.0
        } else {
            (x_right - x_left) * (y_bottom - y_top)
        }
    }

    pub fn iou(&self, other: &Self) -> f32 {
        let inter = self.intersection(other);
        let union = self.area() + other.area() - inter;
        if union > 0.0 {
            inter / union
        } else {
            0.0
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustSpatialAnomaly {
    pub severity: String,
    pub anomaly_type: String,
    pub element_id: String,
    pub message: String,
}

pub struct RustVisualGroundingValidator {
    pub window_width: f32,
    pub window_height: f32,
    pub tolerance: f32,
}

impl RustVisualGroundingValidator {
    pub fn new(window_width: f32, window_height: f32) -> Self {
        Self {
            window_width,
            window_height,
            tolerance: 0.005,
        }
    }

    pub fn validate_layout(&self, elements: &[RustUIBoundingBox]) -> Vec<RustSpatialAnomaly> {
        let mut anomalies = Vec::new();

        for elem in elements {
            if !elem.is_visible {
                continue;
            }

            // Viewport clipping check
            if elem.xmin < 0.0 || elem.ymin < 0.0 || elem.xmax > self.window_width || elem.ymax > self.window_height {
                let clipped = (0.0f32).max(-elem.xmin)
                    + (0.0f32).max(-elem.ymin)
                    + (0.0f32).max(elem.xmax - self.window_width)
                    + (0.0f32).max(elem.ymax - self.window_height);

                anomalies.push(RustSpatialAnomaly {
                    severity: if clipped > 10.0 { "CRITICAL".to_string() } else { "WARNING".to_string() },
                    anomaly_type: "VIEWPORT_CLIPPING_ANOMALY".to_string(),
                    element_id: elem.element_id.clone(),
                    message: format!("Element {} poza oknem ({:.1}px poza zakresem)", elem.element_id, clipped),
                });
            }
        }

        // Control collision check
        for i in 0..elements.len() {
            for j in (i + 1)..elements.len() {
                let e1 = &elements[i];
                let e2 = &elements[j];
                if e1.is_visible && e2.is_visible && e1.z_index == e2.z_index && e1.element_type != "CONTAINER" {
                    let iou = e1.iou(e2);
                    if iou > 0.25 {
                        anomalies.push(RustSpatialAnomaly {
                            severity: "WARNING".to_string(),
                            anomaly_type: "CONTROL_OVERLAP".to_string(),
                            element_id: format!("{}+{}", e1.element_id, e2.element_id),
                            message: format!("Kolizja przestrzenna kontrolek (IoU: {:.2})", iou),
                        });
                    }
                }
            }
        }

        anomalies
    }

    pub fn validate_state_sync(
        &self,
        elem: &RustUIBoundingBox,
        expected_val: f32,
    ) -> Option<RustSpatialAnomaly> {
        if let Some(rendered) = elem.rendered_value {
            let diff = (rendered - expected_val).abs();
            if diff > self.tolerance {
                return Some(RustSpatialAnomaly {
                    severity: "CRITICAL".to_string(),
                    anomaly_type: "STATE_DESYNC_HARD_ANOMALY".to_string(),
                    element_id: elem.element_id.clone(),
                    message: format!(
                        "Desynchronizacja stanu {}: UI renderuje {:.4}, Rust ma {:.4} (Delta: {:.4})",
                        elem.element_id, rendered, expected_val, diff
                    ),
                });
            }
        }
        None
    }
}
