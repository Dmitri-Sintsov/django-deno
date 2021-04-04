import mimetypes
import mmap
import os
from contextlib import contextmanager
from pathlib import Path

from .conf import settings


class SourceFile:

    module_mime_types = [
        "application/javascript"
    ]
    module_detect_bytes = [
        b'export ',
        b'import ',
    ]

    def __init__(self, source_path):
        if isinstance(source_path, Path):
            self.source_path = source_path
            self.source_path_str = str(source_path)
        elif isinstance(source_path, str):
            self.source_path = Path(source_path)
            self.source_path_str = source_path
        else:
            raise ValueError('Invalid source_path value, should be Path or str')
        self.stat = self.source_path.stat()
        content_type, self.encoding = mimetypes.guess_type(self.source_path_str)
        self.content_type = content_type or 'application/octet-stream'

    def is_rollup_module(self, mfile):
        if self.content_type in self.module_mime_types:
            return any([mfile.find(b) != -1 for b in self.module_detect_bytes])
        else:
            return False

    def has_to_import(self):
        if settings.DENO_ENABLE and self.stat.st_size > 0:
            with self.get_mmap() as mfile:
                return self.is_rollup_module(mfile)
        else:
            return False

    @contextmanager
    def get_mmap(self):
        try:
            fd = None
            mfile = None
            fd = os.open(f"{self.source_path_str}", os.O_RDONLY)
            mfile = mmap.mmap(fd, 0, prot=mmap.PROT_READ)
            yield mfile
        finally:
            if mfile is not None:
                mfile.close()
            if fd is not None:
                os.close(fd)

    def should_rollup(self):
        if settings.DENO_ENABLE and self.stat.st_size > 0:
            with self.get_mmap() as mfile:
                if self.is_rollup_module(mfile):
                    for hint in settings.DENO_ROLLUP_HINTS:
                        if mfile[:len(hint)] == hint:
                            return True
        return False
