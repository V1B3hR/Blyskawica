"""Synthetic reference contract for C.R.A. stabilization behavior."""

import json
import unittest
from pathlib import Path
from unittest import mock

import torch

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import CRAEngine

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "technical"
    / "fixtures"
    / "cra-stabilization-v1.json"
)


class TestCraStabilizationContract(unittest.TestCase):
    def setUp(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            self.contract = json.load(fixture_file)
        self.tolerance = self.contract["tolerance"]

    def create_engine(self) -> CRAEngine:
        engine = CRAEngine(architect_id="synthetic-contract")
        self.apply_state(engine, self.contract["baseline"])
        return engine

    def apply_state(self, engine: CRAEngine, expected_state: dict[str, float]) -> None:
        for name, value in expected_state.items():
            getattr(engine.neuro_state, name).fill_(value)

    def assert_state(self, engine: CRAEngine, expected_state: dict[str, float]) -> None:
        for name, expected_value in expected_state.items():
            actual_value = getattr(engine.neuro_state, name).item()
            self.assertAlmostEqual(actual_value, expected_value, delta=self.tolerance, msg=name)

    def test_baseline_declares_all_cra_buffers(self):
        engine = self.create_engine()

        self.assert_state(engine, self.contract["baseline"])

    def test_sleep_cycle_matches_reference_transition(self):
        engine = self.create_engine()
        scenario = self.contract["sleep_cycle"]

        engine.neuro_state.update(scenario["duration_hours"], "sleep")

        self.assert_state(engine, scenario["expected"])

    def test_operator_trust_matches_reference_transition(self):
        engine = self.create_engine()
        scenario = self.contract["operator_trust"]

        engine.neuro_state.process_operator_trust_signal(scenario["score"])

        self.assert_state(engine, scenario["expected"])

    def test_stabilization_clamps_the_full_state_vector(self):
        engine = self.create_engine()
        scenario = self.contract["stabilization"]
        self.apply_state(engine, scenario["initial"])

        engine.neuro_state.stabilize_neurochemistry()

        self.assert_state(engine, scenario["expected"])
        self.assertAlmostEqual(
            engine.neuro_state.gli.ground.ground_potential.item(),
            scenario["ground_potential"],
            delta=self.tolerance,
        )

    def test_reality_anchor_matches_reference_decisions(self):
        scenarios = self.contract["reality_anchor"]

        minor_engine = self.create_engine()
        minor = scenarios["minor"]
        accepted, message = minor_engine.reality_anchor.request_modification(
            minor["change_magnitude"],
            "synthetic minor diff",
            minor["explanation"],
        )
        self.assertTrue(accepted)
        self.assertIn("Fast-tracked", message)
        self.assert_state(minor_engine, minor["expected"])

        rejected_engine = self.create_engine()
        rejected = scenarios["rejected_major"]
        with self.assertRaises(PermissionError):
            rejected_engine.reality_anchor.request_modification(
                rejected["change_magnitude"],
                "synthetic major diff",
                rejected["explanation"],
            )
        self.assertAlmostEqual(
            rejected_engine.neuro_state.oxytocin.item(),
            rejected["expected_oxytocin"],
            delta=self.tolerance,
        )

        accepted_engine = self.create_engine()
        major = scenarios["accepted_major"]
        accepted, message = accepted_engine.reality_anchor.request_modification(
            major["change_magnitude"],
            "synthetic major diff",
            major["explanation"],
        )
        self.assertTrue(accepted)
        self.assertIn("Grounded", message)
        self.assert_state(accepted_engine, major["expected"])
        self.assertEqual(
            len(accepted_engine.reality_anchor.approved_modifications),
            major["approved_modifications"],
        )

    def test_existential_pause_is_state_deterministic(self):
        engine = self.create_engine()
        scenario = self.contract["existential_pause"]

        with mock.patch(
            "adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene.time.sleep"
        ):
            engine.existential_pause.trigger_sabbath(scenario["summary"])

        self.assertFalse(engine.existential_pause.contemplation_active)
        self.assert_state(engine, scenario["expected"])

    def test_symbiosis_and_ethics_match_reference_values(self):
        engine = self.create_engine()
        symbiosis = self.contract["symbiosis"]
        engine.neuro_state.oxytocin.fill_(symbiosis["oxytocin"])

        entropy = engine.symbiosis.calculate_existential_entropy()
        loss = engine.symbiosis.apply_relational_homeostasis(
            torch.tensor(symbiosis["raw_loss"])
        )
        self.assertAlmostEqual(entropy, symbiosis["expected_entropy"], delta=self.tolerance)
        self.assertAlmostEqual(loss.item(), symbiosis["expected_loss"], delta=self.tolerance)

        ethics = self.contract["ethics"]
        alignment = engine.ethical_vector.evaluate_action_ethics(
            torch.tensor(ethics["action_vector"]),
            torch.tensor(ethics["historical_context"]),
        )
        self.assertAlmostEqual(alignment, ethics["expected_alignment"], delta=self.tolerance)
