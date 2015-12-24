import sys

from PyQt5.QtWidgets import QApplication

from app.login import LoginDialog


class Main:
    def __init__(self):
        app = QApplication(sys.argv)
        self.dialog = LoginDialog()
        self.dialog.token_obtained.connect(self.on_token_obtained)
        sys.exit(app.exec_())

    def on_token_obtained(self, token):
        print(token)
        self.dialog.close()


if __name__ == '__main__':
    Main()
