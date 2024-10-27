import os

from django.core.management.base import BaseCommand

from ...process.base import DENO_SCRIPT_PATH
from ...process.compile import DenoCompile


class Command(BaseCommand):
    help = 'Compile django_deno server'

    def handle(self, *args, **options):
        deno_compile = DenoCompile()
        os.chdir(DENO_SCRIPT_PATH)
        deno_process = deno_compile()
        if deno_process.poll() is None:
            self.stdout.write(f"Starting {deno_compile}\npid={deno_process.pid}")
