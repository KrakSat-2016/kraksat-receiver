"""
Utility functions for displaying various data in human-friendly format.
"""
from datetime import timedelta

SIZE_FORMAT = '{:.1f}{}B'


def format_size(size):
    """Format provided size in bytes in a human-friendly format

    :param int size: size to format in bytes
    :return: formatted size with an SI prefix ('k', 'M', 'G', 'T') and unit
        ('B')
    :rtype: str
    """
    if abs(size) < 1000:
        return str(size) + 'B'

    for unit in ('k', 'M', 'G'):
        size /= 1000
        if abs(size) < 1000:
            return SIZE_FORMAT.format(size, unit)

    return SIZE_FORMAT.format(size, 'TB')


def natural_timedelta(delta):
    """Express timedelta in human-friendly format, e.g. 70 => '1min 10s'

    Note that for 60 seconds, the function will return '1min 0s' and not just
    '1min'. The same behavior is for hours.

    :param timedelta|int delta: timedelta object or number of seconds as
        integer
    :return: timedelta in human-friendly format
    :rtype: str
    """
    sec = delta
    if isinstance(delta, timedelta):
        sec = round(delta.total_seconds())
    mins = sec // 60
    hrs = mins // 60
    sec %= 60
    mins %= 60

    result = '{}s'.format(sec)
    if mins or hrs:
        result = '{}min '.format(mins) + result
    if hrs:
        result = '{}h '.format(hrs) + result

    return result
