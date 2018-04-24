"""

"""
"""Modifying the testing structure to include a class setup and teardown"""
from unittest import TestCase
import warnings


class TestClass(TestCase):
    def setUp(self):
        """setUp is called before each test is run, tearDown is called after"""
        pass
    def tearDown(self):
        pass
