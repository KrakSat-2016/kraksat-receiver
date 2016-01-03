import logging
import urllib.parse
from json import JSONDecodeError

import dateutil.parser
import requests
from requests.auth import AuthBase

from app.timeutils import TimeOffset

server_url = None
"""Address of the API server"""

auth = None
"""Authentication class to use"""

logger = logging.getLogger('api')


class TokenAuth(AuthBase):
    """Attaches Token Authentication header to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Token {}'.format(self.token)
        return request


def obtain_token(username, password):
    """Obtain authentication token for provided user

    :param str username: username to get token for
    :param str password: user's password
    :return: token returned by server or None in case of invalid credentials
        or other errors
    """
    data = {'username': username, 'password': password}
    response, json = __request('/token-auth/', data)
    if json and 'token' in json:
        return json['token']
    __unknown_response(response)


def set_token(token):
    global auth  # todo move entire api module into a class
    auth = TokenAuth(token)


def get_gsinfo():
    """Obtain the latest Ground Station info

    :return: Ground Station info, respectively: timestamp, latitude, longitude,
        ground station timezone
    :rtype: tuple[datetime.datetime, float, float, TimeOffset|None]|None
    """
    response, json = __request('/gsinfo/latest/', method='get')
    if json:
        try:
            timezone = TimeOffset.from_minutes(json['timezone'])
        except ValueError:
            logger.warning('Could not create TimeOffset object, received '
                           'offset: %s', json['timezone'])
            timezone = None
        return (__parse_datetime(json['timestamp']), json['latitude'],
                json['longitude'], timezone)
    elif response.status_code != requests.codes.no_content:
        __unknown_response(response)


def __parse_datetime(s):
    """Parse provided string as datetime object

    :param str s: string to parse
    :return: datetime object with timezone info set to current system timezone
    :rtype datetime.datetime
    """
    return dateutil.parser.parse(s).astimezone(tz=None)


def datetime_encode(obj):
    representation = obj.isoformat()
    if representation.endswith('+00:00'):
        representation = representation[:-6] + 'Z'
    return representation


def __request(url, data={}, files=None, method='post'):
    """Make a request to given URL with provided data

    :param str url: relative URL
    :param dict data: data to send
    :param dict|None files: files to send
    :param str method: HTTP method to use
    :return: :py:class:`requests.Response` object and json contents (or None in
        case of errors)
    :rtype: tuple[requests.Response, dict]|tuple[requests.Response, None]
    """
    url = urllib.parse.urljoin(server_url, url)
    response = requests.request(method, url, data=data, files=files, auth=auth)
    if response.status_code in (requests.codes.ok, requests.codes.created):
        try:
            return response, response.json()
        except JSONDecodeError:
            logger.warning("Could not decode JSON despite %d status code\n"
                           "Contents: %s", response.status_code, response.text,
                           exc_info=True)
    return response, None


def __unknown_response(response):
    """Log the event of retrieving invalid response from the server

    :param requests.Response response: Response object
    """
    # todo more sophisticated error logging
    logger.warning("Got an unknown response from the server: %s",
                   response.text)
