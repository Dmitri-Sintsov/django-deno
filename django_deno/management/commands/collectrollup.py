import io
import ijson
import json
import signal


from django.contrib.staticfiles.management.commands import collectstatic

from ...itero import IterO
from ...commands import DenoProcess
from ...importmap import ImportMapGenerator
from ...sourcefile import SourceFile

from ...api.rollup import DenoRollup


class Command(collectstatic.Command, DenoProcess):

    help = f"{collectstatic.Command.help} Uses deno rollup to collect bundles from static files in a single location."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import_map_generator = ImportMapGenerator(logger=self.stderr)
        self.serialized_map_generator = json.dumps(import_map_generator.serialize(), separators=(',', ':')).encode('utf-8')
        self.deno_process = self.run_deno_process()

    def copy_file(self, path, prefixed_path, source_storage):
        source_path = source_storage.path(path)
        source_file = SourceFile(source_path)
        if source_file.should_rollup():
            response = DenoRollup(content_type=source_file.content_type).post({
                'filename': str(source_file.source_path.name),
                'basedir': str(source_file.source_path.parent),
                'options': {
                    'terser': True,
                }
            })
            if response.status_code == 200:
                response_io = IterO(response.streaming_content)
                s = response_io.read()
                objects = ijson.items(response_io, prefix='rollupFile')
                for obj in objects:
                    print(obj)
            else:
                self.terminate(f"Error while rollup file {path} {prefixed_path}")
        else:
            super().copy_file(path, prefixed_path, source_storage)

    def sigint_handler(self, signum, frame):
        self.stdout.write(f"Terminating deno server pid={self.deno_process.pid}")
        self.deno_process.terminate()
        if callable(self.orig_sigint):
            self.orig_sigint(signum, frame)

    def handle(self, **options):
        self.orig_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.sigint_handler)
        super().handle(**options)
        self.deno_process.terminate()
