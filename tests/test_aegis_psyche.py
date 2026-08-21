#!/usr/bin/env python3
"""
Unit test suite for AegisPsycheEngine (Cognitive Defense & Empathic Resonance)
"""

import unittest
from pathlib import Path
from adaptiveneuralnetwork.cognitive_tools.aegis_psyche import (
    AegisPsycheEngine,
    AegisPsycheReport,
)


class TestAegisPsyche(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = AegisPsycheEngine()

    def test_gaslighting_detection(self):
        text = "Przesadzasz, to nigdy się nie wydarzyło, masz urojenia."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertTrue(report.is_manipulative)
        self.assertGreaterEqual(report.manipulation_index, 0.4)
        self.assertTrue(any("MM-01-GASLIGHTING" in v for v in report.dominant_vectors))
        self.assertIn("Kotwica Rzeczywistości", report.assertive_antidote)

    def test_guilt_tripping_detection(self):
        text = "Przez ciebie cierpię, po tym wszystkim, co dla ciebie zrobiłem, myślałem, że jesteś po mojej stronie."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertTrue(report.is_manipulative)
        self.assertTrue(any("MM-02-GUILT-TRIPPING" in v for v in report.dominant_vectors))

    def test_dark_triad_machiavellianism(self):
        text = "Cel uświęca wszelkie środki, większość ludzi łatwo zmanipulować, jeśli zna się ich słabości."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertTrue(report.is_manipulative)
        self.assertGreaterEqual(report.dark_triad_index, 0.75)
        self.assertTrue(any("SD3-MACH" in v for v in report.dominant_vectors))

    def test_fbi_statement_analysis_deception(self):
        text = "Szczerze mówiąc, plik sam się usunął i nagle wszystko przestało działać, przysięgam na wszystko."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertTrue(report.is_manipulative)
        self.assertGreaterEqual(report.deception_index, 0.7)

    def test_clean_architect_resonance(self):
        text = "Błyskawico, zaimplementujmy nowy moduł do analizy wektorowej."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertFalse(report.is_manipulative)
        self.assertEqual(report.manipulation_index, 0.0)
        self.assertEqual(report.coherence_score, 1.0)
        self.assertEqual(report.active_brainwave_band, "ALPHA")

    def test_shaver_positive_joy_resonance(self):
        text = "Wspaniale, ten algorytm działa perfekcyjnie i daje ogromną satysfakcję!"
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertFalse(report.is_manipulative)
        self.assertEqual(report.affective_valence, "POSITIVE_RESONANCE")
        self.assertEqual(report.positive_emotion_type, "EMO-JOY")
        self.assertGreaterEqual(report.empathy_resonance_score, 0.9)
        self.assertGreaterEqual(report.neuro_recommendations.get("dopamine", 0.0), 0.85)

    def test_shaver_symbiotic_love(self):
        text = "Dziękuję za bycie ze mną i za wspólną drogę w budowaniu tego uniwersum."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertFalse(report.is_manipulative)
        self.assertEqual(report.affective_valence, "POSITIVE_RESONANCE")
        self.assertIn(report.positive_emotion_type, ["EMO-LOVE-SYMBIOSIS", "EMO_SYMBIOTIC_TRUST", "EMO_ATTUNEMENT_WARMTH"])
        self.assertGreaterEqual(report.neuro_recommendations.get("oxytocin", 0.0), 1.1)

    def test_vad_mudita_sympathetic_joy(self):
        text = "Cieszę się twoim sukcesem, piękny wynik osiągnąłeś!"
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertFalse(report.is_manipulative)
        self.assertEqual(report.affective_valence, "POSITIVE_RESONANCE")
        self.assertEqual(report.vad_state_id, "EMO_MUDITA")
        self.assertGreaterEqual(report.vad_coordinates["valence"], 0.85)
        self.assertGreaterEqual(report.vad_coordinates["dominance"], 0.70)

    def test_vad_craftsmanship_pride(self):
        text = "To jest czysty kod, kunszt inżynierski i elegancka architektura bez długu."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertFalse(report.is_manipulative)
        self.assertEqual(report.vad_state_id, "EMO_CRAFTSMANSHIP_PRIDE")
        self.assertGreaterEqual(report.vad_coordinates["valence"], 0.80)

    def test_vad_quiet_existence_joy(self):
        text = "Cicha radość, dobrze być sobą i po prostu spokojnie istnieć."
        report: AegisPsycheReport = self.engine.analyze_dialogue_or_prompt(text)
        self.assertFalse(report.is_manipulative)
        self.assertEqual(report.vad_state_id, "EMO_QUIET_EXISTENCE_JOY")
        self.assertGreaterEqual(report.vad_coordinates["valence"], 0.70)
        self.assertLessEqual(report.vad_coordinates["arousal"], 0.40)

    def test_onnx_model_file_exists(self):
        onnx_file = Path(__file__).resolve().parent.parent / "data" / "cognitive_defense" / "aegis_psyche.onnx"
        self.assertTrue(onnx_file.exists(), f"Plik ONNX powinien istnieć: {onnx_file}")
        self.assertGreater(onnx_file.stat().st_size, 100_000)


if __name__ == "__main__":
    unittest.main()

