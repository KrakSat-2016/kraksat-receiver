import logging
import urllib.parse
from json import JSONDecodeError

import dateutil.parser
import requests
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from requests.auth import AuthBase

from app.timeutils import TimeOffset


class APIWorker(QThread):
    """
    Subclass of QThread that makes making async API calls easier, providing
    easy way to call API function (or, actually, any function) and be notified
    as soon as the function ends.
    """
    result_got = pyqtSignal(object)

    def __init__(self, func, parent=None, result_got=None, on_finished=None):
        """Constructs and starts the thread

        :param function func: function to call in another thread
        :param QObject parent: QThread parent
        :param function result_got: function to call when result from ``func``
            is returned. Note that tuples are extracted and if result is
            ``None`` then ``result_got`` is not called.
        :param function on_finished: function to call after the thread is
            terminated. This is always called after ``result_got``
        """
        super().__init__(parent)
        self._func = func

        if result_got is not None:
            self._result_got = result_got
            self.result_got.connect(self._on_result_got)
        if on_finished is not None:
            self.finished.connect(on_finished)
        self.start()

    def _on_result_got(self, result):
        if isinstance(result, tuple):
            self._result_got(*result)
        elif result is not None:
            self._result_got(result)

    def run(self):
        result = self._func()
        self.result_got.emit(result)


class APIError(Exception):
    def __init__(self, message, response=None):
        """Constructor

        :param str message: exception message
        :param requests.Response response: response received from the server
        """
        if response is not None:
            exc_msg = message + '\nResponse body: ' + response.text
        else:
            exc_msg = message
        super().__init__(exc_msg)
        self.message = message
        self.response = response


class TokenAuth(AuthBase):
    """Attaches Token Authentication header to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Token {}'.format(self.token)
        return request


class API:
    logger = logging.getLogger('api')

    def __init__(self):
        self.server_url = None  # Address of the API server
        self.auth = None  # Authentication class to use

    def obtain_token(self, username, password):
        """Obtain authentication token for provided user

        :param str username: username to get token for
        :param str password: user's password
        :return: token returned by server or None in case of invalid
            credentials or other errors
        """
        data = {'username': username, 'password': password}
        response, json = self._request('/token-auth/', data)
        if json and 'token' in json:
            return json['token']
        self.__unknown_response(response)

    def set_server_url(self, url):
        """Set new server URL

        :param str url: URL of the server
        """
        self.server_url = url

    def set_token(self, token):
        """Set new authentication token

        :param str token: token to use
        """
        self.auth = TokenAuth(token)

    # todo data validation in get_* functions
    def get_gsinfo(self):
        """Obtain the latest Ground Station info

        :return: Ground Station info, respectively: timestamp, latitude,
            longitude, ground station timezone
        :rtype: tuple[datetime.datetime, float, float, TimeOffset|None]|None
        """
        response, json = self._request('/gsinfo/latest/', method='get')
        if json:
            try:
                timezone = TimeOffset.from_minutes(json['timezone'])
            except ValueError:
                self.logger.warning('Could not create TimeOffset object, '
                                    'received offset: %s', json['timezone'])
                timezone = None
            return (_parse_datetime(json['timestamp']), json['latitude'],
                    json['longitude'], timezone)
        elif response.status_code != requests.codes.no_content:
            self.__unknown_response(response)

    def get_status(self):
        """Obtain the latest mission status

        :return: Mission status info, respectively: timestamp, phase,
            mission time, is cansat online
        :rtype: tuple[datetime.datetime, str, float|None, bool]
        """
        response, json = self._request('/status/latest/', method='get')
        if json:
            return (_parse_datetime(json['timestamp']), json['phase'],
                    json['mission_time'], json['cansat_online'])
        elif response.status_code != requests.codes.no_content:
            self.__unknown_response(response)

    def create(self, url, data, files=None, requests_object=requests):
        response, json = self._request(url, data, files=files,
                                       requests_object=requests_object)
        if response.status_code != requests.codes.created:
            raise APIError('201 status code was expected when creating '
                           'resource; got {}'.format(response.status_code),
                           response)

    def _request(self, url, data={}, files=None, method='post',
                 requests_object=requests):
        """Make a request to given URL with provided data

        :param str url: relative URL
        :param dict data: data to send
        :param dict|None files: files to send
        :param str method: HTTP method to use
        :param requests_object: requests object to make the request with. Uses
            ``requests`` module by default; ``requests.Session`` instance
            can be used instead.
        :return: :py:class:`requests.Response` object and json contents (or
            ``None`` in case of errors)
        :rtype: tuple[requests.Response, dict]|tuple[requests.Response, None]
        """
        url = urllib.parse.urljoin(self.server_url, url)
        response = requests_object.request(method, url, data=data, files=files,
                                           auth=self.auth)
        if response.status_code in (requests.codes.ok, requests.codes.created):
            try:
                return response, response.json()
            except JSONDecodeError:
                self.logger.warning(
                    "Could not decode JSON despite %d status code\n"
                    "Contents: %s", response.status_code, response.text,
                    exc_info=True
                )
        return response, None

    def __unknown_response(self, response):
        """Log the event of retrieving invalid response from the server

        :param requests.Response response: Response object
        """
        # todo more sophisticated error logging
        self.logger.warning("Got an unknown response from the server: %s",
                            response.text)


def _parse_datetime(s):
    """Parse provided string as datetime object

    :param str s: string to parse
    :return: datetime object with timezone info set to current system timezone
    :rtype datetime.datetime
    """
    return dateutil.parser.parse(s).astimezone(tz=None)


def encode_datetime(dt):
    """Converts provided datetime object into ISO 8601/RFC3339-compliant string

    :param datetime.datetime dt: datetime object
    :return: string representation of dt
    :rtype: str
    """
    s = dt.isoformat()
    if s.endswith('+00:00'):
        s = s[:-6] + 'Z'
    return s
