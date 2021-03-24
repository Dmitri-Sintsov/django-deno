import os

from django.apps import apps
from django.contrib.staticfiles.finders import get_finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStaticCommand


# Todo check with Django 2.2 / Django 3.2.
# from django_deno.importmap import ImportMapGenerator
class ImportMapGenerator:

    def __init__(self):
        self.storage = staticfiles_storage
        self.local = CollectStaticCommand.local
        if not self.local:
            raise ValueError('Only local storage is supported')
        self.ignore_patterns = apps.get_app_config('staticfiles').ignore_patterns
        self.mapped_files = set()
        self.import_map = {}
        self.get_import_map()

    def get_import_map(self):
        for finder in get_finders():
            for path, storage in finder.list(self.ignore_patterns):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in found_files:
                    found_files[prefixed_path] = (storage, path)
                    self.add_import_map(path, prefixed_path, storage)
                else:
                    raise ValueError(
                        "Found another file with the destination path '%s'. It "
                        "will be ignored since only the first encountered file "
                        "is collected. If this is not what you want, make sure "
                        "every static file has a unique path." % prefixed_path,
                        level=1,
                    )
        return self.import_map

    def add_import_map(self, path, prefixed_path, source_storage):
        if prefixed_path not in self.mapped_files:
            self.mapped_files.add(prefixed_path)
            # self.storage.exists(prefixed_path)
            # When was the target file modified last time?
            # target_last_modified = self.storage.get_modified_time(prefixed_path)
            # When was the source file modified last time?
            # source_last_modified = source_storage.get_modified_time(path)
            # The full path of the target file
            # full_path = self.storage.path(prefixed_path)
            # Avoid sub-second precision (see #14665, #19540)
            # file_is_unmodified = (
            #         target_last_modified.replace(microsecond=0) >=
            #         source_last_modified.replace(microsecond=0)
            # )
            # Then delete the existing file if really needed
            # self.storage.delete(prefixed_path)
            # The full path of the source file
            source_path = source_storage.path(path)
            # The full path of the target file
            target_path = self.storage.path(prefixed_path)
            self.import_map[source_path] = target_path
