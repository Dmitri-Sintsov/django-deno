import os
import mmap
import stat
import lzma

from .base import DENO_SCRIPT_PATH


class DenoCompressor:

    def __init__(self, **kwargs):
        self.django_deno_binary_path = self.get_django_deno_binary_path()
        self.django_deno_lzma_path = self.get_django_deno_lzma_path()
        super().__init__(**kwargs)

    def get_django_deno_binary_path(self):
        return os.path.join(DENO_SCRIPT_PATH, 'django_deno')

    def get_django_deno_lzma_path(self):
        return os.path.join(DENO_SCRIPT_PATH, 'django_deno.lzma')

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
