import logging
import traceback

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from app.settings import Settings
from app.ui.ui_login import Ui_LoginDialog


class LoginDialog(QDialog, Ui_LoginDialog):
    logger = logging.getLogger('LoginDialog')
    token_obtained = pyqtSignal(str)

    def __init__(self, api):
        """Constructor

        :param app.api.API api: API instance to use
        """
        super(LoginDialog, self).__init__()
        self.api = api
        self.setupUi(self)
        self.loginButton = self.buttonBox.addButton(
                "&Login", QDialogButtonBox.AcceptRole)
        self.exitButton = self.buttonBox.addButton(
                "&Exit", QDialogButtonBox.RejectRole)

        self.form_fields = (self.serverEdit, self.usernameEdit,
                            self.passwordEdit, self.webappURLEdit)
        self.restore_field_values()

        self.show()
        self.thread = None
        self.logger.info("Login dialog initialized")

    def restore_field_values(self):
        settings = Settings()
        for field in self.form_fields:
            field.setText(settings['login/' + field.objectName()])
        if settings['login/serverEdit']:
            self.rememberCheckBox.setChecked(True)

    def save_field_values(self):
        settings = Settings()
        for field in self.form_fields:
            if self.rememberCheckBox.isChecked():
                settings['login/' + field.objectName()] = field.text()
            else:
                del settings['login/' + field.objectName()]

    def accept(self):
        if not self._is_form_filled():
            QMessageBox(QMessageBox.Information, "Info",
                        "Please fill out all the fields",
                        QMessageBox.Ok).exec()
            return
        self._set_ui_locked(True)

        server, username, password, _ = self._get_form_data()
        api = self.api
        logger = self.logger

        class TokenWorker(QThread):
            token_obtained = pyqtSignal(str)
            error_occurred = pyqtSignal(str, str)

            def run(self):
                try:
                    api.set_server_url(server)
                    token = api.obtain_token(username, password)
                    if token:
                        self.token_obtained.emit(token)
                    else:
                        self.error_occurred.emit("Could not sign in", "")
                except Exception:
                    logger.exception("Could not connect to the server")
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

    def get_webapp_url(self):
        """Return webapp URL set in the form

        :return: webapp URL
        :rtype: str
        """
        return self.webappURLEdit.text()

    def check_server_contents(self):
        self.serverEdit.setText(self.append_http(self.serverEdit.text()))

    def check_webapp_url_contents(self):
        self.webappURLEdit.setText(self.append_http(self.webappURLEdit.text()))

    @staticmethod
    def append_http(url):
        """Append http:// if not present

        :param str url: param to check for http:// presence on
        :return: URL with http://
        :rtype: str
        """
        if url and not (url.startswith('http://') or
                        url.startswith('https://')):
            return 'http://' + url
        return url

    def get_webapp_url(self):
        return self.webappURLEdit.text()

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
