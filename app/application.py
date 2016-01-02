import logging
import sys

from PyQt5.QtWidgets import QApplication

from app.logger import set_up_logging
from app.logindialog import LoginDialog
from app.mainwindow import MainWindow


class Application:
    def __init__(self):
        set_up_logging()
        logging.getLogger('main').info('Starting up the app')

        self.main_window = None
        app = QApplication(sys.argv)
        self.dialog = LoginDialog()
        self.dialog.token_obtained.connect(self.on_token_obtained)
        exit_code = app.exec_()
        logging.getLogger('main').info('Shutting down with exit code %d',
                                       exit_code)
        sys.exit(exit_code)

    def on_token_obtained(self, token):
        self._show_main_window()

    def _show_main_window(self):
        self.main_window = MainWindow()
        self.dialog.close()
        self.dialog = None
        self.main_window.show()
