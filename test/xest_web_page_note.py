# pylint: disable=missing-docstring,redefined-outer-name
import sys
import os
# from unittest.mock import MagicMock

import pytest

sys.path.append(
    os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir)))

# pylint: disable=wrong-import-position
from ithoughts_notes import WebPageNote  # NOQA
# pylint: enable=wrong-import-position


@pytest.fixture
def assest_dir(request):
    filename = os.path.realpath(request.module.__file__)
    directory, _ = os.path.splitext(filename)
    return directory


@pytest.fixture
def web_note(assest_dir):
    url = 'http://foo.bar.local/haa/bang/boom.html'
    filename = os.path.join(assest_dir, 'happy_test.html')
    with open(filename, 'r') as file:
        return WebPageNote(url, file)


def test_sane_defaults(web_note):
    assert web_note.title == 'A Simple HTML Document'
    assert web_note.url == 'http://foo.bar.local/haa/bang/boom.html'
    assert web_note.body == (
        '## A Simple HTML Document\n\n'
        'This is a very simple HTML document\n\n'
        '_[quick link](http://foo.bar.local/haa/bang/boom.html)_')
