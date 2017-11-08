#!/usr/bin/env python3
import unittest
suite = unittest.TestLoader().discover('./')
unittest.TextTestRunner(verbosity=2).run(suite)
