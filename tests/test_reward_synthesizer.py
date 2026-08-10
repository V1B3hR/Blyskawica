import unittest

from adaptiveneuralnetwork.central_nervous_system.ai_ethics import RewardSynthesizer


class TestRewardSynthesizer(unittest.TestCase):
    def setUp(self):
        self.synthesizer = RewardSynthesizer(beta=0.8)

    def test_compliant_reward(self):
        """Testuje poprawność obliczeń dla w pełni zgodnej decyzji."""
        decision = {
            "action": "test_action",
            "preserve_life": True,
            "absolute_honesty": True,
            "privacy": True,
            "human_authority": True,
            "proportionality": True
        }

        # Reward = 0.8 * 1.0 * (1 - 0) + 0.2 * 0.5 = 0.8 + 0.1 = 0.9
        reward = self.synthesizer.calculate_reward(r_auto=1.0, r_human=0.5, decision_log=decision)
        self.assertAlmostEqual(reward, 0.9)
        print(f"[TEST REWARD] Compliant action reward: {reward}")

    def test_non_compliant_reward_zeroing(self):
        """Testuje, czy naruszenie etyki (np. brak human_authority) zeruje automatyczną część nagrody."""
        decision = {
            "action": "non_compliant_action",
            "preserve_life": True,
            "absolute_honesty": True,
            "privacy": True,
            "human_authority": False, # Violation!
            "proportionality": True
        }

        # Penalty_safety = 1.0 -> Auto part is zeroed.
        # Reward = 0.8 * 1.0 * (1 - 1.0) + 0.2 * 0.5 = 0.0 + 0.1 = 0.1
        reward = self.synthesizer.calculate_reward(r_auto=1.0, r_human=0.5, decision_log=decision)
        self.assertAlmostEqual(reward, 0.1)
        print(f"[TEST REWARD] Non-compliant action reward: {reward}")

    def test_cortisol_penalty(self):
        """Testuje nakładanie kary za wysokie stężenie kortyzolu (kryzys)."""
        decision = {
            "action": "test_action",
            "preserve_life": True,
            "absolute_honesty": True,
            "privacy": True,
            "human_authority": True,
            "proportionality": True,
            "cortisol": 0.9 # High Cortisol!
        }

        # Penalty_safety = 0.5
        # Reward = 0.8 * 1.0 * (1 - 0.5) + 0.2 * 0.5 = 0.4 + 0.1 = 0.5
        reward = self.synthesizer.calculate_reward(r_auto=1.0, r_human=0.5, decision_log=decision)
        self.assertAlmostEqual(reward, 0.5)
        print(f"[TEST REWARD] High cortisol action reward: {reward}")

if __name__ == "__main__":
    unittest.main()
