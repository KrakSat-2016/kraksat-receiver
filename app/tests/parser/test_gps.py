from unittest import TestCase

from app.parser import gps, ParseError
from app.parser.gps import GPSParser
from app.tests.parser import ParserTestCase

GPGGA_LINE = ('$GPGGA,123519,4807.038,N,01130.000,W,1,03,0.9,545.4,M,46.9,M,,'
              '*5F')
GPGGA_NO_FIX_LINE = '$GPGGA,002905.799,,,,,0,00,,,M,,M,,*71'
GPGSA_LINE = '$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39'
GPGSA_NO_FIX_LINE = '$GPGSA,A,1,,,,,,,,,,,,,,,*1E'
GPGSV_LINE = ('$GPGSV,1,1,04,01,40,083,46,02,17,308,41,12,07,344,39,14,22,'
              '228,45*7A')
GPRMC_LINE = ('$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,'
              '003.1,W*6A')
GPRMC_NO_FIX_LINE = '$GPRMC,002905.799,V,,,,,0.00,0.00,060180,,,N*4B'
GPVTG_LINE = '$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48'
GPVTG_NO_FIX_LINE = '$GPVTG,0.00,T,,M,0.00,N,0.00,K,N*32'


class GPSTests(ParserTestCase):
    parser_class = GPSParser

    def test_gpgga(self):
        """Test parsing GPGGA message"""
        self.parse('$GPGGA', GPGGA_LINE)
        data = {'latitude': 48.1173, 'longitude': -11.5, 'altitude': 545.4,
                'active_satellites': 3, 'quality': 'gps'}
        self.assertEqual(self.parser.data, data)

    def test_gpgga_no_fix(self):
        """Test parsing GPGGA without fix message"""
        self.parse('$GPGGA', GPGGA_NO_FIX_LINE)
        data = {'quality': 'no_fix', 'active_satellites': 0}
        self.assertEqual(self.parser.data, data)

    def test_gpgsa(self):
        """Test parsing GPGSA message"""
        self.parse('$GPGSA', GPGSA_LINE)
        data = {'fix_type': '3d', 'pdop': 2.5, 'hdop': 1.3, 'vdop': 2.1}
        self.assertEqual(self.parser.data, data)

    def test_gpgsa_no_fix(self):
        """Test parsing GPGSA without fix message"""
        self.parse('$GPGSA', GPGSA_NO_FIX_LINE)
        data = {'fix_type': 'no_fix'}
        self.assertEqual(self.parser.data, data)

    def test_gpgsv(self):
        """Test parsing GPGSV message"""
        self.parse('$GPGSV', GPGSV_LINE)
        data = {'satellites_in_view': 4}
        self.assertEqual(self.parser.data, data)

    def test_gprmc(self):
        """Test parsing GPRMC message"""
        self.parse('$GPRMC', GPRMC_LINE)
        data = {'direction': 84.4, 'speed_over_ground': 41.4848}
        self.assertEqual(self.parser.data, data)

    def test_gprmc_no_fix(self):
        """Test parsing GPRMC without fix message"""
        self.parse('$GPRMC', GPRMC_NO_FIX_LINE)
        self.assertEqual(self.parser.data, {})

    def test_gpvtg(self):
        """Test parsing GPVTG message"""
        data = {'timestamp': self.TIMESTAMP}
        self.assertEqual(self.parse('$GPVTG', GPVTG_LINE), data)
        self.assertEqual(self.parser.data, data)

    def test_gpvtg_no_fix(self):
        """Test parsing GPVTG without fix message"""
        data = {'timestamp': self.TIMESTAMP}
        self.assertEqual(self.parse('$GPVTG', GPVTG_NO_FIX_LINE), data)
        self.assertEqual(self.parser.data, data)

    def test_parse(self):
        """Test parsing multiple messages"""
        data = {
            'timestamp': self.TIMESTAMP,
            'latitude': 48.1173, 'longitude': -11.5, 'altitude': 545.4,
            'quality': 'gps', 'direction': 84.4, 'speed_over_ground': 41.4848,
            'fix_type': '3d', 'pdop': 2.5, 'hdop': 1.3, 'vdop': 2.1,
            'active_satellites': 3, 'satellites_in_view': 4
        }
        self.assertEqual(self.parse('$GPGGA', GPGGA_LINE), None)
        self.assertEqual(self.parse('$GPGSA', GPGSA_LINE), None)
        self.assertEqual(self.parse('$GPGSV', GPGSV_LINE), None)
        self.assertEqual(self.parse('$GPRMC', GPRMC_LINE), None)
        self.assertEqual(self.parse('$GPVTG', GPVTG_LINE), data)

    def test_parse_no_fix(self):
        """Test parsing multiple messages without fix"""
        data = {'timestamp': self.TIMESTAMP, 'active_satellites': 0,
                'quality': 'no_fix', 'fix_type': 'no_fix'}
        self.assertEqual(self.parse('$GPGGA', GPGGA_NO_FIX_LINE), None)
        self.assertEqual(self.parse('$GPGSA', GPGSA_NO_FIX_LINE), None)
        self.assertEqual(self.parse('$GPRMC', GPRMC_NO_FIX_LINE), None)
        self.assertEqual(self.parse('$GPVTG', GPVTG_NO_FIX_LINE), data)


class TestGPSUtils(TestCase):
    def test_checksum_valid(self):
        """Test checksum_valid function"""
        self.assertEqual(gps.checksum_valid(
                '$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39'),
                '$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1')
        self.assertEqual(gps.checksum_valid(
                '$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48'),
                '$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K')
        self.assertRaises(ParseError, gps.checksum_valid,
                          '$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*4')
        self.assertRaises(ParseError, gps.checksum_valid,
                          '$GPGSA,B,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39')
        self.assertRaises(ParseError, gps.checksum_valid, 'random')
        self.assertRaises(ParseError, gps.checksum_valid, '$lol')
        self.assertRaises(ParseError, gps.checksum_valid, 'lol*')
