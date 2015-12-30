from PyQt5.QtCore import QSettings


class Settings(QSettings):
    """
    Class that adds some convenience methods to QSettings.
    """

    def __init__(self):
        super().__init__('kraksat', 'receiver')

    def __getitem__(self, item):
        """Retrieve item from settings"""
        return self.value(item)

    def __setitem__(self, key, value):
        """Set value at key to value in settings"""
        self.setValue(key, value)

    def __delitem__(self, key):
        """Delete given setting"""
        self.remove(key)

    def get_bool_list(self, key, default=[]):
        """Get list of booleans from settings.

        :param str key: key to get the value from
        :param iterable default: default value to return if there is no setting
            for given key
        :rtype: list[bool]
        """
        return [x == 'true' for x in self.value(key, default)]
