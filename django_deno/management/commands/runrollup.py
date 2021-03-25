import psutil
import signal
import sys
import _thread
import threading

from django.conf import settings
from django.contrib.staticfiles.management.commands import runserver

from django_deno import __version__
from ...handlers import RollupFilesHandler
from ...utils import ex_to_str
from ...api.status import get_api_status
from ...run.server import deno_server


lock = threading.Lock()

global deno_process
deno_process = None


class Command(runserver.Command):

    def terminate(self, error_message):
        self.stderr.write(error_message)
        # raising CommandError will not shut down test server as it's running in separate thread.
        _thread.interrupt_main()
        sys.exit()

    def get_handler(self, *args, **options):
        global deno_process
        self.orig_sigint = None
        deno_api_status = get_api_status()
        if deno_api_status is None:
            deno_process = deno_server()
            if deno_process.poll() is None:
                self.stdout.write(f"Starting deno server pid={deno_process.pid}")
            else:
                self.terminate("Error while starting deno server")
        elif isinstance(deno_api_status, Exception):
            self.stderr.write("The service running is not deno server or deno server is not running properly")
            self.terminate(ex_to_str(deno_api_status))
        else:
            deno_process = psutil.Process(deno_api_status['pid'])
            if deno_api_status['api_version'] != __version__:
                self.terminate(
                    f"Version of deno server api does not match, "
                    f"found: {deno_api_status['api_version']}, required: {__version__}"
                )
            else:
                deno_process = psutil.Process(deno_api_status['pid'])
                self.stdout.write(
                    f"Already running deno server pid={deno_process.pid}, api_version={deno_api_status['api_version']}"
                )
        """
        Return the static files serving handler wrapping the default handler,
        if static files should be served. Otherwise return the default handler.
        """
        handler = super().get_handler(*args, **options)
        use_static_handler = options['use_static_handler']
        insecure_serving = options['insecure_serving']
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return RollupFilesHandler(handler)
        return handler

    def sigint_handler(self, signum, frame):
        global deno_process
        with lock:
            if deno_process is not None:
                self.stdout.write(f"Terminating deno server pid={deno_process.pid}")
                deno_process.terminate()
                deno_process = None
        if callable(self.orig_sigint):
            self.orig_sigint(signum, frame)

    def run(self, **options):
        # Run before autoreload.run_with_reloader() spawns another thread:
        if threading.main_thread() == threading.current_thread():
            self.orig_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, self.sigint_handler)
        super().run(**options)
