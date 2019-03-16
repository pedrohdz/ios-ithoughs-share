# pylint: disable=missing-docstring,redefined-outer-name
import os
from unittest import mock
from datetime import (datetime, timezone)
import pytest

from mind_maps import (
    MindMap,
    MindMaps,
    utcnow,
)


TZ = timezone.utc


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def fixed_created():
    return datetime(2001, 6, 25, 17, 53, 33, 78, tzinfo=TZ)


@pytest.fixture
def fixed_modified():
    return datetime(2002, 4, 17, 21, 45, 27, 84, tzinfo=TZ)


@pytest.fixture
def fixed_now():
    return datetime(2008, 3, 28, 8, 15, 46, 0, tzinfo=TZ)


@pytest.fixture
def mind_map(fixed_created, fixed_modified):
    return MindMap(fixed_created, fixed_modified)


@pytest.fixture
def mind_maps_json_file():
    resource_dir = os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            'resources'))
    return os.path.join(resource_dir, 'mind_maps_small.json')


@pytest.fixture
def mind_maps_json(mind_maps_json_file):
    with open(mind_maps_json_file, 'r') as infile:
        return infile.read()


@pytest.fixture
def mind_maps(mind_maps_json_file):
    return MindMaps.loadf(mind_maps_json_file)


# -----------------------------------------------------------------------------
# MindMaps
# -----------------------------------------------------------------------------
def test_mind_maps_constructor_empty():
    sample = MindMaps()
    assert not sample
    assert sample.filepath is None


def test_mind_maps_constructor_empty_with_filepath(tmpdir):
    tmpfile = os.path.join(tmpdir, 'mind_maps+output.json')
    sample = MindMaps(filepath=tmpfile)
    assert not sample
    assert sample.filepath == tmpfile


def test_mind_maps_loadf(mind_maps_json_file, fixed_created, fixed_modified,
                         fixed_now):
    sample = MindMaps.loadf(mind_maps_json_file)
    validate_small_mind_maps(sample, fixed_created, fixed_modified, fixed_now)
    assert sample.filepath == mind_maps_json_file


def test_mind_maps_loadf_create(tmpdir):
    tmpfile = os.path.join(tmpdir, 'mind_maps+output.json')
    sample = MindMaps.loadf(tmpfile, create=True)
    assert not sample
    assert sample.filepath == tmpfile
    assert not os.path.exists(tmpfile)


def test_mind_maps_loadf_no_create(tmpdir):
    tmpfile = os.path.join(tmpdir, 'mind_maps+output.json')
    with pytest.raises(FileNotFoundError):
        MindMaps.loadf(tmpfile)


def test_mind_maps_loads(mind_maps_json, fixed_created, fixed_modified,
                         fixed_now):
    sample = MindMaps.loads(mind_maps_json)
    validate_small_mind_maps(sample, fixed_created, fixed_modified, fixed_now)
    assert sample.filepath is None


def test_mind_maps_dumpf(mind_maps, mind_maps_json, tmpdir):
    tmpfile = os.path.join(tmpdir, 'mind_maps+output.json')
    mind_maps.dumpf(filepath=tmpfile)
    with open(tmpfile, 'r') as infile:
        what_was_writter = infile.read()
    assert what_was_writter == mind_maps_json


def test_mind_maps_dumps(mind_maps, mind_maps_json):
    dumped_string = mind_maps.dumps()
    assert dumped_string == mind_maps_json


def validate_small_mind_maps(sample, fixed_created, fixed_modified, fixed_now):
    assert len(sample) == 4
    assert sample['created/created'].created == fixed_created
    assert sample['created/created'].modified == fixed_created
    assert sample['created/modified'].created == fixed_created
    assert sample['created/modified'].modified == fixed_modified
    assert sample['created/other'].created == fixed_created
    assert sample['created/other'].modified == fixed_now
    assert sample['modified/other'].created == fixed_modified
    assert sample['modified/other'].modified == fixed_now


def test_mind_maps_del(mind_maps):
    del mind_maps['created/created']
    assert len(mind_maps) == 3
    assert 'created/created' not in mind_maps


def test_mind_maps_set_add(mind_maps):
    new_mind_map = MindMap.create()
    mind_maps['something/new/here'] = new_mind_map
    assert len(mind_maps) == 5
    assert mind_maps['something/new/here'] == new_mind_map


def test_mind_maps_set_replace(mind_maps):
    with pytest.raises(TypeError) as exception:
        mind_maps['created/created'] = MindMap.create()
    assert 'Replacing an existing' in str(exception.value)
    assert len(mind_maps) == 4


def test_mind_maps_set_add_bad(mind_maps):
    with pytest.raises(TypeError) as exception:
        mind_maps['something/new/here'] = {'test': 'here'}
    assert 'Value must be of type MindMap' in str(exception.value)
    assert len(mind_maps) == 4


def test_mind_maps_add(mind_maps):
    mind_maps.add('something/new/here')
    assert len(mind_maps) == 5
    assert isinstance(mind_maps['something/new/here'], MindMap)


# -----------------------------------------------------------------------------
# MindMap
# -----------------------------------------------------------------------------
def test_mind_map_happy_state(mind_map, fixed_created, fixed_modified):
    assert mind_map.created == fixed_created
    assert mind_map['created'] == fixed_created
    assert mind_map.modified == fixed_modified
    assert mind_map['modified'] == fixed_modified
    assert set(mind_map.keys()) == set(('created', 'modified'))
    assert set(mind_map.values()) == set((fixed_created, fixed_modified))
    assert len(mind_map) == 2


@mock.patch('mind_maps.utcnow')
def test_mind_map_create(mock_utcnow, fixed_now):
    mock_utcnow.return_value = fixed_now
    value = MindMap.create()
    assert value.created == fixed_now
    assert value.modified == fixed_now


@mock.patch('mind_maps.utcnow')
def test_mind_map_touch(mock_utcnow, mind_map, fixed_created, fixed_now):
    mock_utcnow.return_value = fixed_now
    mind_map.touch()
    assert mind_map.created == fixed_created
    assert mind_map.modified == fixed_now


def test_mind_map_immutable(mind_map):
    with pytest.raises(TypeError):
        del mind_map['created']
    with pytest.raises(TypeError):
        mind_map['foo_bar'] = 'ha ha ha'


# -----------------------------------------------------------------------------
# utcnow()
# -----------------------------------------------------------------------------
def test_utcnow():
    now = datetime.now(timezone.utc)
    delta = (now - utcnow()).total_seconds()
    assert abs(delta) < 5
