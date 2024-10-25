import os

from django.core.management.base import BaseCommand

from ...process.base import DENO_SCRIPT_PATH
from ...process.install import DenoInstall


class Command(BaseCommand):
    help = 'Generate deno vendor bundle'

    def handle(self, *args, **options):
        deno_install = DenoInstall()
        os.chdir(DENO_SCRIPT_PATH)
        deno_process = deno_install()
        if deno_process.poll() is None:
            self.stdout.write(f"Starting {deno_install}\npid={deno_process.pid}")
