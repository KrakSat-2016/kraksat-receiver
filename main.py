import sys

from PyQt5.QtWidgets import QApplication

from app.login import LoginDialog
from app.mainwindow import MainWindow


class Main:
    def __init__(self):
        app = QApplication(sys.argv)
        self.dialog = LoginDialog()
        self.main_window = None
        self.dialog.token_obtained.connect(self.on_token_obtained)
        sys.exit(app.exec_())

    def on_token_obtained(self, token):
        self.main_window = MainWindow()
        self.dialog.close()
        self.main_window.show()


if __name__ == '__main__':
    Main()
