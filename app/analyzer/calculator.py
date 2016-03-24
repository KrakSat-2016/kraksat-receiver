import math
import functools
import operator

from app.analyzer.kundt import Kundt
from app.analyzer.radius_mass import radius_mass


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

    @staticmethod
    def calculate_radius_mass(collector):
        """
        Use linear search to find best radius and derivative to
        find mass
        :param collector: data for calculations
        :type collector: Collector
        :return: (radius, mass)
        :rtype: (float, float)
        """
        accel = []
        alti = []
        for accel_val, alti_val in\
                collector.get_iter('acceleration', 'altitude'):
            accel.append(accel_val)
            alti.append(alti_val)
        return radius_mass(alti, accel, 1e3, 1e7)

    @staticmethod
    def calculate_molar_mass(collector):
        """
        use linear regression
        (in this case arithmetic mean)
        require at least 7 measurements
        :param collector: data for calculations
        :type collector: Collector
        :return: molar mass
        :rtype: float
        """
        avg_temp = collector.get_average_temperature()
        avg_acceleration = collector.get_average_acceleration()
        ground_pressure = collector.get_ground_pressure()
        numerator = 0
        denominator = 0
        for altitude, pressure in\
                collector.get_iter('altitude', 'pressure'):
            try:
                numerator -= (Calculator.R * avg_temp /
                              avg_acceleration / altitude *
                              math.log(pressure / ground_pressure))
            except ZeroDivisionError:
                pass
            else:
                denominator += 1
        return numerator / denominator

    @staticmethod
    def calculate_adiabatic_index(collector, speed_of_sound, molar_mass):
        return (speed_of_sound ** 2 * molar_mass /
                (Calculator.R * collector.get_average_temperature()))

    @staticmethod
    def calculate_esi_index(radius, mass, temperature):
        """
        Compute Earth Similarity Index
        :param radius: radius of planet
        :type radius: float
        :param mass: mass of planet
        :type mass: float
        :param temperature: average surface temperature of planet
        :type temperature: float
        :return: ESI
        :rtype: float
        """
        density = mass / ((4 / 3) * math.pi * radius ** 3)
        escape_velocity = (2 * Calculator.G * mass / radius) ** 0.5

        factors = [
            (radius, 6.3781e6, 0.57/4),
            (density, 5513, 1.07/4),
            (escape_velocity, 11200, 0.70/4),
            (temperature + 273.15, 288, 5.58/4)
        ]
        res = [(1 - abs(x - y)/abs(x + y)) ** z for x, y, z in factors]
        return functools.reduce(operator.mul, res)

    @staticmethod
    def perform_calculations(collector, skip_slow=False, dont_overwrite=False):
        """
        perform all calculations possible with currently collected data
        compute: molar_mass, radius, mass, speed_of_sound, adiabatic_index,
        density_of_atmosphere, average_mass_of_molecule, specific_gas_constant,
        refractive_index, molar_refractivity, speed_of_light
        :param collector: data for calculations
        :type collector: Collector
        :param skip_slow: if set previously calculated value of radius and mass
            will be used; if they don't exist, have no effect
        :param dont_overwrite: if set newly calculated values won't be stored
            in collector.previous
        :return: calculated values
        :rtype: dict
        """
        if skip_slow and collector.previous is not None:
            radius = collector.previous['radius']
            mass = collector.previous['mass']
        else:
            radius, mass = Calculator.calculate_radius_mass(collector)

        molar_mass = Calculator.calculate_molar_mass(collector)
        average_mass_of_molecule = molar_mass / Calculator.A
        specific_gas_constant = Calculator.R / molar_mass

        result = {
            'radius': radius,
            'mass': mass,
            'molar_mass': molar_mass,
            'average_mass_of_molecule': average_mass_of_molecule,
            'specific_gas_constant': specific_gas_constant,
        }

        if collector.is_kundt_ready:
            speed_of_sound = Kundt.speed_of_sound(collector.kundt)
            result['speed_of_sound'] = speed_of_sound

            adiabatic_index = Calculator.calculate_adiabatic_index(
                collector,
                speed_of_sound,
                molar_mass,
            )
            result['adiabatic_index'] = adiabatic_index

            density_of_atmosphere = (adiabatic_index **
                                     collector.get_ground_pressure() /
                                     speed_of_sound ** 2)
            result['density_of_atmosphere'] = density_of_atmosphere

            refractive_index = ((3 * molar_mass *
                                 collector.get_ground_pressure()) -
                                (2 * adiabatic_index * Calculator.R *
                                 collector.get_average_temperature()) /
                                (adiabatic_index * Calculator.R *
                                 collector.get_average_temperature())) ** 0.5
            result['refractive_index'] = refractive_index

            molar_refractivity = (molar_mass /
                                  adiabatic_index *
                                  (refractive_index ** 2 - 1) /
                                  (refractive_index ** 2 + 2))
            result['molar_refractivity'] = molar_refractivity

            speed_of_light = Calculator.C / refractive_index
            result['speed_of_light'] = speed_of_light

        if not dont_overwrite:
            collector.previous = result
        return result
