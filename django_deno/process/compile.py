from .base import ExecDeno

# deno compile --allow-env --allow-ffi --allow-import --allow-net --allow-read --allow-sys --cached-only --frozen=false --vendor --output=django_deno --lock=/home/user/work/djk-sample310/lib/python3.10/site-packages/django_deno/deno/lock.json /home/user/work/djk-sample310/lib/python3.10/site-packages/django_deno/deno/server.ts

class DenoCompile(ExecDeno):

    deno_command = 'compile'

    script_name = 'server.ts'

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        deno_flags.extend([
            "--cached-only",
            "--frozen=false",
            # "--no-remote",
            # "--reload",
            "--vendor",
            "--output=django_deno",
            f"--lock={self.deno_lock_path}",
            # f"--import-map={self.run_importmap_path}",
        ])

        return deno_flags
