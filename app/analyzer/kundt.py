from numpy.polynomial.polynomial import polyfit, polyval
import statistics


class Kundt:
    """
    Calculate speed of sound
    """

    length = 1

    def __init__(self):
        # measurement points in (frequency, output_power) format
        self.points = []

    def get_peak_points(self, length=50):
        """
        Get substring of points sequence with highest median
        :param length: length of searched substring
        :return: points substring
        :rtype: [(float, float)]
        """
        def get_median(x):
            return statistics.median(map(lambda y: y[1], x))
        current_state = self.points[:length]
        result = (get_median(current_state), current_state)
        for i in self.points[length:]:
            current_state.pop(0)
            current_state.append(i)
            result = max(result, (get_median(current_state), current_state))
        return result[1]

    @staticmethod
    def frequency(points):
        """
        Use polynomial approximation to find resonance frequency
        :param points: peak points
        :return: resonance frequency
        """
        coefficients = polyfit(list(map(lambda x: x[0], points)),
                               list(map(lambda x: x[1], points)), 5)
        result = (0, 0)
        for i in range(points[0][0], points[-1][0]):
            result = max(result, (polyval(i, coefficients), i))
        return result[1]

    def speed_of_sound(self):
        return self.frequency(self.get_peak_points()) * self.length
