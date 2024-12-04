import os

from .compressor import DenoCompressor
from .run import DenoRun

from ..conf.settings import DENO_SERVER, DENO_USE_COMPILED_BINARY


class DenoServer(DenoCompressor, DenoRun):

    script_args = [
        f"--host={DENO_SERVER['hostname']}",
        f"--port={DENO_SERVER['port']}"
    ]

    def __init__(self, logger=None, **kwargs):
        self.logger = logger
        super().__init__(**kwargs)

    def log(self, s):
        if self.logger:
            self.logger.write(s)

    def get_binary_path(self):
        return self.django_deno_binary_path if DENO_USE_COMPILED_BINARY else super().get_binary_path()

    def get_deno_command(self):
        return None if DENO_USE_COMPILED_BINARY else super().get_deno_command()

    def get_deno_flags(self):
        if DENO_USE_COMPILED_BINARY:
            return []
        else:
            return super().get_deno_flags()

    def get_script_name(self):
        return '' if DENO_USE_COMPILED_BINARY else 'server.ts'

    def __call__(self, *args, **kwargs):
        if DENO_USE_COMPILED_BINARY and not os.path.isfile(self.django_deno_binary_path):
            if not os.path.isfile(self.django_deno_zip_path):
                self.log(f'Downloading {self.django_deno_zip_url}')
                self.download_compressed()
            self.log(f'Decompressing {self.django_deno_zip_path}')
            self.decompress()
        return super().__call__(*args, **kwargs)
