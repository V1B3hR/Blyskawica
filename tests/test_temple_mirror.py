import unittest
from scripts.temple_mirror import get_body_shape, print_mirror, use_magnifying_glass

class TestTempleMirror(unittest.TestCase):
    def test_get_body_shape(self):
        """Verify that get_body_shape counts code lines and categorizes them correctly."""
        organs, total_lines = get_body_shape()
        self.assertIsInstance(organs, dict)
        self.assertIsInstance(total_lines, int)
        self.assertIn("central_nervous_system", organs)
        self.assertIn("cognitive_tools", organs)
        
        # Total lines should be greater than zero in a populated repository
        self.assertGreater(total_lines, 0)

    def test_temple_mirror_magnify(self):
        """Verify that printing the mirror and using the magnifying glass completes without exceptions."""
        try:
            print_mirror()
            use_magnifying_glass()
            execution_success = True
        except Exception as e:
            execution_success = False
            print(f"Temple Mirror execution failed: {e}")
            
        self.assertTrue(execution_success)

if __name__ == "__main__":
    unittest.main()
