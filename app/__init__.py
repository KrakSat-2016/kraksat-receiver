import logging
import sys

from PyQt5.QtWidgets import QApplication

from app.analyzer import QtAnalyzerWorker
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
        self.analyzer_worker = None
        self.parser_manager = None

        self.q_app = QApplication(sys.argv)
        # Remove ugly frame around Status Bar items on some styles
        self.q_app.setStyleSheet('QStatusBar::item { border-width: 0px }')
        self.dialog = LoginDialog(self.api)
        self.dialog.token_obtained.connect(self._init_app)
        exit_code = self.q_app.exec_()
        self.logger.info('Waiting for all threads to be terminated...')
        if self.analyzer_worker is not None:
            # Analyzer worker is not terminated in MainWindow
            self.analyzer_worker.set_terminated()
        for thread, name in [(self.parser_manager, 'Parser'),
                             (self.analyzer_worker, 'Analyzer'),
                             (self.sender_worker, 'Sender')]:
            if thread and not thread.wait(3000):
                self.logger.error('Thread %s failed to terminate', name)
        self.logger.info('Shutting down with exit code %d', exit_code)
        sys.exit(exit_code)

    def _init_app(self, token):
        self.api.set_token(token)
        self.sender_worker = QtSenderWorker(self.api, self.q_app)
        sender = self.sender_worker.sender
        self.analyzer_worker = QtAnalyzerWorker(sender, self.q_app)
        self.parser_manager = ParserManager(self.q_app, sender,
                                            self.analyzer_worker)
        self._init_main_window(sender, self.parser_manager)

        self.sender_worker.start()
        self.analyzer_worker.start()
        self.main_window.show()

    def _init_main_window(self, sender, parser_manager):
        self.main_window = MainWindow(sender, parser_manager)
        self.main_window.set_webapp_url(self.dialog.get_webapp_url())
        self.dialog.close()
        self.dialog = None
