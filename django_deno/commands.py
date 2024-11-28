import os
import psutil
import subprocess
import _thread

from . import __version__

from .conf import settings as deno_settings
from .utils import ex_to_str
from .api.maps import DenoMaps
from .process.server import DenoServer
from .importmap import ImportMapGenerator


class DenoCommand:

    def __init__(self, stdout=None, stderr=None, **kwargs):
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(**kwargs)

    def terminate(self, error_message):
        self.stderr.write(error_message)
        # raising CommandError will not shut down test server as it's running in separate thread.
        try:
            _thread.interrupt_main()
        except KeyboardInterrupt:
            pass
        # Need to use an OS exit because sys.exit doesn't work in a thread.
        os._exit(1)

    def is_spawned_deno(self, deno_process):
        return isinstance(deno_process, subprocess.Popen)

    def is_separate_deno(self, deno_process):
        return isinstance(deno_process, psutil.Process)

    def get_deno_server_kwargs(self, rollup_options):
        deno_server_kwargs = {}
        # Set both 'swc' and 'sucrase' to False to enable both (not recommended).
        if rollup_options['swc']:
            if deno_settings.DENO_USE_COMPILED_BINARY:
                # https://github.com/denoland/deno/issues/23266
                self.terminate('Compiled binary does not support swc native module (DENO_USE_COMPILED_BINARY)')
            if rollup_options['sucrase']:
                self.terminate('swc and sucrase are mutually exclusive options')
            deno_server_kwargs.update({
                'deno_config_filename': 'deno_swc.json',
                'deno_lock_filename': 'deno_swc.lock',
                'deno_flags': [
                    # the following flag works with deno install, however causes
                    # deno run deadlock / hangup with deno 2.1.1 / swc/core 1.9.3 in Ubuntu Linux, thus is commented out:
                    # "--allow-scripts=npm:@swc/core",
                ],
            })
        elif rollup_options['sucrase']:
            deno_server_kwargs.update({
                'deno_config_filename': 'deno_sucrase.json',
                'deno_lock_filename': 'deno_sucrase.lock',
            })
        return deno_server_kwargs

    def run_deno_process(self, rollup_options):
        deno_process = None
        import_map_generator = ImportMapGenerator(logger=self.stderr)
        serialized_map_generator = import_map_generator.serialize()
        deno_api_status = DenoMaps().set_timeout(0.1).post(serialized_map_generator)
        if deno_api_status is None:
            deno_server_kwargs = self.get_deno_server_kwargs(rollup_options)
            deno_server = DenoServer(logger=self.stdout, **deno_server_kwargs)
            if deno_settings.DENO_DEBUG_EXTERNAL:
                self.stdout.write(f"Expected external deno server command line: {deno_server}")
            else:
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
        if deno_process is None:
            self.terminate("Deno server is not started or is not running properly")
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
