import os

from django.core.management.base import BaseCommand

from ...process.base import DENO_SCRIPT_PATH
from ...process.vendor import DenoVendor


class Command(BaseCommand):
    help = 'Generate deno vendor bundle'

    def handle(self, *args, **options):
        deno_vendor = DenoVendor()
        os.chdir(DENO_SCRIPT_PATH)
        deno_process = deno_vendor()
        if deno_process.poll() is None:
            self.stdout.write(f"Starting {deno_vendor}\npid={deno_process.pid}")
