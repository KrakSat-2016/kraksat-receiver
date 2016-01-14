from unittest import TestCase

from app.parser import gps, ParseError
from app.parser.gps import GPSParser
from app.tests.parser import ParserTestCase

GPGGA_LINE = ('$GPGGA,123519,4807.038,N,01130.000,E,1,03,0.9,545.4,M,46.9,M,,'
              '*4D')
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
    def setUp(self):
        self.parser = GPSParser()

    def test_gpgga(self):
        """Test parsing GPGGA message"""
        self.parser.parse('$GPGGA', self.TIMESTAMP, GPGGA_LINE)
        data = {'latitude': 48.1173, 'longitude': 11.5, 'altitude': 545.4,
                'active_satellites': 3, 'quality': 'gps'}
        self.assertEqual(self.parser.data, data)

    def test_gpgga_no_fix(self):
        """Test parsing GPGGA without fix message"""
        self.parser.parse('$GPGGA', self.TIMESTAMP, GPGGA_NO_FIX_LINE)
        data = {'quality': 'no_fix', 'active_satellites': 0}
        self.assertEqual(self.parser.data, data)

    def test_gpgsa(self):
        """Test parsing GPGSA message"""
        self.parser.parse('$GPGSA', self.TIMESTAMP, GPGSA_LINE)
        data = {'fix_type': '3d', 'pdop': 2.5, 'hdop': 1.3, 'vdop': 2.1}
        self.assertEqual(self.parser.data, data)

    def test_gpgsa_no_fix(self):
        """Test parsing GPGSA without fix message"""
        self.parser.parse('$GPGSA', self.TIMESTAMP, GPGSA_NO_FIX_LINE)
        data = {'fix_type': 'no_fix'}
        self.assertEqual(self.parser.data, data)

    def test_gpgsv(self):
        """Test parsing GPGSV message"""
        self.parser.parse('$GPGSV', self.TIMESTAMP, GPGSV_LINE)
        data = {'satellites_in_view': 4}
        self.assertEqual(self.parser.data, data)

    def test_gprmc(self):
        """Test parsing GPRMC message"""
        self.parser.parse('$GPRMC', self.TIMESTAMP, GPRMC_LINE)
        data = {'direction': 84.4, 'speed_over_ground': 41.4848}
        self.assertEqual(self.parser.data, data)

    def test_gprmc_no_fix(self):
        """Test parsing GPRMC without fix message"""
        self.parser.parse('$GPRMC', self.TIMESTAMP, GPRMC_NO_FIX_LINE)
        self.assertEqual(self.parser.data, {})

    def test_gpvtg(self):
        """Test parsing GPVTG message"""
        data = {'timestamp': self.TIMESTAMP}
        self.assertEqual(self.parser.parse('$GPVTG', self.TIMESTAMP,
                                           GPVTG_LINE), data)
        self.assertEqual(self.parser.data, data)

    def test_gpvtg_no_fix(self):
        """Test parsing GPVTG without fix message"""
        data = {'timestamp': self.TIMESTAMP}
        self.assertEqual(self.parser.parse('$GPVTG', self.TIMESTAMP,
                                           GPVTG_NO_FIX_LINE), data)
        self.assertEqual(self.parser.data, data)

    def test_parse(self):
        """Test parsing multiple messages"""
        data = {
            'timestamp': self.TIMESTAMP,
            'latitude': 48.1173, 'longitude': 11.5, 'altitude': 545.4,
            'quality': 'gps', 'direction': 84.4, 'speed_over_ground': 41.4848,
            'fix_type': '3d', 'pdop': 2.5, 'hdop': 1.3, 'vdop': 2.1,
            'active_satellites': 3, 'satellites_in_view': 4
        }
        self.assertEqual(self.parser.parse('$GPGGA', self.TIMESTAMP,
                                           GPGGA_LINE), None)
        self.assertEqual(self.parser.parse('$GPGSA', self.TIMESTAMP,
                                           GPGSA_LINE), None)
        self.assertEqual(self.parser.parse('$GPGSV', self.TIMESTAMP,
                                           GPGSV_LINE), None)
        self.assertEqual(self.parser.parse('$GPRMC', self.TIMESTAMP,
                                           GPRMC_LINE), None)
        self.assertEqual(self.parser.parse('$GPVTG', self.TIMESTAMP,
                                           GPVTG_LINE), data)

    def test_parse_no_fix(self):
        """Test parsing multiple messages without fix"""
        data = {'timestamp': self.TIMESTAMP, 'active_satellites': 0,
                'quality': 'no_fix', 'fix_type': 'no_fix'}
        self.assertEqual(self.parser.parse('$GPGGA', self.TIMESTAMP,
                                           GPGGA_NO_FIX_LINE), None)
        self.assertEqual(self.parser.parse('$GPGSA', self.TIMESTAMP,
                                           GPGSA_NO_FIX_LINE), None)
        self.assertEqual(self.parser.parse('$GPRMC', self.TIMESTAMP,
                                           GPRMC_NO_FIX_LINE), None)
        self.assertEqual(self.parser.parse('$GPVTG', self.TIMESTAMP,
                                           GPVTG_NO_FIX_LINE), data)


class TestGPSUtils(TestCase):
    def test_parse_latitude(self):
        """Test parse_latitude function"""
        self.assertAlmostEqual(gps.parse_latitude('3855.23816', 'N'),
                               38.920636, 4)
        self.assertAlmostEqual(gps.parse_latitude('3855.23816', 'S'),
                               -38.920636, 4)
        self.assertRaises(ParseError, gps.parse_latitude, '3855.23816', 'X')

    def test_parse_longitude(self):
        """Test parse_longitude function"""
        self.assertAlmostEqual(gps.parse_longitude('00924.41358', 'E'),
                               9.406893, 4)
        self.assertAlmostEqual(gps.parse_longitude('00924.41358', 'W'),
                               -9.406893, 4)
        self.assertRaises(ParseError, gps.parse_longitude, '3855.23816', 'X')

    def test_parse_quality(self):
        """Test parse_quality function"""
        self.assertEqual(gps.parse_quality('0'), 'no_fix')
        self.assertEqual(gps.parse_quality('1'), 'gps')
        self.assertEqual(gps.parse_quality('2'), 'dgps')
        self.assertRaises(ParseError, gps.parse_quality, '4')
        self.assertRaises(ParseError, gps.parse_quality, 'lol1337')

    def test_parse_fix_type(self):
        """Test parse_fix_type function"""
        self.assertEqual(gps.parse_fix_type('1'), 'no_fix')
        self.assertEqual(gps.parse_fix_type('2'), '2d')
        self.assertEqual(gps.parse_fix_type('3'), '3d')
        self.assertRaises(ParseError, gps.parse_quality, '4')
        self.assertRaises(ParseError, gps.parse_quality, 'lol1337')

    def test_parse_speed(self):
        """Test parse_speed function"""
        self.assertAlmostEqual(gps.parse_speed('31.332'), 58.026864, 3)
        self.assertRaises(ParseError, gps.parse_speed, 'lol1337')

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
