from app.parser.kundt import KundtParser
from app.tests.parser import ParserTestCase


class KundtTests(ParserTestCase):
    parser_class = KundtParser

    def test_kundt(self):
        """Test parsing Kundt tube (<number>,<number>) message"""
        d = self.parse('7530,400')
        self.assertDictAlmostEqual(
                d, {'frequency': 2133.26, 'amplitude': 1024}, places=2)

    def test_can_parse(self):
        """Test can_parse method of KundtParser class"""
        self.assertEqual(self.parser.can_parse('123,456'), 'KUNDT')
        self.assertEqual(self.parser.can_parse('123,45f'), False)
        self.assertEqual(self.parser.can_parse('KUNDT,123,456'), False)
        self.assertEqual(self.parser.can_parse('123,456,789'), False)
        self.assertEqual(self.parser.can_parse('foobar'), False)
