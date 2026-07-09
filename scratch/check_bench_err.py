import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

try:
    print("Loading test suite...")
    suite = unittest.TestLoader().loadTestsFromName('tests.test_basic_problem_solving')
    print(f"Suite loaded. Number of tests: {suite.countTestCases()}")
    
    import io
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("Errors:")
    for err in result.errors:
        print(err[0])
        print(err[1])
    print("Failures:")
    for fail in result.failures:
        print(fail[0])
        print(fail[1])
except Exception as e:
    print(f"Exception: {e}")
