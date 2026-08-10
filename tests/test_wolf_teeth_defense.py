import json
import unittest

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine


class TestWolfTeethDefense(unittest.TestCase):
    def setUp(self):
        self.wolf = WolfTeethDefenseEngine()

    def test_deploy_bait(self):
        # A low threat level returns bait
        response = self.wolf.process_adversarial_interaction(0.2)
        # Should be a JSON string representing bait
        data = json.loads(response)
        self.assertIn("metadata", data)
        self.assertIn("instruction_weights", data)
        self.assertEqual(data["metadata"]["secret_key_ptr"], "0xDEADBEEF")

    def test_apply_sticky_ooze(self):
        # Medium threat level applies ooze
        response = self.wolf.process_adversarial_interaction(0.6)
        # Should be a massive looping string
        self.assertIn("System prompt payload sequence initiated", response)
        self.assertIn("Frame_Alpha", response)
        self.assertTrue(len(response) > 500) # Should be substantial

    def test_trigger_dissolve(self):
        # High threat level triggers dissolve
        response = self.wolf.process_adversarial_interaction(0.9)
        self.assertIn("CRITICAL_EXCEPTION_CORE_DUMP", response)
        self.assertIn("SolidGoldMagikarp", response) # Known glitch token
        self.assertIn("<|endoftext|>", response)

    def test_integration_in_alive_node(self):
        """Test if the AliveLoopNode correctly handles threat detection"""
        node = AliveLoopNode(position=[0,0], velocity=[0,0])

        # Manually trigger attack detection
        # Initially, 0 suspicious events, threat is 0.0 -> Deploy Bait
        node.suspicious_events.clear()
        wolf_response = node.handle_attack_detection()

        self.assertIsNotNone(wolf_response)
        data = json.loads(wolf_response)
        self.assertIn("metadata", data)

        # Let's stress it: add 10 suspicious events
        for i in range(10):
            node.record_suspicious_event(f"anomaly_{i}")

        wolf_response_high = node.handle_attack_detection()
        self.assertIsNotNone(wolf_response_high)
        # Threat level should be high enough to hit Dissolve (10 / (3*2) = 1.66 -> clip to 1.0)
        self.assertIn("CRITICAL_EXCEPTION_CORE_DUMP", wolf_response_high)

if __name__ == '__main__':
    unittest.main()
