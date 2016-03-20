from app.parser import Parser
from app.parser.serializer import fields, Serializer, ValidationError


class TelemetrySerializer(Serializer):
    error = fields.HexIntegerField()
    voltage = fields.VoltageField(dict_included=False)
    current = fields.CurrentField(dict_included=False)
    oxygen = fields.OxygenField(dict_included=False)
    geiger_cpm = fields.RadiationField(dict_included=False)
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

    def get_data(self, line_content):
        # Ignore the comma at the end
        if line_content[-1] != ',':
            raise ValidationError('Comma expected at the end')
        return super().get_data(line_content[:-1])


class TelemetryParser(Parser):
    url = '/telemetry/'
    ids = ('S',)
    serializers = {
        'S': TelemetrySerializer
    }
