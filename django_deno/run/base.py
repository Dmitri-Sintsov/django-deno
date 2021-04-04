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

    def get_run_flags(self):
        run_flags = copy(self.run_flags)
        if getattr(settings, 'DENO_DEBUG', False):
            # chrome://inspect
            run_flags.append("--inspect-brk")
        return run_flags

    def get_script_name(self):
        return self.script_name

    def get_script_args(self):
        return self.script_args

    def get_popen_args(self):
        return [
            DENO_PATH, "run"
        ] + self.get_run_flags() + [
            os.path.join(DENO_SCRIPT_PATH, self.get_script_name()),
        ] + self.get_script_args()

    def __call__(self, *args, **kwargs):
        popen_args = self.get_popen_args()
        deno_process = subprocess.Popen(popen_args, shell=False)
        return deno_process


DENO_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(inspect.getfile(RunDeno))),
    'deno'
)
