import logging

from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from app import timeutils
from app.ui.ui_gsinfo import Ui_GSInfoDialog


class GSInfoDialog(QDialog, Ui_GSInfoDialog):
    """Set Ground Station info dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.loginButton = self.buttonBox.addButton(
                "&Submit", QDialogButtonBox.AcceptRole)

        self._init_timezone_combo_box()

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
