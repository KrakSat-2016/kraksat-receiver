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
        with self.modified_lock:
            self.data_added.notify_all()

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
            self.modified = False
        try:
            data = Calculator.perform_calculations(self)
            if data and self.sender is not None:
                self.sender.add_request('Analyzer', '/planetarydata/', data)
        except Exception as e:
            # We don't really want to crash the app because some error occurred
            # during the calculations
            logging.getLogger('Analyzer').critical(
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
