import inspect
import os
import subprocess
from copy import copy

from ..conf.settings import DENO_PATH


class ExecDeno:

    deno_command = None
    deno_flags = [
        "--allow-env",
        "--allow-ffi",
        "--allow-import",
        "--allow-net",
        "--allow-read",
        "--allow-sys",
        # "--unstable",
    ]
    script_name = ''
    script_args = []
    # https://deno.land/manual/linking_to_external_code/integrity_checking
    # https://deno.land/manual/linking_to_external_code
    # https://deno.land/manual/tools/vendor
    deno_config_filename = 'deno.json'
    deno_lock_filename = 'deno.lock'

    def get_deno_flags(self):
        deno_flags = copy(self.deno_flags)
        return deno_flags

    def get_script_name(self):
        return self.script_name

    def get_deno_command(self):
        return self.deno_command

    def get_script_args(self):
        return self.script_args

    def get_binary_path(self):
        return DENO_PATH

    def get_shell_args(self):
        args = [self.get_binary_path()]
        deno_command = self.get_deno_command()
        if deno_command is not None:
            args.append(deno_command)
        args += self.get_deno_flags()
        script_name = self.get_script_name()
        if script_name != '':
            args += [
                os.path.join(DENO_SCRIPT_PATH, self.get_script_name()),
            ]
        args += self.get_script_args()
        return args

    def get_popen_kwargs(self):
        return {
            'shell': False,
        }

    def __init__(self, deno_flags=None, deno_config_filename=None, deno_lock_filename=None, **kwargs):
        if deno_flags is not None:
            self.deno_flags += deno_flags
        module_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
        if deno_config_filename is None:
            deno_config_filename = self.deno_config_filename
        self.deno_config_path = os.path.join(module_dir, 'deno', deno_config_filename)

        if deno_lock_filename is None:
            deno_lock_filename = self.deno_lock_filename
        self.deno_lock_path = os.path.join(DENO_SCRIPT_PATH, deno_lock_filename)

        self.shell_args = self.get_shell_args()

    def __str__(self):
        return ' '.join(self.shell_args)

    def __call__(self, *args, **kwargs):
        popen_kwargs = self.get_popen_kwargs()
        deno_process = subprocess.Popen(self.shell_args, **popen_kwargs)
        return deno_process


DENO_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(inspect.getfile(ExecDeno))),
    'deno'
)
