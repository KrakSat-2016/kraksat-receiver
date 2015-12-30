import logging
import traceback
import urllib

import requests
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from app import api
from app.settings import Settings
from app.ui.ui_login import Ui_LoginDialog


class LoginDialog(QDialog, Ui_LoginDialog):
    token_obtained = pyqtSignal(str)

    def __init__(self):
        super(LoginDialog, self).__init__()
        self.setupUi(self)
        self.loginButton = self.buttonBox.addButton(
                "&Login", QDialogButtonBox.AcceptRole)
        self.exitButton = self.buttonBox.addButton(
                "&Exit", QDialogButtonBox.RejectRole)

        self.form_fields = (self.serverEdit, self.usernameEdit,
                            self.passwordEdit)
        self.restore_field_values()

        self.show()
        self.thread = None
        logging.getLogger('logindialog').info("Login dialog initialized")

    def restore_field_values(self):
        settings = Settings()
        for field in self.form_fields:
            field.setText(settings.value('login/' + field.objectName()))
        if settings.value('login/serverEdit'):
            self.rememberCheckBox.setChecked(True)

    def save_field_values(self):
        settings = Settings()
        for field in self.form_fields:
            if self.rememberCheckBox.isChecked():
                settings.setValue('login/' + field.objectName(), field.text())
            else:
                settings.remove('login/' + field.objectName())

    def accept(self):
        if not self._is_form_filled():
            QMessageBox(QMessageBox.Information, "Info",
                        "Please fill out all the fields",
                        QMessageBox.Ok).exec()
            return
        self._set_ui_locked(True)

        server, username, password = self._get_form_data()

        class TokenWorker(QThread):
            token_obtained = pyqtSignal(str)
            error_occurred = pyqtSignal(str, str)

            def run(self):
                try:
                    api.server_url = server
                    token = api.obtain_token(username, password)
                    if token:
                        self.token_obtained.emit(token)
                    else:
                        self.error_occurred.emit("Could not sign in", "")
                except Exception:
                    logging.getLogger('logindialog').exception(
                            "Could not connect to the server")
                    self.error_occurred.emit("Could not connect to the server",
                                             traceback.format_exc())

        def on_token_obtained(token):
            self.save_field_values()
            self.token_obtained.emit(token)

        def on_error(message, extra_info):
            msg_box = QMessageBox(QMessageBox.Critical, "Error", message,
                                  QMessageBox.Ok)
            if extra_info:
                msg_box.setDetailedText(extra_info)
            msg_box.exec()

        self.thread = TokenWorker()
        self.thread.token_obtained.connect(on_token_obtained)
        self.thread.error_occurred.connect(on_error)
        self.thread.finished.connect(lambda: self._set_ui_locked(False))
        self.thread.start()

    def check_server_contents(self):
        # Append http:// to the server URL if it is not there
        text = self.serverEdit.text()
        if (text and not (text.startswith('http://') or
                              text.startswith('https://'))):
            self.serverEdit.setText('http://' + text)

    def _set_ui_locked(self, locked):
        """Enable or disable login button and form fields

        :param bool locked: True if the UI should be disabled; False otherwise
        """
        widgets = (self.loginButton, self.rememberCheckBox) + self.form_fields
        for widget in widgets:
            widget.setEnabled(not locked)

    def _get_form_data(self):
        """Return data from login form

        :return: values entered in Server, Username and Passwords fields,
            respectively
        :rtype str
        """
        for field in self.form_fields:
            yield field.text()

    def _is_form_filled(self):
        """Check whether all form fields are filled out"""
        return all(self._get_form_data())
