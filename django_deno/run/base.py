import inspect
import os
import subprocess
from copy import copy

from django.conf import settings

from ..conf.settings import DENO_PATH


class RunDeno:

    run_flags = ["-A", "--unstable", "--allow-net"]
    script_name = None
    script_args = []
    # https://deno.land/manual/linking_to_external_code/integrity_checking
    # https://deno.land/manual/linking_to_external_code
    deno_lock_filename = 'lock.json'

    def get_run_flags(self):
        run_flags = copy(self.run_flags)
        if getattr(settings, 'DENO_DEBUG', False):
            # chrome://inspect
            run_flags.append("--inspect-brk")
        # DENO_RELOAD / DENO_CHECK_LOCK_FILE are mutually exclusive options
        if getattr(settings, 'DENO_RELOAD', False):
            run_flags.extend(["--reload", "--lock-write", f"--lock={self.deno_lock_path}"])
        elif getattr(settings, 'DENO_CHECK_LOCK_FILE', False):
            run_flags.extend([f"--lock={self.deno_lock_path}"])

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

    def __init__(self, deno_lock_filename=None, *args, **kwargs):
        if deno_lock_filename is None:
            deno_lock_filename = self.deno_lock_filename
        self.deno_lock_path = os.path.join(settings.BASE_DIR, deno_lock_filename)

    def __call__(self, *args, **kwargs):
        shell_args = self.get_shell_args()
        popen_kwargs = self.get_popen_kwargs()
        deno_process = subprocess.Popen(shell_args, **popen_kwargs)
        return deno_process


DENO_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(inspect.getfile(RunDeno))),
    'deno'
)
