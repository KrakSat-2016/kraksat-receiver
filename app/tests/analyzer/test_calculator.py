import unittest
import random
import math

from app.analyzer.calculator import Calculator

earth_mass = 5.97219e24
earth_radius = 6.3781e6


def acceleration(height, rad=earth_radius, mas=earth_mass):
    return Calculator.G * mas /\
           (rad + height) ** 2


def temperature(height):
    return -6.49 * height / 1000 + 273.15 + 20


def pressure(height):
    numerator = -((9.80665 + acceleration(height))/2) * 0.0289644 * height
    denominator = 8.31432 * ((temperature(height) + 273.15 + 20)/2)
    return 101325 * math.exp(numerator/denominator)


class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.collector = {
            'altitude': [],
            'acceleration': [],
            'pressure': [],
            'temperature': [],
        }
        self.calc = Calculator(self.collector)

    def test_calculate(self):
        for i in range(1000, 0, -3):
            self.collector['altitude'].append(i)
            self.collector['acceleration'].append(acceleration(i))
        radius, mass = self.calc.calculate_radius_mass()
        self.assertAlmostEqual(radius, earth_radius, delta=1e4)
        self.assertAlmostEqual(mass / radius ** 2,
                               earth_mass / earth_radius ** 2, delta=1e7)

    def test_calculate_with_random(self):
        random_mass = random.uniform(1e10, 1e12)
        random_radius = random.uniform(1e5, 1e7)
        for i in range(1000, 0, -3):
            self.collector['altitude'].append(i)
            self.collector['acceleration'].append(
                    acceleration(i, random_radius, random_mass)
            )
        radius, mass = self.calc.calculate_radius_mass()
        self.assertAlmostEqual(radius, random_radius, delta=1e4)
        self.assertAlmostEqual(mass / radius ** 2,
                               random_mass / random_radius ** 2, delta=1e7)

    def test_molar_mass(self):
        for i in range(1000, 0, -3):
            self.collector['altitude'].append(i)
            self.collector['acceleration'].append(acceleration(i))
            self.collector['pressure'].append(pressure(i))
            self.collector['temperature'].append(temperature(i))
        molar_mass = self.calc.calculate_molar_mass()
        self.assertIsNotNone(molar_mass)
