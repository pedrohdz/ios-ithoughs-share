# pylint: disable=missing-docstring,redefined-outer-name
from unittest.mock import Mock

import pytest

from ithoughtsshare.ithoughts_notes import (
    Canceler,
    Finisher,
    IThoughtsDispatcher,
    Initializer,
    MapAdder,
    MapPicker,
    NoteEditor,
    State,
    StateData,
    StateDispatcher,
    UrlEditor,
)


# -----------------------------------------------------------------------------
# Global fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def initializer():
    mocked_item = Mock(Initializer)
    return mocked_item


@pytest.fixture
def state_data():
    mocked_item = Mock(StateData)
    return mocked_item


@pytest.fixture
def url_editor():
    mocked_item = Mock(UrlEditor)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: UrlEditor')
    return mocked_item


@pytest.fixture
def note_editor():
    mocked_item = Mock(NoteEditor)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: NoteEditor')
    return mocked_item


@pytest.fixture
def map_picker():
    mocked_item = Mock(MapPicker)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: MapPicker')
    return mocked_item


@pytest.fixture
def map_adder():
    mocked_item = Mock(MapAdder)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: MapAdder')
    return mocked_item


@pytest.fixture
def ithoughts_dispatcher():
    mocked_item = Mock(IThoughtsDispatcher)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: IThoughtsDispatcher')
    return mocked_item


@pytest.fixture
def finisher():
    mocked_item = Mock(Finisher)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: Finisher')
    return mocked_item


@pytest.fixture
def canceler():
    mocked_item = Mock(Canceler)
    mocked_item.handle.side_effect = Exception(
        'Should not have been called: Canceler')
    return mocked_item


@pytest.fixture
def state_dispatcher(state_data, initializer, url_editor, note_editor,
                     map_picker, map_adder, ithoughts_dispatcher, finisher,
                     canceler):
    # pylint: disable=too-many-arguments,unused-argument
    return StateDispatcher(**locals())


# -----------------------------------------------------------------------------
# General
# -----------------------------------------------------------------------------
def test_initial_state(state_dispatcher):
    assert state_dispatcher.current_state == State.start
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


# -----------------------------------------------------------------------------
# 'FORWARD'
# -----------------------------------------------------------------------------
def test_forward_from_start(state_dispatcher, initializer):
    assert state_dispatcher.current_state == State.start
    initializer.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.initialize
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_initialize(state_dispatcher, map_picker):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.initialize
    map_picker.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.pick_mind_map
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_edit_url(state_dispatcher, note_editor):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.edit_url
    note_editor.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.edit_note
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_edit_note(state_dispatcher, ithoughts_dispatcher):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.edit_note
    ithoughts_dispatcher.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.create_ithoughs_note
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_pick_mind_map(state_dispatcher, url_editor):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.pick_mind_map
    url_editor.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.edit_url
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_add_from_pick_mind_map(state_dispatcher, map_adder):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.pick_mind_map
    map_adder.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('ADD_MIND_MAP')
    assert state_dispatcher.current_state == State.add_mind_map
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_create_ithoughs_note(state_dispatcher, finisher):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.create_ithoughs_note
    finisher.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.end
    assert state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_cancel(state_dispatcher, finisher):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.cancel
    finisher.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert finisher.handle.called
    assert state_dispatcher.current_state == State.end
    assert state_dispatcher.is_end


def test_forward_from_end(state_dispatcher):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.end
    assert state_dispatcher.is_end
    with pytest.raises(KeyError):
        state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


# -----------------------------------------------------------------------------
# 'CANCEL'
# -----------------------------------------------------------------------------
def states():
    # Make more Pythonic, dynamically pull attributes.
    return (
        State.cancel,
        State.create_ithoughs_note,
        State.edit_note,
        State.edit_url,
        State.end,
        State.pick_mind_map,
        State.start)


@pytest.mark.parametrize('state', states())
def test_to_cancel(state, state_dispatcher, canceler):
    # pylint: disable=protected-access
    state_dispatcher._current_state = state
    canceler.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('CANCEL')
    assert not state_dispatcher.is_end
    assert state_dispatcher.is_canceled
