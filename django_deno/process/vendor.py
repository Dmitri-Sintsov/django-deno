from .base import ExecDeno


# deno vendor --unstable --force --lock=/home/user/work/djk-sample38/lib/python3.8/site-packages/django_deno/deno/lock.json --import-map=/home/user/work/djk-sample38/lib/python3.8/site-packages/django_deno/deno/import_map.json /home/user/work/djk-sample38/lib/python3.8/site-packages/django_deno/deno/server.ts
# deno run -A --unstable --allow-net --no-remote --import-map vendor/import_map.json /home/user/work/djk-sample38/lib/python3.8/site-packages/django_deno/deno/server.ts --host=127.0.0.1 --port=8099

class DenoVendor(ExecDeno):

    deno_command = 'vendor'
    deno_flags = ["--unstable", "--force"]
    script_name = "server.ts"

    def get_deno_flags(self):
        deno_flags = super().get_deno_flags()
        deno_flags.extend([
            f"--lock={self.deno_lock_path}",
            f"--import-map={self.run_importmap_path}",
        ])
        return deno_flags
