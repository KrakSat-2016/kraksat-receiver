import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from app.parser import OutputLine, ParseError
from app.parser.kundt import KundtParser
from app.parser.telemetry import TelemetryParser
from app.parser.gps import GPSParser

PARSERS = [GPSParser, TelemetryParser, KundtParser]


class BaseOutputParser:
    """
    Base parser class intended to parse the output file indefinitely
    """

    logger = logging.getLogger('Parser')

    def __init__(self, parsers, sender):
        """Constructor

        :param list parsers: list of parsers to use
        :param app.sender.Sender sender: Sender instance to use to send
            the parsed data
        """
        self._parsers = parsers
        self.sender = sender
        self.is_terminated = False

    def parse_file(self, filename):
        """Opens given file and parses the lines inside it indefinitely

        The function catches ParseErrors and passes them to the logger

        :param str filename: path to the file to parse
        """
        fd = os.open(filename, os.O_RDONLY | os.O_NONBLOCK)
        with open(fd) as f:
            while not self.is_terminated:
                line = f.readline()
                if line == '':
                    # We are not able to differentiate between EOF and blocking
                    # IO, so we just wait a while assuming we'll get some data
                    # later
                    sleep(0.05)
                    continue
                line = line.rstrip('\r\n')
                if line == '':
                    self.logger.warning('Empty line received')
                    continue

                try:
                    self.parse_line(line)
                except ParseError as e:
                    logger = (logging.getLogger(e.parser_name) if e.parser_name
                              else self.logger)
                    logger.exception('Could not parse line: %s (%s)', line,
                                     str(e))

    def parse_line(self, line):
        """Parse single line of output

        The function iterates over the available parsers and tries to use the
        first one which has registered message ID that is present at the
        beginning of the provided line

        :param str line: line to parse
        :raise ParseError: if line was not parsed by any registered parser, or
            any other problem occurred during the validation of data
            (a subclass called :py:class:`ValidationError` is usually raised
            in that case)
        """
        for parser in self._parsers:
            msg_id = parser.can_parse(line)
            if msg_id:
                parser_name = parser.__class__.__name__
                # todo parse datetime from file
                output_line = OutputLine(msg_id, datetime.now(), line)
                try:
                    data = parser.parse(output_line)
                except ParseError as e:
                    # Add parser_name info
                    e.parser_name = parser_name
                    raise
                if data:
                    data['timestamp'] = output_line.timestamp
                    self.sender.add_request(
                        parser_name, parser.url, data, append_timestamp=False)
                return

        raise ParseError('Line was not parsed by any parser')

    def mark_terminated(self):
        """Set the parser terminated

        The effect of calling this function is return from parse_file at the
        next loop iteration (so, in practice, after parsing currently parsed
        line or after waiting at most 50ms).
        """
        self.is_terminated = True


class OutputParser(BaseOutputParser):
    """
    Subclass of :py:class:`BaseOutputParser` that uses all available parsers
    """

    def __init__(self, sender):
        parsers = [Parser() for Parser in PARSERS]
        super().__init__(parsers, sender)


class QtOutputParserWorker(QThread, OutputParser):
    """
    :py:class:`OutputParser` wrapper in Qt's :py:class:`QThread`.
    """

    def __init__(self, path, sender, parent=None):
        """Constructor

        :param str path: path to file to parse
        :param app.sender.Sender sender: Sender instance to use to send
            the parsed data
        :param QObject parent: QObject parent of the thread
        """
        super(QtOutputParserWorker, self).__init__(parent, sender=sender)
        self.path = path

    def run(self):
        try:
            self.parse_file(self.path)
        except OSError as e:
            self.logger.exception('Could not parse file (%s)', str(e))


class ParserManager(QObject):
    """
    Manages QtOutputParserWorker instance and allows to run the parser easily.
    """
    logger = logging.getLogger('Parser')
    parser_started = pyqtSignal()
    parser_terminated = pyqtSignal()

    def __init__(self, parent, sender):
        """Constructor

        :param QObject parent: parent object for the worker QThread
        :param app.sender.Sender sender: Sender instance to use to send
            the parsed data
        """
        super(ParserManager, self).__init__(parent)
        self.sender = sender
        self.worker = None
        self.path = None
        self.parent = parent
        self.terminated_by_user = False

    def is_running(self):
        """Return ``True`` if the worker is currently running

        :return: whether the worker is currently running
        :rtype: bool
        """
        return self.worker is not None and self.worker.isRunning()

    def terminate(self):
        """Terminate the currently working worker thread

        Does nothing if the worker is not running.
        """
        if self.is_running():
            self.terminated_by_user = True
            self.worker.mark_terminated()

    def _on_parser_terminated(self):
        if self.terminated_by_user:
            self.logger.info('Parser was terminated by the user')
        else:
            self.logger.warning('Parser terminated unexpectedly')

    def parse_file(self, path):
        """Starts the worker set to parse given file

        :param str|None path: path to the file to parse
        :raise RuntimeError: if the worker is currently running
        :raise FileNotFoundError: if the raw data file does not exist
        """
        if self.is_running():
            raise RuntimeError('The worker is already running')

        try:
            self.path = str(Path(path).resolve())
        except FileNotFoundError as e:
            self.logger.exception(
                'Parser start failed: could not find data file (%s)',
                str(e))
            return
        self.logger.info('Starting parser: {}'
                                         .format(self.path))

        self.worker = QtOutputParserWorker(self.path, self.sender, self.parent)
        self.worker.started.connect(self.parser_started)
        self.worker.finished.connect(self._on_parser_terminated)
        self.worker.finished.connect(self.parser_terminated)
        self.worker.start()
