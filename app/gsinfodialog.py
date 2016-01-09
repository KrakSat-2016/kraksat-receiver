import logging

from PyQt5.QtCore import QAbstractListModel, Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from app import api, timeutils
from app.ui.ui_gsinfo import Ui_GSInfoDialog


class TimezoneComboBoxModel(QAbstractListModel):
    """
    Model for Combo Box that displays items from timeutils.OFFSETS.
    """

    def rowCount(self, parent=None, *args, **kwargs):
        return len(timeutils.OFFSETS)

    def data(self, index, role=None):
        row = index.row()
        if role == Qt.DisplayRole:
            return str(timeutils.OFFSETS[row])
        elif role == Qt.UserRole:
            return timeutils.OFFSETS[row]


class GSInfoDialog(QDialog, Ui_GSInfoDialog):
    """Set Ground Station info dialog"""

    def __init__(self, sender, parent=None):
        """Constructor

        :param app.sender.Sender sender: Sender instance to use
        :param QWidget parent: dialog parent
        """
        super().__init__(parent)
        self._sender = sender

        self.setupUi(self)
        self.loginButton = self.buttonBox.addButton(
                "&Submit", QDialogButtonBox.AcceptRole)

        self._init_timezone_combo_box()
        self.api_thread = None
        self._set_ui_locked(True)
        self.retrieve_current_info()

    def _init_timezone_combo_box(self):
        self.timezoneComboBox.setModel(TimezoneComboBoxModel(
                self.timezoneComboBox))
        try:
            current = timeutils.TimeOffset.get_current_timezone()
            self.timezoneComboBox.setCurrentIndex(
                    timeutils.OFFSETS.index(current))
        except ValueError:
            logging.getLogger('gsinfodialog').warning(
                    'Could not set current timezone in combo box',
                    exc_info=True)
            self.timezoneComboBox.setCurrentIndex(
                    timeutils.OFFSETS.index(timeutils.TimeOffset(0, 0)))

    def _set_ui_locked(self, locked=False):
        """Enable or disable submit button and form fields

        :param bool locked: True if the UI should be disabled; False otherwise
        """
        for widget in [self.latitudeSpinBox, self.longitudeSpinBox,
                       self.timezoneComboBox, self.loginButton]:
            widget.setEnabled(not locked)

    def retrieve_current_info(self):
        """Retrieve GS info from API server in a separate thread."""
        api.APIWorker(self._sender.api.get_gsinfo, self,
                      self.set_info, self._set_ui_locked)

    def set_info(self, timestamp, latitude, longitude, timezone):
        """Set provided info on form fields

        Called when GS info is retrieved from the API server.

        :param datetime.datetime timestamp: timestamp of the latest change
        :param float latitude: latitude of the Ground Station
        :param float longitude: longitude of the Ground Station
        :param TimeOffset timezone: Ground Station timezone
        """
        self.lastChangedLabel.setText(timestamp.strftime(timeutils.DT_FORMAT))
        self.latitudeSpinBox.setValue(latitude)
        self.longitudeSpinBox.setValue(longitude)
        if timezone is not None:
            self.timezoneComboBox.setCurrentIndex(
                    timeutils.OFFSETS.index(timezone))

    def accept(self):
        self._send_data()
        self.done(QDialog.Accepted)

    def _send_data(self):
        """Send form data to the API server"""
        latitude = self.latitudeSpinBox.value()
        longitude = self.longitudeSpinBox.value()
        timezone = self.timezoneComboBox.currentData().to_minutes()
        self._sender.add_request('GSInfoDialog', '/gsinfo/', {
            'latitude': latitude, 'longitude': longitude, 'timezone': timezone
        })
