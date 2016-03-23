from app.parser import Parser
from app.parser.serializer import fields, Serializer


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


class TelemetryParser(Parser):
    url = '/telemetry/'
    id = 'S'
    serializer = TelemetrySerializer
