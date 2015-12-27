import logging
from collections import namedtuple
from datetime import datetime

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

# Lightweight version of log record class containing only the data we need
LogRecord = namedtuple('LogRecord', 'time, level, module, message')


class LogsTableModel(QAbstractTableModel):
    """
    Table model that retrieves log records from Python logging module and
    uses them as model data.
    """

    def __init__(self, parent=None, memory_handler=None):
        """Constructor

        :param QObject parent: model parent
        :param logging.handlers.MemoryHandler memory_handler: MemoryHandler to
            use as a proxy for log records
        """
        super().__init__(parent)

        self.records = []
        memory_handler.setTarget(self)
        memory_handler.flush()

    def handle(self, record):
        """Handle log record and add it to the model data.

        This is an implementation of `handle()` used as MemoryHandler's target.

        :param logging.LogRecord record: log record to handle
        """
        count = len(self.records)
        self.beginInsertRows(QModelIndex(), count, count)
        self.records.append(LogRecord(record.created, record.levelno,
                                      record.name, record.getMessage()))
        self.endInsertRows()

    def columnCount(self, parent=None, *args, **kwargs):
        return 4

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.records)

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        record = self.records[row]

        if role == Qt.DisplayRole:
            if col == 0:
                return (datetime.fromtimestamp(record.time)
                        .strftime('%H:%M:%S'))
            elif col == 1:
                return logging.getLevelName(record.level)
            elif col == 2:
                return record.module
            elif col == 3:
                return record.message

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["Time", "Level", "Module", "Message"][section]
