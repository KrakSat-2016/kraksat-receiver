import logging
import sys

from PyQt5.QtWidgets import QApplication

from app.api import API
from app.logger import set_up_logging
from app.logindialog import LoginDialog
from app.mainwindow import MainWindow
from app.parser.outputparser import ParserManager
from app.sender import QtSenderWorker


class Application:
    logger = logging.getLogger('Main')

    def __init__(self):
        set_up_logging()
        self.logger.info('Starting up the app')

        self.api = API()
        self.main_window = None
        self.sender_worker = None

        self.q_app = QApplication(sys.argv)
        self.dialog = LoginDialog(self.api)
        self.dialog.token_obtained.connect(self._init_app)
        exit_code = self.q_app.exec_()
        self.logger.info('Waiting for all threads to be terminated...')
        for thread, name in [(self.parser_manager, 'Parser'),
                             (self.sender_worker, 'Sender')]:
            if not thread.wait(1000):
                self.logger.error('Thread %s failed to terminate', name)
        self.logger.info('Shutting down with exit code %d', exit_code)
        sys.exit(exit_code)

    def _init_app(self, token):
        self.api.set_token(token)
        self.sender_worker = QtSenderWorker(self.api, self.q_app)
        sender = self.sender_worker.sender
        self.parser_manager = ParserManager(self.q_app, sender)
        self._init_main_window(sender, self.parser_manager)

        self.sender_worker.start()
        self.main_window.show()

    def _init_main_window(self, sender, parser_manager):
        self.main_window = MainWindow(sender, parser_manager)
        self.dialog.close()
        self.dialog = None
