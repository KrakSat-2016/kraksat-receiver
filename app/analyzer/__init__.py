import logging
import threading

from PyQt5.QtCore import QThread

from app.analyzer.calculator import Calculator
from app.analyzer.collector import Collector


class AnalyzerWorker(Collector):
    """
    Integration of Collector and Calculator classes that performs calculation
    of collected data indefinitely.
    """
    logger = logging.getLogger('Analyzer')

    def __init__(self, sender):
        """Constructor

        :param app.sender.Sender sender: Sender instance to use to send
            the parsed data
        """
        super().__init__()

        self.sender = sender
        # Set to True whenever new value is added and to False when calculation
        # is done
        # Since adding values and calculations are done in separate threads,
        # we need mutex for the modified field
        self.modified = False
        self.modified_lock = threading.Lock()
        self.data_added = threading.Condition(self.modified_lock)

        self._paused = False
        self.pause_lock = threading.Lock()
        self.unpaused = threading.Condition(self.pause_lock)

        self.terminated = False

    def _data_modified(self):
        with self.modified_lock:
            self.modified = True
            self.data_added.notify()

    def set_terminated(self):
        """Terminate Analyzer thread

        Releases any lock :py:method:`_calculate` may be waiting for;
        also prevents this method from being called again. Note that this may
        not terminate the thread immediately as it may wait for the current
        calculation to be performed.
        """
        self.terminated = True
        with self.modified_lock, self.pause_lock:
            self.data_added.notify_all()
            self.unpaused.notify_all()

    @property
    def paused(self):
        """Check if the analyzer is currently paused

        :return: ``True`` if the analyzer is currently paused; ``False``
            otherwise
        :rtype: bool
        """
        return self._paused

    @paused.setter
    def paused(self, paused):
        """(Un)pause the analyzer

        :param bool paused: whether or not data processing should be withheld
            until unpause
        """
        self.logger.info('Analyzer %s', 'paused' if paused else 'unpaused')
        with self.pause_lock:
            self._paused = paused
            if not paused:
                self.unpaused.notify()

    def calculate_indefinitely(self):
        """Process data as long as Analyzer is not terminated

        See :py:method:`set_terminated` to terminate executing of this
        function.
        """
        while not self.terminated:
            self._calculate()

    def _calculate(self):
        """Wait for a modification and then calculate the planetary data."""
        with self.modified_lock:
            while not self.modified:
                self.data_added.wait()
                if self.terminated:
                    return
        with self.pause_lock:
            while self.paused:
                self.unpaused.wait()
                if self.terminated:
                    return
        with self.modified_lock:
            self.modified = False

        try:
            data = Calculator.perform_calculations(self)
            if data and self.sender is not None:
                self.sender.add_request('Analyzer', '/planetarydata/', data)
        except Exception as e:
            # We don't really want to crash the app because some error occurred
            # during the calculations
            self.logger.critical(
                'Unknown exception thrown during calculations: %s', str(e),
                exc_info=True)


class QtAnalyzerWorker(QThread, AnalyzerWorker):
    """
    Subclass of :py:class:`AnalyzerWorker` that performs the calculation on a
    separate thread.
    """

    def __init__(self, sender, parent=None):
        """Constructor

        :param app.sender.Sender sender: Sender instance to use to send
            the parsed data
        :param QObject parent: parent object for the worker QThread
        """
        super().__init__(parent, sender=sender)

    def run(self):
        self.calculate_indefinitely()
