import json
import requests
import traceback

from django.http import (
    HttpResponse, StreamingHttpResponse
)


rollup_hints = [b'"use rollup"', b"'use rollup'"]
proxy_chunk_size = 256 * 1024


def should_rollup(fullpath):
    with fullpath.open('rb') as f:
        hint = f.read(len(rollup_hints[0]))
        return hint in rollup_hints


def get_rollup_response(fullpath, content_type):
    try:
        rollup_response = requests.post(
            'http://127.0.0.1:8000/rollup/',
            data={'filename': str(fullpath)},
            stream=True
        )
        if rollup_response.status_code == 200:
            return StreamingHttpResponse(
                rollup_response.iter_content(chunk_size=proxy_chunk_size), content_type=content_type
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
