import logging
import urllib.parse

import requests


server_url = None
"""Address of the API server"""

logger = logging.getLogger('api')


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


def __request(url, data={}, method='post'):
    """Make a POST request to given URL with provided data

    :param str url: relative URL
    :param dict data: data to send
    :return: :class:`requests.Response` object and json contents (or None in
        case of errors)
    :rtype: tuple[requests.Response, dict]|tuple[requests.Response, None]
    """
    url = urllib.parse.urljoin(server_url, url)
    response = requests.request(method, url, data=data)
    if response.ok:
        return response, response.json()
    return response, None


def __unknown_response(response):
    """Log the event of retrieving invalid response from the server

    :param requests.Response response: Response object
    """
    # todo more sophisticated error logging
    logger.warning("Got an unknown response from the server: %s",
                   response.text)
