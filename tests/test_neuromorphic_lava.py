import unittest
import math
import os
import json
import torch
import torch.nn as nn
from adaptiveneuralnetwork.central_nervous_system.neuromorphic.network_topology import HierarchicalNetwork, TopologyConfig
from adaptiveneuralnetwork.central_nervous_system.neuromorphic.config import NeuromorphicConfig
from adaptiveneuralnetwork.central_nervous_system.neuromorphic.advanced_neurons import NeuronV3Config
from adaptiveneuralnetwork.central_nervous_system.neuromorphic.lava_compiler import LavaCompiler

class TestNeuromorphicLava(unittest.TestCase):
    def setUp(self):
        # Create a simple 2-layer network configuration
        self.config = TopologyConfig(
            num_layers=2,
            layer_sizes=[8, 4],
            connection_probability=0.5,
            device="cpu"
        )
        self.base_config = NeuromorphicConfig(
            dt=0.001,
            tau_mem=0.01,
            tau_syn=0.005,
            v_threshold=1.2
        )
        self.neuron_config = NeuronV3Config(base_config=self.base_config)
        self.network = HierarchicalNetwork(
            config=self.config,
            neuron_configs=[self.neuron_config, self.neuron_config],
            layer_types=["adaptive_threshold", "adaptive_threshold"]
        )
        self.compiler = LavaCompiler()
        self.test_json_path = "test_lava_network.json"

    def tearDown(self):
        if os.path.exists(self.test_json_path):
            try:
                os.remove(self.test_json_path)
            except Exception:
                pass

    def test_float_to_lava_decay(self):
        """Tests physical tau conversion to Lava decay rate float."""
        tau = 0.01
        dt = 0.001
        expected = 1.0 - math.exp(-dt / tau)
        result = self.compiler.float_to_lava_decay(tau, dt)
        self.assertAlmostEqual(result, expected, places=6)
        
        # Test boundary case
        self.assertEqual(self.compiler.float_to_lava_decay(0.0), 1.0)
        self.assertEqual(self.compiler.float_to_lava_decay(-5.0), 1.0)

    def test_float_to_lava_decay_fixed_point(self):
        """Tests physical tau conversion to Lava decay rate fixed-point integer."""
        tau = 0.01
        dt = 0.001
        bit_precision = 12
        decay_float = 1.0 - math.exp(-dt / tau)
        expected = int(round(decay_float * 4095))
        result = self.compiler.float_to_lava_decay_fixed_point(tau, dt, bit_precision)
        self.assertEqual(result, expected)

    def test_compile_to_json(self):
        """Tests that compiling HierarchicalNetwork outputs correct JSON schema."""
        lava_graph = self.compiler.compile_to_json(self.network, self.test_json_path)
        
        # Assert keys
        self.assertIn("compiler", lava_graph)
        self.assertIn("processes", lava_graph)
        self.assertIn("connections", lava_graph)
        
        # Assert processes correspond to layers
        processes = lava_graph["processes"]
        self.assertEqual(len(processes), 2)
        
        # Check first layer
        lif_0 = processes[0]
        self.assertEqual(lif_0["id"], "lif_0")
        self.assertEqual(lif_0["shape"], [8])
        self.assertEqual(lif_0["vth"], 1.2)
        self.assertAlmostEqual(lif_0["du"], 1.0 - math.exp(-0.001/0.005), places=6)
        self.assertAlmostEqual(lif_0["dv"], 1.0 - math.exp(-0.001/0.01), places=6)
        
        # Assert connections correspond to feedforward synapses
        connections = lava_graph["connections"]
        self.assertEqual(len(connections), 2)  # Feedforward + Feedback
        
        # Check feedforward connection
        ff_conn = connections[0]
        self.assertEqual(ff_conn["id"], "dense_ff_0")
        self.assertEqual(ff_conn["source"], "lif_0")
        self.assertEqual(ff_conn["target"], "lif_1")
        # Transposed weights: target (post) size is 4, source (pre) size is 8
        self.assertEqual(ff_conn["shape"], [4, 8])
        
        # Check file was written
        self.assertTrue(os.path.exists(self.test_json_path))
        with open(self.test_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data["compiler"], "Blyskawica LavaCompiler V1")

    def test_compile_to_script_syntax(self):
        """Tests that the compiler generates syntactically valid Python code."""
        script_str = self.compiler.compile_to_script(self.network)
        self.assertIsInstance(script_str, str)
        self.assertIn("from lava.proc.lif.process import LIF", script_str)
        self.assertIn("from lava.proc.dense.process import Dense", script_str)
        self.assertIn("lif_0 = LIF", script_str)
        self.assertIn("dense_ff_0 = Dense", script_str)
        
        # Verify script compiles syntactically
        try:
            compile(script_str, "<string>", "exec")
        except SyntaxError as e:
            self.fail(f"Generated Lava script has syntax errors: {e}")

if __name__ == "__main__":
    unittest.main()
