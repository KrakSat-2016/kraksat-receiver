import math
import statistics


class Calculator:
    """
    Perform calculations based on received data
    """
    G = 6.674e-11
    R = 8.3144598

    def __init__(self, collector):
        """
        :param dictionary collector: dictionary witch contains lists of values
        for calculations
        """
        self.collector = collector

    def calculate_radius_mass(self):
        """
        Use linear search to find best radius and derivative to
        find mass
        :return: (radius, mass)
        :rtype: (float, float)
        """
        best = {
            'error': float('inf'),
            'mass': 0,
            'radius': 0
        }

        # could be set to smaller steps to get better precision,
        # but since measurement error are so big compared to
        # measured values I find it not necessary
        for radius in range(1, int(1e8+1), 10000):
            accel = self.collector['acceleration']
            alti = self.collector['altitude']
            msum = 0
            for acceleration, altitude in zip(accel, alti):
                msum += acceleration * (radius + altitude) ** 2 / Calculator.G
            mass = msum / min(len(accel), len(alti))

            error = 0
            for acceleration, altitude in zip(accel, alti):
                error += (acceleration - Calculator.G *
                          mass / (radius + altitude) ** 2)**2

            if error < best['error']:
                best.update({
                    'error': error,
                    'mass': mass,
                    'radius': radius
                })
        return best['radius'], best['mass']

    def calculate_molar_mass(self):
        """
        use linear regression
        (in this case arithmetic mean)
        :return: molar mass
        """
        alti = self.collector['altitude']
        press = self.collector['pressure']
        avg_temp = statistics.mean(self.collector['temperature'])
        # acceleration can be treat as constant, so median should
        # give best approximation
        avg_acceleration = statistics.median(self.collector['acceleration'])
        # to avoid big measurement errors use median instead of last point
        ground_pressure = statistics.median(self.collector['pressure'][-10:])
        numerator = 0
        denominator = 0
        for altitude, pressure in zip(alti, press):
            try:
                numerator -= Calculator.R * avg_temp \
                            / avg_acceleration / altitude \
                            * math.log(pressure / ground_pressure)
            except ZeroDivisionError:
                pass
            else:
                denominator += 1
        return numerator / denominator
