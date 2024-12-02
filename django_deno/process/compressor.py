import hashlib
import os
import mmap
import platform
import stat
import lzma

import requests

from .base import DENO_SCRIPT_PATH
from .. import __version__


class MMapContextManager:

    def __init__(self, filename, mode="rb", access=mmap.ACCESS_READ):
        self.filename = filename
        self.mode = mode
        self.access = access

    def __enter__(self):
        self.file = open(self.filename, mode=self.mode)
        self.mmap = mmap.mmap(self.file.fileno(), length=0, access=self.access, offset=0)
        self.sha256 = hashlib.sha256(self.mmap)
        return self.mmap, self.sha256

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mmap.close()
        self.file.close()
        if exc_type:
            return False


"""
from django_deno.process.compressor import DenoCompressor
dc = DenoCompressor()
dc.download_compressed()
dc.compress()
dc.decompress()
"""


class DenoCompressor:

    def __init__(self, **kwargs):
        self.platform = platform.system()
        self.platform_architecture = f'{self.platform}.{platform.machine()}'
        self.lzma_base_file_name = f'django_deno.{self.platform_architecture}.lzma'
        self.django_deno_binary_path = self.get_django_deno_binary_path()
        self.django_deno_hash_path = self.get_django_deno_hash_path()
        self.django_deno_lzma_path = self.get_django_deno_lzma_path()
        self.django_deno_lzma_url = self.get_django_deno_lzma_url()
        super().__init__(**kwargs)

    def get_django_deno_binary_path(self):
        django_deno_binary = 'django_deno.exe' if self.platform == 'Windows' else 'django_deno'
        return os.path.join(DENO_SCRIPT_PATH, django_deno_binary)

    def get_django_deno_hash_path(self):
        return os.path.join(DENO_SCRIPT_PATH, f'django_deno.{self.platform_architecture}.hash')

    def get_django_deno_lzma_path(self):
        return os.path.join(DENO_SCRIPT_PATH, self.lzma_base_file_name)

    def get_django_deno_lzma_url(self):
        # https://stackoverflow.com/questions/8779197/how-to-link-files-directly-from-github-raw-github-com
        # to see the actual location:
        # curl -v https://github.com/Dmitri-Sintsov/django-deno/raw/refs/tags/v0.2.0/django_deno/deno/django_deno.lzma
        return f'https://raw.githubusercontent.com/Dmitri-Sintsov/django-deno/refs/tags/v{__version__}/django_deno/deno/{self.lzma_base_file_name}'

    def download_compressed(self):
        response = requests.get(self.django_deno_lzma_url, stream=True)
        # todo: add progress percentage
        total_size = int(response.headers.get("content-length", 0))
        with open(self.django_deno_lzma_path, 'wb') as dest_file:
            for chunk in response.iter_content(65536):
                dest_file.write(chunk)

    def compress(self):
        with lzma.open(self.django_deno_lzma_path, mode="wb", format=lzma.FORMAT_ALONE, preset=9) as dest_file:
            with MMapContextManager(self.django_deno_binary_path) as (source_mmap, sha256):
                dest_file.write(source_mmap)
                with open(self.django_deno_hash_path, mode="w") as hash_file:
                    hash_file.write(sha256.hexdigest())

    def decompress(self):
        with open(self.django_deno_hash_path, mode="r") as hash_file:
            hash_file_hexdigest = hash_file.read()
            with lzma.open(self.django_deno_lzma_path, mode="rb") as source_file:
                with open(self.django_deno_binary_path, mode="wb") as dest_file:
                    dest_file.write(source_file.read())
                with MMapContextManager(self.django_deno_binary_path) as (dest_mmap, sha256):
                    if sha256.hexdigest() != hash_file_hexdigest:
                        os.unlink(self.django_deno_binary_path)
                        raise Exception(f'sha256 hexdigest for {self.django_deno_binary_path} does not match, found: \n{sha256.hexdigest()} \nneed: \n{hash_file_hexdigest}')

        st_mode = os.stat(self.django_deno_binary_path).st_mode
        os.chmod(self.django_deno_binary_path, st_mode | stat.S_IEXEC)
