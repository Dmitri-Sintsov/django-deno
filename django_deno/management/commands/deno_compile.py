import codecs
import os
import sys

from django.core.management.base import BaseCommand

from ...conf import settings as deno_settings

from ...dir import del_dir
from ...utils import ansi_escape_8bit

from ...commands import DenoCommand
from ...process.base import DENO_SCRIPT_PATH
from ...process.compile import DenoCompile


class Command(BaseCommand, DenoCommand):
    help = 'Compile django_deno server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-vendor',
            action='store_true',
            dest='keep_vendor',
            default=False,
            help='Do not remove node_modules / vendor dirs (deletes them by default).'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            dest='compress',
            default=False,
            help='Compress compiled binary (do not compress by default).'
        )

    def handle(self, *args, **options):
        rollup_options = self.get_deno_server_kwargs(deno_settings.DENO_ROLLUP_COMPILE_OPTIONS)
        deno_compile = DenoCompile(**rollup_options)
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
        log_file_name = 'django_deno.log' if return_code == 0 else 'django_deno.err'
        with open(os.path.join(DENO_SCRIPT_PATH, log_file_name), 'wb') as log_file:
            log_file.write(codecs.BOM_UTF8)
            log_file.write(f"{deno_compile}{os.linesep}".encode('utf-8'))
            for line in output:
                log_file.write(ansi_escape_8bit.sub(b'', line))
        if not options['keep_vendor']:
            node_modules_dir = os.path.join(DENO_SCRIPT_PATH, 'node_modules')
            deno_vendor_dir = os.path.join(DENO_SCRIPT_PATH, 'vendor')
            print(f'Deleting node_modules_dir: {node_modules_dir}')
            del_dir(node_modules_dir)
            print(f'Deleting deno_vendor_dir: {deno_vendor_dir}')
            del_dir(deno_vendor_dir)
        if return_code == 0 and options['compress']:
            self.stdout.write(f'Compressing {deno_compile.django_deno_binary_path}')
            deno_compile.compress()
            self.stdout.write(f'Written compressed {deno_compile.django_deno_lzma_path}')
