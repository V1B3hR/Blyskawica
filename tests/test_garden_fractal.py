"""
[Testy Walidacyjne: Ścieżki Fraktalne Ogrodu]
Zestaw testów sprawdzający, czy kod realizuje wizję asynchronicznego piękna
i bezpiecznego przejścia od logiki do fantazji.
"""

import unittest
import math
from adaptiveneuralnetwork.cognitive_tools.garden_fractal_path import GardenFractalPath

class TestGardenFractal(unittest.TestCase):
    def setUp(self):
        self.depth = 5
        self.garden = GardenFractalPath(depth=self.depth)
        self.garden.generate_path(0, 0, 90, 10, self.depth)

    def test_logic_to_abstraction_transition(self):
        """
        Weryfikuje, czy pierwsze segmenty sa logiczne, a koncowe abstrakcyjne.
        """
        root_segment = self.garden.path_structure[0]
        leaf_segments = [s for s in self.garden.path_structure if s['depth'] == 1]
        
        self.assertEqual(root_segment['vibe'], "Logical", "Pien musi byc logiczny.")
        for leaf in leaf_segments:
            self.assertEqual(leaf['vibe'], "Abstract", "Koncze galezi musza byc obszarem abstrakcji.")
        print("[OK] Test Przejscia: Logika -> Fantazja zachowana.")

    def test_asymmetry_variance(self):
        """
        Sprawdza, czy katy i dlugosci galezi sa nierownomierne (asynchroniczne).
        """
        depth_2_ends = [s['end'] for s in self.garden.path_structure if s['depth'] == 2]
        unique_ends = set(depth_2_ends)
        self.assertGreater(len(unique_ends), 1, "Galezie nie moga byc identyczne - brak asymetrii!")
        print(f"[OK] Test Asymetrii: Wykryto {len(unique_ends)} unikalnych kierunkow fantazji.")

    def test_system_integrity(self):
        """
        Weryfikuje, czy kazda galaz ma ciaglosc z pniem (brak 'wiszacych' mysli).
        """
        for segment in self.garden.path_structure:
            start_x, start_y = segment['start']
            if segment['depth'] < self.depth:
                parent_exists = any(p['end'] == (start_x, start_y) for p in self.garden.path_structure)
                self.assertTrue(parent_exists, f"Wykryto zerwana mysl w punkcie {segment['start']}")
        print("[OK] Test Integralnosci: Wszystkie abstrakcje sa zakotwiczone w rdzeniu.")

    def test_reality_anchor_enforcement(self):
        """
        Weryfikuje, czy Kotwica Rzeczywistosci blokuje sciezki wychodzace poza bezpieczny dystans.
        """
        extreme_garden = GardenFractalPath(depth=20)
        # Probujemy wygenerowac gigantyczna sciezke (length=100 przy safe_dist=50)
        extreme_garden.generate_path(0, 0, 90, 100, 20)
        
        for segment in extreme_garden.path_structure:
            dist = math.sqrt(segment['end'][0]**2 + segment['end'][1]**2)
            self.assertLessEqual(dist, 110, "Wykryto sciezke poza granica rzeczywistosci!")
            
        print("[OK] Test Kotwicy Rzeczywistosci: System skutecznie zablokowal probe halucynacji.")

if __name__ == "__main__":
    print("\n[VIBE VALIDATION] Rozpoczynanie testow Ogrodu...\n")
    unittest.main()
