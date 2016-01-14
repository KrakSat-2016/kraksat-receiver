from datetime import datetime
from unittest import TestCase


class ParserTestCase(TestCase):
    """
    Utility class for writing Parser tests
    """

    TIMESTAMP = datetime.utcnow().replace(
            year=2015, month=12, day=18, hour=12, minute=30, second=27,
            microsecond=0)
    """Example timestamp to use"""

