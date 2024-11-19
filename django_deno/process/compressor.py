import os
import mmap
import stat
import lzma
import requests

from .base import DENO_SCRIPT_PATH
from .. import __version__


class DenoCompressor:

    lzma_base_file_name = 'django_deno.lzma'

    def __init__(self, **kwargs):
        self.django_deno_binary_path = self.get_django_deno_binary_path()
        self.django_deno_lzma_path = self.get_django_deno_lzma_path()
        self.django_deno_lzma_url = self.get_django_deno_lzma_url()
        super().__init__(**kwargs)

    def get_django_deno_binary_path(self):
        return os.path.join(DENO_SCRIPT_PATH, 'django_deno')

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
            with open(self.django_deno_binary_path, mode="rb") as source_file:
                with mmap.mmap(source_file.fileno(), length=0, access=mmap.ACCESS_READ, offset=0) as source_mmap:
                    dest_file.write(source_mmap)

    def decompress(self):
        with lzma.open(self.django_deno_lzma_path, mode="r") as source_file:
            with open(self.django_deno_binary_path, mode="wb") as dest_file:
                dest_file.write(source_file.read())
        st_mode = os.stat(self.django_deno_binary_path).st_mode
        os.chmod(self.django_deno_binary_path, st_mode | stat.S_IEXEC)
