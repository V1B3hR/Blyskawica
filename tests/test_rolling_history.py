import unittest
from collections import deque
import time

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from tests.test_utils import get_test_seed, set_seed


class TestRollingHistory(unittest.TestCase):
    def setUp(self):
        """Initialize an AliveLoopNode instance for testing rolling history"""
        set_seed(get_test_seed())

        self.node = AliveLoopNode(
            position=(0, 0),
            velocity=(1, 1),
            initial_energy=10.0,
            field_strength=1.0,
            node_id=1
        )

    def test_history_initialization(self):
        """Test that all history deques are properly initialized"""
        self.assertIsInstance(self.node.anxiety_history, deque)
        self.assertIsInstance(self.node.calm_history, deque)
        self.assertIsInstance(self.node.energy_history, deque)

        # Check max length is set to 20 (or default config)
        self.assertGreaterEqual(self.node.anxiety_history.maxlen, 10)
        
        # Should start empty
        self.assertEqual(len(self.node.anxiety_history), 0)
        self.assertEqual(len(self.node.calm_history), 0)
        self.assertEqual(len(self.node.energy_history), 0)

    def test_history_population(self):
        """Test that histories are populated during step_phase"""
        initial_anxiety = self.node.anxiety
        initial_calm = self.node.calm
        initial_energy = self.node.energy

        # Run several steps
        for i in range(5):
            self.node.step_phase(current_time=i)

        # Check that histories have been populated
        self.assertEqual(len(self.node.anxiety_history), 5)
        self.assertEqual(len(self.node.calm_history), 5)
        self.assertEqual(len(self.node.energy_history), 5)

        # Check that first values match initial values (unpacking timestamp tuple)
        self.assertEqual(self.node.anxiety_history[0][1], initial_anxiety)
        self.assertEqual(self.node.calm_history[0][1], initial_calm)
        self.assertEqual(self.node.energy_history[0][1], initial_energy)

    def test_history_max_length(self):
        """Test that histories don't exceed maxlen"""
        # Run more than 30 steps
        for i in range(30):
            self.node.step_phase(current_time=i)

        maxlen = self.node.anxiety_history.maxlen
        # Check that histories are capped at maxlen
        self.assertEqual(len(self.node.anxiety_history), maxlen)
        self.assertEqual(len(self.node.calm_history), maxlen)
        self.assertEqual(len(self.node.energy_history), maxlen)

    def test_trend_analysis_stable(self):
        """Test trend analysis with stable values"""
        # Set current value
        self.node.anxiety = 5.0
        # Stable prediction
        def mock_predict(state_name, steps):
            return 5.0
        self.node.predict_emotional_state = mock_predict
        
        trends = self.node.get_emotional_trends()
        self.assertEqual(trends["anxiety"], "stable")

    def test_trend_analysis_increasing(self):
        """Test trend analysis with increasing values"""
        self.node.anxiety = 5.0
        # Increasing prediction
        def mock_predict(state_name, steps):
            return 6.0
        self.node.predict_emotional_state = mock_predict
        
        trends = self.node.get_emotional_trends()
        self.assertEqual(trends["anxiety"], "increasing")

    def test_trend_analysis_decreasing(self):
        """Test trend analysis with decreasing values"""
        self.node.energy = 8.0
        # Decreasing prediction
        def mock_predict(state_name, steps):
            if state_name == 'energy': return 6.0
            return getattr(self.node, state_name, 0.0)
        self.node.predict_emotional_state = mock_predict
        
        trends = self.node.get_emotional_trends()
        self.assertEqual(trends["energy"], "decreasing")

    def test_intervention_detection_anxiety(self):
        """Test intervention detection for high anxiety"""
        self.node.anxiety = 9.0
        self.node.calm = 1.0
        
        def mock_predict(state_name, steps):
            if state_name == 'anxiety': return 9.5
            return getattr(self.node, state_name, 0.0)
        self.node.predict_emotional_state = mock_predict

        result = self.node.assess_intervention_need()

        self.assertTrue(result["intervention_needed"])
        self.assertEqual(result["intervention_type"], "anxiety_help")

    def test_intervention_detection_combined_risk(self):
        """Test intervention detection for energy risk scenario"""
        self.node.energy = 2.0
        self.node.anxiety = 8.0
        
        def mock_predict(state_name, steps):
            if state_name == 'energy': return 1.5
            if state_name == 'anxiety': return 8.5
            return getattr(self.node, state_name, 0.0)
        self.node.predict_emotional_state = mock_predict

        result = self.node.assess_intervention_need()

        self.assertTrue(result["intervention_needed"])
        self.assertIn(result["intervention_type"], ["energy_conservation", "anxiety_help"])

    def test_get_anxiety_status(self):
        """Test that get_anxiety_status returns proper keys"""
        status = self.node.get_anxiety_status()
        self.assertIn("anxiety_level", status)
        self.assertIn("calm_level", status)
        self.assertIn("is_overwhelmed", status)
        self.assertIn("can_send_help", status)

    def test_integration_with_step_phase(self):
        """Test step phase handles proactive interventions gracefully"""
        self.node.anxiety = 10.0
        self.node.calm = 0.5
        
        def mock_predict(state_name, steps):
            if state_name == 'anxiety': return 11.0
            return getattr(self.node, state_name, 0.0)
        self.node.predict_emotional_state = mock_predict

        # Should test without crashing
        for i in range(15):
            self.node.step_phase(current_time=i)
            
        self.assertIsNotNone(self.node._last_intervention_assessment)
        self.assertTrue(self.node._last_intervention_assessment["intervention_needed"])

if __name__ == "__main__":
    unittest.main()
