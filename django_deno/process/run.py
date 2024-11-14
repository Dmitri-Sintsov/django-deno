import os
import re
# from urllib.parse import urlsplit, urlunsplit

from .base import ExecDeno

from ..conf.settings import DENO_DEBUG, DENO_RELOAD, DENO_CHECK_LOCK_FILE, DENO_NO_REMOTE


class DenoRun(ExecDeno):

    deno_command = 'run'

    # https://regexr.com
    module_version_split = re.compile(r'/[^/]+@.+?/')
    module_version_replace = re.compile(r'@.+?/')

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        if DENO_DEBUG:
            # chrome://inspect
            deno_flags.append("--inspect-brk")
        deno_flags.append(
            f"--config={self.deno_config_path}"
        )
        if DENO_NO_REMOTE:
            deno_flags.extend([
                "--vendor",
                "--no-remote",
            ])
        else:
            if DENO_RELOAD and DENO_CHECK_LOCK_FILE:
                raise ValueError("DENO_RELOAD / DENO_CHECK_LOCK_FILE are mutually exclusive options")
            if DENO_RELOAD:
                deno_flags.extend([
                    "--reload",
                    # "--lock-write",
                    f"--lock={self.deno_lock_path}"]
                )
            if DENO_CHECK_LOCK_FILE:
                if not os.path.isfile(self.deno_lock_path):
                    raise ValueError(
                        f"Lock file is not found: {self.deno_lock_path}\n"
                        f"Please use DENO_RELOAD=True option to create the lock file first."
                    )
                deno_flags.append(f"--lock={self.deno_lock_path}")
        return deno_flags
