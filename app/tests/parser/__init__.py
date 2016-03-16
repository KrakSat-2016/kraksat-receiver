from datetime import datetime
from unittest import TestCase

from app.parser import OutputLine


class ParserTestCase(TestCase):
    """
    Utility class for writing Parser tests
    """
    TIMESTAMP = datetime.utcnow().replace(
            year=2015, month=12, day=18, hour=12, minute=30, second=27,
            microsecond=0)
    """Example timestamp to use"""

    parser_class = None

    def setUp(self):
        self.parser = self.parser_class()

    def parse(self, id, line):
        return self.parser.parse(OutputLine(id, self.TIMESTAMP, line))

    def assertDictAlmostEqual(self, first, second, places=7):
        """Assert that all dict items are equal or "almost equal" for floats.

        :param dict first: first dictionary to compare
        :param dict second: second dictionary to compare
        :param int places: number of decimal places to check in case of
            float values
        """
        self.assertEqual(first.keys(), second.keys(),
                         'Dictionary keys are not the same')
        for key in first.keys():
            if isinstance(first[key], float):
                self.assertAlmostEqual(first[key], second[key], places,
                                       "'{}' item is not equal".format(key))
            else:
                self.assertEqual(first[key], second[key],
                                 "'{}' item is not equal".format(key))
