from PyQt5.QtCore import QSettings


def get_settings():
    return QSettings('kraksat', 'receiver')
