import json
import requests

from requests.exceptions import ConnectionError
from urllib3.exceptions import HTTPError


from ..conf import settings


def get_api_status():
    try:
        response = requests.get(
            f'{settings.DENO_URL}/status/'
        )
        try:
            result = response.json()
            return {
                'api_version': result['version'],
                'pid': int(result['pid']),
            }
        except Exception as ex:
            return ex
    except ConnectionError as ex:
        # none indicates server is not running
        return None
    except HTTPError as ex:
        return ex
