import os
import ijson
import json
import signal


from django.contrib.staticfiles.management.commands import collectstatic

from ...itero import IterO
from ...commands import DenoProcess
from ...importmap import ImportMapGenerator
from ...sourcefile import SourceFile

from ...conf import settings as deno_settings
from ...api.rollup import DenoRollup


class Command(collectstatic.Command, DenoProcess):

    help = f"{collectstatic.Command.help} Uses deno rollup to collect bundles from static files in a single location."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import_map_generator = ImportMapGenerator(logger=self.stderr)
        self.serialized_map_generator = json.dumps(import_map_generator.serialize(), separators=(',', ':')).encode('utf-8')
        self.deno_process = self.run_deno_process()
        self.rollup_files = []

    def write_response(self, response, prefixed_path):
        response_io = IterO(response.streaming_content)
        # s = response_io.read()
        objects = ijson.items(response_io, prefix='rollupFiles')
        for chunks in objects:
            for obj in chunks:
                is_main_chunk = prefixed_path.endswith(obj['filename'])
                dest_js_filename = self.storage.path(prefixed_path)
                dest_dir = os.path.dirname(dest_js_filename)
                if not is_main_chunk:
                    dest_js_filename = dest_dir + os.sep + obj['filename']
                os.makedirs(dest_dir, exist_ok=True)
                dest_map_filename = f"{dest_js_filename}.map"
                with open(dest_js_filename, "w", encoding='utf-8') as f:
                    f.write(obj['code'])
                    f.write(f"//# sourceMappingURL={obj['filename']}.map")
                with open(dest_map_filename, "w", encoding='utf-8') as f:
                    f.write(obj['map'])

    def rollup_file(self, path, prefixed_path, source_file):
        if not self.is_local_storage():
            self.terminate("Only local storage is supported for rollup files")
        response = DenoRollup(content_type=source_file.content_type).post({
            'filename': str(source_file.source_path.name),
            'basedir': str(source_file.source_path.parent),
            'options': deno_settings.DENO_ROLLUP_COLLECT_OPTIONS,
        })
        if response.status_code == 200 and hasattr(response, 'streaming_content'):
            self.write_response(response, prefixed_path)
        else:
            self.terminate(f"Error: status={response.status_code} content={response.content}")

    def copy_file(self, path, prefixed_path, source_storage):
        source_path = source_storage.path(path)
        source_file = SourceFile(source_path)
        if source_file.should_rollup():
            destination_path = self.storage.path(path)
            self.rollup_files.append([path, prefixed_path, destination_path])
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
        for path, prefixed_path, destination_path in self.rollup_files:
            destination_file = SourceFile(destination_path)
            self.rollup_file(path, prefixed_path, destination_file)
        if self.is_spawned_deno(deno_process=self.deno_process):
            self.deno_process.terminate()
