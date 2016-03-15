class Calculator:
    """
    Perform calculations based on received data
    """
    G = 6.674e-11

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
        for radius in range(1, int(1e8+1), 3333):
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
