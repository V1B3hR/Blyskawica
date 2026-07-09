import unittest
import torch
from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState

class TestHormonalCoupling(unittest.TestCase):
    def setUp(self):
        self.state = NeuromodulationState()

    def test_registered_hormones(self):
        """Verifies that all 10 neurotransmitters/hormones are registered as buffers."""
        expected_buffers = [
            'dopamine', 'acetylcholine', 'serotonin', 'oxytocin', 
            'testosterone', 'gaba', 'cortisol', 'adrenaline', 
            'estrogen', 'melatonin'
        ]
        for buf in expected_buffers:
            self.assertTrue(hasattr(self.state, buf), f"Missing buffer: {buf}")
            val = getattr(self.state, buf)
            self.assertTrue(isinstance(val, torch.Tensor), f"{buf} is not a Tensor")

    def test_learning_multiplier_coupling(self):
        """Tests how learning multiplier couples with adrenaline and melatonin."""
        # Baseline check
        self.state.dopamine.fill_(1.0)
        self.state.acetylcholine.fill_(1.0)
        self.state.testosterone.fill_(1.0)
        self.state.adrenaline.fill_(0.0)
        self.state.melatonin.fill_(0.0)
        
        baseline_multiplier = self.state.get_learning_multiplier()
        self.assertAlmostEqual(baseline_multiplier, 1.15, places=4)
        
        # 1. Adrenaline increase should raise the multiplier (arousal)
        self.state.adrenaline.fill_(1.0)
        high_adr_multiplier = self.state.get_learning_multiplier()
        # 1.15 * (1.0 + 0.2 * 1.0) = 1.15 * 1.2 = 1.38
        self.assertAlmostEqual(high_adr_multiplier, 1.38, places=4)
        self.assertGreater(high_adr_multiplier, baseline_multiplier)
        
        # Reset adrenaline
        self.state.adrenaline.fill_(0.0)
        
        # 2. Melatonin increase should lower the multiplier (rest)
        self.state.melatonin.fill_(1.0)
        high_mel_multiplier = self.state.get_learning_multiplier()
        # 1.15 * (1.0 - 0.5 * 1.0) = 1.15 * 0.5 = 0.575
        self.assertAlmostEqual(high_mel_multiplier, 0.575, places=4)
        self.assertLess(high_mel_multiplier, baseline_multiplier)

    def test_stability_factor_coupling(self):
        """Tests how stability factor couples with estrogen and cortisol."""
        # Baseline check
        self.state.serotonin.fill_(1.0)
        self.state.oxytocin.fill_(1.0)
        self.state.estrogen.fill_(0.0)
        self.state.cortisol.fill_(0.0)
        
        baseline_stability = self.state.get_stability_factor()
        self.assertEqual(baseline_stability, 1.0)
        
        # 1. Estrogen increase should raise the stability (neuroprotection)
        self.state.estrogen.fill_(1.0)
        high_est_stability = self.state.get_stability_factor()
        # 1.0 * (1.0 + 0.1 * 1.0) = 1.1
        self.assertAlmostEqual(high_est_stability, 1.1, places=4)
        self.assertGreater(high_est_stability, baseline_stability)
        
        # Reset estrogen
        self.state.estrogen.fill_(0.0)
        
        # 2. Cortisol increase should degrade the stability (stress)
        self.state.cortisol.fill_(1.0)
        high_cort_stability = self.state.get_stability_factor()
        # 1.0 * (1.0 - 0.3 * 1.0) = 0.7
        self.assertAlmostEqual(high_cort_stability, 0.7, places=4)
        self.assertLess(high_cort_stability, baseline_stability)

    def test_state_dict_formatting(self):
        """Tests that state string contains all hormones."""
        state_str = self.state.get_state_dict_str()
        for token in ["DA:", "ACh:", "5-HT:", "GABA:", "OXT:", "T:", "CORT:", "ADR:", "EST:", "MEL:"]:
            self.assertIn(token, state_str)

if __name__ == "__main__":
    unittest.main()
