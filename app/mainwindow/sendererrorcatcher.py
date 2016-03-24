import json

import requests
from PyQt5.QtWidgets import QMessageBox

from app.api import APIError


class SenderErrorCatcher:
    """Class that aims to simplify handling errors occurred when making API
    calls by the queue.

    Note that this class does not do anything useful itself; see
    :py:class:`QtSenderErrorCatcher` for an implementation that has an actual
    UI.
    """

    def process_error(self, exception, traceback_exception):
        """Generate message and error details to be displayed for the user

        :return: two strings: message and error details to display
        :rtype: tuple
        """
        if isinstance(exception, requests.exceptions.RequestException):
            msg = 'Could not connect to the server:\n\n' + str(exception)
            details = ''.join(traceback_exception.format())
        elif isinstance(exception, APIError):
            msg = exception.message
            try:
                json_contents = exception.response.json()
                details = json.dumps(json_contents, indent=4)
            except json.JSONDecodeError:
                details = exception.response.text
        return msg, details


class QtSenderErrorCatcher(SenderErrorCatcher):
    """Subclass of :py:class:`SenderErrorCatcher` that displays a QMessageBox
    when an error occurs during processing a request from the request queue.
    """

    def __init__(self, parent, sender):
        """Constructor

        :param QWidget parent: parent of the ``QMessageBox``
        :param app.sender.QtSender sender: QtSender instance to connect to its
            ``error_occurred`` signal
        """
        self.parent = parent
        sender.error_occurred.connect(self.on_error)

    def on_error(self, request_data, exception, traceback_exception):
        msg, details = self.process_error(exception, traceback_exception)
        msg_box = QMessageBox(
            QMessageBox.Critical, 'Error processing a request', msg,
            QMessageBox.Ok, self.parent)
        msg_box.setInformativeText(
            'Request queue was paused automatically. Unpause it to continue '
            'sending the data.')
        msg_box.setDetailedText(details)
        msg_box.exec()
