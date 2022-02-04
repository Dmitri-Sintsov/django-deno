import os
import psutil
import subprocess
import _thread

from django_deno import __version__

from .utils import ex_to_str
from .api.maps import DenoMaps
from .run.server import DenoServer
from .importmap import ImportMapGenerator


class DenoProcess:

    def terminate(self, error_message):
        self.stderr.write(error_message)
        # raising CommandError will not shut down test server as it's running in separate thread.
        _thread.interrupt_main()
        # Need to use an OS exit because sys.exit doesn't work in a thread
        os._exit(1)

    def is_spawned_deno(self, deno_process):
        return isinstance(deno_process, subprocess.Popen)

    def is_separate_deno(self, deno_process):
        return isinstance(deno_process, psutil.Process)

    def run_deno_process(self):
        import_map_generator = ImportMapGenerator(logger=self.stderr)
        serialized_map_generator = import_map_generator.serialize()
        deno_api_status = DenoMaps().set_timeout(0.1).post(serialized_map_generator)
        if deno_api_status is None:
            deno_server = DenoServer()
            deno_process = deno_server()
            if deno_process.poll() is None:
                self.stdout.write(f"Starting deno server {deno_server}\npid={deno_process.pid}")
            else:
                self.terminate("Error while starting deno server")
        elif isinstance(deno_api_status, Exception):
            self.stderr.write("The service running is not deno server or deno server is not running properly")
            self.terminate(ex_to_str(deno_api_status))
        else:
            deno_process = psutil.Process(deno_api_status['pid'])
            self.stdout.write(
                f"Already running deno server pid={deno_process.pid}, api version={deno_api_status['version']}"
            )
        if not isinstance(deno_api_status, dict):
            self.stdout.write(f"Sending import maps to deno server pid={deno_process.pid}")
            deno_api_status = DenoMaps().post(serialized_map_generator)
        if isinstance(deno_api_status, Exception) or deno_api_status is None:
            self.stderr.write("The service running is not deno server or deno server is not running properly")
            if isinstance(deno_api_status, Exception):
                self.terminate(ex_to_str(deno_api_status))
            else:
                self.terminate('')
        elif deno_api_status['version'] != __version__:
            self.terminate(
                f"Version of deno server api does not match, "
                f"found: {deno_api_status['version']}, required: {__version__}"
            )
        self.stdout.write(f"Sent import maps to deno server pid={deno_process.pid}")
        return deno_process
