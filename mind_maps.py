#!/usr/bin/env python
# pylint: disable=missing-docstring

import collections
import logging as log
import json

from datetime import (datetime, timezone)


class MindMaps(collections.abc.MutableMapping):
    # pylint: disable=too-many-ancestors
    def __init__(self, data):
        self._log = log.getLogger(type(self).__name__)
        self._data = data

    @classmethod
    def load(cls, string, *args, **kwds):
        if 'object_hook' in kwds:
            raise TypeError('object_hook is not allowed')
        return json.load(string, object_hook=_object_hook, *args, **kwds)

    @classmethod
    def loads(cls, string, *args, **kwds):
        if 'object_hook' in kwds:
            raise TypeError('object_hook is not allowed')
        return json.loads(string, object_hook=_object_hook, *args, **kwds)

    def dump(self, *args, **kwds):
        if 'cls' in kwds:
            raise TypeError('cls is not allowed')
        return json.dump(self, cls=_MindMapsEncoder, *args, **kwds)

    def dumps(self, *args, **kwds):
        if 'cls' in kwds:
            raise TypeError('cls is not allowed')
        return json.dumps(self, cls=_MindMapsEncoder, *args, **kwds)

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
            raise TypeError('Replacing and existing MindMap is not allowed')
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
            datetime.fromisoformat(created),
            datetime.fromisoformat(modified))

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


def utcnow():
    return datetime.now(timezone.utc)
