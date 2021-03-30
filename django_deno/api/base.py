import requests
import socket
import time

from dict_schema_validator import validator
from requests.exceptions import ConnectionError
from urllib3.exceptions import HTTPError

from ..conf import settings


class Api:

    server = settings.DENO_SERVER
    url = settings.DENO_URL
    schema = None
    location = '/'

    def post_response(self, response):
        r = response.json()
        if self.schema is not None:
            errors = validator.validate(self.schema, r)
            for err in errors:
                raise TypeError(err['msg'])
        return r

    def post(self, json_data, timeout=None):
        if timeout is None:
            timeout = settings.DENO_TIMEOUT
        try:
            self.wait_for_port(self.server['port'], self.server['host'], timeout)
            response = requests.post(
                f'{self.url}{self.location}',
                json=json_data,
            )
            try:
                return self.post_response(response)
            except Exception as ex:
                return ex
        except (ConnectionError, TimeoutError) as ex:
            # none indicates server is not responding (or not running)
            return None
        except HTTPError as ex:
            return ex

    # https://gist.github.com/butla/2d9a4c0f35ea47b7452156c96a4e7b12
    def wait_for_port(self, port, host='localhost', timeout=5.0):
        """Wait until a port starts accepting TCP connections.
        Args:
            port (int): Port number.
            host (str): Host address on which the port should exist.
            timeout (float): In seconds. How long to wait before raising errors.
        Raises:
            TimeoutError: The port isn't accepting connection after time specified in `timeout`.
        """
        if timeout is not None:
            start_time = time.perf_counter()
            while True:
                try:
                    with socket.create_connection((host, port), timeout=timeout):
                        break
                except OSError as ex:
                    time.sleep(0.01)
                    if time.perf_counter() - start_time >= timeout:
                        raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
                                           'connections.'.format(port, host)) from ex
