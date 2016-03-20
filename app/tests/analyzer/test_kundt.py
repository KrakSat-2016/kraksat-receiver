import unittest

from app.analyzer.kundt import Kundt


class KundtTest(unittest.TestCase):
    def test_basic(self):
        kundt = Kundt()
        for i in range(0, 1000, 10):
            kundt.points.append((i, i))
        speed_of_sound = kundt.speed_of_sound()
        self.assertIsNotNone(speed_of_sound)
