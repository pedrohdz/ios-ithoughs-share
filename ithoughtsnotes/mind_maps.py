#!/usr/bin/env python
# pylint: disable=missing-docstring

import collections
import logging as log
import json

from datetime import (datetime, timezone)


class MindMaps(collections.abc.MutableMapping):
    # pylint: disable=too-many-ancestors
    def __init__(self, data=None, filepath=None):
        self._log = log.getLogger(type(self).__name__)
        self._data = data if data else {}
        self._filepath = filepath

    @classmethod
    def loadf(cls, filepath, create=False):
        try:
            # pylint: disable=protected-access
            with open(filepath, 'r') as handle:
                maps = json.load(handle, object_hook=_object_hook)
            maps._filepath = filepath
            return maps
        except FileNotFoundError as exception:
            if create:
                return MindMaps(filepath=filepath)
            raise exception

    @classmethod
    def loads(cls, string):
        return json.loads(string, object_hook=_object_hook)

    def _dump(self, handle):
        return json.dump(self, handle, cls=_MindMapsEncoder, sort_keys=True,
                         indent=2)

    def dumpf(self, filepath=None):
        filepath = filepath if filepath is not None else self.filepath
        with open(filepath, 'w') as handle:
            self._dump(handle)

    def dumps(self):
        return json.dumps(self, cls=_MindMapsEncoder, sort_keys=True, indent=2)

    @property
    def filepath(self):
        return self._filepath

    def add(self, key):
        self[key] = MindMap.create()

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __delitem__(self, key):
        del self._data[key]

    def __setitem__(self, key, value):
        if key in self._data:
            raise TypeError('Replacing an existing MindMap is not allowed')
        if not isinstance(value, MindMap):
            raise TypeError('Value must be of type MindMap')
        self._data[key] = value


def _object_hook(dictionary):
    if set(('created', 'modified')).issubset(set(dictionary.keys())):
        return MindMap.decode(**dictionary)
    return MindMaps(dictionary)


class _MindMapsEncoder(json.JSONEncoder):
    def default(self, o):
        # pylint: disable=method-hidden
        if isinstance(o, (MindMap, MindMaps)):
            return dict(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class MindMap(collections.abc.Mapping):
    def __init__(self, created, modified):
        self._data = {
            'created': created,
            'modified': modified}

    @classmethod
    def create(cls):
        now = utcnow()
        return MindMap(now, now)

    @classmethod
    def decode(cls, created, modified):
        return MindMap(
            fromisoformat(created),
            fromisoformat(modified))

    @property
    def created(self):
        return self._data['created']

    @property
    def modified(self):
        return self._data['modified']

    def touch(self):
        now = utcnow()
        self._data['modified'] = now
        return now

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


def fromisoformat(string):
    import re
    string = re.sub(r'([+-])(\d{2}):(\d{2})$', r'\1\2\3', string)
    try:
        return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z')


def utcnow():
    return datetime.now(timezone.utc)
