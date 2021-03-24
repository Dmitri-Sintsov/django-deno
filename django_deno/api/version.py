import json
import requests

from requests.exceptions import ConnectionError
from urllib3.exceptions import HTTPError


from ..conf import settings


def get_api_version():
    try:
        response = requests.get(
            f'{settings.DENO_URL}/'
        )
        try:
            result = response.json()
            return {
                'version': result['version'],
                'pid': int(result['pid']),
            }
        except ex:
            return ex
    except ConnectionError as ex:
        # none indicates server is not running
        return None
    except HTTPError as ex:
        return ex
