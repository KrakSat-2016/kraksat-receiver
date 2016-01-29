import logging
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from app.parser import OutputLine, ParseError
from app.parser.gps import GPSParser
from app.settings import Settings

PARSERS = [GPSParser]


class BaseOutputParser:
    """
    Base parser class intended to parse the output file indefinitely
    """

    def __init__(self, parsers):
        """Constructor

        :param list parsers: list of parsers to use
        """
        self._parsers = parsers
        self._ids_to_parsers = {parser.ids: parser for parser in parsers}

    def parse_file(self, filename):
        """Opens given file and parses the lines inside it indefinitely

        The function catches ParseErrors and passes them to the logger

        :param str filename: path to the file to parse
        """
        with open(filename, 'r') as f:
            # todo a way to terminate the thread by using non-blocking IO and
            # something like while not self.is_terminated
            while True:
                line = f.readline()
                if line == '':
                    break  # todo display message we've reached the end of file
                try:
                    self.parse_line(line.rstrip('\r\n'))
                except ParseError as e:
                    logging.getLogger('parser').exception(
                        'Could not parse line: {} ({})'
                        .format(line, str(e))
                    )

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
        for ids, parser in self._ids_to_parsers.items():
            for id in ids:
                if line.startswith(id):
                    # todo parse datetime from file
                    parser.parse(OutputLine(id, datetime.now(), line))
                    return

        raise ParseError('Line was not parsed by any parser')


class OutputParser(BaseOutputParser):
    """
    Subclass of :py:class:`BaseOutputParser` that uses all available parsers
    """

    def __init__(self):
        parsers = [Parser() for Parser in PARSERS]
        super().__init__(parsers)


class QtOutputParserWorker(QThread, OutputParser):
    """
    :py:class:`OutputParser` wrapper in Qt's :py:class:`QThread`.
    """

    def __init__(self, path, parent=None):
        """Constructor

        :param str path: path to file to parse
        :param QObject parent: QObject parent of the thread
        """
        super(QtOutputParserWorker, self).__init__(parent)
        self.path = path

    def run(self):
        try:
            self.parse_file(self.path)
        except OSError as e:
            logging.getLogger('parser').exception('Could not parse file ({})'
                                                  .format(str(e)))


class ParserManager(QObject):
    """
    Manages QtOutputParserWorker instance and allows to run the parser easily.
    """
    parser_started = pyqtSignal()
    parser_terminated = pyqtSignal()

    def __init__(self, parent):
        """Constructor

        :param QObject parent: parent object for the worker QThread
        """
        super(ParserManager, self).__init__(parent)
        self.worker = None
        self.path = None
        self.parent = parent

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
            # todo implement ParserManage.terminate()
            raise NotImplementedError

    def _on_parser_terminated(self):
        logging.getLogger('parser').warning('Parser terminated unexpectedly')

    def parse_file(self, path=None):
        """Starts the worker set to parse given file

        :param str|None path: path to the file to parse. ``None`` means the
            path will be retrieved from the settings (``parser/filename`` key)
            or the default filename (``data``) will be used if there's no
            value in settings
        :raise RuntimeError: if the worker is currently running
        :raise FileNotFoundError: if the raw data file does not exist
        """
        if self.is_running():
            raise RuntimeError('The worker is already running')
        if path is None:
            path = Settings().value('parser/filename', 'data')

        try:
            self.path = str(Path(path).resolve())
        except FileNotFoundError as e:
            logging.getLogger('parser').exception(
                    'Parser start failed: could not find data file ({})'
                    .format(str(e)))
            return

        self.worker = QtOutputParserWorker(self.path, self.parent)
        self.worker.started.connect(self.parser_started)
        self.worker.finished.connect(self._on_parser_terminated)
        self.worker.finished.connect(self.parser_terminated)
        self.worker.start()
