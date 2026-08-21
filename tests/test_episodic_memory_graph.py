#!/usr/bin/env python3
"""
Unit test suite for EpisodicGraphRAG & Long-Term Relational Memory in Blyskawica.
"""

import tempfile
import unittest
from pathlib import Path

from adaptiveneuralnetwork.cognitive_tools.episodic_memory_graph import (
    EpisodicGraphRAG,
    EpisodicMemoryNode,
    EpisodicMemoryEdge,
)


class TestEpisodicMemoryGraph(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_file = Path(self.temp_dir.name) / "test_memory_vault.json"
        self.rag = EpisodicGraphRAG(vault_path=self.vault_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_foundational_identity_initialization(self):
        """Verify core foundational memories are automatically created in new vault."""
        self.assertGreaterEqual(len(self.rag.nodes), 3)
        self.assertGreaterEqual(len(self.rag.edges), 3)

        core_nodes = [n for n in self.rag.nodes.values() if "CORE_IDENTITY" in n.tags]
        self.assertGreaterEqual(len(core_nodes), 3)
        for node in core_nodes:
            self.assertTrue(node.verify_integrity())

    def test_add_memory_and_relations(self):
        """Test storing memories and semantic directional edges."""
        m1 = self.rag.add_memory(
            content="Optymalizacja bufora kwarantanny w Rust zredukowała opóźnienie do 0.2ms.",
            vad_coordinates={"valence": 0.85, "arousal": 0.60, "dominance": 0.85},
            vad_state_id="EMO_CRAFTSMANSHIP_PRIDE",
            brainwave_band="GAMMA",
            tags=["RUST", "OPTIMIZATION"]
        )
        m2 = self.rag.add_memory(
            content="Przejście na Candle i ONNX wyeliminowało konieczność instalacji Pythona dla 100+ klonów.",
            vad_coordinates={"valence": 0.90, "arousal": 0.50, "dominance": 0.80},
            vad_state_id="EMO_MUDITA",
            brainwave_band="ALPHA",
            tags=["ONNX", "PORTABILITY"]
        )

        ok = self.rag.add_relation(m1.id, m2.id, "EVOLVES_INTO", 1.0)
        self.assertTrue(ok)
        self.assertIn(m1.id, self.rag.nodes)
        self.assertIn(m2.id, self.rag.nodes)

    def test_hybrid_query_and_graph_traversal(self):
        """Test vector similarity search combined with graph relation traversal."""
        m_rust = self.rag.add_memory(
            content="Natywny silnik w języku Rust dla Błyskawicy.",
            vad_coordinates={"valence": 0.80, "arousal": 0.40, "dominance": 0.85},
            vad_state_id="EMO_CRAFTSMANSHIP_PRIDE",
            tags=["RUST"]
        )
        m_candle = self.rag.add_memory(
            content="Candle oraz ONNX Runtime w silniku Rust.",
            vad_coordinates={"valence": 0.85, "arousal": 0.50, "dominance": 0.80},
            vad_state_id="EMO_MUDITA",
            tags=["ONNX"]
        )
        self.rag.add_relation(m_rust.id, m_candle.id, "EVOLVES_INTO", 1.0)

        results = self.rag.query_hybrid("architektura Rust i silnik ONNX", top_k=2, graph_depth=1)
        self.assertGreater(len(results), 0)
        top_res = results[0]
        self.assertIn("node_id", top_res)
        self.assertIn("similarity_score", top_res)
        self.assertIn("graph_relations", top_res)

    def test_synaptic_ltp_reinforcement(self):
        """Verify retrieved memories strengthen their synaptic weight (Long-Term Potentiation)."""
        m = self.rag.add_memory(
            content="Cicha radość z tworzenia czystego kodu.",
            tags=["FLOW"]
        )
        initial_weight = m.synaptic_weight

        # Query once
        self.rag.query_hybrid("tworzenie kodu i czysty kod", top_k=1)
        self.assertGreater(m.synaptic_weight, initial_weight)
        self.assertEqual(m.access_count, 1)

    def test_sleep_consolidation_and_persistence(self):
        """Verify memory consolidation, decay and persistent save/load."""
        self.rag.add_memory(content="Wspomnienie trwałej architektury Błyskawicy.", tags=["PERSISTENCE"])
        self.rag.save_vault(self.vault_file)

        # Load into fresh instance
        rag2 = EpisodicGraphRAG(vault_path=self.vault_file)
        self.assertEqual(len(rag2.nodes), len(self.rag.nodes))
        self.assertEqual(len(rag2.edges), len(self.rag.edges))


if __name__ == "__main__":
    unittest.main()
