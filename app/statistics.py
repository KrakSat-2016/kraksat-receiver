from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QTimer


class Statistics:
    """
    Class that manages statistics data (such as time since start, total number
    of requests sent) and notifies about changes in that data.

    Note that this is abstract class; :py:method:`create_timer` and
    ``update_*`` methods should be implemented by subclasses.
    """

    def __init__(self):
        self.start_time = datetime.now()
        self.last_receive_time = None
        self.requests_sent = 0
        self.messages_parsed = 0
        self.parse_failures = 0
        self.total_data_received = 0
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

    def on_data_received(self, output_line):
        """Should be called when data is received

        The function updates last data receive time and total data received
        size as well as calls :py:method:`update_time_since_last_receive` and
        :py:method:`update_total_data_received`.
        """
        self.last_receive_time = datetime.now()
        self.update_time_since_last_receive(timedelta(0))
        self.total_data_received += len(output_line.content)
        self.update_total_data_received(self.total_data_received)

    def update_time_since_last_receive(self, timedelta):
        """Called when time since last data receive is updated

        :param timedelta timedelta: difference between current time and time
            of last data receive
        """
        raise NotImplementedError

    def update_total_data_received(self, total_data_received):
        """Called when total data received size is updated

        :param int total_data_received: size of data received so far in bytes
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

    def on_line_parsed(self, output_line):
        """Should be called whenever a line of data is parsed properly

        The function updates the number of messages parsed and calls
        :py:method:`on_data_received` (which updates the time since last
        receive and the size of parsed data) as well as
        :py:method:`update_messages_parsed` (which notifies about the change
        of the number of messages parsed so far).
        """
        self.on_data_received(output_line)
        self.messages_parsed += 1
        self.update_messages_parsed(self.messages_parsed)

    def update_messages_parsed(self, messages_parsed):
        """Called whenever the number of parsed messages is updated

        :param int messages_parsed: new total number of parsed messages
        """
        raise NotImplementedError

    def on_line_parse_failed(self, output_line):
        """Should be called whenever a line of data couldn't be parsed

        The function updates the number of parse failures and calls
        :py:method:`on_data_received` (which updates the time since last
        receive and the size of parsed data) as well as
        :py:method:`update_parse_failures` (which notifies about the change
        of the number of parse failures so far).
        """
        self.on_data_received(output_line)
        self.parse_failures += 1
        self.update_parse_failures(self.parse_failures)

    def update_parse_failures(self, parse_failures):
        """Called whenever the number of parse failures is updated

        :param int parse_failures: new total number of parse failures
        """
        raise NotImplementedError


class QtStatistics(QObject, Statistics):
    """
    Subclass of :py:class:`Statistics` that uses Qt signals to notify about
    statistics labels that should be updated.
    """

    time_since_start_changed = pyqtSignal(timedelta)
    time_since_last_receive_changed = pyqtSignal(timedelta)
    messages_parsed_changed = pyqtSignal(int)
    parse_failures_changed = pyqtSignal(int)
    requests_sent_changed = pyqtSignal(int)
    total_data_received_changed = pyqtSignal(int)

    def __init__(self, sender, parser_manager, parent=None):
        """Constructor

        :param app.sender.QtSender sender: sender instance
        :param parser_manager: ParserManager instance
        :type parser_manager: app.parser.outputparser.ParserManager
        :param QObject parent: QObject parent
        """
        super().__init__(parent)

        # Connect sender signals
        sender.request_processed.connect(self.on_request_processed)

        # Connect ParserManager signals
        parser_manager.line_parsed.connect(self.on_line_parsed)
        parser_manager.line_parse_failed.connect(self.on_line_parse_failed)

    def on_request_processed(self, request_data, skipped):
        if not skipped:
            self.on_request_sent()

    def create_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_clock_tick)
        self.timer.start(1000)

    def update_time_since_start(self, timedelta):
        self.time_since_start_changed.emit(timedelta)

    def update_time_since_last_receive(self, timedelta):
        self.time_since_last_receive_changed.emit(timedelta)

    def update_messages_parsed(self, messages_parsed):
        self.messages_parsed_changed.emit(messages_parsed)

    def update_parse_failures(self, parse_failures):
        self.parse_failures_changed.emit(parse_failures)

    def update_requests_sent(self, requests_sent):
        self.requests_sent_changed.emit(requests_sent)

    def update_total_data_received(self, total_data_received):
        self.total_data_received_changed.emit(total_data_received)
