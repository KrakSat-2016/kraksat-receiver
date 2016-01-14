from app.parser import Parser, ParseError

NO_FIX = 'no_fix'
GPS_QUALITY = 'gps'
DGPS_QUALITY = 'dgps'
FIX_2D = '2d'
FIX_3D = '3d'


class GPSParser(Parser):
    """Parser for GPS fix data

    The GPS unit sends data using NMEA 0183 protocol. For documentation see:

    * http://www.gpsinformation.org/dale/nmea.htm
    * http://aprs.gids.nl/nmea/
    """

    url = '/gps/'
    ids = ('$GPGGA', '$GPGSA', '$GPGSV', '$GPRMC', '$GPVTG')

    def __init__(self):
        self.data = {}

    def parse(self, id, timestamp, line):
        line = checksum_valid(line)
        if id == '$GPGGA':
            return self._parse_gpgga(line)
        elif id == '$GPGSA':
            return self._parse_gpgsa(line)
        elif id == '$GPGSV':
            return self._parse_gpgsv(line)
        elif id == '$GPRMC':
            return self._parse_gprmc(line)
        elif id == '$GPVTG':
            # We don't get any data from GPVTG, but it's the last message, so
            # we can send gathered data here
            self.data['timestamp'] = timestamp
            return self.data

    def _parse_gpgga(self, line):
        """Parse GPGGA message (Global Positioning System Fix Data)

        :param str line: output line to parse
        """
        (
            _,  # UTC timestamp
            latitude, latitude_dir,
            longitude, longitude_dir,
            quality, satellites, _,  # HDOP (retrieved in GPGSA)
            altitude, _,  # Altitude unit (always meters)
            _, _,  # Geoidal separation - value and unit (not used)
            _, _  # Diff. station last update time and ID (not used)
        ) = self._get_args(line)

        quality = parse_quality(quality)
        satellites = int(satellites)
        self.data.update({
            'quality': quality,
            'active_satellites': satellites
        })
        if quality != NO_FIX:
            latitude = parse_latitude(latitude, latitude_dir)
            longitude = parse_longitude(longitude, longitude_dir)
            altitude = float(altitude)
            self.data.update({
                'latitude': latitude,
                'longitude': longitude,
                'altitude': altitude
            })

    def _parse_gpgsa(self, line):
        """Parse GPGSA message (GPS DOP and active satellites)

        :param str line: output line to parse
        """
        (
            _,  # Mode
            fix_type, _, _, _, _, _, _, _, _, _, _, _, _,  # IDs of SVs
            pdop, hdop, vdop
        ) = self._get_args(line)

        fix_type = parse_fix_type(fix_type)
        self.data.update({
            'fix_type': fix_type
        })
        if fix_type != NO_FIX:
            pdop = float(pdop)
            hdop = float(hdop)
            vdop = float(vdop)
            self.data.update({
                'pdop': pdop,
                'hdop': hdop,
                'vdop': vdop
            })

    def _parse_gpgsv(self, line):
        """Parse GPGSV message (GPS Satellites in view)

        :param str line: output line to parse
        """
        satellites = int(self._get_args(line)[2])
        self.data['satellites_in_view'] = satellites

    def _parse_gprmc(self, line):
        """Parse GPRMC message (Recommended minimum specific GPS/Transit data)

        :param str line: output line to parse
        """
        (
            _,  # UTC timestamp
            validity, _, _, _, _,  # Latitude, dir, longitude, dir
            speed, direction, _,  # Date stamp
            _, *_  # Variation, east/west, mode indicator for NMEA 3.00+
        ) = self._get_args(line)

        if validity == 'A':
            speed = parse_speed(speed)
            direction = float(direction)
            self.data.update({
                'speed_over_ground': speed,
                'direction': direction
            })


def parse_latitude(latitude, latitude_dir):
    """Convert given latitude string to float value

    :param str latitude: latitude string
    :param str latitude_dir: string indicating the hemisphere (``N`` or ``S``)
    :return: converted latitude string as float value
    :rtype: float
    :raise ParseError: when ``latitude_dir`` is neither ``N`` nor ``S``
    """
    return _parse_coord(latitude, latitude_dir, 'N', 'S')


def parse_longitude(longitude, longitude_dir):
    """Convert given longitude string to float value

    :param str longitude: longitude string
    :param str longitude_dir: string indicating the hemisphere (``E`` or ``W``)
    :return: converted longitude string as float value
    :rtype: float
    :raise ParseError: when ``longitude_dir`` is neither ``E`` nor ``W``
    """
    return _parse_coord(longitude, longitude_dir, 'E', 'W')


def _parse_coord(coord, direction, positive_sign, negative_sign):
    """Convert given geographic coordinate string to float value

    :param str coord: coordinate string
    :param str direction: direction string
    :param str positive_sign: direction when the return value is supposed to
        be positive
    :param str negative_sign: direction when the return value is supposed to
        be negative
    :rtype: float
    :raise ParseError: when ``coord_dir`` is not equal ``positive_sign`` or
        ``negative_sign``
    """
    if direction != positive_sign and direction != negative_sign:
        raise ParseError("Coordinate direction '{}' is neither '{}' nor '{}'"
                         .format(direction, positive_sign, negative_sign))

    dot = coord.index('.')
    sign = 1 if direction == positive_sign else -1
    return sign * (float(coord[:dot - 2]) + float(coord[dot - 2:]) / 60)


def parse_quality(quality):
    """Parse GPS fix quality field value

    :param str quality: ID of the quality
    :return: one of the values: ``NO_FIX``, ``GPS_QUALITY``, ``DGPS_QUALITY``
    :rtype: str
    """
    try:
        return [NO_FIX, GPS_QUALITY, DGPS_QUALITY][int(quality)]
    except (IndexError, ValueError):
        raise ParseError("'{}' is not valid quality ID".format(quality))


def parse_fix_type(fix_type):
    """Parse GPS fix type field value

    :param str fix_type: ID of the fix type
    :return: one of the values: ``NO_FIX``, ``FIX_2D``, ``FIX_3D``
    :rtype: str
    """
    try:
        # I have literally no idea why quality is indexed from 0, but type
        # from 1
        return [NO_FIX, FIX_2D, FIX_3D][int(fix_type) - 1]
    except (IndexError, ValueError):
        raise ParseError("'{}' is not valid fix type ID".format(fix_type))


def parse_speed(speed_in_knots):
    """Convert speed in knots to kilometers per hour

    :param str speed_in_knots: string containing speed in knots
    :rtype: float
    """
    try:
        return float(speed_in_knots) * 1.852
    except ValueError:
        raise ParseError("'{}' is not valid speed value"
                         .format(speed_in_knots))


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
