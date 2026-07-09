#!/usr/bin/env python3
"""
Comprehensive tests for the Bioart Translator module
"""

import sys
import os
import tempfile
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from translator import BioartTranslator, translate_text_to_dna, translate_dna_to_text


class TestBioartTranslator(unittest.TestCase):
    """Test suite for BioartTranslator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.translator = BioartTranslator()
    
    # ======================================
    # TEXT TO DNA TRANSLATION TESTS
    # ======================================
    
    def test_text_to_dna_simple(self):
        """Test simple text to DNA conversion"""
        text = "Hi"
        dna = self.translator.text_to_dna(text)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
        self.assertEqual(len(dna), len(text) * 4)  # 4 nucleotides per byte
    
    def test_text_to_dna_longer(self):
        """Test longer text to DNA conversion"""
        text = "Hello, World!"
        dna = self.translator.text_to_dna(text)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
        self.assertEqual(len(dna), len(text.encode('utf-8')) * 4)
    
    def test_text_to_dna_empty(self):
        """Test empty text to DNA conversion"""
        text = ""
        dna = self.translator.text_to_dna(text)
        self.assertEqual(dna, "")
    
    def test_text_to_dna_special_chars(self):
        """Test special characters in text to DNA conversion"""
        text = "!@#$%^&*()"
        dna = self.translator.text_to_dna(text)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
    
    def test_text_to_dna_unicode(self):
        """Test unicode text to DNA conversion"""
        text = "Hello 世界 🌍"
        dna = self.translator.text_to_dna(text)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
    
    # ======================================
    # DNA TO TEXT TRANSLATION TESTS
    # ======================================
    
    def test_dna_to_text_simple(self):
        """Test simple DNA to text conversion"""
        text = "Hi"
        dna = self.translator.text_to_dna(text)
        restored = self.translator.dna_to_text(dna)
        self.assertEqual(restored, text)
    
    def test_dna_to_text_longer(self):
        """Test longer DNA to text conversion"""
        text = "Hello, World!"
        dna = self.translator.text_to_dna(text)
        restored = self.translator.dna_to_text(dna)
        self.assertEqual(restored, text)
    
    def test_dna_to_text_roundtrip(self):
        """Test complete roundtrip for various texts"""
        test_texts = [
            "A",
            "Hello",
            "The quick brown fox jumps over the lazy dog",
            "1234567890",
            "!@#$%^&*()",
        ]
        for text in test_texts:
            with self.subTest(text=text):
                dna = self.translator.text_to_dna(text)
                restored = self.translator.dna_to_text(dna)
                self.assertEqual(restored, text)
    
    # ======================================
    # BINARY TO DNA TRANSLATION TESTS
    # ======================================
    
    def test_binary_to_dna_bytes(self):
        """Test bytes to DNA conversion"""
        data = b"Hello"
        dna = self.translator.binary_to_dna(data)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
        self.assertEqual(len(dna), len(data) * 4)
    
    def test_binary_to_dna_bytearray(self):
        """Test bytearray to DNA conversion"""
        data = bytearray([72, 101, 108, 108, 111])
        dna = self.translator.binary_to_dna(data)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
    
    def test_binary_to_dna_list(self):
        """Test list of integers to DNA conversion"""
        data = [72, 101, 108, 108, 111]
        dna = self.translator.binary_to_dna(data)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
    
    def test_dna_to_binary_roundtrip(self):
        """Test complete binary roundtrip"""
        test_data = [
            b"Hello",
            b"\x00\x01\x02\x03\x04",
            b"\xff\xfe\xfd\xfc",
            bytes(range(256))  # All possible byte values
        ]
        for data in test_data:
            with self.subTest(data=data[:10]):  # Show first 10 bytes in subtest
                dna = self.translator.binary_to_dna(data)
                restored = self.translator.dna_to_binary(dna)
                self.assertEqual(restored, data)
    
    # ======================================
    # FILE OPERATIONS TESTS
    # ======================================
    
    def test_file_to_dna_and_back(self):
        """Test file to DNA conversion and back"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_data = "Hello, World!\nThis is a test file."
            f.write(test_data)
            temp_file = f.name
        
        try:
            # Convert file to DNA
            dna = self.translator.file_to_dna(temp_file)
            self.assertIsInstance(dna, str)
            self.assertTrue(all(c in 'AUCG' for c in dna))
            
            # Convert DNA back to file
            output_file = temp_file + '.restored'
            self.translator.dna_to_file(dna, output_file)
            
            # Verify restored file
            with open(output_file, 'r') as f:
                restored_data = f.read()
            self.assertEqual(restored_data, test_data)
            
            # Clean up
            os.unlink(output_file)
        finally:
            os.unlink(temp_file)
    
    def test_file_to_dna_binary(self):
        """Test binary file to DNA conversion"""
        # Create temporary binary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            test_data = bytes(range(256))
            f.write(test_data)
            temp_file = f.name
        
        try:
            # Convert to DNA and back
            dna = self.translator.file_to_dna(temp_file)
            output_file = temp_file + '.restored'
            self.translator.dna_to_file(dna, output_file)
            
            # Verify
            with open(output_file, 'rb') as f:
                restored_data = f.read()
            self.assertEqual(restored_data, test_data)
            
            # Clean up
            os.unlink(output_file)
        finally:
            os.unlink(temp_file)
    
    # ======================================
    # MODIFICATION TESTS
    # ======================================
    
    def test_modify_nucleotide(self):
        """Test single nucleotide modification"""
        dna = "AAAA"
        modified = self.translator.modify_nucleotide(dna, 0, 'G')
        self.assertEqual(modified, "GAAA")
        
        modified = self.translator.modify_nucleotide(dna, 3, 'U')
        self.assertEqual(modified, "AAAU")
    
    def test_modify_nucleotide_invalid(self):
        """Test invalid nucleotide modification"""
        dna = "AAAA"
        with self.assertRaises(ValueError):
            self.translator.modify_nucleotide(dna, 0, 'X')
        
        with self.assertRaises(ValueError):
            self.translator.modify_nucleotide(dna, 10, 'A')
    
    def test_insert_sequence(self):
        """Test sequence insertion"""
        dna = "AAAA"
        modified = self.translator.insert_sequence(dna, 2, "UU")
        self.assertEqual(modified, "AAUUAA")
        
        modified = self.translator.insert_sequence(dna, 0, "GG")
        self.assertEqual(modified, "GGAAAA")
        
        modified = self.translator.insert_sequence(dna, 4, "CC")
        self.assertEqual(modified, "AAAACC")
    
    def test_delete_sequence(self):
        """Test sequence deletion"""
        dna = "AAAUUUGGGG"
        modified = self.translator.delete_sequence(dna, 3, 3)
        self.assertEqual(modified, "AAAGGGG")
        
        modified = self.translator.delete_sequence(dna, 0, 4)
        self.assertEqual(modified, "UUGGGG")
    
    def test_replace_sequence(self):
        """Test sequence replacement"""
        dna = "AAAAUUUU"
        modified = self.translator.replace_sequence(dna, 2, 4, "GG")
        self.assertEqual(modified, "AAGGUU")  # Replace 4 chars starting at pos 2 with "GG"
        
        modified = self.translator.replace_sequence(dna, 0, 4, "CCCC")
        self.assertEqual(modified, "CCCCUUUU")
    
    # ======================================
    # VALIDATION TESTS
    # ======================================
    
    def test_validate_dna_valid(self):
        """Test DNA validation with valid sequences"""
        valid_sequences = [
            "AAAA",
            "AUCG",
            "aucg",  # lowercase
            "AAAUUUCCGGG",
            "A" * 100
        ]
        for seq in valid_sequences:
            with self.subTest(seq=seq[:20]):
                self.assertTrue(self.translator.validate_dna(seq))
    
    def test_validate_dna_invalid(self):
        """Test DNA validation with invalid sequences"""
        invalid_sequences = [
            "AAAX",
            "123",
            "ATCG",  # T instead of U
            "AAA UCG",  # space
            "AAA\nUCG",  # newline
        ]
        for seq in invalid_sequences:
            with self.subTest(seq=seq):
                self.assertFalse(self.translator.validate_dna(seq))
    
    def test_verify_reversibility_text(self):
        """Test reversibility verification for text"""
        text = "Hello, World!"
        result = self.translator.verify_reversibility(text)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['match'])
        self.assertEqual(result['original_size'], len(text))
        self.assertEqual(result['restored_size'], len(text.encode('utf-8')))
        self.assertIsNone(result['error'])
    
    def test_verify_reversibility_binary(self):
        """Test reversibility verification for binary"""
        data = bytes(range(256))
        result = self.translator.verify_reversibility(data)
        
        self.assertTrue(result['success'])
        self.assertTrue(result['match'])
        self.assertEqual(result['original_size'], len(data))
        self.assertEqual(result['restored_size'], len(data))
        self.assertIsNone(result['error'])
    
    # ======================================
    # UTILITY TESTS
    # ======================================
    
    def test_get_sequence_info(self):
        """Test sequence information retrieval"""
        dna = "AUCGAUCG"
        info = self.translator.get_sequence_info(dna)
        
        self.assertEqual(info['length'], 8)
        self.assertEqual(info['byte_capacity'], 2)
        self.assertTrue(info['is_valid'])
        self.assertTrue(info['is_complete'])
        self.assertEqual(info['nucleotide_counts']['A'], 2)
        self.assertEqual(info['nucleotide_counts']['U'], 2)
        self.assertEqual(info['nucleotide_counts']['C'], 2)
        self.assertEqual(info['nucleotide_counts']['G'], 2)
    
    def test_get_sequence_info_incomplete(self):
        """Test sequence info for incomplete sequence"""
        dna = "AUCGAU"  # Not divisible by 4
        info = self.translator.get_sequence_info(dna)
        
        self.assertEqual(info['length'], 6)
        self.assertEqual(info['byte_capacity'], 1)  # Floor division
        self.assertTrue(info['is_valid'])
        self.assertFalse(info['is_complete'])
    
    def test_format_dna(self):
        """Test DNA formatting"""
        dna = "AAAUUUCCGGGAAAUUUCCGGG"
        formatted = self.translator.format_dna(dna, width=20, group_size=4)
        
        self.assertIn("AAAU", formatted)
        self.assertIn(" ", formatted)  # Should have spaces between groups
    
    def test_get_stats(self):
        """Test statistics tracking"""
        # Reset stats
        self.translator.reset_stats()
        
        # Perform operations
        self.translator.text_to_dna("Hello")
        self.translator.text_to_dna("World")
        dna = self.translator.text_to_dna("Test")
        self.translator.dna_to_text(dna)
        
        stats = self.translator.get_stats()
        self.assertEqual(stats['translations'], 3)
        self.assertEqual(stats['reversals'], 1)
    
    def test_reset_stats(self):
        """Test statistics reset"""
        self.translator.text_to_dna("Test")
        self.translator.reset_stats()
        
        stats = self.translator.get_stats()
        self.assertEqual(stats['translations'], 0)
        self.assertEqual(stats['reversals'], 0)
        self.assertEqual(stats['modifications'], 0)
        self.assertEqual(stats['validations'], 0)
    
    # ======================================
    # CONVENIENCE FUNCTION TESTS
    # ======================================
    
    def test_convenience_functions(self):
        """Test module-level convenience functions"""
        text = "Hello"
        
        # Test text translation
        dna = translate_text_to_dna(text)
        self.assertIsInstance(dna, str)
        self.assertTrue(all(c in 'AUCG' for c in dna))
        
        restored = translate_dna_to_text(dna)
        self.assertEqual(restored, text)
    
    # ======================================
    # EDGE CASES AND STRESS TESTS
    # ======================================
    
    def test_all_byte_values(self):
        """Test all possible byte values 0-255"""
        data = bytes(range(256))
        dna = self.translator.binary_to_dna(data)
        restored = self.translator.dna_to_binary(dna)
        self.assertEqual(restored, data)
    
    def test_large_text(self):
        """Test large text conversion"""
        text = "A" * 10000
        dna = self.translator.text_to_dna(text)
        restored = self.translator.dna_to_text(dna)
        self.assertEqual(restored, text)
    
    def test_repeated_conversions(self):
        """Test multiple roundtrip conversions"""
        text = "Test data"
        current = text
        
        for _ in range(10):
            dna = self.translator.text_to_dna(current)
            current = self.translator.dna_to_text(dna)
        
        self.assertEqual(current, text)


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.translator = BioartTranslator()
    
    def test_store_document(self):
        """Test storing a document in DNA"""
        document = """
        Important Document
        ==================
        This is a test document that needs to be stored in DNA format.
        It contains multiple lines and special characters!
        """
        
        dna = self.translator.text_to_dna(document)
        restored = self.translator.dna_to_text(dna)
        self.assertEqual(restored, document)
    
    def test_store_json_data(self):
        """Test storing JSON data in DNA"""
        import json
        data = {"name": "Test", "value": 123, "items": [1, 2, 3]}
        json_str = json.dumps(data)
        
        dna = self.translator.text_to_dna(json_str)
        restored = self.translator.dna_to_text(dna)
        restored_data = json.loads(restored)
        
        self.assertEqual(restored_data, data)
    
    def test_store_program_code(self):
        """Test storing program code in DNA"""
        code = """
def hello_world():
    print("Hello, World!")
    return 42
"""
        dna = self.translator.text_to_dna(code)
        restored = self.translator.dna_to_text(dna)
        self.assertEqual(restored, code)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("BIOART TRANSLATOR TEST SUITE")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBioartTranslator))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print(f"Success rate:  {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
