import time

from datetime import datetime

DT_FORMAT = '%Y-%m-%d %H:%M:%S'

UTC_FORMAT = 'UTC{}{:02}:{:02}'
ISO_8601_FORMAT = '{}{:02}:{:02}'


class TimeOffset:
    """Utility class for storing timezones as UTC offsets"""

    def __new__(cls, hours, minutes):
        """Constructor

        :param int hours: number of hours. Might be negative, then it applies
            to whole time offset.
        :param int minutes: number of minutes
        :raise ValueError: if minutes parameter is negative
        """
        if minutes < 0:
            raise ValueError('Minutes must be positive')

        self = super(TimeOffset, cls).__new__(cls)
        self.negative = hours < 0
        self.hours = abs(hours)
        self.minutes = minutes
        self.__hash = ((self.hours * 100 + self.minutes) *
                       (-1 if self.negative else 1))
        return self

    @classmethod
    def from_seconds(cls, seconds):
        """Return new TimeOffset object created from given number of seconds.

        The function checks if created object exists in `OFFSET` list and
        raises :class:`ValueError` if it does not.

        :param int seconds: offset in seconds
        :return: Created TimeOffset object
        :rtype: TimeOffset
        :raise ValueError: if created TimeOffset is not present within
            OFFSETS list
        """
        negative = seconds < 0
        seconds = abs(seconds)
        seconds //= 36

        hours = seconds // 100
        minutes = seconds % 100 // 25 * 15
        result = cls(hours * (-1 if negative else 1), minutes)
        if result not in OFFSETS_SET:
            raise ValueError('Created TimeOffset is not in OFFSETS')
        return result

    @classmethod
    def from_minutes(cls, minutes):
        """Return new TimeOffset object created from given number of minutes.

        See :method:`from_seconds <TimeOffset.from_seconds>` for more info.

        :param int minutes: offset in minutes
        :return: Created TimeOffset object
        :rtype: TimeOffset
        """
        return cls.from_seconds(minutes * 60)

    def to_minutes(self):
        """Return the timezone offset as the number of minutes

        :return: offset as the number of minutes
        :rtype: int
        """
        return (self.hours * 60 + self.minutes) * (-1 if self.negative else 1)

    @classmethod
    def get_current_timezone(cls):
        """Get timezone currently set in system

        :return: Created TimeOffset object
        :rtype: TimeOffset
        :raise ValueError: if created TimeOffset is not present within
            OFFSETS list
        """
        t = time.time()
        delta = datetime.fromtimestamp(t) - datetime.utcfromtimestamp(t)
        return cls.from_seconds(delta.seconds)

    def as_iso(self):
        """Get this TimeOffset as ISO-8601 (RFC3339-compliant) string

        :rtype: str
        """
        sign = '-' if self.negative else '+'
        return ISO_8601_FORMAT.format(sign, self.hours, self.minutes)

    def __eq__(self, other):
        return (self.negative == other.negative and
                self.hours == other.hours and
                self.minutes == other.minutes)

    def __repr__(self):
        hours = self.hours * (-1 if self.negative else 1)
        return 'TimeOffset({}, {})'.format(hours, self.minutes)

    def __str__(self):
        sign = '−' if self.negative else '+'
        if self.hours == 0 and self.minutes == 0:
            sign = '±'
        return UTC_FORMAT.format(sign, self.hours, self.minutes)

    def __hash__(self):
        return self.__hash


OFFSETS = [
    # Based on https://en.wikipedia.org/wiki/List_of_UTC_time_offsets
    TimeOffset(-12, 00),  # UTC−12:00
    TimeOffset(-11, 0),  # UTC−11:00
    TimeOffset(-10, 0),  # UTC−10:00
    TimeOffset(-9, 30),  # UTC−09:30
    TimeOffset(-9, 0),  # UTC−09:00
    TimeOffset(-8, 0),  # UTC−08:00
    TimeOffset(-7, 0),  # UTC−07:00
    TimeOffset(-6, 0),  # UTC−06:00
    TimeOffset(-5, 0),  # UTC−05:00
    TimeOffset(-4, 30),  # UTC−04:30
    TimeOffset(-4, 0),  # UTC−04:00
    TimeOffset(-3, 30),  # UTC−03:30
    TimeOffset(-3, 0),  # UTC−03:00
    TimeOffset(-2, 0),  # UTC−02:00
    TimeOffset(-1, 0),  # UTC−01:00
    TimeOffset(0, 0),  # UTC±00:00
    TimeOffset(1, 0),  # UTC+01:00
    TimeOffset(2, 0),  # UTC+02:00
    TimeOffset(3, 0),  # UTC+03:00
    TimeOffset(3, 30),  # UTC+03:30
    TimeOffset(4, 0),  # UTC+04:00
    TimeOffset(4, 30),  # UTC+04:30
    TimeOffset(5, 0),  # UTC+05:00
    TimeOffset(5, 30),  # UTC+05:30
    TimeOffset(5, 45),  # UTC+05:45
    TimeOffset(6, 0),  # UTC+06:00
    TimeOffset(6, 30),  # UTC+06:30
    TimeOffset(7, 0),  # UTC+07:00
    TimeOffset(8, 0),  # UTC+08:00
    TimeOffset(8, 30),  # UTC+08:30
    TimeOffset(8, 45),  # UTC+08:45
    TimeOffset(9, 0),  # UTC+09:00
    TimeOffset(9, 30),  # UTC+09:30
    TimeOffset(10, 0),  # UTC+10:00
    TimeOffset(10, 30),  # UTC+10:30
    TimeOffset(11, 0),  # UTC+11:00
    TimeOffset(12, 0),  # UTC+12:00
    TimeOffset(12, 45),  # UTC+12:45
    TimeOffset(13, 0),  # UTC+13:00
    TimeOffset(14, 0)  # UTC+14:00
]
OFFSETS_SET = set(OFFSETS)
