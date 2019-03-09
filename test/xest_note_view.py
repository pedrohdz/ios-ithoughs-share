# pylint: disable=missing-docstring,redefined-outer-name
import sys
import os
from unittest.mock import MagicMock

import pytest

sys.path.append(
    os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir)))

# pylint: disable=wrong-import-position
from ithoughts_notes import IThoughtsNoteView  # NOQA
# pylint: enable=wrong-import-position


@pytest.fixture
def note_view():
    return IThoughtsNoteView(
        title='Some title',
        url='http://foo.bar.local/haa/bang/boom.html',
        body='Some info\n\n- one\n- two\n- three\n',
        view=MagicMock())


# ----
# __init__()
# ----
# FIXME
# def test_init_sane_defaults(note_view):
#     assert note_view.title == 'Some title'
#     assert note_view.url == 'http://foo.bar.local/haa/bang/boom.html'
#     assert note_view.body == 'Some info\n\n- one\n- two\n- three\n'
#     assert not note_view.accepted


# ----
# present()
# ----
def test_present_calls_view(note_view):
    note_view.present()
    assert note_view.view.present.called


# ----
# cancel()
# ----
def test_cancel_closes_view(note_view):
    note_view.cancel(None)
    assert note_view.view.close.called


def test_cancel_not_accepted(note_view):
    note_view.cancel(None)
    assert not note_view.accepted


# ----
# ok()
# ----
def test_ok_closes_view(note_view):
    note_view.ok(None)
    assert note_view.view.close.called


def test_ok_accepted(note_view):
    note_view.ok(None)
    assert note_view.accepted
