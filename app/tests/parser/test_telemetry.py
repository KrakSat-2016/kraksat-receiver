from app.parser.telemetry import TelemetryParser
from app.tests.parser import ParserTestCase


TELEMETRY_LINE = ('S,3a98,146,1ab,64,7fc6,1d06a,6464,1d094,3d2011,1d095,3e,'
                  'fda0,62,1d096,569,3a1f,1ac6,fcf4,f9b6,f608,1d098')
TELEMETRY_DATA = {
    'humidity': 56.38937378,
    'temperature': 22.05875244,
    'pressure': 978.00415039,
    'gyro_x': 0.5425, 'gyro_y': -5.32, 'gyro_z': 0.8575,
    'accel_x': 0.084485, 'accel_y': 0.907619, 'accel_z': 0.418094,
    'magnet_x': -0.0624, 'magnet_y': -0.1288, 'magnet_z': -0.20416
}


class TelemetryTests(ParserTestCase):
    parser_class = TelemetryParser

    def test_telemetry(self):
        """Test parsing telemetry ("S") message"""
        d = self.parse('S', TELEMETRY_LINE)
        self.assertDictAlmostEqual(d, TELEMETRY_DATA)
