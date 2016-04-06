from unittest.mock import patch

from app.analyzer import Collector
from app.parser.kundt import KundtParser
from app.tests.parser import ParserTestCase


class KundtTests(ParserTestCase):
    parser_class = KundtParser


    def test_kundt(self):
        """Test parsing Kundt tube (<number>,<number>) message"""
        with patch.object(Collector, 'add_value', return_value=None) as \
                add_value:
            collector = Collector()
            self.parse('7530,400', collector)
            add_value.assert_called_once_with(
                self.TIMESTAMP, 'kundt', (8777.05483999469, 400))

    def test_can_parse(self):
        """Test can_parse method of KundtParser class"""
        self.assertEqual(self.parser.can_parse('123,456'), 'KUNDT')
        self.assertEqual(self.parser.can_parse('123,45f'), False)
        self.assertEqual(self.parser.can_parse('KUNDT,123,456'), False)
        self.assertEqual(self.parser.can_parse('123,456,789'), False)
        self.assertEqual(self.parser.can_parse('foobar'), False)
