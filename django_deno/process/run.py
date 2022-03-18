import json
import os
import re
from urllib.parse import urlsplit, urlunsplit

from .base import ExecDeno

from ..regex import finditer_with_separators, MatchGroup

from ..conf.settings import DENO_RELOAD, DENO_CHECK_LOCK_FILE, DENO_USE_VENDOR


class DenoRun(ExecDeno):

    deno_command = 'run'
    deno_flags = ["-A", "--unstable", "--allow-net"]

    # https://regexr.com
    module_version_split = re.compile(r'/[^/]+@.+?/')
    module_version_replace = re.compile(r'@.+?/')

    def generate_importmap(self):
        deno_import_map = {}
        with open(self.deno_lock_path, "r") as deno_lock_file:
            deno_lock = json.load(deno_lock_file)
            for specific_url in deno_lock.keys():
                url_parts = urlsplit(specific_url)._asdict()
                version_parts = finditer_with_separators(self.module_version_split, url_parts['path'])
                for i, version_part in enumerate(version_parts):
                    if isinstance(version_part, MatchGroup):
                        version_parts[i] = self.module_version_replace.sub('/', version_part)
                        url_parts['path'] = ''.join(version_parts)
                        unspecific_url = urlunsplit(url_parts.values())
                        deno_import_map[unspecific_url] = specific_url
                        break
            if len(deno_import_map) > 0:
                with open(self.run_importmap_path, "w+") as deno_import_map_file:
                    json.dump({'imports': deno_import_map}, deno_import_map_file, indent=2, ensure_ascii=False)

    # return true if importmap exists, false otherwise
    def cache_importmap(self):
        try:
            deno_importmap_mtime = os.path.getmtime(self.run_importmap_path)
        except OSError:
            deno_importmap_mtime = None
        try:
            if deno_importmap_mtime is None or os.path.getmtime(self.deno_lock_path) > deno_importmap_mtime:
                self.generate_importmap()
                return True
            else:
                return deno_importmap_mtime is not None
        except OSError:
            return False

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        if DENO_USE_VENDOR:
            deno_flags.extend([
                "--no-remote",
                f"--import-map={self.vendor_importmap_path}"
            ])
        else:
            if DENO_RELOAD and DENO_CHECK_LOCK_FILE:
                raise ValueError("DENO_RELOAD / DENO_CHECK_LOCK_FILE are mutually exclusive options")
            if DENO_RELOAD:
                deno_flags.extend(["--reload", "--lock-write", f"--lock={self.deno_lock_path}"])
            if DENO_CHECK_LOCK_FILE:
                if not os.path.isfile(self.deno_lock_path):
                    raise ValueError(
                        f"Lock file is not found: {self.deno_lock_path}\n"
                        f"Please use DENO_RELOAD=True option to create the lock file first."
                    )
                deno_flags.append(f"--lock={self.deno_lock_path}")
                if self.cache_importmap():
                    deno_flags.append(f"--import-map={self.run_importmap_path}")
        return deno_flags
