# pylint: disable=missing-docstring,redefined-outer-name
import sys
import os
from unittest.mock import Mock

import pytest

sys.path.append(
    os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir)))

# pylint: disable=wrong-import-position
from ithoughts_notes import (
    Canceler,
    Finisher,
    IThoughtsDispatcher,
    MapPicker,
    NoteEditor,
    State,
    StateData,
    StateDispatcher,
    UrlEditor,
)  # NOQA
# pylint: enable=wrong-import-position


# -----------------------------------------------------------------------------
# Global fixtures
# -----------------------------------------------------------------------------
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
def state_dispatcher(state_data, url_editor, note_editor, map_picker,
                     ithoughts_dispatcher, finisher, canceler):
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
def test_forward_from_start(state_dispatcher, url_editor):
    assert state_dispatcher.current_state == State.start
    url_editor.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.edit_url
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


def test_forward_from_edit_note(state_dispatcher, map_picker):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.edit_note
    map_picker.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.pick_mind_map
    assert not state_dispatcher.is_end
    assert not state_dispatcher.is_canceled


def test_forward_from_pick_mind_map(state_dispatcher, ithoughts_dispatcher):
    # pylint: disable=protected-access
    state_dispatcher._current_state = State.pick_mind_map
    ithoughts_dispatcher.handle.reset_mock(side_effect=True)
    state_dispatcher.next_state('FORWARD')
    assert state_dispatcher.current_state == State.create_ithoughs_note
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
