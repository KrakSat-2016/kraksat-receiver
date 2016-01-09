import logging
import sys

from PyQt5.QtWidgets import QApplication

from app.api import API
from app.logger import set_up_logging
from app.logindialog import LoginDialog
from app.mainwindow import MainWindow
from app.sender import QtSenderWorker


class Application:
    def __init__(self):
        set_up_logging()
        logging.getLogger('main').info('Starting up the app')

        self.api = API()
        self.main_window = None
        self.sender_worker = None

        self.q_app = QApplication(sys.argv)
        self.dialog = LoginDialog(self.api)
        self.dialog.token_obtained.connect(self._init_app)
        exit_code = self.q_app.exec_()
        logging.getLogger('main').info('Shutting down with exit code %d',
                                       exit_code)
        sys.exit(exit_code)

    def _init_app(self, token):
        self.api.set_token(token)
        self.sender_worker = QtSenderWorker(self.api, self.q_app)
        sender = self.sender_worker.sender
        self._init_main_window(sender)
        # todo gracefully terminate the thread on quit
        self.sender_worker.start()
        self.main_window.show()

    def _init_main_window(self, sender):
        self.main_window = MainWindow(sender)
        self.dialog.close()
        self.dialog = None
