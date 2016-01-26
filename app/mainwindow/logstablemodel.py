import logging
from collections import namedtuple
from datetime import datetime
from enum import IntEnum

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from PyQt5.QtGui import QBrush, QColor

# Lightweight version of log record class containing only the data we need
LogRecord = namedtuple('LogRecord', 'time, level, module, message')

DISPLAY_DATETIME_FORMAT = '%H:%M:%S'
TOOLTIP_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

ERROR_BRUSH = QBrush(QColor(255, 148, 148))


class Column(IntEnum):
    timestamp = 0
    level = 1
    module = 2
    message = 3


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
        self.records.append(LogRecord(
            record.created, record.levelno, record.name,
            record.getMessage().splitlines()[0]))
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
            if col == Column.timestamp:
                return (datetime.fromtimestamp(record.time)
                        .strftime(DISPLAY_DATETIME_FORMAT))
            elif col == Column.level:
                return logging.getLevelName(record.level)
            elif col == Column.module:
                return record.module
            elif col == Column.message:
                return record.message
        elif role == Qt.ToolTipRole:
            if col == Column.timestamp:
                return (datetime.fromtimestamp(record.time)
                        .strftime(TOOLTIP_DATETIME_FORMAT))
        elif role == Qt.BackgroundRole:
            if record.level >= logging.ERROR:
                return ERROR_BRUSH

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["Time", "Level", "Module", "Message"][section]
