import inspect
import os
import subprocess
from copy import copy

from ..conf.settings import DENO_PATH, DENO_DEBUG


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
    deno_lock_filename = 'lock.json'
    run_importmap_filename = 'import_map.json'

    def get_deno_flags(self):
        deno_flags = copy(self.deno_flags)
        if DENO_DEBUG:
            # chrome://inspect
            deno_flags.append("--inspect-brk")
        return deno_flags

    def get_script_name(self):
        return self.script_name

    def get_deno_command(self):
        return self.deno_command

    def get_script_args(self):
        return self.script_args

    def get_shell_args(self):
        args = [
            DENO_PATH, self.get_deno_command()
        ] + self.get_deno_flags()
        script_name = self.get_script_name()
        if script_name != '':
            args += [
                os.path.join(DENO_SCRIPT_PATH, self.get_script_name()),
            ] + self.get_script_args()
        return args

    def get_popen_kwargs(self):
        return {
            'shell': False,
        }

    def __init__(self, deno_config_filename=None, deno_lock_filename=None, run_importmap_filename=None, **kwargs):
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

        if run_importmap_filename is None:
            run_importmap_filename = self.run_importmap_filename
        self.run_importmap_path = os.path.join(DENO_SCRIPT_PATH, run_importmap_filename)

        self.vendor_importmap_path = os.path.join(DENO_SCRIPT_PATH, 'vendor', 'import_map.json')

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
