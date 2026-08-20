#!/usr/bin/env python3
"""
Unit test suite for AegisPsycheEngine (Cognitive Defense & Empathic Resonance)
"""

import unittest
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


if __name__ == "__main__":
    unittest.main()
