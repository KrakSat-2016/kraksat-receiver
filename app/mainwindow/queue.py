from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtWidgets import QDockWidget, QHeaderView, QLabel

from app.mainwindow.queuetablemodel import QueueTableModel
from app.parser import outputparser
from app.ui.ui_queue import Ui_QueueDock
from app.uiutils import (
    get_max_text_width, TABLE_WIDTH_PADDING, TABLE_HEIGHT_PADDING
)


class QueueDock(QDockWidget, Ui_QueueDock):
    CONFIG_QUEUE_FILTER_STATE_KEY = 'mainWindow/queue/filterCheckState'

    def __init__(self, parent, sender):
        """Constructor

        :param QWidget parent: parent of the QueueDock
        :param app.sender.QtSender sender: QtSender instance
        """
        super().__init__(parent)
        self._sender = sender
        self.setupUi(self)
        self._init_table()
        sender.queue_paused.connect(self.on_paused)

    def _init_table(self):
        source_model = QueueTableModel(self._sender, self)
        model = QSortFilterProxyModel(self)
        model.setSourceModel(source_model)
        model.setFilterKeyColumn(1)  # module column
        self.table.setModel(model)

        self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Fixed)
        # Resize columns basing on maximum contents widths
        fm = self.table.fontMetrics()
        # We don't expect the number of requests to exceed 1M
        self.table.horizontalHeader().resizeSection(
                0, fm.width('000000') + TABLE_WIDTH_PADDING)
        self.table.horizontalHeader().resizeSection(1, get_max_text_width(
                fm, self.get_known_queue_modules()) + TABLE_WIDTH_PADDING)
        # Row height
        self.table.verticalHeader().setDefaultSectionSize(
                fm.height() + TABLE_HEIGHT_PADDING)

    @staticmethod
    def get_known_queue_modules():
        """Get names of all app modules that sends requests via Sender"""
        return ([cls.__name__ for cls in outputparser.PARSERS] +
                ['Analyzer', 'GSInfoDialog', 'VideoIDDialog', 'MissionStatus'])

    def create_statusbar_widget(self):
        """Create label for status bar showing number of requests processed

        :return: label widget
        :rtype: QLabel
        """
        queue_status_label = QLabel()
        queue_model = self.table.model().sourceModel()

        def update_text():
            """Update "Processing ... requests" label text on status bar"""
            count = queue_model.rowCount()
            queue_status_label.setText("Processing {} requests"
                                       .format(count))

        update_text()
        queue_model.rowsInserted.connect(update_text)
        queue_model.rowsRemoved.connect(update_text)
        return queue_status_label

    def on_paused(self, paused):
        self.setWindowTitle('&Queue' + (' [paused]' if paused else ''))
