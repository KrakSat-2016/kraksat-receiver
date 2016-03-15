import unittest
import random

from app.analyzer.calculator import Calculator

earth_mass = 5.97219e24
earth_radius = 6.3781e6


def eval_acceleration(x, rad, mas):
    return Calculator.G * mas /\
           (rad + x) ** 2


class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.collector = {
            'altitude': [],
            'acceleration': [],
        }
        self.calc = Calculator(self.collector)

    def test_calculate(self):
        for i in range(333):
            self.collector['altitude'].append(i*3)
            self.collector['acceleration'].append(
                    eval_acceleration(i*3, earth_radius, earth_mass))
        radius, mass = self.calc.calculate_radius_mass()
        self.assertAlmostEqual(radius, earth_radius, delta=1e4)
        self.assertAlmostEqual(mass / radius ** 2,
                               earth_mass / earth_radius ** 2, delta=1e7)

    def test_calculate_with_random(self):
        random_mass = random.uniform(1e10, 1e12)
        random_radius = random.uniform(1e5, 1e7)
        print(random_mass, " ", random_radius)
        for i in range(333):
            self.collector['altitude'].append(i*3)
            self.collector['acceleration'].append(
                    eval_acceleration(i*3, random_radius, random_mass))
        radius, mass = self.calc.calculate_radius_mass()
        self.assertAlmostEqual(radius, random_radius, delta=1e4)
        self.assertAlmostEqual(mass / radius ** 2,
                               random_mass / random_radius ** 2, delta=1e7)
