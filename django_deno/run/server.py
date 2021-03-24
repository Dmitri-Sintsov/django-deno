import inspect
import os
import subprocess

from ..conf.settings import DENO_PATH, DENO_RUN_FLAGS, DENO_SERVER

def deno_server():
    deno_process = subprocess.Popen(
        [
            DENO_PATH, "run"
        ] +
        DENO_RUN_FLAGS +
        [
            os.path.join(DENO_SCRIPT_PATH, "server.ts"),
            f"--host={DENO_SERVER['host']}", f"--port={DENO_SERVER['port']}"
        ],
        shell=False
    )
    return deno_process

DENO_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(inspect.getfile(deno_server))),
    'deno'
)
