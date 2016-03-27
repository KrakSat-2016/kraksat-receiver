from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import QDialog

from app.ui.ui_probestart import Ui_ProbeStartDialog


class ProbeStartDialog(QDialog, Ui_ProbeStartDialog):
    """Set Probe Start Time dialog"""

    def __init__(self, parser_manager, parent=None):
        """Constructor

        :param parser_manager: ParserManager instance to use to get and set
            the time from/to
        :type parser_manager: app.parser.outputparser.ParserManager
        :param QWidget parent: dialog parent
        """
        super().__init__(parent)
        self.setupUi(self)
        self._parser_manager = parser_manager

        edit = self.probeStartTimeEdit
        if self._parser_manager.probe_start_time is not None:
            # Convert saved datetime from UTC back to local time
            dt = QDateTime(self._parser_manager.probe_start_time)
            dt.setTimeSpec(Qt.UTC)
            edit.setDateTime(dt.toLocalTime())
        else:
            edit.setDateTime(QDateTime.currentDateTime())

    def accept(self):
        # ParserManager expects datetime in UTC
        dt = self.probeStartTimeEdit.dateTime().toUTC().toPyDateTime()
        self._parser_manager.probe_start_time = dt
        self.done(QDialog.Accepted)
