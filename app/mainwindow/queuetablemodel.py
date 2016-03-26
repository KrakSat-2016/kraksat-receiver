import logging
from collections import deque, namedtuple
from enum import IntEnum

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from app.colors import ERROR_BRUSH


class Status(IntEnum):
    waiting = 0
    processing = 1
    error = 2

    @staticmethod
    def as_string(status_id):
        status_to_string = {
            Status.waiting: 'Waiting',
            Status.processing: 'Processing',
            Status.error: 'Error'
        }
        return status_to_string[status_id]


# Lightweight version of RequestData that only keeps fields we need to display
# in the table
LightRequestData = namedtuple('LightRequestData', 'id, module, status')


class QueueTableModel(QAbstractTableModel):
    """
    Table model that displays data from Sender's request queue.

    The class keeps its own lightweight copy of queue to avoid expensive
    thread-safe queue retrieval.
    """

    logger = logging.getLogger('MainWindow')

    def __init__(self, sender, parent=None):
        """Constructor

        :param app.sender.QtSender sender: sender instance
        :param QObject parent: parent of the model
        """
        super().__init__(parent)
        self.queue = deque()
        sender.request_added.connect(self.add_request)
        sender.request_processing.connect(self.set_request_status)
        sender.error_occurred.connect(self.on_error)
        sender.request_processed.connect(self.remove_request)

    def add_request(self, request_data):
        """Add given request to the queue.

        :param app.sender.RequestData request_data: request data of the new
            request
        """
        count = len(self.queue)
        self.beginInsertRows(QModelIndex(), count, count)
        self.queue.append(LightRequestData(request_data.id,
                                           request_data.module,
                                           Status.waiting))
        self.endInsertRows()

    def on_error(self, request_data, exception, traceback_exception):
        self.set_request_status(request_data, Status.error)

    def set_request_status(self, request_data, status_id=Status.processing):
        """Set status of given request

        If provided ``request_data`` was not found in our local list, the
        incident is logged as a warning.

        :param app.sender.RequestData request_data: request data of the request
            to change status of
        :param int status_id: status ID to set
        """
        for index, item in enumerate(self.queue):
            if request_data.id == item.id:
                self.queue[index] = item._replace(status=status_id)
                model_index = self.index(index, 2)
                self.dataChanged.emit(model_index, model_index)
                return
        self.logger.warning(
            'QueueTableModel was requested to set status on invalid '
            'RequestData object: %s', request_data)

    def remove_request(self, request_data):
        """Remove provided request from the queue

        If provided ``request_data`` was not found in our local list, the
        incident is logged as a warning.

        :param app.sender.RequestData request_data: request data of the request
            to remove
        """
        for index, item in enumerate(self.queue):
            if request_data.id == item.id:
                self.beginRemoveRows(QModelIndex(), index, index)
                del self.queue[index]
                self.endRemoveRows()
                return
        self.logger.warning(
            'QueueTableModel was requested to remove invalid RequestData '
            'object: %s', request_data)

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.queue)

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        request_data = self.queue[row]

        if role == Qt.DisplayRole:
            if col == 2:
                return Status.as_string(request_data.status)
            return request_data[col]
        if role == Qt.TextAlignmentRole and col == 0:
            return Qt.AlignRight + Qt.AlignVCenter
        elif role == Qt.BackgroundRole:
            if request_data.status == Status.error:
                return ERROR_BRUSH

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["ID", "Module", "Status"][section]
