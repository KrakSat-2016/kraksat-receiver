import logging

from app import logger
from app.parser import Parser
from app.parser.serializer import fields, Serializer


class TelemetrySerializer(Serializer):
    error = fields.ErrorField(dict_included=False)
    voltage = fields.VoltageField()
    current = fields.CurrentField()
    oxygen = fields.OxygenField()
    ion_radiation = fields.RadiationField()
    timestamp = fields.TimestampField()
    humidity = fields.HumidityField()
    temperature = fields.TemperatureField()
    sht_timestamp = fields.TimestampField()
    pressure = fields.PressureField()
    gyro_x = fields.GyroField()
    gyro_y = fields.GyroField()
    gyro_z = fields.GyroField()
    accel_x = fields.AccelerationField()
    accel_y = fields.AccelerationField()
    accel_z = fields.AccelerationField()
    magnet_x = fields.MagneticField()
    magnet_y = fields.MagneticField()
    magnet_z = fields.MagneticField()

    def parse(self, line_content, probe_start_time):
        data = super().parse(line_content, probe_start_time)
        err = data.error
        if err != fields.ErrorField.OK:
            if len(err) == 0:
                logging.getLogger('Probe').log(
                    logger.PROBE, 'The probe reported an unspecified error')
            elif len(err) == 1:
                logging.getLogger('Probe').log(
                    logger.PROBE, 'The probe reported an error: %s',
                    list(err)[0].name)
            else:
                logging.getLogger('Probe').log(
                    logger.PROBE, 'The probe reported multiple errors: %s',
                    ', '.join(error.name for error in err))
        return data

    def get_collector_data(self, data):
        acceleration_axes = [data.accel_x, data.accel_y, data.accel_z]
        return {
            # Vector length [g]
            'acceleration': sum(x ** 2 for x in acceleration_axes) ** .5,
            'temperature': data.temperature + 273.15,
            'pressure': data.pressure * 100
        }


class TelemetryParser(Parser):
    url = '/telemetry/'
    id = 'S'
    serializer = TelemetrySerializer
