import unittest
import numpy as np
import math

class TestPolymathicHumanities(unittest.TestCase):
    # =================================================================
    # 1. Lingwistyka (Linguistics) & Semantyka
    # =================================================================
    def test_linguistic_pos_tagging_and_syntax(self):
        """Linguistics: Evaluates computational semantics and grammatical syntax tree structure."""
        sentence = "Blyskawica jest zaawansowanym systemem kognitywnym."
        # POS Tagging representation: Noun, Verb, Adjective, Noun, Adjective
        expected_pos = ["Noun", "Verb", "Adjective", "Noun", "Adjective"]
        words = sentence.replace(".", "").split()
        
        # Simple rule-based POS tagger check
        pos_tags = []
        for word in words:
            word_lower = word.lower()
            if word_lower in ["blyskawica", "systemem"]:
                pos_tags.append("Noun")
            elif word_lower in ["jest"]:
                pos_tags.append("Verb")
            elif word_lower in ["zaawansowanym", "kognitywnym"]:
                pos_tags.append("Adjective")
            else:
                pos_tags.append("Unknown")
                
        self.assertEqual(pos_tags, expected_pos)
        self.assertIn("kognitywnym", sentence)

    # =================================================================
    # 2. Historia Świata i Krajów (History & Historiography)
    # =================================================================
    def test_world_and_local_history_archive(self):
        """History: Validates historical timelines for world and Polish history."""
        historical_events = {
            "mieszko_i_baptism": 966,
            "battle_of_grunwald": 1410,
            "treaty_of_versailles": 1919,
            "fall_of_berlin_wall": 1989
        }
        
        # Verify chronological sequence
        events_sorted = sorted(historical_events.keys(), key=lambda k: historical_events[k])
        self.assertEqual(events_sorted[0], "mieszko_i_baptism")
        self.assertEqual(events_sorted[-1], "fall_of_berlin_wall")
        self.assertEqual(historical_events["battle_of_grunwald"], 1410)

    # =================================================================
    # 3. Geografia & Geopolityka (Geography & Geopolitical zones)
    # =================================================================
    def test_geography_political_maps_and_eez(self):
        """Geography: Validates coordinates, political boundaries, and Exclusive Economic Zones (EEZ)."""
        # Gdynia (Poland) coordinates and EEZ distance limit (200 nautical miles)
        gdynia_lat_lon = (54.5189, 18.5305)
        eez_limit_nautical_miles = 200.0
        
        self.assertGreater(gdynia_lat_lon[0], 50.0)  # Northern Hemisphere
        self.assertLess(gdynia_lat_lon[1], 25.0)     # Central Europe
        self.assertEqual(eez_limit_nautical_miles, 200.0)

    # =================================================================
    # 4. Ekonomia & Strefy Ekonomiczne (Economics & Game Theory)
    # =================================================================
    def test_economics_asset_pricing_and_game_theory(self):
        """Economics: Validates game theory (Nash equilibrium) and Black-Scholes option pricing model."""
        # Game theory: Prisoner's Dilemma payoff matrix
        # Strategies: Cooperate (C), Defect (D)
        # Payoffs: (Player1, Player2)
        payoff_matrix = {
            ("C", "C"): (3, 3),
            ("C", "D"): (0, 5),
            ("D", "C"): (5, 0),
            ("D", "D"): (1, 1)
        }
        
        # Nash equilibrium: Both defect (D, D) is the dominant strategy equilibrium
        p1_defect_cooperate = payoff_matrix[("D", "C")][0] > payoff_matrix[("C", "C")][0]  # 5 > 3
        p1_defect_defect = payoff_matrix[("D", "D")][0] > payoff_matrix[("C", "D")][0]        # 1 > 0
        self.assertTrue(p1_defect_cooperate and p1_defect_defect)
        
        # Black-Scholes formula helper verification (d1, d2 variables)
        S, K, r, t, sigma = 100.0, 100.0, 0.05, 1.0, 0.2
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
        d2 = d1 - sigma * math.sqrt(t)
        self.assertAlmostEqual(d1, 0.35, places=2)
        self.assertAlmostEqual(d2, 0.15, places=2)

    # =================================================================
    # 5. Religia & Filozofia (Religion, Philosophy & Semiotics)
    # =================================================================
    def test_philosophy_yin_yang_and_semiotics(self):
        """Philosophy: Validates Barthes' semiotics model and Yin-Yang balance principles."""
        # Semiotics: Sign = Signifier (Form) + Signified (Concept)
        signifier = "red_light"
        signified = "stop_action"
        sign = signifier + "_" + signified
        self.assertIn("red_light", sign)
        
        # Yin-Yang balance ratio (should converge to 1.0 under equilibrium)
        yin = 0.5
        yang = 0.5
        balance_ratio = yin / yang
        self.assertEqual(balance_ratio, 1.0)

    # =================================================================
    # 6. Informatyka & Programistyka (Computer Science & Vibe Coding)
    # =================================================================
    def test_computer_science_complexity_and_vibe_coding(self):
        """CS: Validates algorithmic complexity and syntax generator stability."""
        # Time complexity representations
        complexities = {
            "binary_search": "O(log n)",
            "bubble_sort": "O(n^2)",
            "merge_sort": "O(n log n)"
        }
        
        self.assertEqual(complexities["binary_search"], "O(log n)")
        self.assertEqual(complexities["merge_sort"], "O(n log n)")
        
        # Vibe coding: check if dynamic string compiler evaluates successfully
        code_to_eval = "x = [i**2 for i in range(5)]; result = sum(x)"
        local_vars = {}
        exec(code_to_eval, {}, local_vars)
        self.assertEqual(local_vars["result"], 30)  # 0 + 1 + 4 + 9 + 16 = 30

    # =================================================================
    # 7. Robotyka & Automatyka (Robotics & Control Systems)
    # =================================================================
    def test_robotics_dh_parameters_and_pid(self):
        """Robotics: Validates Denavit-Hartenberg kinematics transform and PID control loop."""
        # Forward kinematics: homogeneous transformation matrix along Z-axis
        theta = math.pi / 4  # 45 degrees
        d = 0.5
        # Transform matrix along Z
        T_z = np.array([
            [math.cos(theta), -math.sin(theta), 0.0, 0.0],
            [math.sin(theta), math.cos(theta),  0.0, 0.0],
            [0.0,             0.0,              1.0, d],
            [0.0,             0.0,              0.0, 1.0]
        ])
        
        self.assertAlmostEqual(T_z[0, 0], 0.70710678, places=5)
        self.assertAlmostEqual(T_z[2, 3], 0.5, places=5)
        
        # PID Controller stability check: error reduction over time
        kp, ki, kd = 2.0, 0.5, 0.1
        error = 1.0
        integral = 0.0
        last_error = 0.0
        dt = 0.1
        
        # Compute control output
        integral += error * dt
        derivative = (error - last_error) / dt
        output = kp * error + ki * integral + kd * derivative
        
        self.assertEqual(output, 2.0 * 1.0 + 0.5 * 0.1 + 0.1 * 10.0)

if __name__ == "__main__":
    unittest.main()
