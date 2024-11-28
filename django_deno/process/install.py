from .base import ExecDeno


# deno install --allow-env --allow-ffi --allow-import --allow-net --allow-read --allow-sys --frozen=false --force --reload --vendor --lock=deno.lock --entrypoint server.ts
class DenoInstall(ExecDeno):

    deno_command = 'install'

    script_name = 'server.ts'

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        deno_flags.extend([
            "--allow-scripts=npm:@swc/core",
            "--frozen=false",
            "--force",
            "--reload",
            "--vendor",
            f"--config={self.deno_config_path}",
            f"--lock={self.deno_lock_path}",
            "--entrypoint",
        ])

        return deno_flags
