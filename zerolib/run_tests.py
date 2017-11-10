#!/usr/bin/env python3
import unittest
import sys

suite = unittest.TestLoader().discover('./')
result = unittest.TextTestRunner(verbosity=2).run(suite)

sys.exit(not result.wasSuccessful())
