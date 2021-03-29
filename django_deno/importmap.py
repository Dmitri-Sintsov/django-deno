from collections import MutableMapping
import mimetypes
import os

from pathlib import Path

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
import_map = import_map_generator.get_import_map(os.path.join(settings.BASE_DIR, 'drf_gallery', 'static', 'components', 'main.js'))
serialized_map_generator = import_map_generator.serialize()
import_map_generator = ImportMapGenerator(cache_entry=serialized_map_generator)
serialized_map_generator == import_map_generator.serialize()
import_map == import_map_generator.get_import_map(os.path.join(settings.BASE_DIR, 'drf_gallery', 'static', 'components', 'main.js'))
"""


class CommonBasePath:

    def __init__(self, cache_entry=None):
        if cache_entry is None:
            self.create()
        else:
            self.deserialize(cache_entry)

    def __str__(self):
        return os.path.join(*(self.common_base + ['']))

    @property
    def common_base(self):
        return self._common_base

    @common_base.setter
    def common_base(self, path_parts):
        self._common_base = path_parts
        self.common_base_str = str(self)

    def create(self):
        # dict with path parts
        self.common_base = []
        # path str
        self.common_base_str = ''

    def serialize(self):
        return str(self)

    def yield_path_parts(self, path_obj):
        yield from reversed(path_obj.parents)
        yield path_obj.name

    def deserialize(self, cache_entry: str):
        path_obj = Path(cache_entry)
        self.common_base = self.split_path(
            self.yield_path_parts(path_obj)
        )

    def __repr__(self):
        return f"{type(self).__name__}({self.common_base})"

    def split_path(self, path_obj_iterator):
        return list(
            os.sep if parent == '' else parent
            for parent in
            list(os.path.basename(parent) for parent in path_obj_iterator)
        )

    def split_parents(self, path_obj):
        return self.split_path(reversed(path_obj.parents))

    def apply_path(self, path):
        path_obj = Path(path)
        if len(self.common_base) == 0:
            self.common_base = self.split_parents(path_obj)
        else:
            path_parents = self.split_parents(path_obj)
            for idx, common_parent in enumerate(self.common_base):
                if path_parents[idx] != common_parent:
                    self.common_base = self.common_base[:idx]
                    break

    def pack(self, path_str):
        if path_str.startswith(self.common_base_str):
            return path_str[len(self.common_base_str):]
        else:
            return path_str

    def unpack(self, path_str):
        if path_str.startswith(self.common_base_str):
            return path_str
        else:
            return f"{self.common_base_str}{path_str}"


class PathMap(MutableMapping):

    def __init__(self, cache_entry=None):
        if cache_entry is None:
            self.create()
        else:
            self.deserialize(cache_entry)

    def create(self):
        self.map = {}
        self.base_key = CommonBasePath()
        self.base_val = CommonBasePath()

    def __getitem__(self, k):
        return self.map[k]

    # Warning: Assumes k:v are unpacked. Automatically begins to unpack k:v.
    # Do not call after .pack(), otherwise one have to perform .unpack() / .pack() later.
    def __setitem__(self, k, v):
        self.map[k] = v
        self.base_key.apply_path(k)
        self.base_val.apply_path(v)

    def __delitem__(self, k):
        raise NotImplementedError('Operation is not supported')

    def __iter__(self):
        return iter(self.map)

    def __len__(self):
        return len(self.map)

    def __repr__(self):
        return f"{type(self).__name__}({self.map})"

    def unpack_relation(self, rel_k, rel_v):
        packed_v = rel_k if rel_v == '' else rel_v
        return rel_k, packed_v

    def pack_relation(self, k, v):
        rel_v = '' if k == v else v
        return k, rel_v

    def get_unpacked(self, k):
        # Assuming that map is currently packed
        rel_k = self.base_key.pack(k)
        packed_k, packed_v = self.unpack_relation(rel_k, self.map[rel_k])
        return self.base_val.unpack(packed_v)

    def unpacked_items(self):
        for rel_k, rel_v in self.map.items():
            packed_k, packed_v = self.unpack_relation(rel_k, rel_v)
            yield self.base_key.unpack(packed_k), self.base_val.unpack(packed_v)

    def pack(self):
        map = {}
        for k, v in self.map.items():
            packed_k = self.base_key.pack(k)
            packed_v = self.base_val.pack(v)
            rel_k, rel_v = self.pack_relation(packed_k, packed_v)
            map[rel_k] = rel_v
        self.map = map

    def serialize(self):
        return {
            'map': self.map,
            'base_key': self.base_key.serialize(),
            'base_val': self.base_val.serialize(),
        }

    def deserialize(self, cache_entry):
        self.map = cache_entry['map']
        self.base_key = CommonBasePath(cache_entry=cache_entry['base_key'])
        self.base_val = CommonBasePath(cache_entry=cache_entry['base_val'])

    def __str__(self):
        return str(self.serialize())


class ImportMapGenerator:

    map_mime_types = [
        "application/javascript"
    ]

    def __init__(self, cache_entry=None):
        if cache_entry is None:
            self.create()
        else:
            self.deserialize(cache_entry)

    def create(self):
        self.module_basedir = None
        self.storage = staticfiles_storage
        if not self.local:
            raise ValueError('Only local storage is supported')
        self.ignore_patterns = apps.get_app_config('staticfiles').ignore_patterns
        self.mapped_files = set()
        self.base_map = PathMap()
        self.import_map = PathMap()
        self.collect_import_map()
        self.base_map.pack()
        self.import_map.pack()

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

    def has_to_import(self, source_path):
        content_type, encoding = mimetypes.guess_type(source_path)
        return content_type in self.map_mime_types

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
            if self.has_to_import(source_path):
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
    # warning: called after .deserialize(), thus only .base_map / .import_map instance attributes are
    # assumed to be properly initialized.
    def get_import_map(self, es_module_path):
        self.module_basedir = os.path.dirname(
            self.base_map.get_unpacked(es_module_path)
        )
        relative_import_map = {
            self.to_relative_path(target_path): source_path
            for target_path, source_path
            in self.import_map.unpacked_items()
            if self.has_common_path(source_path)
        }
        return relative_import_map

    def serialize(self):
        return {
            'base_map': self.base_map.serialize(),
            'import_map': self.import_map.serialize(),
        }

    def deserialize(self, cache_entry):
        self.base_map = PathMap(cache_entry=cache_entry['base_map'])
        self.import_map = PathMap(cache_entry=cache_entry['import_map'])
