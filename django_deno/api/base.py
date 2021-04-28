import base64
import hashlib
import json
import requests
import socket
import time

from jsonschema import validate
from requests.exceptions import ConnectionError
from urllib3.exceptions import HTTPError

from django.conf import settings

from ..conf.settings import DENO_SERVER, DENO_URL, DENO_TIMEOUT


class JsonApi:

    server = DENO_SERVER
    url = DENO_URL
    request_schema = None
    response_schema = None
    location = '/'
    extra_post_kwargs = {}
    use_site_id = True

    def parse_post_response(self, response):
        r = response.json()
        if self.response_schema is not None:
            validate(instance=r, schema=self.response_schema)
        return r

    def get_json_data(self):
        if self.use_site_id:
            site_hash = hashlib.sha256(f"{settings.BASE_DIR}{settings.SESSION_COOKIE_NAME}".encode('utf-8')).digest()
            self.json_data['site_id'] = base64.b64encode(site_hash).decode('utf-8')
        return self.json_data

    def get_post_kwargs(self):
        post_kwargs = {
            'url': f'{self.url}{self.location}',
            'json': self.get_json_data(),
        }
        post_kwargs.update(self.extra_post_kwargs)
        return post_kwargs

    def parse_not_responding_error(self, ex):
        # none indicates server is not responding (or not running)
        return None

    def parse_http_error(self, ex):
        return ex

    def post(self, json_data, timeout=DENO_TIMEOUT):
        self.json_data = json_data
        if self.request_schema is not None:
            validate(instance=self.json_data, schema=self.request_schema)
        try:
            self.wait_socket(timeout)
            post_kwargs = self.get_post_kwargs()
            response = requests.post(**post_kwargs)
            try:
                return self.parse_post_response(response)
            except json.decoder.JSONDecodeError as ex:
                return HTTPError(f"JSONDecodeError {str(ex)} {response.text}")
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
