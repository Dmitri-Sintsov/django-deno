import mimetypes
import os

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles.finders import get_finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.functional import cached_property


# Todo check with Django 2.2 / Django 3.2.
"""
import os
from django.conf import settings
from django_deno.importmap import ImportMapGenerator
import_map_generator = ImportMapGenerator()
import_map_generator.get_import_map(os.path.join(settings.BASE_DIR, 'drf_gallery', 'static', 'components', 'main.js'))
"""


class ImportMapGenerator:

    map_mime_types = [
        "application/javascript"
    ]

    def __init__(self):
        self.module_basedir = None
        self.storage = staticfiles_storage
        if not self.local:
            raise ValueError('Only local storage is supported')
        self.ignore_patterns = apps.get_app_config('staticfiles').ignore_patterns
        self.mapped_files = set()
        self.base_map = {}
        self.import_map = {}
        self.collect_import_map()

    # django.contrib.staticfiles.management.commands.collectstatic.Command.local
    @cached_property
    def local(self):
        try:
            self.storage.path('')
        except NotImplementedError:
            return False
        return True

    def collect_import_map(self):
        found_files = {}
        for finder in get_finders():
            for path, storage in finder.list(self.ignore_patterns):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in found_files:
                    found_files[prefixed_path] = (storage, path)
                    self.add_to_import_map(path, prefixed_path, storage)
                else:
                    raise ValueError(
                        "Found another file with the destination path '%s'. It "
                        "will be ignored since only the first encountered file "
                        "is collected. If this is not what you want, make sure "
                        "every static file has a unique path." % prefixed_path,
                        level=1,
                    )
        return self.import_map

    def add_to_import_map(self, path, prefixed_path, source_storage):
        if prefixed_path not in self.mapped_files:
            self.mapped_files.add(prefixed_path)
            # self.storage.exists(prefixed_path)
            # When was the target file modified last time?
            # target_last_modified = self.storage.get_modified_time(prefixed_path)
            # When was the source file modified last time?
            # source_last_modified = source_storage.get_modified_time(path)
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
            content_type, encoding = mimetypes.guess_type(source_path)
            if content_type in self.map_mime_types:
                if source_path.startswith(settings.BASE_DIR):
                    self.base_map[source_path] = target_path
                else:
                    self.import_map[target_path] = source_path

    def has_common_path(self, path):
        try:
            common_path = os.path.commonpath([self.module_basedir, path])
        except ValueError:
            return False
        return True

    def to_relative_path(self, path):
        relative_path = os.path.relpath(path, self.module_basedir)
        return relative_path

    # es_module_path - a full path to valid existing es module
    def get_import_map(self, es_module_path):
        self.module_basedir = os.path.dirname(self.base_map[es_module_path])
        relative_import_map = {
            self.to_relative_path(target_path): source_path
            for target_path, source_path
            in self.import_map.items()
            if self.has_common_path(source_path)
        }
        return relative_import_map

    def to_cache(self):
        return {
            'base_map': self.base_map,
            'import_map': self.import_map,
        }

    def from_cache(self, cache_entry):
        self.base_map = cache_entry['base_map']
        self.import_map = cache_entry['import_map']
