import unittest

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode, SocialSignal
from adaptiveneuralnetwork.cognitive_tools.polymathic_hub import PolymathicHub


class TestPolymathicHub(unittest.TestCase):
    def setUp(self):
        self.node = AliveLoopNode(position=[0, 0], velocity=[0, 0])
        self.hub = PolymathicHub()

    def test_physics_routing(self):
        # Sending a query with physics keywords
        cost, response = self.hub.process_polymathic_signal("what is the quantum gravity variance?", current_energy=10.0)
        self.assertEqual(cost, 2.4)
        self.assertIn("[POLYMATH_HUB]", response)
        self.assertIn("Physics", response)

    def test_chemistry_routing(self):
        # Sending a query with chemistry keywords
        cost, response = self.hub.process_polymathic_signal("simulate the chemical reaction of this molecule", current_energy=10.0)
        self.assertEqual(cost, 1.6)
        self.assertIn("[POLYMATH_HUB]", response)
        self.assertIn("Chemistry", response)

    def test_node_polymathic_query_interception(self):
        # Ensure node responds properly via hub without sharing a normal memory
        signal = SocialSignal(content="check the quantum gravity variance", signal_type="query", urgency=0.5, source_id=2, requires_response=True)
        self.node.energy = 50.0  # Ensure enough energy

        response_signal = self.node._process_query_signal(signal)
        self.assertIsNotNone(response_signal)
        self.assertEqual(response_signal.signal_type, "memory")  # Dispatched as a memory response
        self.assertIn("[POLYMATH_HUB]", str(response_signal.content))

        # Check energy deduction (50.0 - 1.5 = 48.5)
        self.assertEqual(self.node.energy, 47.6)

    def test_new_disciplines_routing(self):
        # Astronomy (galaxy, cost=1.5)
        cost, response = self.hub.process_polymathic_signal("tell me about the andromeda galaxy", 10.0)
        self.assertEqual(cost, 1.5)
        self.assertIn("Astronomy & Cosmology", response)

        # Civil Engineering (structural integrity, cost=1.4)
        cost, response = self.hub.process_polymathic_signal("what are stress-strain metrics in structural integrity?", 10.0)
        self.assertEqual(cost, 1.4)
        self.assertIn("Civil & Mechanical", response)

        # Economics (macroeconomics, cost=1.3)
        cost, response = self.hub.process_polymathic_signal("explain microeconomics and macroeconomics models", 10.0)
        self.assertEqual(cost, 1.3)
        self.assertIn("Economics & Finance", response)

        # Linguistics (syntax tree, cost=1.0)
        cost, response = self.hub.process_polymathic_signal("draw a syntax tree for linguistics", 10.0)
        self.assertEqual(cost, 1.0)
        self.assertIn("Historical & Linguistic", response)

if __name__ == '__main__':
    unittest.main()

