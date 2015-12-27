import logging
import sys

from PyQt5.QtWidgets import QApplication

from app.logger import set_up_logging
from app.login import LoginDialog
from app.mainwindow import MainWindow


class Main:
    def __init__(self):
        set_up_logging()
        logging.getLogger('main').info('Starting up the app')

        app = QApplication(sys.argv)
        self.dialog = LoginDialog()
        self.main_window = None
        self.dialog.token_obtained.connect(self.on_token_obtained)
        exit_code = app.exec_()
        logging.getLogger('main').info('Shutting down with exit code %d',
                                       exit_code)
        sys.exit(exit_code)

    def on_token_obtained(self, token):
        self.main_window = MainWindow()
        self.dialog.close()
        self.main_window.show()


if __name__ == '__main__':
    Main()
