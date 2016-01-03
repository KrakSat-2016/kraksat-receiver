from collections import deque, namedtuple
from datetime import datetime
from threading import RLock, Condition

from PyQt5.QtCore import QThread, QObject, pyqtSignal

from app import api

RequestData = namedtuple('RequestData', 'id, module, url, data, files')


class Sender:
    """
    Class that maintains API request queue, as well as allows adding and
    processing elements within it.

    The operations are thread-safe. Note that you probably want to use this
    class in a separate thread (see :py:class:`QtSenderWorker`).
    """

    def __init__(self):
        self.id = 1
        self.lock = RLock()
        self.not_empty = Condition(self.lock)
        self.queue = deque()

    def add_request(self, module, url, data, files=None,
                    append_timestamp=True):
        """Add request to the queue

        :param str module: name of the module that adds the queue. The value
            is only used when displaying the queue
        :param str url: relative URL to send the request to
        :param dict data: POST data to send
        :param dict files: files to send
        :param bool append_timestamp: whether or not "timestamp" should be
            included in POST data
        """
        if append_timestamp:
            data['timestamp'] = api.encode_datetime(datetime.utcnow())

        with self.lock:
            request_data = RequestData(self.id, module, url, data, files)
            self.id += 1
            self.queue.append(request_data)
            self.not_empty.notify()
        self.on_request_added(request_data)

    def process_request(self):
        """Process single request"""
        with self.lock:
            while not len(self.queue):
                self.not_empty.wait()
            request_data = self.queue.popleft()
        self.on_request_processing(request_data)
        api.create(request_data.url, request_data.data, request_data.files)
        # todo better error handling (catching APIErrors and possibly other)
        self.on_request_processed(request_data)

    def on_request_added(self, request_data):
        """Called when a request is added to the queue.

        The method is supposed to be overridden by subclasses.

        :param RequestData request_data: data of the request being added
        """
        pass

    def on_request_processing(self, request_data):
        """Called when a request is started being processed.

        The method is supposed to be overridden by subclasses.

        :param RequestData request_data: data of the request being added
        """
        pass

    def on_request_processed(self, request_data):
        """Called when a request was processed and removed from the queue.

        The method is supposed to be overridden by subclasses.

        :param RequestData request_data: data of the request being added
        """
        pass


class QtSender(QObject, Sender):
    """
    Subclass of :py:class:`Sender` that uses Qt signals to notify about
    requests being added or processed.
    """

    request_added = pyqtSignal(RequestData)
    request_processing = pyqtSignal(RequestData)
    request_processed = pyqtSignal(RequestData)

    def on_request_added(self, request_data):
        self.request_added.emit(request_data)

    def on_request_processing(self, request_data):
        self.request_processing.emit(request_data)

    def on_request_processed(self, request_data):
        self.request_processed.emit(request_data)


class QtSenderWorker(QThread):
    """
    Creates QtSender and processes the requests indefinitely.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sender = QtSender()

    def run(self):
        while True:
            self.sender.process_request()