from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtWidgets import (
    QDockWidget, QHeaderView, QStylePainter, QAbstractItemView,
    QLabel
)

from app.mainwindow.queuetablemodel import QueueTableModel
from app.ui.ui_queue import Ui_QueueDock


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
        # todo init queue filter combo box

    def _init_table(self):
        def on_rows_inserted(index, first, last):
            for i in range(first, last + 1):
                self.table.resizeRowToContents(i)

        source_model = QueueTableModel(self._sender, self)
        model = QSortFilterProxyModel(self)
        model.setSourceModel(source_model)
        model.setFilterKeyColumn(1)  # module column
        self.table.setModel(model)
        model.rowsInserted.connect(on_rows_inserted)

        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Fixed)
        # Resize columns basing on maximum contents widths
        fm = QStylePainter(self.table).fontMetrics()
        # We don't expect the number of requests to exceed 10M
        self.table.horizontalHeader().resizeSection(
                0, fm.width('0000000') + 6)
        # todo set to the longest module name width
        self.table.horizontalHeader().resizeSection(
                1, fm.width('0000000') + 6)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setWordWrap(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.table.resizeRowsToContents()

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

    def set_paused(self, paused):
        """Set whether or not the request queue will be paused"""
        self._sender.set_paused(paused)
