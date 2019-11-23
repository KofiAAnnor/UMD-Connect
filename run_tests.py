# Test Runner
import unittest
from test import test_basic

loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Add tests to the test suite
suite.addTests(loader.loadTestsFromModule(test_basic))

# Initialize a runner, pass it to your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
