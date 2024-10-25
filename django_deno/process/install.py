from .base import ExecDeno

# deno install --allow-env --allow-ffi --allow-import --allow-net --allow-read --allow-sys --force --reload --vendor --entrypoint /home/user/work/djk-sample310/lib/python3.10/site-packages/django_deno/deno/server.ts

class DenoInstall(ExecDeno):

    deno_command = 'install'

    script_name = 'server.ts'

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        deno_flags.extend([
            "--force",
            "--reload",
            "--vendor",
            # f"--lock={self.deno_lock_path}",
            # f"--import-map={self.run_importmap_path}",
            "--entrypoint",
        ])

        return deno_flags
