import unittest
import inspect
import os

from app.analyzer.kundt import Kundt


class KundtTest(unittest.TestCase):
    def test_basic(self):
        points = []
        for i in range(0, 1000, 10):
            points.append((i, i))
        speed_of_sound = Kundt.speed_of_sound(points)
        self.assertIsNotNone(speed_of_sound)

    def test_with_real_data(self):
        data = open(os.path.dirname(__file__) + '/capture8.csv')
        points = []
        for line in data:
            i, y, x = line.strip().split(sep=';')
            points.append((int(float(x.replace(',', '.'))), int(y)))
        data.close()
        speed_of_sound = Kundt.speed_of_sound(points)
        self.assertAlmostEqual(340, speed_of_sound, delta=5)
