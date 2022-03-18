import json

from django.http import (
    HttpResponse, StreamingHttpResponse
)

from .deno import DenoApi

from ..conf import settings
from ..utils import ex_to_str


class DenoRollup(DenoApi):

    location = '/rollup/'
    extra_post_kwargs = {'stream': True}

    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        super().__init__(**kwargs)

    def parse_post_response(self, response):
        if response.status_code == 200:
            response = StreamingHttpResponse(
                response.iter_content(chunk_size=settings.DENO_PROXY_CHUNK_SIZE), content_type=self.content_type
            )
        else:
            response = HttpResponse(
                'throw Error({});'.format(json.dumps(response.text)),
                content_type=self.content_type
            )
            response.status_code = 200
        return response

    def parse_not_responding_error(self, ex):
        ex_string = json.dumps(ex_to_str(ex))
        response = HttpResponse(
            f'throw Error({ex_string});',
            content_type=self.content_type
        )
        response.status_code = 200
        return response

    def parse_http_error(self, ex):
        return self.parse_not_responding_error(ex)
