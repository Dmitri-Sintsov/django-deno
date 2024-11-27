import os

from django.core.management.base import BaseCommand

from ...conf import settings as deno_settings

from ...commands import DenoCommand

from ...process.base import DENO_SCRIPT_PATH
from ...process.install import DenoInstall


class Command(BaseCommand, DenoCommand):
    help = 'Generate deno vendor bundle'

    def handle(self, *args, **options):
        rollup_options = self.get_deno_server_kwargs(deno_settings.DENO_ROLLUP_INSTALL_OPTIONS)
        deno_install = DenoInstall(**rollup_options)
        os.chdir(DENO_SCRIPT_PATH)
        deno_process = deno_install()
        if deno_process.poll() is None:
            self.stdout.write(f"Starting {deno_install}\npid={deno_process.pid}")
