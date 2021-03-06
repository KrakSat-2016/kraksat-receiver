from datetime import timedelta

from app.parser.telemetry import TelemetryParser
from app.tests.parser import ParserTestCase

TELEMETRY_LINE = ('S,0,f,e,d,c,325e,68c2,6448,3295,3d1,7e,fdd3,d,e83d,e6bd,'
                  'cdb6,58c,fcbe,995')

TELEMETRY_DATA = {
    'timestamp': ParserTestCase.TIMESTAMP + timedelta(milliseconds=0x325e),
    'sht_timestamp': ParserTestCase.TIMESTAMP + timedelta(milliseconds=0x3295),
    'voltage': 15, 'current': 14, 'oxygen': 13, 'ion_radiation': 12,
    'humidity': 45.15127563, 'temperature': 21.98367676,
    'pressure': 0.23852539,
    'gyro_x': 1.1025, 'gyro_y': -4.87375, 'gyro_z': 0.11375,
    'accel_x': -0.371063, 'accel_y': -0.394487, 'accel_z': -0.785314,
    'magnet_x': 0.1136, 'magnet_y': -0.06672, 'magnet_z': 0.19624
}


class TelemetryTests(ParserTestCase):
    parser_class = TelemetryParser

    def test_telemetry(self):
        """Test parsing telemetry ("S") message"""
        d = self.parse(TELEMETRY_LINE)
        self.assertDictAlmostEqual(d, TELEMETRY_DATA)
