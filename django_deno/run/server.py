from .base import RunDeno

from ..conf.settings import DENO_SERVER


class DenoServer(RunDeno):

    script_name = "server.ts"
    script_args = [
        f"--host={DENO_SERVER['host']}",
        f"--port={DENO_SERVER['port']}"
    ]
