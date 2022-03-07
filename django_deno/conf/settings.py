import os

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

DENO_ENABLE = getattr(settings, 'DENO_ENABLE', True)
DENO_RELOAD = getattr(settings, 'DENO_RELOAD', False)
DENO_CHECK_LOCK_FILE = getattr(settings, 'DENO_CHECK_LOCK_FILE', False)
DENO_ROLLUP_MATCH_PATH = getattr(settings, 'DENO_ROLLUP_MATCH_PATH', True)

DENO_INSTALL = getattr(settings, 'DENO_INSTALL', os.getenv('DENO_INSTALL'))
if DENO_INSTALL is None:
    raise ImproperlyConfigured('Please set DENO_INSTALL environment variable or project settings.DENO_INSTALL path')

DENO_PATH = os.path.join(DENO_INSTALL, 'bin', 'deno')

if getattr(settings, 'DENO_DEBUG', False):
    DENO_TIMEOUT = 60
else:
    DENO_TIMEOUT = 20

DENO_SERVER = {
    'scheme': 'http',
    'hostname': '127.0.0.1',
    'port': 8099,
}
DENO_SERVER.update(getattr(settings, 'DENO_SERVER', {}))

DENO_URL = f'{DENO_SERVER["scheme"]}://{DENO_SERVER["hostname"]}:{DENO_SERVER["port"]}'

DENO_PROXY_CHUNK_SIZE = getattr(settings, 'DENO_PROXY_CHUNK_SIZE', 256 * 1024)

# Map of rollup.js output module type to html script tag module type:
DENO_OUTPUT_MODULE_FORMATS = {
    'module': 'es',
    'systemjs-module': 'system',
}
DENO_OUTPUT_MODULE_FORMATS.update(getattr(settings, 'DENO_OUTPUT_MODULE_FORMATS', {}))

DENO_ROLLUP_SERVE_OPTIONS = {
    'inlineFileMap': True,
    'relativePaths': True,
    'preserveEntrySignatures': False,
    'staticFilesResolver': True,
    'withCache': True,
}
DENO_ROLLUP_SERVE_OPTIONS.update(getattr(settings, 'DENO_ROLLUP_SERVE_OPTIONS', {}))

DENO_OUTPUT_MODULE_TYPE = getattr(settings, 'DENO_OUTPUT_MODULE_TYPE', 'module')

DENO_ROLLUP_COLLECT_OPTIONS = {
    # 'relativePaths': True,
    # 'staticFilesResolver': True,
    'terser': True,
    'bundles': getattr(settings, 'DENO_ROLLUP_BUNDLES', {}),
    'moduleFormat': DENO_OUTPUT_MODULE_FORMATS[DENO_OUTPUT_MODULE_TYPE],
}
DENO_ROLLUP_COLLECT_OPTIONS.update(getattr(settings, 'DENO_ROLLUP_COLLECT_OPTIONS', {}))

DENO_ROLLUP_ENTRY_POINTS = getattr(settings, 'DENO_ROLLUP_ENTRY_POINTS', [])
