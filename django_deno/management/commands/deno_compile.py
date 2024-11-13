import codecs
import os
import sys
import subprocess

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
        output = []
        while True:
            while True:
                line = deno_process.stdout.readline()
                if line:
                    sys.stdout.write(line.decode('utf-8'))
                    output.append(line)
                else:
                    break
            # returns None while subprocess is running
            return_code = deno_process.poll()
            if return_code is not None:
                break
        return_code = deno_process.wait()
        self.stdout.write(f"Finished with return code = {return_code}")
        if return_code == 0:
            with open(os.path.join(DENO_SCRIPT_PATH, 'django_deno.log'), 'wb') as log_file:
                log_file.write(codecs.BOM_UTF8)
                for line in output:
                    log_file.write(line)
        if not options['keep_vendor']:
            node_modules_dir = os.path.join(DENO_SCRIPT_PATH, 'node_modules')
            deno_vendor_dir = os.path.join(DENO_SCRIPT_PATH, 'vendor')
            print(f'Deleting node_modules_dir: {node_modules_dir}')
            del_dir(node_modules_dir)
            print(f'Deleting deno_vendor_dir: {deno_vendor_dir}')
            del_dir(deno_vendor_dir)
