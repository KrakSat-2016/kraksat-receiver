import urllib
from threading import Thread

import requests
from gi.repository import Gtk, GLib


class Main:
    LOGIN_FORM_FIELDS = ['server_entry', 'username_entry', 'password_entry']

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui/login.glade')
        self.builder.connect_signals(self)
        login_window = self.builder.get_object('login_window')
        self.prepare_ui()
        login_window.show_all()
        Gtk.main()

    def prepare_ui(self):
        # Override tab order in button box
        action_buttonbox = self.builder.get_object('action_buttonbox')
        login_button = self.builder.get_object('login_button')
        exit_button = self.builder.get_object('exit_button')
        action_buttonbox.set_focus_chain((login_button, exit_button))

    def login(self, *args):
        if not self._is_form_filled():
            self._set_infobar_error('Please fill out all the fields')
            return
        self._set_ui_locked(True)

        server, username, password = self._get_form_data()

        def request():
            try:
                token = obtain_token(server, username, password)
                if token:
                    GLib.idle_add(self._set_infobar_error, 'Token: ' + token)
                else:
                    GLib.idle_add(self._set_infobar_error, 'Could not sign in')
            except Exception as e:
                print(e)  # todo use logger
                GLib.idle_add(self._set_infobar_error,
                              'Could not connect to the server')
            finally:
                GLib.idle_add(self._set_ui_locked, False)

        thread = Thread(target=request)
        thread.start()

    def check_server_contents(self, *args):
        # Append http:// to the server URL if it is not there
        server = self.builder.get_object('server_entry')
        text = server.get_text()
        if (text and not (text.startswith('http://') or
                          text.startswith('https://'))):
            text = 'http://' + text
        server.set_text(text)

    def _set_ui_locked(self, locked):
        self.builder.get_object('login_button').set_sensitive(not locked)
        for field in self.LOGIN_FORM_FIELDS:
            self.builder.get_object(field).set_sensitive(not locked)

    def _set_infobar_error(self, message):
        """Set message on error infobar and display it

        :param message: message to set
        """
        self.builder.get_object('error_infobar_label').set_text(message)
        self.builder.get_object('error_infobar').show()

    def hide_infobar(self, *args):
        """Hide error infobar"""
        self.builder.get_object('error_infobar').hide()

    def update_login_sensitive(self, *args):
        # Enable login button only if all fields are filled out
        self.builder.get_object('login_button').set_sensitive(
            self._is_form_filled())

    def _get_form_data(self):
        """Return data from login form

        :return: values entered in Server, Username and Passwords fields,
            respectively
        :rtype str
        """
        for field in self.LOGIN_FORM_FIELDS:
            yield self.builder.get_object(field).get_text()

    def _is_form_filled(self):
        """Check whether all form fields are filled out"""
        return all(self._get_form_data())

    def quit(self, *args):
        Gtk.main_quit()


def obtain_token(server, username, password):
    """Obtains authentication token for provided user

    :param str server: address of API server to use
    :param str username: username to get token for
    :param str password: user's password
    :return: token returned by server or None in case of invalid credentials
        or other errors
    """
    url = urllib.parse.urljoin(server, '/token-auth/')
    data = {'username': username, 'password': password}
    response = requests.post(url, data=data)
    json = response.json()
    if response.status_code == 200 and 'token' in json:
        return json['token']
    else:
        # todo use logger/throw an exception
        print(response.text)
        return None


if __name__ == '__main__':
    Main()
