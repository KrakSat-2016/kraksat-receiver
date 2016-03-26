from unittest import TestCase

from app.parser.serializer.fields import ErrorField, ValidationError


class TestTelemetryFields(TestCase):
    def test_error_field(self):
        """Test ErrorField"""
        self.assertEqual(ErrorField().to_python('0'), ErrorField.OK)
        self.assertEqual(ErrorField().to_python('1'),
                         {ErrorField.ERROR_HARD_RST})
        self.assertEqual(
            ErrorField().to_python('6'),
            {ErrorField.ERROR_HTU21D_DISABLED, ErrorField.ERROR_GYRO_DISABLED})
        self.assertEqual(ErrorField().to_python('1ff'), set(ErrorField.ERRORS))
        self.assertRaises(ValidationError, ErrorField().to_python,
                          'foobar')
