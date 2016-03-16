from app.parser import Parser
from app.parser.serializer import fields, Serializer


class TelemetrySerializer(Serializer):
    adc_voltage = fields.VoltageField(dict_included=False)
    adc_current = fields.CurrentField(dict_included=False)
    adc_oxygen = fields.OxygenField(dict_included=False)
    geiger_cpm = fields.RadiationField(dict_included=False)
    humidity = fields.HumidityField()
    humidity_measure_time = fields.HexIntegerField(dict_included=False)
    temperature = fields.TemperatureField()
    temperature_measure_time = fields.HexIntegerField(dict_included=False)
    pressure = fields.PressureField()
    pressure_measure_time = fields.HexIntegerField(dict_included=False)
    gyro_x = fields.GyroField()
    gyro_y = fields.GyroField()
    gyro_z = fields.GyroField()
    gyro_measure_time = fields.HexIntegerField(dict_included=False)
    accel_x = fields.AccelerationField()
    accel_y = fields.AccelerationField()
    accel_z = fields.AccelerationField()
    magnet_x = fields.MagneticField()
    magnet_y = fields.MagneticField()
    magnet_z = fields.MagneticField()
    accel_magnet_measure_time = fields.HexIntegerField(dict_included=False)


class TelemetryParser(Parser):
    url = '/telemetry/'
    ids = ('S',)
    serializers = {
        'S': TelemetrySerializer
    }
