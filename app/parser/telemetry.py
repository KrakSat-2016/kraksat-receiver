import logging

from app import logger
from app.parser import Parser
from app.parser.serializer import fields, Serializer


ERROR_ID_TO_NAME = {
    1: 'ALL_OK',
    2: 'ERROR_HARD_RST',
    3: 'ERROR_HTU21D_DISABLED',
    4: 'ERROR_GYRO_DISABLED',
    5: 'ERROR_ACC_MAGN_DISABLED',
    6: 'ERROR_LOW_BAT',
    7: 'ERROR_SD_CARD_DISABLED',
    8: 'ERROR_GPS',
    9: 'ERROR_KUNDT_TUBE',
    10: 'ERROR_WATCHDOG'
}
ERROR_NAME_TO_ID = {v: k for k, v in ERROR_ID_TO_NAME.items()}


class TelemetrySerializer(Serializer):
    error = fields.HexIntegerField(dict_included=False)
    voltage = fields.VoltageField()
    current = fields.CurrentField()
    oxygen = fields.OxygenField()
    ion_radiation = fields.RadiationField()
    humidity_measure_time = fields.HexIntegerField(dict_included=False)
    humidity = fields.HumidityField()
    temperature = fields.TemperatureField()
    temperature_measure_time = fields.HexIntegerField(dict_included=False)
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

    def parse(self, line_content):
        data = super().parse(line_content)
        if data.error != ERROR_NAME_TO_ID['ALL_OK']:
            logging.getLogger('probe').log(
                logger.PROBE, 'The probe reported an error: ' +
                              ERROR_ID_TO_NAME[data.error])
        return data


class TelemetryParser(Parser):
    url = '/telemetry/'
    id = 'S'
    serializer = TelemetrySerializer
