#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

path = str(Path(__file__).parent.absolute())
suite = unittest.TestLoader().discover(path)
result = unittest.TextTestRunner(verbosity=2).run(suite)

sys.exit(not result.wasSuccessful())
