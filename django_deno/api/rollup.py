import json
import requests
import traceback

from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError

from django.http import (
    HttpResponse, StreamingHttpResponse
)

from ..conf import settings


def should_rollup(fullpath):
    if settings.DENO_ENABLE:
        with fullpath.open('rb') as f:
            file_begin = f.read(settings.DENO_ROLLUP_HINTS_MAXLEN)
            for hint in settings.DENO_ROLLUP_HINTS:
                if file_begin.startswith(hint):
                    return True
    return False


def post_rollup(fullpath, content_type):
    try:
        rollup_response = requests.post(
            f'{settings.DENO_URL}/rollup/',
            data={
                'filename': str(fullpath.name),
                'basedir': str(fullpath.parent),
            },
            stream=True
        )
        if rollup_response.status_code == 200:
            return StreamingHttpResponse(
                rollup_response.iter_content(chunk_size=settings.DENO_PROXY_CHUNK_SIZE), content_type=content_type
            )
        else:
            response = HttpResponse(
                'throw Error({});'.format(json.dumps(rollup_response.text)),
                content_type=content_type
            )
            response.status_code = 200
            return response
    except (HTTPError, RequestException) as ex:
        ex_string = json.dumps('\n'.join(
            list(traceback.TracebackException.from_exception(ex).format())
        ))
        response = HttpResponse(
            f'throw Error({ex_string});',
            content_type=content_type
        )
        response.status_code = 200
        return response
