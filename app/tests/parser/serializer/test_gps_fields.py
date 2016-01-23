from unittest import TestCase

from app.parser.serializer.fields import (
    FixQualityField, ValidationError, FixTypeField, KnotsSpeedField,
    LatitudeField, LongitudeField, LatitudeDirectionField,
    LongitudeDirectionField
)


class TestGPSFields(TestCase):
    def test_latitude_field(self):
        """Test LatitudeField"""
        self.assertAlmostEqual(LatitudeField().to_python('3855.23816'),
                               38.920636, 4)
        self.assertRaises(ValidationError, LatitudeField().to_python,
                          '13855.23816')
        self.assertRaises(ValidationError, LatitudeField().to_python,
                          'foobar')

    def test_latitude_direction_field(self):
        """Test LatitudeDirectionField"""
        self.assertEqual(LatitudeDirectionField().to_python('N'), 1)
        self.assertEqual(LatitudeDirectionField().to_python('S'), -1)
        self.assertRaises(ValidationError, LatitudeDirectionField().to_python,
                          'foobar')

    def test_longitude_field(self):
        """Test LongitudeField"""
        self.assertAlmostEqual(LongitudeField().to_python('00924.41358'),
                               9.406893, 4)
        self.assertRaises(ValidationError, LongitudeField().to_python,
                          '20924.41358')
        self.assertRaises(ValidationError, LongitudeField().to_python,
                          'foobar')

    def test_longitude_direction_field(self):
        """Test LongitudeDirectionField"""
        self.assertEqual(LongitudeDirectionField().to_python('E'), 1)
        self.assertEqual(LongitudeDirectionField().to_python('W'), -1)
        self.assertRaises(ValidationError, LongitudeDirectionField().to_python,
                          'foobar')

    def test_fix_quality_field(self):
        """Test FixQualityField"""
        self.assertEqual(FixQualityField().to_python('0'), 'no_fix')
        self.assertEqual(FixQualityField().to_python('1'), 'gps')
        self.assertEqual(FixQualityField().to_python('2'), 'dgps')
        self.assertRaises(ValidationError, FixQualityField().to_python, '4')
        self.assertRaises(ValidationError, FixQualityField().to_python,
                          'lol1337')

    def test_fix_type_field(self):
        """Test FixTypeField"""
        self.assertEqual(FixTypeField().to_python('1'), 'no_fix')
        self.assertEqual(FixTypeField().to_python('2'), '2d')
        self.assertEqual(FixTypeField().to_python('3'), '3d')
        self.assertRaises(ValidationError, FixTypeField().to_python, '4')
        self.assertRaises(ValidationError, FixTypeField().to_python, 'lol1337')

    def test_knots_speed_field(self):
        """Test KnotsSpeedField"""
        self.assertAlmostEqual(KnotsSpeedField().to_python('31.332'),
                               58.026864, 3)
        self.assertRaises(ValidationError, KnotsSpeedField().to_python,
                          'lol1337')
