"""
Utility functions for displaying various data in human-friendly format.
"""

SIZE_FORMAT = '{:.1f}{}B'


def format_size(size):
    """Format provided size in bytes in a human-friendly format

    :param int size: size to format in bytes
    :return: formatted size with an SI prefix ('k', 'M', 'G', 'T') and unit
        ('B')
    :rtype: str
    """
    if abs(size) < 1000:
        return SIZE_FORMAT.format(size, '')

    for unit in ('k', 'M', 'G'):
        size /= 1000
        if abs(size) < 1000:
            return SIZE_FORMAT.format(size, unit)

    return SIZE_FORMAT.format(size, 'TB')
