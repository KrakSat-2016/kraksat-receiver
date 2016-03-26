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
        self.sender = sender
        sender.error_occurred.connect(self.on_error)

    def on_error(self, request_data, exception, traceback_exception):
        msg, details = self.process_error(exception, traceback_exception)
        msg_box = QMessageBox(
            QMessageBox.Critical, 'Error processing a request', msg,
            QMessageBox.Ok, self.parent)
        msg_box.setInformativeText(
            'Request queue was paused automatically. You can unpause the '
            'queue later to resend the request, try again now or remove the '
            'request from the queue and continue.')
        try_again_btn = msg_box.addButton('Try again', QMessageBox.AcceptRole)
        remove_req_btn = msg_box.addButton('Remove request and unpause',
                                           QMessageBox.DestructiveRole)
        msg_box.setDetailedText(details)

        msg_box.exec()
        clicked_button = msg_box.clickedButton()
        if clicked_button == remove_req_btn:
            self.sender.set_skip_current()
        if clicked_button in (try_again_btn, remove_req_btn):
            self.sender.paused = False
