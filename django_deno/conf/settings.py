import os

from django.conf import settings

DENO_INSTALL = getattr(settings, 'DENO_INSTALL', os.getenv('DENO_INSTALL'))
if DENO_INSTALL is None:
    raise ValueError('Please set DENO_INSTALL environment variable or project settings.DENO_INSTALL path')

DENO_PATH = os.path.join(DENO_INSTALL, 'bin', 'deno')

if getattr(settings, 'DENO_DEBUG', False):
    # chrome://inspect
    DENO_RUN_FLAGS = ["-A", "--inspect-brk", "--unstable", "--allow-net"]
else:
    DENO_RUN_FLAGS = ["-A", "--unstable", "--allow-net"]

DENO_SERVER = {
    'protocol': 'http',
    'host': '127.0.0.1',
    'port': 8000,
}
DENO_SERVER.update(getattr(settings, 'DENO_SERVER', {}))

DENO_URL = f'{DENO_SERVER["protocol"]}://{DENO_SERVER["host"]}:{DENO_SERVER["port"]}'

DENO_PROXY_CHUNK_SIZE = getattr(settings, 'DENO_PROXY_CHUNK_SIZE', 256 * 1024)

DENO_ROLLUP_HINTS = getattr(settings, 'DENO_ROLLUP_HINTS', [b'"use rollup"', b"'use rollup'"])
DENO_ROLLUP_HINTS_MAXLEN = max([len(hint) for hint in DENO_ROLLUP_HINTS])
