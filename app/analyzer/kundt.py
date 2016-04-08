from numpy.polynomial.polynomial import polyfit, polyval
from numpy import arange
import statistics

from app.analyzer.collector import NoDataError


class Kundt:
    """
    Calculate speed of sound
    """
    # Half the length of the tube
    LENGTH = 88 / 1000 / 2

    @staticmethod
    def get_peak_points(points, length=200):
        """
        Get substring of points sequence with highest median
        :param points: measured data
        :type points: [(float, float)]
        :param length: length of searched substring
        :return: points substring
        :rtype: [(float, float)]
        """
        if len(points) < length:
            raise NoDataError("Not enough data co compute speed of sound")

        def get_median(x): return statistics.median(map(lambda y: y[1], x))
        current_state = list(points[:length])
        maxval = get_median(current_state)
        state_of_maxval = current_state.copy()
        for i in points[length:]:
            current_state.pop(0)
            current_state.append(i)
            if get_median(current_state) > maxval:
                maxval = get_median(current_state)
                state_of_maxval = current_state.copy()
        return state_of_maxval

    @staticmethod
    def frequency(points):
        """
        Use polynomial approximation to find resonance frequency
        :param points: peak points
        :return: resonance frequency in Hz
        """
        coefficients = polyfit(list(map(lambda x: x[0], points)),
                               list(map(lambda x: x[1], points)), 5)
        result, amplitude = 0, 0
        for i in arange(points[0][0], points[-1][0], -0.1):
            if polyval(i, coefficients) > amplitude:
                amplitude = polyval(i, coefficients)
                result = i
        return result

    @staticmethod
    def speed_of_sound(points):
        return Kundt.frequency(Kundt.get_peak_points(points)) * Kundt.LENGTH
