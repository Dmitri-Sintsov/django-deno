import subprocess

from .base import ExecDeno
from .compressor import DenoCompressor


# deno compile --allow-env --allow-ffi --allow-import --allow-net --allow-read --allow-sys --frozen=false --vendor --output=django_deno --lock=deno.lock server.ts
class DenoCompile(DenoCompressor, ExecDeno):

    deno_command = 'compile'

    script_name = 'server.ts'

    def get_popen_kwargs(self):
        popen_kwargs = super().get_popen_kwargs()
        popen_kwargs.update({
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
        })
        return popen_kwargs

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        deno_flags.extend([
            # "--cached-only",
            "--frozen=false",
            # "--no-remote",
            # "--reload",
            "--vendor",
            f"--config={self.deno_config_path}",
            f"--lock={self.deno_lock_path}",
            f"--output={self.django_deno_binary_path}",
        ])
        return deno_flags
