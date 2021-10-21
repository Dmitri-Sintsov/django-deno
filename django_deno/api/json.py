import json
import requests
import socket
import time

from jsonschema import validate
from urllib.parse import urlparse
from requests.exceptions import ConnectionError
from urllib3.exceptions import HTTPError


class JsonApi:

    server = None
    url = None
    timeout = None
    request_get_schema = None
    request_post_schema = None
    response_get_schema = None
    response_post_schema = None
    location = '/'
    extra_get_kwargs = {}
    extra_post_kwargs = {}

    scheme_ports = {
        'http': 80,
        'https': 443,
    }

    def __init__(self, **kwargs):
        if self.server is None:
            parts = urlparse(self.url)
            self.server = {
                'scheme': parts.scheme,
                'hostname': parts.hostname,
                'port': self.scheme_ports[parts.scheme] if parts.port is None else parts.port
            }
        elif self.url is None:
            self.url = f'{self.server["scheme"]}://{self.server["hostname"]}:{self.server["port"]}'

    def parse_get_response(self, response):
        response_data = response.json()
        if self.response_get_schema is not None:
            validate(instance=response_data, schema=self.response_get_schema)
        return response_data

    def parse_post_response(self, response):
        response_data = response.json()
        if self.response_post_schema is not None:
            validate(instance=response_data, schema=self.response_post_schema)
        return response_data

    def build_request_json(self):
        return self.request_json

    def build_get_request_json(self):
        return self.build_request_json()

    def build_post_request_json(self):
        return self.build_request_json()

    def build_request_kwargs(self, context):
        request_kwargs = {
            'url': f'{self.url}{self.location}',
        }
        request_json = context['build_request_json']()
        if request_json is not None:
            request_kwargs['json'] = request_json
        request_kwargs.update(context['extra_kwargs'])
        return request_kwargs

    def build_get_kwargs(self):
        return self.build_request_kwargs({
            'build_request_json': self.build_get_request_json,
            'extra_kwargs': self.extra_get_kwargs,
        })

    def build_post_kwargs(self):
        return self.build_request_kwargs({
            'build_request_json': self.build_post_request_json,
            'extra_kwargs': self.extra_post_kwargs,
        })

    def parse_not_responding_error(self, ex):
        # none indicates server is not responding (or not running)
        return None

    def parse_http_error(self, ex):
        return ex

    def set_timeout(self, timeout):
        self.timeout = timeout
        return self

    def get(self, request_json=None):
        context = {
            'requests_method': requests.get,
            'validate_request': self.validate_get_request,
            'build_kwargs': self.build_get_kwargs,
            'parse_response': self.parse_get_response,
        }
        return self.method(context, request_json)

    def post(self, request_json=None):
        context = {
            'requests_method': requests.post,
            'validate_request': self.validate_post_request,
            'build_kwargs': self.build_post_kwargs,
            'parse_response': self.parse_post_response,
        }
        return self.method(context, request_json)

    def validate_get_request(self):
        if self.request_get_schema is not None:
            validate(instance=self.request_json, schema=self.request_get_schema)

    def validate_post_request(self):
        if self.request_post_schema is not None:
            validate(instance=self.request_json, schema=self.request_post_schema)

    def method(self, context, request_json):
        self.request_json = request_json
        context['validate_request']()
        try:
            self.wait_socket(self.timeout)
            request_kwargs = context['build_kwargs']()
            response = context['requests_method'](**request_kwargs)
            try:
                return context['parse_response'](response)
            except json.decoder.JSONDecodeError as ex:
                return HTTPError(f'JSONDecodeError {str(ex)} received text: "{response.text}"')
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
                    with socket.create_connection((self.server['hostname'], self.server['port']), timeout=timeout):
                        break
                except OSError as ex:
                    time.sleep(0.01)
                    if time.perf_counter() - start_time >= timeout:
                        raise TimeoutError(
                            f"Waited too long for the port {self.server['port']} on host {self.server['hostname']} "
                            "to start accepting connections."
                        ) from ex
