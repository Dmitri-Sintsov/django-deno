import os

from .base import DENO_SCRIPT_PATH
from .run import DenoRun

from ..conf.settings import DENO_SERVER, DENO_USE_COMPILED_BINARY


class DenoServer(DenoRun):

    script_args = [
        f"--host={DENO_SERVER['hostname']}",
        f"--port={DENO_SERVER['port']}"
    ]

    def get_binary_path(self):
        return os.path.join(DENO_SCRIPT_PATH, 'django_deno') if DENO_USE_COMPILED_BINARY else super().get_binary_path()

    def get_deno_command(self):
        return None if DENO_USE_COMPILED_BINARY else super().get_deno_command()

    def get_deno_flags(self):
        if DENO_USE_COMPILED_BINARY:
            return []
        else:
            return super().get_deno_flags()

    def get_script_name(self):
        return '' if DENO_USE_COMPILED_BINARY else 'server.ts'
