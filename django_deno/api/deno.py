import base64
import hashlib

from django.conf import settings

from ..conf.settings import DENO_SERVER, DENO_URL, DENO_TIMEOUT

from .json import JsonApi


class DenoApi(JsonApi):

    server = DENO_SERVER
    url = DENO_URL
    timeout = DENO_TIMEOUT
    use_site_id = True

    def build_post_request_json(self):
        self.request_json = super().build_post_request_json()
        if self.use_site_id:
            site_hash = hashlib.sha256(f"{settings.BASE_DIR}{settings.SESSION_COOKIE_NAME}".encode('utf-8')).digest()
            self.request_json['site_id'] = base64.b64encode(site_hash).decode('utf-8')
        return self.request_json
