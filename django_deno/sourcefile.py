import mimetypes
from pathlib import Path

from .conf import settings


class SourceFile:

    module_mime_types = [
        "application/javascript"
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
        content_type, self.encoding = mimetypes.guess_type(self.source_path_str)
        self.content_type = content_type or 'application/octet-stream'

    def is_rollup_module(self):
        return self.content_type in self.module_mime_types

    def has_to_import(self):
        if settings.DENO_ENABLE:
            return self.is_rollup_module()
        else:
            return False

    def should_rollup(self):
        if settings.DENO_ENABLE and self.is_rollup_module():
            with self.source_path.open('rb') as f:
                file_begin = f.read(settings.DENO_ROLLUP_HINTS_MAXLEN)
                for hint in settings.DENO_ROLLUP_HINTS:
                    if file_begin.startswith(hint):
                        return True
        return False
