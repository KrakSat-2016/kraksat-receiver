from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QTimer


class Statistics:
    """
    Class that manages statistics data (such as time since start, total number
    of requests sent) and notifies about changes in that data.

    Note that this is abstract class; :py:method:`create_timer`,
    :py:method:`update_time_since_start`,
    :py:method:`update_time_since_last_receive` and
    :py:method:`update_requests_sent` methods should be implemented by
    subclasses.
    """

    def __init__(self):
        self.start_time = datetime.now()
        self.last_receive_time = None
        self.requests_sent = 0
        self.create_timer()

    def create_timer(self):
        """Create a timer that calls :py:method:`on_clock_tick` every second

        Subclasses are supposed to implement this method; it's called
        automatically in the constructor.
        """
        raise NotImplementedError

    def on_clock_tick(self):
        """Called every clock tick. Updates time since start and receive."""
        now = datetime.now()
        self.update_time_since_start(now - self.start_time)
        if self.last_receive_time is not None:
            self.update_time_since_last_receive(now - self.last_receive_time)

    def update_time_since_start(self, timedelta):
        """Called when time since start is updated (so basically every second)

        :param timedelta timedelta: difference between current time and time
            of application start
        """
        raise NotImplementedError

    def on_data_received(self):
        """Should be called when data is received

        The function updated last data receive time and calls
        :py:method:`update_time_since_last_receive`.
        """
        self.last_receive_time = datetime.now()
        self.update_time_since_last_receive(timedelta(0))

    def update_time_since_last_receive(self, timedelta):
        """Called when time since last data receive is updated

        :param timedelta timedelta: difference between current time and time
            of last data receive
        """
        raise NotImplementedError

    def on_request_sent(self):
        """Should be called when a request is processed

        The function updates the number of requests sent and calls
        :py:method:`update_requests_sent`.
        """
        self.requests_sent += 1
        self.update_requests_sent(self.requests_sent)

    def update_requests_sent(self, requests_sent):
        """Called whenever the number of requests sent is updated

        :param int requests_sent: new total number of requests sent
        """
        raise NotImplementedError


class QtStatistics(QObject, Statistics):
    """
    Subclass of :py:class:`Statistics` that uses Qt signals to notify about
    statistics labels that should be updated.
    """

    time_since_start_changed = pyqtSignal(timedelta)
    time_since_last_receive_changed = pyqtSignal(timedelta)
    requests_sent_changed = pyqtSignal(int)

    def __init__(self, sender, parent=None):
        """Constructor

        :param app.sender.QtSender sender: sender instance
        :param QObject parent: QObject parent
        """
        super().__init__(parent)

        # Connect sender signals
        sender.request_processed.connect(self.on_request_sent)

    def create_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_clock_tick)
        self.timer.start(1000)

    def update_time_since_start(self, timedelta):
        self.time_since_start_changed.emit(timedelta)

    def update_time_since_last_receive(self, timedelta):
        self.time_since_last_receive_changed.emit(timedelta)

    def update_requests_sent(self, requests_sent):
        self.requests_sent_changed.emit(requests_sent)
