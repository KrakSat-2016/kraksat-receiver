import logging

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from app import api, timeutils
from app.ui.ui_gsinfo import Ui_GSInfoDialog


class GSInfoDialog(QDialog, Ui_GSInfoDialog):
    """Set Ground Station info dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.loginButton = self.buttonBox.addButton(
                "&Submit", QDialogButtonBox.AcceptRole)

        self._init_timezone_combo_box()
        self.api_thread = None
        self._set_ui_locked(True)
        self.retrieve_current_info()

    def _init_timezone_combo_box(self):
        for offset in timeutils.OFFSETS:
            self.timezoneComboBox.addItem(str(offset))
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
        class APIWorker(QThread):
            state_got = pyqtSignal(object, object, object, object)

            def run(self):
                result = api.get_gsinfo()
                if result:
                    self.state_got.emit(*result)

        self.api_thread = APIWorker()
        self.api_thread.state_got.connect(self.set_info)
        self.api_thread.finished.connect(self._set_ui_locked)
        self.api_thread.start()

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
