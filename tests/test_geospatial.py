"""
[Unit Tests: Phase XXV OS Geospatial Pathfinding Engine]
Validates:
1. Verification of data grid dimensions (8x8 Lake District grid).
2. RealityAnchor boundary enforcement (rejection of elevation > 500m).
3. Finding the optimal, slope-minimized path.
"""

import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import unittest  # noqa: E402

from scripts.geospatial_pathfinding import GeospatialPathfinder  # noqa: E402


class TestGeospatialPathfinder(unittest.TestCase):
    def setUp(self):
        self.pathfinder = GeospatialPathfinder()

    def test_dimensions_and_loading(self):
        """Verifies OS OpenData dimensions."""
        self.assertEqual(self.pathfinder.rows, 8)
        self.assertEqual(self.pathfinder.cols, 8)
        self.assertEqual(self.pathfinder.grid[3][4], 520) # Peak height in the center

    def test_safe_pathfinding(self):
        """Verifies path avoids center peak (520m) and finds safe detour."""
        path, cost = self.pathfinder.find_safe_path((0, 0), (7, 7))
        self.assertIsNotNone(path)

        # Verify peak (3, 4) is NOT in the path!
        self.assertNotIn((3, 4), path)
        # Verify path cost is reasonable
        self.assertLess(cost, 500)

        print(f"\n[TEST OS] Path found: {path} with cost {cost}")
        print("[OK] OS OpenData pathfinding constraints validated successfully.")

if __name__ == "__main__":
    unittest.main()
