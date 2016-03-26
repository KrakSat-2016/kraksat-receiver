import logging
import sys
from collections import deque, namedtuple
from datetime import datetime
from threading import RLock, Condition
from traceback import TracebackException

import requests
from PyQt5.QtCore import QThread, QObject, pyqtSignal

from app import api
from app.api import APIError

RequestData = namedtuple('RequestData', 'id, module, url, data, files, '
                                        'callback')


class Sender:
    """
    Class that maintains API request queue, as well as allows adding and
    processing elements within it.

    The operations are thread-safe. Note that you probably want to use this
    class in a separate thread (see :py:class:`QtSenderWorker`).
    """

    logger = logging.getLogger('Sender')

    def __init__(self, api):
        """Constructor

        :param app.api.API api: API instance to use
        """
        self.api = api  # API instance
        # Session instance for persistent connection
        self.session = requests.Session()
        # ID for the next RequestData to use
        self.id = 1

        # Queue containing RequestData objects
        self.queue = deque()

        # Lock to avoid overriding queue data by multiple threads (also used
        # for variables listed immediately below)
        self.lock = RLock()
        # Condition object that notifies waiting thread whenever an item is
        # added to the queue, so the thread can grab it and process
        self.not_empty = Condition(self.lock)
        # Whether or not a request is currently being processed in
        # process_request. Used for better estimation of queue size in __len__
        self.currently_processing = False
        # Whether or not the next request should be skipped by process_request
        self.skip_current = False
        # Whether or not the sender was told to be terminated and
        # process_request or process_indefinitely should return ASAP
        self.terminated = False

        # Lock to avoid overriding "paused" variable by multiple threads
        self.pause_lock = RLock()
        # Whether or not sending data is temporarily suspended
        self._paused = False
        # Condition object that notifies waiting thread that "paused"
        # variable was set to False, so processing the queue can continue
        self.unpaused = Condition(self.pause_lock)

    def add_request(self, module, url, data, files=None,
                    append_timestamp=True, callback=None):
        """Add request to the queue

        :param str module: name of the module that adds the queue. The value
            is only used when displaying the queue
        :param str url: relative URL to send the request to
        :param dict data: POST data to send
        :param dict files: files to send
        :param bool append_timestamp: whether or not "timestamp" should be
            included in POST data
        :param function callback: function to be called when the request is
            processed
        """
        if append_timestamp:
            data['timestamp'] = api.encode_datetime(datetime.utcnow())

        with self.lock:
            request_data = RequestData(self.id, module, url, data, files,
                                       callback)
            self.id += 1
            self.queue.append(request_data)
            self.on_request_added(request_data)
            self.not_empty.notify()

    def __len__(self):
        """Return number of requests currently in the request queue

        Note that this returns 1 more than just a length of the underlying
        queue if some request is currently being processed.

        :rtype: int
        """
        with self.lock:
            return len(self.queue) + (1 if self.currently_processing else 0)

    def process_indefinitely(self):
        """Process requests as long as sender is not terminated

        See :py:method:`set_terminated` to terminate executing of this
        function.
        """
        while not self.terminated:
            self.process_request()

    def process_request(self):
        """Process single request"""
        with self.lock:
            self.currently_processing = False
            while not len(self.queue):
                self.not_empty.wait()
                if self.terminated:
                    return
            request_data = self.queue.popleft()
            self.currently_processing = True

        repeat = True
        while repeat:
            repeat = False

            with self.pause_lock:
                if self._paused:
                    self.unpaused.wait()
            with self.lock:
                if self.skip_current:
                    self.skip_current = False
                    break
                if self.terminated:
                    return

            self.on_request_processing(request_data)

            try:
                self.api.create(
                    request_data.url, request_data.data, request_data.files,
                    requests_object=self.session)
            except (requests.exceptions.RequestException, APIError):
                exc_type, exc_value, exc_traceback = sys.exc_info()
                request = exc_value.response.request
                self.logger.exception(
                    'Could not send request: %s\nURL: %s\nRequest body: %s',
                    str(exc_value), request.url, request.body)
                tb_exc = TracebackException.from_exception(exc_value)
                self.on_error(request_data, exc_value, tb_exc)
                self.paused = True

                repeat = True

        self.on_request_processed(request_data)
        if request_data.callback:
            request_data.callback()

    @property
    def paused(self):
        """Check if the sender is currently paused

        :return: ``True`` if the sender is currently paused; ``False``
            otherwise
        :rtype: bool
        """
        with self.pause_lock:
            return self._paused

    @paused.setter
    def paused(self, paused):
        """(Un)pause the queue

        :param bool paused: whether or not request processing should be paused
        """
        with self.pause_lock:
            self._paused = paused
            if not paused:
                self.unpaused.notify()
            self.on_paused(paused)

    def set_skip_current(self):
        """Causes the currently processed request to be skipped"""
        with self.lock:
            if not self.skip_current:
                self.skip_current = True
                self.logger.warning('Skipping current request')

    def set_terminated(self):
        """Terminate processing requests

        Releases any lock :py:method:`process_request` may be waiting for;
        also prevents this method from being called again.
        """
        self.terminated = True
        with self.lock, self.pause_lock:
            self.not_empty.notify_all()
            self.unpaused.notify_all()

    def on_request_added(self, request_data):
        """Called when a request is added to the queue.

        The method is supposed to be overridden by subclasses.

        :param RequestData request_data: RequestData instance for the request
            being added to the queue
        """
        pass

    def on_request_processing(self, request_data):
        """Called when a request is started being processed.

        The method is supposed to be overridden by subclasses.

        :param RequestData request_data: RequestData instance for the request
            being currently processed
        """
        pass

    def on_request_processed(self, request_data):
        """Called when a request was processed and removed from the queue.

        The method is supposed to be overridden by subclasses.

        :param RequestData request_data: RequestData instance for the request
            being removed from the queue
        """
        pass

    def on_paused(self, paused):
        """Called when the queue is (un)paused.

        The method is supposed to be overridden by subclasses.

        :param bool paused: whether or not the queue is paused
        """
        pass

    def on_error(self, request_data, exception, traceback_exception):
        """Called when an error occurs when processing given request.

        :param RequestData request_data: RequestData instance for the request
            being processed when the error occurred
        :param BaseException exception: exception thrown
        :param TracebackException traceback_exception: TracebackException
            object for the exception
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
    queue_paused = pyqtSignal(bool)
    error_occurred = pyqtSignal(RequestData, BaseException, TracebackException)

    def on_request_added(self, request_data):
        self.request_added.emit(request_data)

    def on_request_processing(self, request_data):
        self.request_processing.emit(request_data)

    def on_request_processed(self, request_data):
        self.request_processed.emit(request_data)

    def on_paused(self, paused):
        self.queue_paused.emit(paused)

    def on_error(self, request_data, exception, traceback_exception):
        self.error_occurred.emit(request_data, exception, traceback_exception)


class QtSenderWorker(QThread):
    """
    Creates QtSender and processes the requests indefinitely.
    """

    def __init__(self, api, parent=None):
        """Constructor

        :param app.api.API api: API instance to use
        :param QObject parent: thread parent
        """
        super().__init__(parent)
        self.sender = QtSender(self, api=api)

    def run(self):
        self.sender.process_indefinitely()
