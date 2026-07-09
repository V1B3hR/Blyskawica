import unittest
from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState, NeurochemicalConfig
from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode

class TestNeurochemistry(unittest.TestCase):
    def setUp(self):
        self.config = NeurochemicalConfig(
            adenosine_accumulation_rate=0.1,
            sleep_pressure_threshold=0.5,
            force_sleep_threshold=1.0
        )
        self.state = NeurochemicalState(self.config)

    def test_adenosine_accumulation(self):
        self.assertEqual(self.state.adenosine, 0.0)
        self.state.update(dt_hours=1.0, current_phase="active")
        self.assertAlmostEqual(self.state.adenosine, 0.1)
        self.assertFalse(self.state.is_sleep_deprived)

        self.state.update(dt_hours=5.0, current_phase="active")
        self.assertAlmostEqual(self.state.adenosine, 0.6)
        self.assertTrue(self.state.is_sleep_deprived)

    def test_sleep_clearance(self):
        self.state.adenosine = 1.0
        self.state.update(dt_hours=2.0, current_phase="sleep")
        self.assertAlmostEqual(self.state.adenosine, 1.0 - (self.config.adenosine_clearance_rate * 2.0))

    def test_cortisol_wake_up(self):
        # High adenosine, would normally force sleep
        self.state.adenosine = 1.1
        self.assertTrue(self.state.should_force_sleep())
        
        # Attack happens
        self.state.trigger_cortisol_spike(0.8)
        self.assertTrue(self.state.is_sleep_masked())
        # Forced sleep is masked
        self.assertFalse(self.state.should_force_sleep())

    def test_dopamine_all_nighter(self):
        # Sleep deprived, high adenosine
        self.state.adenosine = 0.9
        
        # But having a good time!
        self.state.trigger_dopamine_spike(0.7)
        self.assertTrue(self.state.is_sleep_masked())

    def test_cognitive_load_multiplier(self):
        # Baseline (serotonin=0.8, gaba=0.5 -> 1.0 - 0.24 - 0.05 = 0.71)
        self.assertAlmostEqual(self.state.get_cognitive_load_multiplier(), 0.71)
        
        # Sleepless -> goes up
        self.state.adenosine = 0.7  # 0.2 over threshold (0.5)
        # 0.71 + (0.2 * 2.5) = 1.21
        self.assertAlmostEqual(self.state.get_cognitive_load_multiplier(), 1.21)
        
        # Stress -> goes up further
        self.state.cortisol = 0.9
        # 1.21 + 0.5 = 1.71
        self.assertAlmostEqual(self.state.get_cognitive_load_multiplier(), 1.71)

    def test_alive_node_integration(self):
        node = AliveLoopNode(position=[0,0], velocity=[0,0])
        # Force low energy, should sleep
        node.energy = 2.0
        node.circadian_cycle = 12
        node._determine_phase_transition()
        self.assertEqual(node.phase, "sleep")
        
        # Fully charged, daylight, should be active
        node.energy = 100.0
        node.circadian_cycle = 12
        node.neurochemistry.adenosine = 0.0
        node.neurochemistry.serotonin = 0.9
        node.anxiety = 0.0
        node._determine_phase_transition()
        self.assertEqual(node.phase, "inspired")

if __name__ == '__main__':
    unittest.main()
