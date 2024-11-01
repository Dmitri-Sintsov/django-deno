import os

from django.core.management.base import BaseCommand

from ...dir import del_dir

from ...process.base import DENO_SCRIPT_PATH
from ...process.compile import DenoCompile


class Command(BaseCommand):
    help = 'Compile django_deno server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-vendor',
            action='store_true',
            dest='keep_vendor',
            default=False,
            help='Do not remove node_modules / vendor dirs (deletes them by default).'
        )

    def handle(self, *args, **options):
        deno_compile = DenoCompile()
        os.chdir(DENO_SCRIPT_PATH)
        deno_process = deno_compile()
        self.stdout.write(f"Starting {deno_compile}\npid={deno_process.pid}")
        return_code = deno_process.wait()
        self.stdout.write(f"Finished with return code = {return_code}")
        if not options['keep_vendor']:
            node_modules_dir = os.path.join(DENO_SCRIPT_PATH, 'node_modules')
            deno_vendor_dir = os.path.join(DENO_SCRIPT_PATH, 'vendor')
            print(f'Deleting node_modules_dir: {node_modules_dir}')
            del_dir(node_modules_dir)
            print(f'Deleting deno_vendor_dir: {deno_vendor_dir}')
            del_dir(deno_vendor_dir)
