#!/usr/bin/env python3
"""
Unit test suite for Visual Grounding (Roboflow/Caniverse-Win11) & Deep Sleep LogHub Hard Anomaly Parser.
"""

import tempfile
import unittest
from pathlib import Path

from adaptiveneuralnetwork.cognitive_tools.visual_grounding_validator import (
    UIBoundingBox,
    UILayoutSnapshot,
    VisualGroundingValidator,
)
from adaptiveneuralnetwork.central_nervous_system.deep_sleep_loghub_parser import (
    DeepSleepLogHubParser,
    LogCategory,
)


class TestVisualGroundingAndLogHub(unittest.TestCase):
    def setUp(self):
        self.validator = VisualGroundingValidator(tolerance=0.005)
        self.parser = DeepSleepLogHubParser()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_visual_grounding_healthy_layout(self):
        """Verify normal compliant layout produces 100% health score and 0 anomalies."""
        snapshot = UILayoutSnapshot(window_width=1280, window_height=720, fps_render_rate=60.0)
        snapshot.add_element(UIBoundingBox("slider_dopamine", "SLIDER", (50, 50, 250, 80), rendered_value=0.72))
        snapshot.add_element(UIBoundingBox("slider_serotonin", "SLIDER", (50, 100, 250, 130), rendered_value=1.20))
        snapshot.add_element(UIBoundingBox("yant_canvas", "OSCILLOSCOPE", (300, 50, 600, 350)))

        rust_state = {
            "slider_dopamine": 0.72,
            "slider_serotonin": 1.20
        }

        report = self.validator.audit_visual_health(snapshot, rust_state)
        self.assertTrue(report.is_healthy)
        self.assertEqual(len(report.anomalies), 0)
        self.assertEqual(report.health_score, 1.0)
        self.assertEqual(report.synced_elements, 3)

    def test_visual_grounding_viewport_clipping_detection(self):
        """Verify elements pushed outside window boundaries are flagged as VIEWPORT_CLIPPING_ANOMALY."""
        snapshot = UILayoutSnapshot(window_width=800, window_height=600)
        # Element clipped past right window border (xmax = 850 > 800)
        snapshot.add_element(UIBoundingBox("oversized_badge", "BADGE", (700, 50, 850, 90)))

        anomalies = self.validator.validate_layout_geometry(snapshot)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["type"], "VIEWPORT_CLIPPING_ANOMALY")
        self.assertEqual(anomalies[0]["element_id"], "oversized_badge")

    def test_visual_grounding_state_desynchronization_hard_anomaly(self):
        """Verify discrepancy between UI slider and Rust logic is flagged as CRITICAL Hard Anomaly."""
        snapshot = UILayoutSnapshot(window_width=1280, window_height=720)
        # UI is frozen at 0.50 while Rust state progressed to 0.90
        snapshot.add_element(UIBoundingBox("slider_dopamine", "SLIDER", (50, 50, 250, 80), rendered_value=0.50))

        rust_state = {"slider_dopamine": 0.90}

        report = self.validator.audit_visual_health(snapshot, rust_state)
        self.assertFalse(report.is_healthy)
        self.assertTrue(any(a["type"] == "STATE_DESYNC_HARD_ANOMALY" for a in report.anomalies))
        self.assertLess(report.health_score, 0.80)

    def test_loghub_clean_logs_no_anomaly(self):
        """Verify normal operational logs produce STABLE_CLEAN status."""
        logs = [
            "2026-08-21 08:00:00 [INFO] (TAURI_CORE): Webview window initialized successfully.",
            "2026-08-21 08:00:01 [INFO] (RUST_CORE): HNSW vector index loaded with 128-dim embeddings.",
            "2026-08-21 08:00:02 [INFO] (NEUROCHEMISTRY): Homeostasis steady state achieved."
        ]
        report = self.parser.process_log_batch(logs)
        self.assertEqual(report.integrity_status, "STABLE_CLEAN")
        self.assertEqual(report.hard_anomalies_detected, 0)

    def test_loghub_directx_shader_hard_anomaly_detection(self):
        """Verify DirectX/WGSL shader crash is relentlessly captured as HARD_ANOMALY."""
        logs = [
            "2026-08-21 08:10:00 [INFO] (GPU): Rendering Yant oscilloscope frame 1204.",
            "2026-08-21 08:10:01 [ERROR] (DIRECTX): DXGI_ERROR_DEVICE_HUNG in shader pipeline compilation.",
            "2026-08-21 08:10:02 [INFO] (TAURI): Attempting fallback recovery."
        ]
        report = self.parser.process_log_batch(logs)
        self.assertEqual(report.integrity_status, "HARD_ANOMALIES_DETECTED")
        self.assertEqual(report.hard_anomalies_detected, 1)
        self.assertEqual(report.critical_shader_errors, 1)
        self.assertTrue(any("WARP" in r for r in report.remediation_suggestions))

    def test_loghub_tauri_ipc_latency_spike_detection(self):
        """Verify dropped IPC packets or latency spikes are captured as HARD_ANOMALY."""
        logs = [
            "2026-08-21 08:15:00 [WARNING] (TAURI_IPC): IPC latency > 48ms during large state serialization.",
            "2026-08-21 08:15:05 [CRITICAL] (TAURI_IPC): IPC channel closed unexpectedly on worker thread."
        ]
        report = self.parser.process_log_batch(logs)
        self.assertEqual(report.integrity_status, "HARD_ANOMALIES_DETECTED")
        self.assertEqual(report.ipc_failures, 2)

    def test_loghub_audit_export_persistence(self):
        """Verify Hard Anomaly Report is successfully exported to JSON."""
        logs = [
            "2026-08-21 08:20:00 [CRITICAL] (WIN_EVENT_LOG): EventID: 1000 Application Error in WebView2Loader.dll"
        ]
        report = self.parser.process_log_batch(logs)
        out_file = Path(self.temp_dir.name) / "integrity_audit_test.json"
        ok = self.parser.export_audit_report(report, out_path=out_file)
        self.assertTrue(ok)
        self.assertTrue(out_file.exists())


if __name__ == "__main__":
    unittest.main()
