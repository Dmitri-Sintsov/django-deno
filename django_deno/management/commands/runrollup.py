import signal
import threading

import psutil
from django.conf import settings
from django.contrib.staticfiles.management.commands import runserver

from ...conf import settings as deno_settings
from ...commands import DenoCommand
from ...handlers import RollupFilesHandler

lock = threading.Lock()

deno_process = None


class Command(runserver.Command, DenoCommand):

    help = f"{runserver.Command.help} Starts Deno Web server to serve rollup bundles from static files."

    def get_handler(self, *args, **options):
        global deno_process
        self.orig_sigint = None
        deno_process = self.run_deno_process(rollup_options=deno_settings.DENO_ROLLUP_SERVE_OPTIONS)
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

    def terminate_deno(self):
        global deno_process
        with lock:
            if deno_process is not None:
                self.stdout.write(f"Terminating deno server pid={deno_process.pid}")
                try:
                    deno_process.terminate()
                except psutil.NoSuchProcess:
                    self.stdout.write(f"NoSuchProcess: process no longer exists (pid={deno_process.pid})")
                deno_process = None

    def sigint_handler(self, signum, frame):
        self.terminate_deno()
        if callable(self.orig_sigint):
            self.orig_sigint(signum, frame)

    def run(self, **options):
        # Run before autoreload.run_with_reloader() spawns another thread:
        if threading.main_thread() == threading.current_thread():
            self.orig_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, self.sigint_handler)
        super().run(**options)
