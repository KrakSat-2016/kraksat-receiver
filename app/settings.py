from PyQt5.QtCore import QSettings


def get_settings():
    return QSettings('kraksat', 'receiver')


def settings_get_bool_list(settings, key, default=[]):
    """Get list of booleans from settings.

    :param QSettings settings: QSettings object
    :param str key: key to get the value from
    :param iterable default: default value to return if there is no setting
        for given key
    :rtype: list[bool]
    """
    return [x == 'true' for x in settings.value(key, default)]
