import os

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

DENO_ENABLE = getattr(settings, 'DENO_ENABLE', True)

DENO_INSTALL = getattr(settings, 'DENO_INSTALL', os.getenv('DENO_INSTALL'))
if DENO_INSTALL is None:
    raise ImproperlyConfigured('Please set DENO_INSTALL environment variable or project settings.DENO_INSTALL path')

DENO_PATH = os.path.join(DENO_INSTALL, 'bin', 'deno')

if getattr(settings, 'DENO_DEBUG', False):
    DENO_TIMEOUT = 60
else:
    DENO_TIMEOUT = 20

DENO_SERVER = {
    'protocol': 'http',
    'host': '127.0.0.1',
    'port': 8099,
}
DENO_SERVER.update(getattr(settings, 'DENO_SERVER', {}))

DENO_URL = f'{DENO_SERVER["protocol"]}://{DENO_SERVER["host"]}:{DENO_SERVER["port"]}'

DENO_PROXY_CHUNK_SIZE = getattr(settings, 'DENO_PROXY_CHUNK_SIZE', 256 * 1024)
