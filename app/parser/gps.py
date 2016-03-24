from app.parser import Parser, ParseError
from app.parser.serializer import Serializer, fields


class GPGGASerializer(Serializer):
    """Serializer for GPGGA messages"""
    timestamp = fields.IgnoredField()
    latitude = fields.LatitudeField(empty=True)
    latitude_dir = fields.LatitudeDirectionField(empty=True)
    longitude = fields.LongitudeField(empty=True)
    longitude_dir = fields.LongitudeDirectionField(empty=True)
    quality = fields.FixQualityField()
    active_satellites = fields.IntegerField()
    hdop = fields.FloatField(empty=True)
    altitude = fields.FloatField(empty=True)
    altitude_unit = fields.IgnoredField(choices=('M',))  # Always M (meters)
    geoidal_separation = fields.IgnoredField()
    geoidal_separation_unit = fields.IgnoredField()
    diff_station_last_update = fields.IgnoredField()
    diff_station_id = fields.IgnoredField()

    def post_parse_data(self, data):
        if (data.latitude is not None and data.latitude_dir is not None and
                data.longitude is not None and data.longitude_dir is not None):
            data.latitude = data.latitude * data.latitude_dir
            data.longitude = data.longitude * data.longitude_dir


class GPGSASerializer(Serializer):
    """Serializer for GPGSA messages"""
    mode = fields.IgnoredField()
    fix_type = fields.FixTypeField()
    sv_id_1 = fields.IgnoredField()
    sv_id_2 = fields.IgnoredField()
    sv_id_3 = fields.IgnoredField()
    sv_id_4 = fields.IgnoredField()
    sv_id_5 = fields.IgnoredField()
    sv_id_6 = fields.IgnoredField()
    sv_id_7 = fields.IgnoredField()
    sv_id_8 = fields.IgnoredField()
    sv_id_9 = fields.IgnoredField()
    sv_id_10 = fields.IgnoredField()
    sv_id_11 = fields.IgnoredField()
    sv_id_12 = fields.IgnoredField()
    pdop = fields.FloatField(empty=True)
    hdop = fields.FloatField(empty=True)
    vdop = fields.FloatField(empty=True)


class GPGSVSerializer(Serializer):
    """Serializer for GPGSV messages"""
    no_of_messages = fields.IgnoredField()
    message_no = fields.IgnoredField()
    satellites_in_view = fields.IntegerField()
    sv_prn_no_1 = fields.IgnoredField()
    elevation_1 = fields.IgnoredField()
    azimuth_1 = fields.IgnoredField()
    snr_1 = fields.IgnoredField()
    sv_prn_no_2 = fields.IgnoredField()
    elevation_2 = fields.IgnoredField()
    azimuth_2 = fields.IgnoredField()
    snr_2 = fields.IgnoredField()
    sv_prn_no_3 = fields.IgnoredField()
    elevation_3 = fields.IgnoredField()
    azimuth_3 = fields.IgnoredField()
    snr_3 = fields.IgnoredField()
    sv_prn_no_4 = fields.IgnoredField()
    elevation_4 = fields.IgnoredField()
    azimuth_4 = fields.IgnoredField()
    snr_4 = fields.IgnoredField()


class GPRMCSerializer(Serializer):
    """Serializer for GPRMC messages"""
    VALIDITY_VALID = 'A'
    VALIDITY_INVALID = 'V'

    timestamp = fields.IgnoredField()
    validity = fields.StringField(choices=(VALIDITY_VALID, VALIDITY_INVALID),
                                  dict_included=False)
    latitude = fields.IgnoredField()
    latitude_dir = fields.IgnoredField()
    longitude = fields.IgnoredField()
    longitude_dir = fields.IgnoredField()
    speed_over_ground = fields.KnotsSpeedField()
    direction = fields.FloatField()
    date_stamp = fields.IgnoredField()
    variation = fields.IgnoredField()
    variation_dir = fields.IgnoredField()
    mode = fields.IgnoredField(optional=True)  # Introduced in NMEA 3.00

    def post_parse_data(self, data):
        if data.validity == self.VALIDITY_INVALID:
            data.direction = None
            data.speed_over_ground = None


class GPSParser(Parser):
    """Parser for GPS fix data

    The GPS unit sends data using NMEA 0183 protocol. For documentation see:

    * http://www.gpsinformation.org/dale/nmea.htm
    * http://aprs.gids.nl/nmea/
    """
    url = '/gps/'
    id = ('$GPGGA', '$GPRMC')
    serializer = {
        '$GPGGA': GPGGASerializer,
        '$GPRMC': GPRMCSerializer
    }

    def __init__(self):
        super().__init__()
        self.data = {}

    def parse(self, line):
        line.content = checksum_valid(line.content)
        self.data.update(super().parse(line))
        if line.id == '$GPRMC':
            return self.data.copy()


class ExtendedGPSParser(GPSParser):
    """Subclass of GPSParser that parses a few more GPS messages

    The class is intended only to test possible future use - parsing more
    messages than only '$GPGGA' and '$GPRMC'. It isn't (and shouldn't be) used
    anywhere in application's code.
    """

    url = '/gps/'
    id = ('$GPGGA', '$GPGSA', '$GPGSV', '$GPRMC', '$GPVTG')
    serializer = {
        '$GPGGA': GPGGASerializer,
        '$GPGSA': GPGSASerializer,
        '$GPGSV': GPGSVSerializer,
        '$GPRMC': GPRMCSerializer
    }

    def parse(self, line):
        line.content = checksum_valid(line.content)
        if line.id == '$GPVTG':
            # We don't get any data from GPVTG, but it's the last message, so
            # we can send gathered data here
            return self.data.copy()
        else:
            # Use the serializers
            self.data.update(super(GPSParser, self).parse(line))


def checksum_valid(line):
    """Check the checksum of given GPS output and return line without it

    The checksum is XOR of all bytes between $ and * characters
    (excluding themselves).

    :param str line: line of output to check
    :return: provided line without the checksum
    :rtype: str
    :raise ParseError: if the checksum is invalid
    """
    try:
        l = line.index('$')
        r = line.rindex('*')
    except ValueError:
        raise ParseError("Couldn't find $ or *")

    checksum = 0
    for char in line[l + 1: r]:
        checksum ^= ord(char)

    original_checksum = line[r + 1: r + 3]
    checksum = '{:02X}'.format(checksum)
    if original_checksum != checksum:
        raise ParseError("Calculated checksum: '{}' is not equal to the one "
                         "got: '{}'".format(checksum, original_checksum))
    return line[:r]
