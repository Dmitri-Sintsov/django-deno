import signal
import threading

from django.conf import settings
from django.contrib.staticfiles.management.commands import runserver

from ...handlers import RollupFilesHandler
from ...run import deno_server


class Command(runserver.Command):

    def get_handler(self, *args, **options):
        self.deno_process = deno_server()
        self.set_sigint_handler()
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

    def set_sigint_handler(self):
        current_thread = threading.current_thread()
        main_thread = threading.main_thread()
        main_thread.join()
        signal.signal(signal.SIGINT, self.sigint_handler)
        current_thread.join()

    def sigint_handler(self, signum, frame):
        self.deno_process.terminate()
