from django.contrib.staticfiles.management.commands import collectstatic


class Command(collectstatic.Command):

    help = f"{collectstatic.Command.help} Uses deno rollup to collect bundles from static files in a single location."

    def copy_file(self, path, prefixed_path, source_storage):
        super().copy_file(path, prefixed_path, source_storage)
