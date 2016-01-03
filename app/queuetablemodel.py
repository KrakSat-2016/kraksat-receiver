from collections import deque, namedtuple

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

from app.sender import RequestData

STATUS_WAITING = 0
STATUS_PROCESSING = 1
STATUS_ERROR = 2
STATUS_TO_STRING = {
    STATUS_WAITING: 'Waiting',
    STATUS_PROCESSING: 'Processing',
    STATUS_ERROR: 'Error'
}


# Lightweight version of RequestData that only keeps fields we need to display
# in the table
LightRequestData = namedtuple('LightRequestData', 'id, module, status')


class QueueTableModel(QAbstractTableModel):
    """
    Table model that displays data from Sender's request queue.

    The class keeps its own lightweight copy of queue to avoid expensive
    thread-safe queue retrieval.
    """

    def __init__(self, sender, parent=None):
        """Constructor

        :param app.sender.QtSender sender: sender instance
        :param QObject parent: parent of the model
        """
        super().__init__(parent)
        self.queue = deque()
        sender.request_added.connect(self.add_request)
        sender.request_processing.connect(self.set_status_processing)
        sender.request_processed.connect(self.remove_request)

    def add_request(self, request_data):
        """Add given request to the queue.

        :param RequestData request_data: request data of the new request
        """
        count = len(self.queue)
        self.beginInsertRows(QModelIndex(), count, count)
        self.queue.append(LightRequestData(request_data.id,
                                           request_data.module,
                                           STATUS_WAITING))
        self.endInsertRows()

    def set_status_processing(self, request_data):
        """Set status of given request to "Processing"

        :param RequestData request_data: request data of the request to change
            status of
        """
        for index, item in enumerate(self.queue):
            if request_data.id == item.id:
                self.queue[index] = item._replace(status=STATUS_PROCESSING)
                model_index = self.index(index, 2)
                self.dataChanged.emit(model_index, model_index)
                return
        # todo error

    def remove_request(self, request_data):
        """Remove provided request from the queue

        :param RequestData request_data: request data of the request to remove
        """
        for index, item in enumerate(self.queue):
            if request_data.id == item.id:
                self.beginRemoveRows(QModelIndex(), index, index)
                del self.queue[index]
                self.endRemoveRows()
                return
        # todo error

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
                return STATUS_TO_STRING[request_data.status]
            return request_data[col]
        if role == Qt.TextAlignmentRole and col == 0:
            return Qt.AlignRight + Qt.AlignVCenter

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["ID", "Parser", "Status"][section]
