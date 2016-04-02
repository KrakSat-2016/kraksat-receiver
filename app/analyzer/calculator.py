import math
import functools
import operator

from app.analyzer.kundt import Kundt
from app.analyzer.radius_mass import radius_mass, molar_mass


class NoDataError(Exception):
    """
    Raised when there is insufficient data to perform requested calculation.
    """
    pass


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
        if len(alti) == 0:
            raise NoDataError('No altitude data to calculate radius/mass')
        return radius_mass(alti, accel, 1e3, 1e7)

    @staticmethod
    def calculate_molar_mass_method2(collector):
        """
        Wrapper for C molar_mass function. Looks at every pair of
        measurement points instead of treating ground pressure as known
        constant.
        :param collector: Collector object
        :return: molar_mass
        """
        avg_temp = collector.get_average_temperature()
        avg_acceleration = collector.get_average_acceleration()
        altitude_list = []
        pressure_list = []
        for altitude, pressure in\
                collector.get_iter('altitude', 'pressure'):
            altitude_list.append(altitude)
            pressure_list.append(pressure)
        if len(altitude_list) == 0:




    @staticmethod
    def calculate_molar_mass(collector):
        """
        Use linear regression (in this case arithmetic mean)
        :param collector: data for calculations
        :type collector: Collector
        :return: molar mass [kg/mol]
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
        if denominator == 0:
            raise NoDataError('No altitude/pressure to calculate molar mass')
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
        density = Calculator.calculate_average_density(radius, mass)
        escape_velocity = Calculator.calculate_escape_velocity(radius, mass)

        factors = [
            (radius, 6.3781e6, 0.57/4),
            (density, 5513, 1.07/4),
            (escape_velocity, 11200, 0.70/4),
            (temperature, 288, 5.58/4)
        ]
        res = [(1 - abs(x - y)/abs(x + y)) ** z for x, y, z in factors]
        return functools.reduce(operator.mul, res)

    @staticmethod
    def calculate_average_density(radius, mass):
        return mass / ((4 / 3) * math.pi * radius ** 3)

    @staticmethod
    def calculate_escape_velocity(radius, mass):
        return (2 * Calculator.G * mass / radius) ** 0.5

    @staticmethod
    def perform_calculations(collector):
        """
        perform all calculations possible with currently collected data
        compute: molar_mass, radius, mass, speed_of_sound, adiabatic_index,
        density_of_atmosphere, average_mass_of_molecule, specific_gas_constant,
        refractive_index, molar_refractivity, speed_of_light
        :param collector: data for calculations
        :type collector: Collector
        :return: calculated values
        :rtype: dict
        """
        result = {}
        try:
            radius, mass = Calculator.calculate_radius_mass(collector)
            result['radius'] = radius
            result['mass'] = mass
            average_density = Calculator.calculate_average_density(radius,
                                                                   mass)
            result['average_density'] = average_density
            escape_velocity = Calculator.calculate_escape_velocity(radius,
                                                                   mass)
            result['escape_velocity'] = escape_velocity
            earth_similarity_index = Calculator.calculate_esi_index(
                radius, mass, collector.get_average_temperature())
            result['earth_similarity_index'] = earth_similarity_index
        except NoDataError:
            pass

        try:
            avg_atm_molar_mass = Calculator.calculate_molar_mass(collector)
        except NoDataError:
            avg_atm_molar_mass = None
        if avg_atm_molar_mass == 0:
            avg_atm_molar_mass = None

        if avg_atm_molar_mass is not None:
            result['avg_atm_molar_mass'] = avg_atm_molar_mass
            avg_molecule_mass = avg_atm_molar_mass / Calculator.A
            result['avg_molecule_mass'] = avg_molecule_mass
            specific_gas_const = Calculator.R / avg_atm_molar_mass
            result['specific_gas_const'] = specific_gas_const

        if collector.is_kundt_ready:
            speed_of_sound = Kundt.speed_of_sound(collector.kundt)
            result['speed_of_sound'] = speed_of_sound

            if avg_atm_molar_mass is None:
                # All further calculations require valid molar mass
                return result

            # Since calculate_molar_mass already uses get_average_temperature
            # and get_ground_pressure, it's safe to use these functions here
            # without worrying about NoDataError
            adiabatic_index = Calculator.calculate_adiabatic_index(
                collector, speed_of_sound, avg_atm_molar_mass)
            result['adiabatic_index'] = adiabatic_index

            atmosphere_density = (adiabatic_index *
                                     collector.get_ground_pressure() /
                                     speed_of_sound ** 2)
            result['atmosphere_density'] = atmosphere_density

            refractive_index = (3 * avg_atm_molar_mass *
                                collector.get_ground_pressure() /
                                atmosphere_density / Calculator.R /
                                collector.get_average_temperature() - 2) ** 0.5
            result['refractive_index'] = refractive_index

            molar_refractivity = (avg_atm_molar_mass /
                                  atmosphere_density *
                                  (refractive_index ** 2 - 1) /
                                  (refractive_index ** 2 + 2))
            result['molar_refractivity'] = molar_refractivity

            atm_speed_of_light = Calculator.C / refractive_index
            result['atm_speed_of_light'] = atm_speed_of_light

        return result
