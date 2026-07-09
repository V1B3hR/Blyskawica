#!/usr/bin/env python3
"""
Repository Test Script
Verifies that the Bioart Programming Language repository is set up correctly
"""

import sys
import os

def test_repository_structure():
    """Test that all required files and directories exist"""
    print("🧬 Bioart Programming Language - Repository Test")
    print("=" * 50)
    
    required_files = [
        "README.md",
        "LICENSE", 
        ".gitignore",
        "requirements.txt",
        "src/bioart.py",
        "examples/dna_demo.py",
        "examples/program.dna",
        "tests/advanced_tests.py",
        "tests/stress_tests.py",
        "docs/readme.txt",
        "docs/comprehensive_test_summary.txt"
    ]
    
    print("1. Checking repository structure...")
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} files missing!")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present")
        return True

def test_imports():
    """Test that the main module can be imported"""
    print("\n2. Testing module imports...")
    
    try:
        sys.path.insert(0, 'src')
        from bioart import Bioart
        print("   ✓ Bioart imported successfully")
        
        # Test basic functionality
        dna = Bioart()
        test_seq = dna.byte_to_dna(72)  # 'H'
        restored = dna.dna_to_byte(test_seq)
        
        if restored == 72:
            print("   ✓ Basic DNA encoding/decoding works")
            return True
        else:
            print("   ❌ DNA encoding/decoding failed")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Runtime error: {e}")
        return False

def test_examples():
    """Test that examples can be run"""
    print("\n3. Testing examples...")
    
    try:
        # Test demo script
        sys.path.insert(0, 'examples')
        from dna_demo import bioart_encode_demo
        print("   ✓ Demo script imports successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Example import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Example error: {e}")
        return False

def test_documentation():
    """Test that documentation files are readable"""
    print("\n4. Testing documentation...")
    
    try:
        with open('README.md', 'r') as f:
            readme_content = f.read()
            if 'DNA Programming Language' in readme_content or 'Bioart Programming Language' in readme_content:
                print("   ✓ README.md is valid")
            else:
                print("   ❌ README.md content invalid")
                return False
        
        with open('docs/readme.txt', 'r') as f:
            docs_content = f.read()
            if 'DNA Programming Language' in docs_content:
                print("   ✓ Technical documentation is valid")
            else:
                print("   ❌ Technical documentation invalid")
                return False
                
        return True
        
    except Exception as e:
        print(f"   ❌ Documentation test failed: {e}")
        return False

def run_repository_tests():
    """Run all repository tests"""
    print("Testing Bioart Programming Language repository setup...\n")
    
    tests = [
        ("Repository Structure", test_repository_structure),
        ("Module Imports", test_imports),
        ("Examples", test_examples),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print("🎯 Repository Test Results")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ REPOSITORY SETUP SUCCESSFUL")
        print("\nThe Bioart Programming Language repository is ready to use!")
        print("\nQuick start:")
        print("  python examples/dna_demo.py")
        print("  python src/bioart.py")
        return True
    else:
        print("❌ REPOSITORY SETUP ISSUES DETECTED")
        print("Please check the missing files or errors above.")
        return False

if __name__ == "__main__":
    success = run_repository_tests()
    sys.exit(0 if success else 1) 