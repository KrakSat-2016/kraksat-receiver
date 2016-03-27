import unittest
from app.humanize import format_size


class HumanizeTests(unittest.TestCase):
    def test_format_size(self):
        self.assertEqual(format_size(999), '999B')
        self.assertEqual(format_size(1000), '1.0kB')
        self.assertEqual(format_size(1e6), '1.0MB')
        self.assertEqual(format_size(1.8e9), '1.8GB')
        self.assertEqual(format_size(1e12), '1.0TB')
        self.assertEqual(format_size(1e15), '1000.0TB')
        self.assertEqual(format_size(0), '0B')
        self.assertEqual(format_size(-1000), '-1.0kB')
