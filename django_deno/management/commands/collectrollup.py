from django.contrib.staticfiles.management.commands import collectstatic

from ...sourcefile import SourceFile


class Command(collectstatic.Command):

    help = f"{collectstatic.Command.help} Uses deno rollup to collect bundles from static files in a single location."

    def copy_file(self, path, prefixed_path, source_storage):
        source_file = SourceFile(prefixed_path)
        if source_file.should_rollup():
            pass
        else:
            super().copy_file(path, prefixed_path, source_storage)
