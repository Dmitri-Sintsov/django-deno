import json
import requests
import traceback

from django.http import (
    HttpResponse, StreamingHttpResponse
)

from .conf import settings


def should_rollup(fullpath):
    with fullpath.open('rb') as f:
        file_begin = f.read(settings.DENO_ROLLUP_HINTS_MAXLEN)
        for hint in settings.DENO_ROLLUP_HINTS:
            if file_begin.startswith(hint):
                return True
    return False


def get_rollup_response(filename, basedir, content_type):
    try:
        rollup_response = requests.post(
            f'{settings.DENO_URL}/rollup/',
            data={
                'filename': filename,
                'basedir': basedir,
            },
            stream=True
        )
        if rollup_response.status_code == 200:
            return StreamingHttpResponse(
                rollup_response.iter_content(chunk_size=settings.DENO_PROXY_CHUNK_SIZE), content_type=content_type
            )
        else:
            response = HttpResponse('throw Error({});'.format(json.dumps(rollup_response.text)))
            response.status_code = rollup_response.status_code
            return response
    except ConnectionError as ex:
        ex_string = json.dumps('\n'.join(
            list(traceback.TracebackException.from_exception(ex).format())
        ))
        return HttpResponse(f'throw Error({ex_string});', content_type=content_type)
