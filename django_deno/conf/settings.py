from django.conf import settings

DENO_SERVER = {
    'protocol': 'http',
    'host': '127.0.0.1',
    'port': 8000,
}
DENO_SERVER.update(getattr(settings, 'DENO_SERVER', {}))

DENO_URL = f'{DENO_SERVER["protocol"]}://{DENO_SERVER["host"]}:{DENO_SERVER["port"]}'
