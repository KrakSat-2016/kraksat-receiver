from unittest import TestCase

from app.parser.serializer import ValidationError
from app.parser.serializer.fields import HexSignedIntegerField, HexIntegerField


class TestFields(TestCase):
    def test_hex_integer_field(self):
        """Test HexIntegerField"""
        # Case not important
        self.assertEqual(
                HexIntegerField().to_python('1234567890abcdef'),
                HexIntegerField().to_python('1234567890ABCDEF'))
        # Random values
        self.assertEqual(HexIntegerField().to_python('8000'), 0x8000)
        self.assertEqual(HexIntegerField().to_python('94D0A575'), 0x94D0A575)
        self.assertEqual(HexIntegerField().to_python('1c7'), 0x1C7)
        # Errors
        self.assertRaises(ValidationError, HexIntegerField().to_python,
                          'foobar')

    def test_hex_signed_integer_field(self):
        """Test HexSignedIntegerField"""
        # Case not important
        self.assertEqual(
                HexSignedIntegerField(64).to_python('1234567890abcdef'),
                HexSignedIntegerField(64).to_python('1234567890ABCDEF'))
        # Positive and negative values
        self.assertEqual(HexSignedIntegerField(16).to_python('8000'), -0x8000)
        self.assertEqual(HexSignedIntegerField(16).to_python('7FFF'), 0x7FFF)
        # Uncommon length
        self.assertEqual(HexSignedIntegerField(12).to_python('7ff'), 0x7FF)
        self.assertEqual(HexSignedIntegerField(12).to_python('800'), -0x800)
        # Errors
        self.assertRaises(ValidationError, HexSignedIntegerField(16).to_python,
                          '10000')
        self.assertRaises(ValidationError, HexSignedIntegerField(16).to_python,
                          'foobar')
