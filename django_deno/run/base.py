import json
import inspect
import os
import re
import subprocess
from urllib.parse import urlsplit, urlunsplit
from copy import copy

from django.conf import settings

from ..regex import finditer_with_separators, MatchGroup

from ..conf.settings import DENO_PATH, DENO_RELOAD, DENO_CHECK_LOCK_FILE


class RunDeno:

    run_flags = ["-A", "--unstable", "--allow-net"]
    script_name = None
    script_args = []
    # https://deno.land/manual/linking_to_external_code/integrity_checking
    # https://deno.land/manual/linking_to_external_code
    deno_lock_filename = 'lock.json'
    deno_importmap_filename = 'import_map.json'
    # https://regexr.com
    module_version_split = re.compile(r'\/[^\/]+@.+?\/')
    module_version_replace = re.compile(r'@.+?\/')

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
                with open(self.deno_importmap_path, "w+") as deno_import_map_file:
                    json.dump({'imports': deno_import_map}, deno_import_map_file, indent=2, ensure_ascii=False)

    # return true if importmap exists, false otherwise
    def cache_importmap(self):
        try:
            deno_importmap_mtime = os.path.getmtime(self.deno_importmap_path)
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

    def get_run_flags(self):
        run_flags = copy(self.run_flags)
        if getattr(settings, 'DENO_DEBUG', False):
            # chrome://inspect
            run_flags.append("--inspect-brk")
        if DENO_RELOAD and DENO_CHECK_LOCK_FILE:
            raise ValueError("DENO_RELOAD / DENO_CHECK_LOCK_FILE are mutually exclusive options")
        if DENO_RELOAD:
            run_flags.extend(["--reload", "--lock-write", f"--lock={self.deno_lock_path}"])
        if DENO_CHECK_LOCK_FILE:
            if not os.path.isfile(self.deno_lock_path):
                raise ValueError(
                    f"Lock file is not found: {self.deno_lock_path}\n" 
                    f"Please use DENO_RELOAD=True option to create the lock file first."
                )
            run_flags.append(f"--lock={self.deno_lock_path}")
            if self.cache_importmap():
                run_flags.append(f"--import-map={self.deno_importmap_path}")
        return run_flags

    def get_script_name(self):
        return self.script_name

    def get_script_args(self):
        return self.script_args

    def get_shell_args(self):
        return [
            DENO_PATH, "run"
        ] + self.get_run_flags() + [
            os.path.join(DENO_SCRIPT_PATH, self.get_script_name()),
        ] + self.get_script_args()

    def get_popen_kwargs(self):
        return {
            'shell': False,
        }

    def __init__(self, deno_lock_filename=None, deno_importmap_filename=None, *args, **kwargs):
        if deno_lock_filename is None:
            deno_lock_filename = self.deno_lock_filename
        if deno_importmap_filename is None:
            deno_importmap_filename = self.deno_importmap_filename
        self.deno_lock_path = os.path.join(DENO_SCRIPT_PATH, deno_lock_filename)
        self.deno_importmap_path = os.path.join(DENO_SCRIPT_PATH, deno_importmap_filename)
        self.shell_args = self.get_shell_args()

    def __str__(self):
        return ' '.join(self.shell_args)

    def __call__(self, *args, **kwargs):
        popen_kwargs = self.get_popen_kwargs()
        deno_process = subprocess.Popen(self.shell_args, **popen_kwargs)
        return deno_process


DENO_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(inspect.getfile(RunDeno))),
    'deno'
)
