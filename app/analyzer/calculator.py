import math
import statistics

from app.analyzer.kundt import Kundt


class Calculator:
    """
    Perform calculations based on received data
    """
    # gravitational constant
    G = 6.674e-11
    # gas constant
    R = 8.3144598
    # Avogadro's constant
    A = 6.02214e23
    # Speed of light
    C = 299792458

    def __init__(self, collector):
        """
        :param Collector collector: data for calculations
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
            numerator = 0
            denominator = 0
            print(radius)

            for acceleration, altitude in\
                    self.collector.get_iter('acceleration', 'altitude'):
                numerator += (acceleration * (radius + altitude) ** 2 /
                              Calculator.G)
                denominator += 1
            mass = numerator / denominator

            error = 0
            for acceleration, altitude in\
                    self.collector.get_iter('acceleration', 'altitude'):
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
        require at least 7 measurements
        :return: molar mass
        :rtype: float
        """
        avg_temp = statistics.mean(
                list(self.collector.get_iter('temperature')))
        # acceleration can be treat as constant, so median should
        # give best approximation
        avg_acceleration = statistics.median(
                list(self.collector.get_iter('acceleration')))
        # to avoid big measurement errors use median instead of last point
        ground_pressure = self.collector.get_ground_pressure()
        numerator = 0
        denominator = 0
        for altitude, pressure in\
                self.collector.get_iter('altitude', 'pressure'):
            try:
                numerator -= Calculator.R * avg_temp \
                            / avg_acceleration / altitude \
                            * math.log(pressure / ground_pressure)
            except ZeroDivisionError:
                pass
            else:
                denominator += 1
        return numerator / denominator

    def calculate_adiabatic_index(self, speed_of_sound, molar_mass):
        return speed_of_sound ** 2 * molar_mass / (self.R *
                   self.collector.get_average_temperature())

    def perform_calculations(self):
        """
        perform all calculations possible with currently collected data
        compute: molar_mass, radius, mass, speed_of_sound, adiabatic_index,
        density_of_atmosphere, average_mass_of_molecule, specific_gas_constant,
        refractive_index, molar_refractivity, speed_of_light
        :return: dict with calculated values
        """
        radius, mass = self.calculate_radius_mass()
        molar_mass = self.calculate_molar_mass()
        average_mass_of_molecule = molar_mass / self.A
        specific_gas_constant = self.R / molar_mass

        result = {
            'radius': radius,
            'mass': mass,
            'molar_mass': molar_mass,
            'average_mass_of_molecule': average_mass_of_molecule,
            'specific_gas_constant': specific_gas_constant,
        }

        if self.collector.is_kundt_ready:
            speed_of_sound = Kundt.speed_of_sound(self.collector.kundt)
            result['speed_of_sound'] = speed_of_sound

            adiabatic_index = self.calculate_adiabatic_index(
                speed_of_sound,
                molar_mass,
            )
            result['adiabatic_index'] = adiabatic_index

            density_of_atmosphere = (adiabatic_index **
                self.collector.get_ground_pressure() / speed_of_sound ** 2)
            result['density_of_atmosphere'] = density_of_atmosphere

            refractive_index = (
                (3 * molar_mass * self.collector.get_ground_pressure()) -
                (2 * adiabatic_index * self.R *
                    self.collector.get_average_temperature) /
                (
                    adiabatic_index * self.R *
                    self.collector.get_average_temperature())
                ) ** 0.5
            result['refractive_index'] = refractive_index

            molar_refractivity = (molar_mass / adiabatic_index *
                (refractive_index ** 2 - 1) / (refractive_index ** 2 + 2))
            result['molar_refractivity'] = molar_refractivity

            speed_of_light = self.C / refractive_index
            result['speed_of_light'] = speed_of_light

        return result
