import requests
import socket
import time

from jsonschema import validate
from requests.exceptions import ConnectionError
from urllib3.exceptions import HTTPError

from ..conf import settings


class JsonApi:

    server = settings.DENO_SERVER
    url = settings.DENO_URL
    source_schema = None
    target_schema = None
    location = '/'
    extra_post_kwargs = {}

    def parse_post_response(self, response):
        r = response.json()
        if self.target_schema is not None:
            validate(instance=r, schema=self.target_schema)
        return r

    def get_post_kwargs(self, json_data):
        post_kwargs = {
            'url': f'{self.url}{self.location}',
            'json': json_data,
        }
        post_kwargs.update(self.extra_post_kwargs)
        return post_kwargs

    def parse_not_responding_error(self, ex):
        # none indicates server is not responding (or not running)
        return None

    def parse_http_error(self, ex):
        return ex

    def post(self, json_data, timeout=settings.DENO_TIMEOUT):
        if self.source_schema is not None:
            validate(instance=json_data, schema=self.source_schema)
        try:
            self.wait_socket(timeout)
            post_kwargs = self.get_post_kwargs(json_data)
            response = requests.post(**post_kwargs)
            try:
                return self.parse_post_response(response)
            except Exception as ex:
                return ex
        except (ConnectionError, TimeoutError) as ex:
            return self.parse_not_responding_error(ex)
        except HTTPError as ex:
            return self.parse_http_error(ex)

    # https://gist.github.com/butla/2d9a4c0f35ea47b7452156c96a4e7b12
    def wait_socket(self, timeout=None):
        """Wait until a port starts accepting TCP connections.
        Args:
            timeout (float): In seconds. How long to wait before raising errors.
        Raises:
            TimeoutError: The port isn't accepting connection after time specified in `timeout`.
        """
        if timeout is not None:
            start_time = time.perf_counter()
            while True:
                try:
                    with socket.create_connection((self.server['host'], self.server['port']), timeout=timeout):
                        break
                except OSError as ex:
                    time.sleep(0.01)
                    if time.perf_counter() - start_time >= timeout:
                        raise TimeoutError(
                            f"Waited too long for the port {self.server['port']} on host {self.server['host']} "
                            "to start accepting connections."
                        ) from ex
