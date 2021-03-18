from django.conf import settings

DENO_SERVER = {
    'protocol': 'http',
    'host': '127.0.0.1',
    'port': 8000,
}
DENO_SERVER.update(getattr(settings, 'DENO_SERVER', {}))

DENO_URL = f'{DENO_SERVER["protocol"]}://{DENO_SERVER["host"]}:{DENO_SERVER["port"]}'

DENO_PROXY_CHUNK_SIZE = getattr(settings, 'DENO_PROXY_CHUNK_SIZE', 256 * 1024)

DENO_ROLLUP_HINTS = getattr(settings, 'DENO_ROLLUP_HINTS', [b'"use rollup"', b"'use rollup'"])
