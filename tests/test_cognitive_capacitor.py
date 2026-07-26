"""
Unit tests for CognitiveCapacitor in Błyskawica immune system.
Tests voltage spike absorption, movable plate dynamic expansion, RC low-pass filtering, and bleed-off discharge.
"""

import sys
import unittest
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from adaptiveneuralnetwork.immune_system.cognitive_capacitor import CognitiveCapacitor


class TestCognitiveCapacitor(unittest.TestCase):
    def setUp(self):
        self.capacitor = CognitiveCapacitor(
            nominal_capacitance_uF=100.0,
            resistance_ohms=1000.0,
            max_voltage_threshold=10.0,
            bleed_rate=0.1,
        )

    def test_initial_state(self):
        """Test initial status of capacitor"""
        status = self.capacitor.get_capacitor_status()
        self.assertEqual(status["plate_distance_mm"], 1.0)
        self.assertEqual(status["voltage"], 0.0)
        self.assertEqual(status["spike_events"], 0)

    def test_smooth_voltage_signal(self):
        """Test low-pass RC filtering on smooth signal"""
        res = self.capacitor.absorb_signal_spike(raw_input_voltage=1.0)
        self.assertLess(res["smoothed_voltage"], 1.0)
        self.assertFalse(res["spike_absorbed"])

    def test_voltage_spike_and_movable_plates(self):
        """Test reaction to huge voltage spike burst (movable plates expanding)"""
        res = self.capacitor.absorb_signal_spike(raw_input_voltage=8.0)
        self.assertTrue(res["spike_absorbed"])
        self.assertGreater(res["plate_distance_mm"], 1.0)
        self.assertEqual(self.capacitor.spike_events_count, 1)

    def test_bleed_off_discharge(self):
        """Test energy discharge over time"""
        self.capacitor.absorb_signal_spike(raw_input_voltage=5.0)
        v_after_spike = self.capacitor.current_voltage
        
        time.sleep(0.05)
        self.capacitor.absorb_signal_spike(raw_input_voltage=0.0)
        v_after_bleed = self.capacitor.current_voltage
        
        self.assertLess(v_after_bleed, v_after_spike)


if __name__ == "__main__":
    unittest.main()
